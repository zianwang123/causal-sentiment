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
            lag_hours = edge_data.get("transmission_lag_hours", 0.0)
            lag_factor = 1.0 / (1.0 + 0.1 * lag_hours) if lag_hours > 0 else 1.0

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
