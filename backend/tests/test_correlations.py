"""Tests for the correlation and dynamic weight system."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.graph_engine.correlations import (
    _align_timeseries,
    _pearson_correlation,
    update_dynamic_weights,
)
from app.models.graph import EdgeDirection


# --- _align_timeseries tests ---


def _ts(hours_offsets: list[int], values: list[float]) -> list[tuple[datetime, float]]:
    """Helper: create a time series from hour offsets and values."""
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    from datetime import timedelta
    return [(base + timedelta(hours=h), v) for h, v in zip(hours_offsets, values)]


def test_align_timeseries_basic():
    # Two series with overlapping 6h buckets
    ts_a = _ts([0, 1, 6, 7, 12, 13, 18, 19, 24], [1, 2, 3, 4, 5, 6, 7, 8, 9])
    ts_b = _ts([0, 6, 12, 18, 24], [10, 20, 30, 40, 50])
    a, b = _align_timeseries(ts_a, ts_b, bucket_hours=6)
    assert len(a) == 5
    assert len(b) == 5


def test_align_timeseries_empty():
    a, b = _align_timeseries([], [], bucket_hours=6)
    assert len(a) == 0
    assert len(b) == 0

    a, b = _align_timeseries(_ts([0], [1.0]), [], bucket_hours=6)
    assert len(a) == 0


def test_align_timeseries_no_overlap():
    ts_a = _ts([0, 6, 12, 18, 24], [1, 2, 3, 4, 5])
    ts_b = _ts([1000, 1006, 1012, 1018, 1024], [10, 20, 30, 40, 50])
    a, b = _align_timeseries(ts_a, ts_b, bucket_hours=6)
    assert len(a) == 0  # No common buckets


def test_align_timeseries_insufficient_buckets():
    # Only 3 common buckets, below min_data_points=5
    ts_a = _ts([0, 6, 12], [1, 2, 3])
    ts_b = _ts([0, 6, 12], [10, 20, 30])
    a, b = _align_timeseries(ts_a, ts_b, bucket_hours=6)
    assert len(a) == 0  # Insufficient


# --- _pearson_correlation tests ---


def test_pearson_positive():
    a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    b = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
    corr = _pearson_correlation(a, b)
    assert corr is not None
    assert abs(corr - 1.0) < 0.001


def test_pearson_negative():
    a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    b = np.array([10.0, 8.0, 6.0, 4.0, 2.0])
    corr = _pearson_correlation(a, b)
    assert corr is not None
    assert abs(corr - (-1.0)) < 0.001


def test_pearson_insufficient_data():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])
    corr = _pearson_correlation(a, b)
    assert corr is None


def test_pearson_constant_series():
    a = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
    b = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    corr = _pearson_correlation(a, b)
    assert corr is None  # Zero std


# --- update_dynamic_weights direction flip tests ---


def _make_mock_edge(source_id, target_id, direction, base_weight=0.5, dynamic_weight=0.5):
    """Create a mock Edge object."""
    edge = MagicMock()
    edge.source_id = source_id
    edge.target_id = target_id
    edge.direction = direction
    edge.base_weight = base_weight
    edge.dynamic_weight = dynamic_weight
    return edge


def _mock_graph_for_edge(source_id, target_id):
    """Create a mock NetworkX graph that supports graph[source][target] access."""
    edge_data = {"dynamic_weight": 0.5, "effective_weight": 0.5, "direction": EdgeDirection.POSITIVE}
    graph = MagicMock()
    graph.has_edge.return_value = True
    # NetworkX uses graph[source][target] which is dict-of-dict access
    graph.__getitem__ = MagicMock(return_value={target_id: edge_data})
    return graph, edge_data


def _mock_session_with_edges(edges):
    """Create a mock session that returns given edges from execute()."""
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = edges
    session.execute.return_value = mock_result
    return session


@pytest.mark.asyncio
async def test_direction_flip_on_sign_disagreement():
    """POSITIVE edge with strong negative correlation should flip to NEGATIVE."""
    edge = _make_mock_edge("A", "B", EdgeDirection.POSITIVE, 0.5, 0.5)
    session = _mock_session_with_edges([edge])
    graph, _ = _mock_graph_for_edge("A", "B")

    with patch("app.graph_engine.correlations.compute_pairwise_correlations") as mock_corr:
        mock_corr.return_value = {("A", "B"): -0.8}
        updated = await update_dynamic_weights(session, graph, direction_flip_threshold=0.3)

    assert updated == 1
    assert edge.direction == EdgeDirection.NEGATIVE


@pytest.mark.asyncio
async def test_no_direction_flip_below_threshold():
    """Weak negative correlation should NOT flip a POSITIVE edge."""
    edge = _make_mock_edge("A", "B", EdgeDirection.POSITIVE, 0.5, 0.5)
    session = _mock_session_with_edges([edge])
    graph, _ = _mock_graph_for_edge("A", "B")

    with patch("app.graph_engine.correlations.compute_pairwise_correlations") as mock_corr:
        mock_corr.return_value = {("A", "B"): -0.15}  # Below 0.3 threshold
        await update_dynamic_weights(session, graph, direction_flip_threshold=0.3)

    # Direction should remain POSITIVE (weak correlation, not enough to flip)
    assert edge.direction == EdgeDirection.POSITIVE


@pytest.mark.asyncio
async def test_complex_direction_never_flips():
    """COMPLEX edges should never have their direction changed."""
    edge = _make_mock_edge("A", "B", EdgeDirection.COMPLEX, 0.5, 0.5)
    session = _mock_session_with_edges([edge])
    graph, _ = _mock_graph_for_edge("A", "B")

    with patch("app.graph_engine.correlations.compute_pairwise_correlations") as mock_corr:
        mock_corr.return_value = {("A", "B"): -0.9}  # Strong negative
        await update_dynamic_weights(session, graph, direction_flip_threshold=0.3)

    assert edge.direction == EdgeDirection.COMPLEX


@pytest.mark.asyncio
async def test_negative_edge_flips_to_positive():
    """NEGATIVE edge with strong positive correlation should flip to POSITIVE."""
    edge = _make_mock_edge("A", "B", EdgeDirection.NEGATIVE, 0.5, 0.5)
    session = _mock_session_with_edges([edge])
    graph, _ = _mock_graph_for_edge("A", "B")

    with patch("app.graph_engine.correlations.compute_pairwise_correlations") as mock_corr:
        mock_corr.return_value = {("A", "B"): 0.85}
        await update_dynamic_weights(session, graph, direction_flip_threshold=0.3)

    assert edge.direction == EdgeDirection.POSITIVE
