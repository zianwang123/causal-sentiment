"""Prediction resolution — compares agent predictions against actual outcomes."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.observations import Prediction, SentimentObservation

logger = logging.getLogger(__name__)


async def resolve_expired_predictions(session: AsyncSession) -> int:
    """Resolve all predictions whose horizon has expired.

    For each expired prediction, looks up the latest agent sentiment observation
    for that node and compares predicted vs actual direction.

    Returns count of newly resolved predictions.
    """
    now = datetime.now(UTC)

    # Find unresolved predictions whose horizon has passed
    result = await session.execute(
        select(Prediction).where(
            Prediction.resolved_at.is_(None),
        )
    )
    predictions = result.scalars().all()

    resolved_count = 0
    for pred in predictions:
        horizon_end = pred.created_at + timedelta(hours=pred.horizon_hours)
        if horizon_end > now:
            continue  # Not expired yet

        # Get latest sentiment observation for this node near/after horizon
        # Check agent observations first, fall back to market/FRED data
        source_priority = case(
            (SentimentObservation.source.in_(["agent", "deep_dive"]), 0),
            else_=1,
        )
        obs_result = await session.execute(
            select(SentimentObservation)
            .where(SentimentObservation.node_id == pred.node_id)
            .where(SentimentObservation.source.in_(["agent", "deep_dive", "market_scheduled", "fred_scheduled"]))
            .where(SentimentObservation.created_at >= pred.created_at)
            .order_by(source_priority, SentimentObservation.created_at.desc())
            .limit(1)
        )
        obs = obs_result.scalar_one_or_none()

        if obs is None:
            # No observation to compare against — resolve as inconclusive
            pred.resolved_at = now
            pred.hit = None
            resolved_count += 1
            continue

        actual = obs.sentiment
        pred.actual_sentiment = actual
        pred.resolved_at = now

        # Direction matching
        direction = pred.predicted_direction.lower()
        if direction == "bullish":
            pred.hit = 1 if actual > 0 else 0
        elif direction == "bearish":
            pred.hit = 1 if actual < 0 else 0
        elif direction == "neutral":
            pred.hit = 1 if abs(actual) < 0.2 else 0
        else:
            pred.hit = None

        # Magnitude accuracy: how close was the predicted sentiment to actual?
        # Score 1.0 = perfect match, 0.0 = off by ≥1.0 (max possible in [-1, 1])
        if pred.predicted_sentiment is not None:
            error = abs(pred.predicted_sentiment - actual)
            pred.magnitude_score = round(max(0.0, 1.0 - error), 3)

        resolved_count += 1

    if resolved_count > 0:
        await session.commit()

    return resolved_count
