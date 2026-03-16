"""Node importance ranking — combined centrality score.

Score = 0.4 * degree_centrality + 0.4 * betweenness_centrality + 0.2 * eigenvector_centrality

Eigenvector centrality may fail to converge on some graph topologies;
in that case we fall back to in-degree centrality as a substitute.
"""
from __future__ import annotations

import logging
from typing import Any

import networkx as nx

logger = logging.getLogger(__name__)

_W_DEGREE = 0.4
_W_BETWEENNESS = 0.4
_W_EIGENVECTOR = 0.2


def rank_nodes_by_importance(
    g: nx.DiGraph,
    top_n: int | None = None,
) -> list[dict[str, Any]]:
    """Rank nodes by combined centrality score.

    Parameters
    ----------
    g : nx.DiGraph
        Causal graph (edges may have ``weight`` attribute).
    top_n : int | None
        If set, return only the top N nodes.

    Returns
    -------
    list[dict]
        Sorted list (descending) of {node_id, score, degree, betweenness,
        eigenvector} dicts.
    """
    if len(g) == 0:
        return []

    degree = nx.degree_centrality(g)
    betweenness = nx.betweenness_centrality(g, weight="weight")

    try:
        eigenvector = nx.eigenvector_centrality(
            g, max_iter=1000, weight="weight"
        )
    except (nx.PowerIterationFailedConvergence, nx.NetworkXException):
        logger.warning(
            "Eigenvector centrality failed to converge; falling back to in-degree centrality"
        )
        eigenvector = nx.in_degree_centrality(g)

    # Normalize each metric to [0, 1] range
    def _normalize(d: dict[str, float]) -> dict[str, float]:
        vals = list(d.values())
        max_val = max(vals) if vals else 1.0
        if max_val == 0:
            return {k: 0.0 for k in d}
        return {k: v / max_val for k, v in d.items()}

    deg_norm = _normalize(degree)
    bet_norm = _normalize(betweenness)
    eig_norm = _normalize(eigenvector)

    ranking: list[dict[str, Any]] = []
    for node in g.nodes():
        d = deg_norm.get(node, 0.0)
        b = bet_norm.get(node, 0.0)
        e = eig_norm.get(node, 0.0)
        score = _W_DEGREE * d + _W_BETWEENNESS * b + _W_EIGENVECTOR * e
        ranking.append({
            "node_id": node,
            "score": round(score, 6),
            "degree": round(d, 6),
            "betweenness": round(b, 6),
            "eigenvector": round(e, 6),
        })

    ranking.sort(key=lambda r: r["score"], reverse=True)

    if top_n is not None:
        ranking = ranking[:top_n]

    return ranking
