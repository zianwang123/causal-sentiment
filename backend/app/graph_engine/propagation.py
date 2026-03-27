"""Weighted BFS impact propagation through the causal factor graph."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import networkx as nx

from app.config import settings
from app.models.graph import EdgeDirection


@dataclass
class PropagationResult:
    """Result of propagating a signal through the graph."""
    source_node: str
    initial_signal: float
    impacts: dict[str, float] = field(default_factory=dict)
    paths: dict[str, list[str]] = field(default_factory=dict)


def propagate_signal(
    graph: nx.DiGraph,
    source_node: str,
    signal: float,
    max_depth: int | None = None,
    decay_per_hop: float | None = None,
    min_threshold: float | None = None,
    regime: str | None = None,
) -> PropagationResult:
    """Propagate a sentiment signal from source through the causal graph.

    Uses weighted BFS with exponential decay. Multiple paths to the same
    node are summed (interference pattern).
    """
    if max_depth is None:
        max_depth = settings.propagation_max_depth
    if decay_per_hop is None:
        decay_per_hop = settings.propagation_decay_per_hop
    if min_threshold is None:
        min_threshold = settings.propagation_min_threshold

    result = PropagationResult(source_node=source_node, initial_signal=signal)

    if source_node not in graph:
        return result

    # BFS queue: (node_id, current_signal, depth, path)
    queue: deque[tuple[str, float, int, list[str]]] = deque()
    queue.append((source_node, signal, 0, [source_node]))

    visited_edges: set[tuple[str, str]] = set()

    while queue:
        node_id, current_signal, depth, path = queue.popleft()

        if depth >= max_depth:
            continue

        for _, target_id, edge_data in graph.out_edges(node_id, data=True):
            edge_key = (node_id, target_id)
            if edge_key in visited_edges:
                continue
            visited_edges.add(edge_key)

            weight = edge_data.get("effective_weight", edge_data.get("base_weight", 0.5))
            direction = edge_data.get("direction", EdgeDirection.POSITIVE)

            if direction == EdgeDirection.POSITIVE:
                direction_sign = 1.0
            elif direction == EdgeDirection.NEGATIVE:
                direction_sign = -1.0
            else:
                direction_sign = 0.5  # complex — attenuated positive

            # Regime-aware decay: in risk-off, fear propagates faster (less decay on negative edges)
            effective_decay = decay_per_hop
            if regime == "risk_off":
                effective_decay = decay_per_hop * 0.7 if direction_sign < 0 else decay_per_hop * 1.3
            elif regime == "risk_on":
                effective_decay = decay_per_hop * 1.3 if direction_sign < 0 else decay_per_hop * 0.7
            effective_decay = min(0.9, max(0.1, effective_decay))

            # Transmission lag: longer lag = more decay
            # Tuned for report lag ranges: hours→0.96, days→0.81, weeks→0.37, months→0.12, quarters→0.04
            lag_hours = edge_data.get("transmission_lag_hours", 0.0)
            lag_factor = 1.0 / (1.0 + 0.01 * lag_hours) if lag_hours > 0 else 1.0

            # Regime-dependent edge sign override (from edge metadata)
            metadata = edge_data.get("metadata", {}) or {}
            regime_behavior = metadata.get("regime_behavior", {})
            if regime and regime in regime_behavior:
                rb = regime_behavior[regime]
                if rb == "+":
                    direction_sign = 1.0
                elif rb == "-":
                    direction_sign = -1.0
                # Weight modifier from threshold dynamics
            threshold_cfg = metadata.get("threshold", {})
            if threshold_cfg:
                trigger_level = threshold_cfg.get("normalized_level", 1.0)
                source_sentiment = abs(graph.nodes[node_id].get("composite_sentiment", 0.0))
                if source_sentiment >= trigger_level:
                    weight *= threshold_cfg.get("multiplier", 2.0)

            propagated = current_signal * weight * direction_sign * (1 - effective_decay) * lag_factor

            if abs(propagated) < min_threshold:
                continue

            # Sum multiple paths (interference)
            if target_id in result.impacts:
                result.impacts[target_id] += propagated
            else:
                result.impacts[target_id] = propagated

            # Clamp to [-1, 1]
            result.impacts[target_id] = max(-1.0, min(1.0, result.impacts[target_id]))

            # Track first path only
            if target_id not in result.paths:
                result.paths[target_id] = path + [target_id]

            queue.append((target_id, propagated, depth + 1, path + [target_id]))

    return result


def _compress_impact(impact: float, stress_mult: float) -> float:
    """Apply stress multiplier + sigmoid compression for extreme values.

    When multiple shocks fire simultaneously, total impact is scaled by the
    stress multiplier (> 1.0 for 4+ shocks). Impacts near ±1.0 are compressed
    via a sigmoid-like curve to model diminishing returns.
    """
    import math

    adjusted = impact * stress_mult
    if abs(adjusted) > 0.8:
        sign = 1.0 if adjusted > 0 else -1.0
        excess = abs(adjusted) - 0.8
        compressed = 0.8 + 0.2 * (1 - math.exp(-excess * 2.5))
        adjusted = sign * compressed
    return max(-1.0, min(1.0, adjusted))


def merge_multi_shock_impacts(
    shocks: list[dict],
    graph: nx.DiGraph,
    regime_val: str | None = None,
) -> tuple[dict[str, dict], float]:
    """Propagate multiple shocks and merge impacts with non-linear interaction.

    For each shock, runs propagate_signal independently, then merges impacts
    additively. When 4+ shocks fire simultaneously, a stress multiplier
    amplifies the combined impact (modeling systemic stress). Extreme values
    are compressed via sigmoid to model diminishing returns.

    Returns (merged_impacts, stress_multiplier) where merged_impacts maps
    node_id -> {"total_impact": float, "contributing_shocks": list, "hops": int}.
    """
    shocked_ids = {s.get("node_id") for s in shocks if s.get("node_id")}
    merged: dict[str, dict] = {}

    valid_shocks = 0
    for shock in shocks:
        nid = shock.get("node_id", "")
        shock_value = shock.get("shock_value", 0.0)
        if not nid or nid not in graph:
            continue

        current = graph.nodes[nid].get("composite_sentiment", 0.0) or 0.0
        delta = shock_value - current
        if abs(delta) < 0.001:
            continue

        valid_shocks += 1
        prop_result = propagate_signal(graph, nid, delta, regime=regime_val)

        for affected_nid, impact in prop_result.impacts.items():
            if affected_nid in shocked_ids:
                continue

            if affected_nid not in merged:
                merged[affected_nid] = {
                    "total_impact": 0.0,
                    "contributing_shocks": [],
                    "hops": len(prop_result.paths.get(affected_nid, [])) - 1,
                }

            merged[affected_nid]["total_impact"] += impact
            merged[affected_nid]["contributing_shocks"].append(nid)
            new_hops = len(prop_result.paths.get(affected_nid, [])) - 1
            if new_hops > 0:
                merged[affected_nid]["hops"] = min(
                    merged[affected_nid]["hops"], new_hops
                )

    # Non-linear interaction: stress multiplier for simultaneous shocks
    stress_multiplier = 1.0
    if valid_shocks > 3:
        stress_multiplier = 1.0 + 0.15 * (valid_shocks - 3)

    # Apply stress multiplier + sigmoid compression
    for nid in merged:
        merged[nid]["total_impact"] = _compress_impact(
            merged[nid]["total_impact"], stress_multiplier
        )

    return merged, stress_multiplier


def build_networkx_graph(nodes: list[dict], edges: list[dict]) -> nx.DiGraph:
    """Build a NetworkX DiGraph from node and edge dicts."""
    g = nx.DiGraph()

    for node in nodes:
        g.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})

    base_ratio = settings.edge_weight_base_ratio
    for edge in edges:
        base_w = edge.get("base_weight", 0.5)
        dyn_w = edge.get("dynamic_weight", 0.5)
        effective_weight = base_ratio * base_w + (1 - base_ratio) * dyn_w
        g.add_edge(
            edge["source_id"],
            edge["target_id"],
            direction=edge.get("direction", EdgeDirection.POSITIVE),
            base_weight=base_w,
            dynamic_weight=dyn_w,
            effective_weight=effective_weight,
            transmission_lag_hours=edge.get("transmission_lag_hours", 0.0),
            description=edge.get("description", ""),
        )

    return g
