"""Graph weight utilities and centrality calculations."""

import time

import networkx as nx
import numpy as np

from app.config import settings

_centrality_cache: dict[str, float] | None = None
_centrality_cache_time: float = 0.0


def compute_centralities(graph: nx.DiGraph) -> dict[str, float]:
    """Compute eigenvector centrality for node sizing in viz.

    Cached with configurable TTL to avoid recomputation on every request.
    """
    global _centrality_cache, _centrality_cache_time
    now = time.monotonic()
    if _centrality_cache is not None and (now - _centrality_cache_time) < settings.centrality_cache_ttl:
        return _centrality_cache

    try:
        result = nx.eigenvector_centrality_numpy(graph, weight="effective_weight")
    except Exception:
        # Fallback for disconnected graphs
        result = nx.degree_centrality(graph)

    _centrality_cache = result
    _centrality_cache_time = now
    return result


def invalidate_centrality_cache() -> None:
    """Invalidate the centrality cache (call after topology changes)."""
    global _centrality_cache
    _centrality_cache = None


def clamp_sentiment(value: float) -> float:
    return max(-1.0, min(1.0, value))


def exponential_decay(value: float, age_hours: float, half_life_hours: float | None = None) -> float:
    """Apply exponential decay to a sentiment value based on age."""
    if half_life_hours is None:
        half_life_hours = settings.sentiment_half_life_hours
    decay_factor = np.exp(-0.693 * age_hours / half_life_hours)
    return value * decay_factor
