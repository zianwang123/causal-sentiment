"""Anchor polarity propagation via BFS through a causal graph.

Anchors are nodes with known polarity (e.g. sp500 = +1 means "up is good
from an equity perspective"). Polarity propagates BIDIRECTIONALLY through
edges: positive edges preserve the sign, negative edges flip it.

Bidirectional propagation is essential because discovered causal graphs are
sparse and many nodes only have incoming edges from anchors (not outgoing).
Forward-only BFS would miss them. The sign-flip rule is symmetric:
  - Forward:  A → B (negative) means A_polarity × (-1) = B_polarity
  - Backward: A → B (negative) means B_polarity × (-1) = A_polarity
"""
from __future__ import annotations

import logging
from collections import deque
from typing import Dict

import networkx as nx

logger = logging.getLogger(__name__)


def propagate_polarity(
    g: nx.DiGraph,
    anchors: Dict[str, int],
) -> Dict[str, int]:
    """Bidirectional BFS polarity propagation from anchor nodes.

    Traverses edges in BOTH directions (outgoing and incoming). The edge
    direction attribute (positive/negative) determines sign flipping
    regardless of traversal direction. This ensures all nodes in the
    connected component are reached, not just downstream nodes.

    Parameters
    ----------
    g : nx.DiGraph
        Causal graph. Edges should have a ``direction`` attribute
        ("positive" or "negative") and optionally a ``weight``.
    anchors : dict[str, int]
        Mapping of anchor node_id to polarity (+1 or -1).

    Returns
    -------
    dict[str, int]
        Mapping of every reachable node_id to its inferred polarity
        (+1, -1, or 0 if signals cancel out).
    """
    signal: Dict[str, float] = {}

    for anchor_id, anchor_pol in anchors.items():
        if anchor_id not in g:
            continue
        signal.setdefault(anchor_id, 0.0)
        signal[anchor_id] += float(anchor_pol)

        # BFS from this anchor — follow edges in BOTH directions
        queue: deque[tuple[str, float]] = deque()
        queue.append((anchor_id, float(anchor_pol)))
        visited: set[str] = {anchor_id}

        while queue:
            node, current_pol = queue.popleft()

            # Forward: follow outgoing edges (node → neighbor)
            for _, neighbor, edge_data in g.out_edges(node, data=True):
                direction = edge_data.get("direction", "positive")
                multiplier = -1.0 if direction == "negative" else 1.0
                neighbor_pol = current_pol * multiplier

                signal.setdefault(neighbor, 0.0)
                signal[neighbor] += neighbor_pol

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, neighbor_pol))

            # Backward: follow incoming edges (neighbor → node)
            # Same sign-flip rule applies: if neighbor → node is negative,
            # neighbor has opposite polarity to node
            for neighbor, _, edge_data in g.in_edges(node, data=True):
                direction = edge_data.get("direction", "positive")
                multiplier = -1.0 if direction == "negative" else 1.0
                neighbor_pol = current_pol * multiplier

                signal.setdefault(neighbor, 0.0)
                signal[neighbor] += neighbor_pol

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, neighbor_pol))

    # Convert accumulated signal to discrete polarity.
    # Anchors always keep their defined polarity (cannot be overridden by
    # conflicting path signals).
    polarity: Dict[str, int] = {}
    for node_id, val in signal.items():
        # Lock anchor polarity — don't let path signals cancel it
        if node_id in anchors:
            polarity[node_id] = anchors[node_id]
        elif val > 0:
            polarity[node_id] = 1
        elif val < 0:
            polarity[node_id] = -1
        else:
            polarity[node_id] = 0

    logger.info(
        "Propagated polarity from %d anchor(s) to %d node(s) (bidirectional)",
        len(anchors),
        len(polarity),
    )
    return polarity
