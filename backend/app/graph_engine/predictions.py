"""Prediction resolution — compares agent predictions against actual outcomes."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.observations import Prediction, SentimentObservation

logger = logging.getLogger(__name__)


async def resolve_expired_predictions(session: AsyncSession) -> int:
    """Resolve all predictions whose horizon has expired.

    For each expired prediction, looks up the latest agent sentiment observation
    for that node and compares predicted vs actual direction.

    Returns count of newly resolved predictions.
    """
    now = datetime.utcnow()

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

        # Get latest agent sentiment observation for this node near/after horizon
        obs_result = await session.execute(
            select(SentimentObservation)
            .where(SentimentObservation.node_id == pred.node_id)
            .where(SentimentObservation.source.in_(["agent", "deep_dive"]))
            .where(SentimentObservation.created_at >= pred.created_at)
            .order_by(SentimentObservation.created_at.desc())
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

        resolved_count += 1

    if resolved_count > 0:
        await session.commit()

    return resolved_count
