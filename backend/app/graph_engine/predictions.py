"""Prediction resolution — compares agent predictions against actual outcomes."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

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

        # Get latest sentiment observation for this node near/after horizon
        # Check agent observations first, fall back to market/FRED data
        source_priority = case(
            (SentimentObservation.source.in_(["agent", "deep_dive"]), 0),
            else_=1,
        )
        obs_result = await session.execute(
            select(SentimentObservation)
            .where(SentimentObservation.node_id == pred.node_id)
            .where(SentimentObservation.source.in_(["agent", "deep_dive", "market_scheduled", "fred_scheduled", "reddit_scheduled", "news_scheduled"]))
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


async def resolve_scenario_predictions(session: AsyncSession) -> int:
    """Resolve expired scenario predictions by checking against actual market data.

    For market-related predictions (those with a ticker + threshold), fetches the
    current price via yfinance and compares against the threshold.
    Qualitative predictions (no ticker) are marked as 'unresolvable'.
    """
    import asyncio
    from app.models.scenarios import ScenarioPrediction

    now = datetime.utcnow()

    result = await session.execute(
        select(ScenarioPrediction).where(
            ScenarioPrediction.resolved_at.is_(None),
            ScenarioPrediction.expires_at.isnot(None),
            ScenarioPrediction.expires_at <= now,
        )
    )
    predictions = result.scalars().all()

    if not predictions:
        return 0

    # Batch unique tickers to minimize yfinance calls
    tickers_needed = set()
    for pred in predictions:
        if pred.ticker and pred.threshold_value is not None:
            tickers_needed.add(pred.ticker)

    # Fetch current prices for all needed tickers
    ticker_prices: dict[str, float] = {}
    if tickers_needed:
        try:
            import yfinance as yf

            def _fetch_prices(tickers: list[str]) -> dict[str, float]:
                prices = {}
                for ticker in tickers:
                    try:
                        data = yf.download(ticker, period="1d", interval="1d", progress=False)
                        if not data.empty:
                            if hasattr(data.columns, "levels") and len(data.columns.levels) > 1:
                                data.columns = data.columns.droplevel(1)
                            prices[ticker] = float(data["Close"].iloc[-1])
                    except Exception as e:
                        logger.warning("Failed to fetch price for %s: %s", ticker, e)
                return prices

            ticker_prices = await asyncio.to_thread(_fetch_prices, list(tickers_needed))
        except Exception as e:
            logger.warning("Failed to fetch ticker prices for scenario resolution: %s", e)

    resolved_count = 0
    for pred in predictions:
        if pred.ticker and pred.threshold_value is not None and pred.ticker in ticker_prices:
            # Market-resolvable prediction
            actual = ticker_prices[pred.ticker]
            pred.actual_value = actual
            pred.resolved_at = now
            pred.resolution_type = "market_resolved"

            if pred.threshold_direction == "above":
                pred.hit = actual >= pred.threshold_value
            elif pred.threshold_direction == "below":
                pred.hit = actual <= pred.threshold_value
            else:
                pred.hit = None
                pred.resolution_type = "unresolvable"
        else:
            # Qualitative prediction — can't auto-resolve
            pred.resolved_at = now
            pred.resolution_type = "unresolvable"
            pred.hit = None

        resolved_count += 1

    if resolved_count > 0:
        await session.commit()

    return resolved_count
