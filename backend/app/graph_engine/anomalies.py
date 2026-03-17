"""Anomaly detection for graph nodes based on z-score analysis."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.observations import SentimentObservation

logger = logging.getLogger(__name__)


@dataclass
class Anomaly:
    node_id: str
    z_score: float
    latest_value: float
    mean: float
    std: float
    direction: str  # "up" or "down"
    detected_at: datetime


async def detect_anomalies(
    session: AsyncSession,
    lookback_days: int = 30,
    z_threshold: float | None = None,
) -> list[Anomaly]:
    """Detect nodes where the latest observation deviates >z_threshold from recent mean.

    Uses raw_data numeric values (FRED series values, market prices) when available,
    falls back to sentiment scores.
    """
    if z_threshold is None:
        z_threshold = settings.anomaly_z_threshold
    min_obs = settings.anomaly_min_observations

    # Get all nodes with recent observations
    cutoff = datetime.utcnow() - timedelta(days=lookback_days)
    result = await session.execute(
        select(SentimentObservation)
        .where(SentimentObservation.created_at >= cutoff)
        .order_by(SentimentObservation.node_id, SentimentObservation.created_at.asc())
    )
    observations = result.scalars().all()

    # Group by node_id
    node_obs: dict[str, list[SentimentObservation]] = {}
    for obs in observations:
        node_obs.setdefault(obs.node_id, []).append(obs)

    anomalies: list[Anomaly] = []

    for node_id, obs_list in node_obs.items():
        if len(obs_list) < min_obs:
            continue

        # Extract numeric values — prefer raw_data price/value, fallback to sentiment
        values = []
        for obs in obs_list:
            val = _extract_numeric(obs)
            if val is not None:
                values.append(val)

        if len(values) < min_obs:
            continue

        arr = np.array(values)
        mean = float(np.mean(arr[:-1]))  # Mean of all but latest
        std = float(np.std(arr[:-1]))
        latest = float(arr[-1])

        if std < 1e-10:  # No variance — can't detect anomalies
            continue

        z_score = (latest - mean) / std

        if abs(z_score) >= z_threshold:
            anomalies.append(Anomaly(
                node_id=node_id,
                z_score=round(z_score, 2),
                latest_value=round(latest, 4),
                mean=round(mean, 4),
                std=round(std, 4),
                direction="up" if z_score > 0 else "down",
                detected_at=datetime.utcnow(),
            ))

    anomalies.sort(key=lambda a: abs(a.z_score), reverse=True)
    logger.info("Anomaly detection: found %d anomalies across %d nodes", len(anomalies), len(node_obs))
    return anomalies


def _extract_numeric(obs: SentimentObservation) -> float | None:
    """Extract the best numeric value from an observation."""
    raw = obs.raw_data
    if isinstance(raw, dict):
        # Market data: use close price
        if "close" in raw:
            try:
                return float(raw["close"])
            except (ValueError, TypeError):
                pass
        # Market data: use change_pct for comparison
        if "change_pct" in raw:
            try:
                return float(raw["change_pct"])
            except (ValueError, TypeError):
                pass
        # FRED data: use latest observation value
        if "observations" in raw and isinstance(raw["observations"], list):
            try:
                return float(raw["observations"][0]["value"])
            except (IndexError, KeyError, ValueError, TypeError):
                pass
    # Fallback to sentiment score
    if obs.sentiment != 0.0:
        return obs.sentiment
    return None
