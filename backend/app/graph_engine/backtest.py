"""Backtesting engine — measures sentiment prediction accuracy against actual returns."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data_pipeline.market import MARKET_TICKER_MAP
from app.models.observations import SentimentObservation

logger = logging.getLogger(__name__)

# Reverse map: node_id -> ticker
NODE_TO_TICKER = {v: k for k, v in MARKET_TICKER_MAP.items()}


@dataclass
class BacktestResult:
    node_id: str
    correlation: float | None = None
    hit_rate: float | None = None
    ic: float | None = None  # Information coefficient
    n_observations: int = 0
    avg_return_bullish: float | None = None
    avg_return_bearish: float | None = None
    scatter_points: list[list[float]] = field(default_factory=list)  # [[sentiment, return], ...]


async def backtest_node(
    session: AsyncSession,
    node_id: str,
    lookback_days: int = 90,
    forward_days: int = 5,
) -> BacktestResult:
    """Backtest sentiment predictions for a single node.

    For each agent-sourced sentiment observation, looks up market return
    over the next forward_days and computes predictive stats.
    """
    result = BacktestResult(node_id=node_id)

    cutoff = datetime.utcnow() - timedelta(days=lookback_days)

    # Get agent sentiment observations
    sent_result = await session.execute(
        select(SentimentObservation)
        .where(SentimentObservation.node_id == node_id)
        .where(SentimentObservation.source.in_(["agent", "deep_dive"]))
        .where(SentimentObservation.created_at >= cutoff)
        .order_by(SentimentObservation.created_at.asc())
    )
    sentiment_obs = sent_result.scalars().all()

    if len(sentiment_obs) < 3:
        return result

    # Get market price observations for this node
    market_result = await session.execute(
        select(SentimentObservation)
        .where(SentimentObservation.node_id == node_id)
        .where(SentimentObservation.source == "market_scheduled")
        .where(SentimentObservation.created_at >= cutoff)
        .order_by(SentimentObservation.created_at.asc())
    )
    market_obs = market_result.scalars().all()

    if len(market_obs) < 3:
        return result

    # Build a price time series from market observations
    price_series: list[tuple[datetime, float]] = []
    for obs in market_obs:
        raw = obs.raw_data
        if isinstance(raw, dict) and "close" in raw:
            try:
                price_series.append((obs.created_at, float(raw["close"])))
            except (ValueError, TypeError):
                continue

    if len(price_series) < 3:
        return result

    # For each sentiment observation, find forward return
    pairs: list[tuple[float, float]] = []
    for sent_obs in sentiment_obs:
        sent_time = sent_obs.created_at
        sent_value = sent_obs.sentiment

        # Find price at sentiment time (closest before)
        price_at_signal = None
        for pt, pv in price_series:
            if pt <= sent_time:
                price_at_signal = pv
            else:
                break

        # Find price forward_days later
        forward_time = sent_time + timedelta(days=forward_days)
        price_forward = None
        for pt, pv in price_series:
            if pt <= forward_time:
                price_forward = pv

        if price_at_signal and price_forward and price_at_signal > 0:
            forward_return = (price_forward - price_at_signal) / price_at_signal
            pairs.append((sent_value, forward_return))

    result = compute_predictive_stats(node_id, pairs)
    return result


def compute_predictive_stats(node_id: str, pairs: list[tuple[float, float]]) -> BacktestResult:
    """Compute prediction quality metrics from (sentiment, return) pairs."""
    result = BacktestResult(node_id=node_id, n_observations=len(pairs))

    if len(pairs) < 5:
        result.scatter_points = [[s, r] for s, r in pairs]
        return result

    sentiments = np.array([p[0] for p in pairs])
    returns = np.array([p[1] for p in pairs])

    # Pearson correlation
    std_s, std_r = np.std(sentiments), np.std(returns)
    if std_s > 1e-10 and std_r > 1e-10:
        corr = np.corrcoef(sentiments, returns)[0, 1]
        if not np.isnan(corr):
            result.correlation = round(float(corr), 4)
            result.ic = result.correlation  # IC ≈ correlation for simple case

    # Hit rate: % of times sentiment direction matched return direction
    hits = sum(
        1 for s, r in pairs
        if (s > 0 and r > 0) or (s < 0 and r < 0) or (abs(s) < 0.05 and abs(r) < 0.005)
    )
    result.hit_rate = round(hits / len(pairs), 4) if pairs else None

    # Average return by sentiment direction
    bullish = [r for s, r in pairs if s > 0.1]
    bearish = [r for s, r in pairs if s < -0.1]
    if bullish:
        result.avg_return_bullish = round(float(np.mean(bullish)) * 100, 4)
    if bearish:
        result.avg_return_bearish = round(float(np.mean(bearish)) * 100, 4)

    result.scatter_points = [[round(s, 4), round(r * 100, 4)] for s, r in pairs]
    return result


async def backtest_all_nodes(
    session: AsyncSession,
    lookback_days: int = 90,
    forward_days: int = 5,
) -> list[BacktestResult]:
    """Run backtest for all nodes that have market data."""
    results: list[BacktestResult] = []

    # Only backtest nodes with market ticker mappings
    for node_id in NODE_TO_TICKER:
        bt = await backtest_node(session, node_id, lookback_days, forward_days)
        if bt.n_observations >= 3:
            results.append(bt)

    # Sort by hit rate descending
    results.sort(key=lambda r: r.hit_rate or 0, reverse=True)
    return results
