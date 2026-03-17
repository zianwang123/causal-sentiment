"""Tests for anomaly detection."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graph_engine.anomalies import _extract_numeric, detect_anomalies


# --- _extract_numeric tests ---


def _mock_obs(sentiment=0.0, raw_data=None):
    obs = MagicMock()
    obs.sentiment = sentiment
    obs.raw_data = raw_data
    return obs


def test_extract_numeric_close_price():
    obs = _mock_obs(raw_data={"close": 150.0})
    assert _extract_numeric(obs) == 150.0


def test_extract_numeric_change_pct():
    obs = _mock_obs(raw_data={"change_pct": 2.5})
    assert _extract_numeric(obs) == 2.5


def test_extract_numeric_fred_observations():
    obs = _mock_obs(raw_data={"observations": [{"value": "3.5"}]})
    assert _extract_numeric(obs) == 3.5


def test_extract_numeric_fallback_sentiment():
    obs = _mock_obs(sentiment=0.5, raw_data={})
    assert _extract_numeric(obs) == 0.5


def test_extract_numeric_zero_sentiment_none():
    obs = _mock_obs(sentiment=0.0, raw_data={})
    assert _extract_numeric(obs) is None


def test_extract_numeric_close_priority_over_sentiment():
    """raw_data close price should take priority over sentiment."""
    obs = _mock_obs(sentiment=0.8, raw_data={"close": 200.0})
    assert _extract_numeric(obs) == 200.0


def test_extract_numeric_invalid_close():
    """Non-numeric close should fall through to next option."""
    obs = _mock_obs(sentiment=0.3, raw_data={"close": "invalid"})
    # Should fall through to change_pct, then fred, then sentiment
    assert _extract_numeric(obs) == 0.3


# --- detect_anomalies tests ---


def _make_observations(node_id: str, values: list[float]) -> list:
    """Create mock SentimentObservation objects with raw_data close prices."""
    now = datetime.now(UTC)
    obs_list = []
    for i, v in enumerate(values):
        obs = MagicMock()
        obs.node_id = node_id
        obs.sentiment = 0.0
        obs.raw_data = {"close": v}
        obs.created_at = now - timedelta(hours=len(values) - i)
        obs_list.append(obs)
    return obs_list


@pytest.mark.asyncio
async def test_detect_anomalies_finds_outlier():
    """A 3σ move should be detected as anomalous."""
    # 9 normal values around 100, then one outlier at 130 (~3σ)
    values = [100, 101, 99, 100, 102, 98, 100, 101, 99, 130]
    mock_obs = _make_observations("test_node", values)

    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_obs
    session.execute.return_value = mock_result

    anomalies = await detect_anomalies(session, lookback_days=30, z_threshold=2.0)
    assert len(anomalies) == 1
    assert anomalies[0].node_id == "test_node"
    assert anomalies[0].direction == "up"


@pytest.mark.asyncio
async def test_detect_anomalies_skips_insufficient_data():
    """Nodes with fewer than min_observations should not produce anomalies."""
    mock_obs = _make_observations("test_node", [100, 101, 102])  # Only 3

    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_obs
    session.execute.return_value = mock_result

    anomalies = await detect_anomalies(session, lookback_days=30, z_threshold=2.0)
    assert len(anomalies) == 0


@pytest.mark.asyncio
async def test_detect_anomalies_respects_threshold():
    """A 1.5σ move with threshold=2.0 should NOT be flagged."""
    # Values around 100 with std ~1, then a 1.5σ outlier
    values = [100, 101, 99, 100, 101, 99, 100, 101, 99, 101.5]
    mock_obs = _make_observations("test_node", values)

    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_obs
    session.execute.return_value = mock_result

    anomalies = await detect_anomalies(session, lookback_days=30, z_threshold=2.0)
    assert len(anomalies) == 0
