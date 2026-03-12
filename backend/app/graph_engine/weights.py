"""Graph weight utilities and centrality calculations."""

import networkx as nx
import numpy as np


def compute_centralities(graph: nx.DiGraph) -> dict[str, float]:
    """Compute eigenvector centrality for node sizing in viz."""
    try:
        return nx.eigenvector_centrality_numpy(graph, weight="effective_weight")
    except Exception:
        # Fallback for disconnected graphs
        return nx.degree_centrality(graph)


def clamp_sentiment(value: float) -> float:
    return max(-1.0, min(1.0, value))


def exponential_decay(value: float, age_hours: float, half_life_hours: float = 24.0) -> float:
    """Apply exponential decay to a sentiment value based on age."""
    decay_factor = np.exp(-0.693 * age_hours / half_life_hours)
    return value * decay_factor
