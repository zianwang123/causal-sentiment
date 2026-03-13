"""Dynamic weight recalculation from empirical correlations."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.graph import Edge, EdgeDirection
from app.models.observations import SentimentObservation

logger = logging.getLogger(__name__)


async def _get_node_timeseries(
    session: AsyncSession,
    node_id: str,
    lookback_days: int,
) -> list[tuple[datetime, float]]:
    """Fetch sentiment observations as a time series for a node."""
    cutoff = datetime.utcnow() - timedelta(days=lookback_days)
    result = await session.execute(
        select(SentimentObservation.created_at, SentimentObservation.sentiment)
        .where(SentimentObservation.node_id == node_id)
        .where(SentimentObservation.created_at >= cutoff)
        .order_by(SentimentObservation.created_at.asc())
    )
    return [(row[0], row[1]) for row in result.all()]


def _align_timeseries(
    ts_a: list[tuple[datetime, float]],
    ts_b: list[tuple[datetime, float]],
    bucket_hours: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Align two irregular time series into matching buckets.

    Groups observations into time buckets and takes the mean within each bucket.
    Returns only buckets where both series have data.
    """
    if bucket_hours is None:
        bucket_hours = settings.correlation_bucket_hours

    if not ts_a or not ts_b:
        return np.array([]), np.array([])

    def to_buckets(ts: list[tuple[datetime, float]]) -> dict[int, list[float]]:
        buckets: dict[int, list[float]] = {}
        for dt, val in ts:
            ts_aware = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
            bucket_key = int(ts_aware.timestamp()) // (bucket_hours * 3600)
            buckets.setdefault(bucket_key, []).append(val)
        return {k: v for k, v in buckets.items()}

    buckets_a = to_buckets(ts_a)
    buckets_b = to_buckets(ts_b)

    min_data_points = settings.correlation_min_data_points
    common_keys = sorted(set(buckets_a.keys()) & set(buckets_b.keys()))
    if len(common_keys) < min_data_points:
        return np.array([]), np.array([])

    vals_a = np.array([np.mean(buckets_a[k]) for k in common_keys])
    vals_b = np.array([np.mean(buckets_b[k]) for k in common_keys])

    return vals_a, vals_b


def _pearson_correlation(a: np.ndarray, b: np.ndarray) -> float | None:
    """Compute Pearson correlation, returning None if insufficient data."""
    if len(a) < settings.correlation_min_data_points:
        return None
    std_a, std_b = np.std(a), np.std(b)
    if std_a < 1e-10 or std_b < 1e-10:
        return None
    corr = np.corrcoef(a, b)[0, 1]
    if np.isnan(corr):
        return None
    return float(corr)


async def compute_pairwise_correlations(
    session: AsyncSession,
    lookback_days: int = 90,
) -> dict[tuple[str, str], float]:
    """Compute correlations for all connected node pairs."""
    edges_result = await session.execute(select(Edge))
    edges = edges_result.scalars().all()

    # Collect unique node IDs from edges
    node_ids = set()
    for edge in edges:
        node_ids.add(edge.source_id)
        node_ids.add(edge.target_id)

    # Fetch time series for all relevant nodes
    ts_cache: dict[str, list[tuple[datetime, float]]] = {}
    for node_id in node_ids:
        ts_cache[node_id] = await _get_node_timeseries(session, node_id, lookback_days)

    # Compute correlations for each edge
    correlations: dict[tuple[str, str], float] = {}
    for edge in edges:
        ts_a = ts_cache.get(edge.source_id, [])
        ts_b = ts_cache.get(edge.target_id, [])

        aligned_a, aligned_b = _align_timeseries(ts_a, ts_b)
        corr = _pearson_correlation(aligned_a, aligned_b)

        if corr is not None:
            correlations[(edge.source_id, edge.target_id)] = corr

    return correlations


async def update_dynamic_weights(
    session: AsyncSession,
    graph,  # nx.DiGraph — avoid import for typing
    lookback_days: int | None = None,
    direction_flip_threshold: float | None = None,
) -> int:
    """Update dynamic_weight on edges from empirical correlations.

    When the sign of the empirical correlation strongly disagrees with the
    edge's declared direction, the direction is flipped (POSITIVE ↔ NEGATIVE).
    COMPLEX edges are never flipped.

    Returns the number of edges updated.
    """
    if lookback_days is None:
        lookback_days = settings.correlation_lookback_days
    if direction_flip_threshold is None:
        direction_flip_threshold = settings.correlation_direction_flip_threshold

    correlations = await compute_pairwise_correlations(session, lookback_days)

    if not correlations:
        logger.info("No correlations computed — insufficient data")
        return 0

    edges_result = await session.execute(select(Edge))
    edges = edges_result.scalars().all()

    base_ratio = settings.edge_weight_base_ratio
    updated = 0
    flipped = 0
    for edge in edges:
        corr = correlations.get((edge.source_id, edge.target_id))
        if corr is None:
            continue

        # Dynamic weight is correlation magnitude, clamped to [0.0, 1.0]
        new_dynamic_weight = min(1.0, max(0.0, abs(corr)))

        # Check if correlation sign disagrees with edge direction
        new_direction = edge.direction
        if edge.direction != EdgeDirection.COMPLEX:
            expected_positive = edge.direction == EdgeDirection.POSITIVE
            if expected_positive and corr < -direction_flip_threshold:
                new_direction = EdgeDirection.NEGATIVE
                flipped += 1
                logger.warning(
                    "Direction flip: %s → %s (was POSITIVE, corr=%.3f)",
                    edge.source_id, edge.target_id, corr,
                )
            elif not expected_positive and corr > direction_flip_threshold:
                new_direction = EdgeDirection.POSITIVE
                flipped += 1
                logger.warning(
                    "Direction flip: %s → %s (was NEGATIVE, corr=%.3f)",
                    edge.source_id, edge.target_id, corr,
                )

        # Only update if meaningfully different (avoid unnecessary DB writes)
        weight_changed = abs(new_dynamic_weight - edge.dynamic_weight) >= 0.01
        direction_changed = new_direction != edge.direction

        if not weight_changed and not direction_changed:
            continue

        edge.dynamic_weight = new_dynamic_weight
        if direction_changed:
            edge.direction = new_direction
        updated += 1

        # Update in-memory graph edge
        if graph.has_edge(edge.source_id, edge.target_id):
            edge_data = graph[edge.source_id][edge.target_id]
            edge_data["dynamic_weight"] = new_dynamic_weight
            edge_data["effective_weight"] = (
                base_ratio * edge.base_weight + (1 - base_ratio) * new_dynamic_weight
            )
            if direction_changed:
                edge_data["direction"] = new_direction

    await session.commit()
    logger.info(
        "Dynamic weights updated: %d edges (%d direction flips) from %d correlations",
        updated,
        flipped,
        len(correlations),
    )
    return updated
