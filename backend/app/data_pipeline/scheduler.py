"""APScheduler setup for periodic data fetching, agent triggers, and maintenance."""

from __future__ import annotations

import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scheduled_fred_fetch():
    """Fetch all FRED series and store as observations."""
    from app.data_pipeline.fred import fetch_all_fred_series
    from app.db.connection import async_session
    from app.models.observations import SentimentObservation
    from app.agent.tools import FRED_SERIES_MAP

    logger.info("Scheduled FRED fetch starting")
    try:
        data = await fetch_all_fred_series()
        async with async_session() as session:
            count = 0
            for series_id, observations in data.items():
                if not observations:
                    continue
                node_id = FRED_SERIES_MAP.get(series_id)
                if not node_id:
                    continue
                latest = observations[0]
                obs = SentimentObservation(
                    node_id=node_id,
                    sentiment=0.0,  # Raw data, not sentiment — agent will interpret
                    confidence=1.0,
                    source="fred_scheduled",
                    evidence=f"{series_id}: {latest['value']} ({latest['date']})",
                    raw_data={"series_id": series_id, "observations": observations},
                )
                session.add(obs)
                count += 1
            await session.commit()
            logger.info("FRED fetch complete: %d series stored", count)
        # Check for anomalies after fresh data
        await _check_anomalies_and_trigger()
    except Exception as e:
        logger.exception("Scheduled FRED fetch failed: %s", e)


async def scheduled_market_fetch():
    """Fetch market prices and store as observations."""
    from app.data_pipeline.market import MARKET_TICKER_MAP, fetch_all_market_prices
    from app.db.connection import async_session
    from app.models.observations import SentimentObservation

    logger.info("Scheduled market fetch starting")
    try:
        prices = await fetch_all_market_prices()
        async with async_session() as session:
            count = 0
            for ticker, data in prices.items():
                node_id = MARKET_TICKER_MAP.get(ticker)
                if not node_id:
                    continue
                obs = SentimentObservation(
                    node_id=node_id,
                    sentiment=0.0,  # Raw data — agent will interpret
                    confidence=1.0,
                    source="market_scheduled",
                    evidence=f"{ticker}: ${data['close']} ({data['change_pct']:+.2f}%)",
                    raw_data={"ticker": ticker, **data},
                )
                session.add(obs)
                count += 1
            await session.commit()
            logger.info("Market fetch complete: %d tickers stored", count)
        # Check for anomalies after fresh data
        await _check_anomalies_and_trigger()
    except Exception as e:
        logger.exception("Scheduled market fetch failed: %s", e)


async def scheduled_agent_analysis():
    """Trigger agent analysis on nodes that have fresh data since last run."""
    from sqlalchemy import select, func

    from app.agent.orchestrator import run_analysis
    from app.db.connection import async_session
    from app.models.observations import AgentRun, SentimentObservation

    logger.info("Scheduled agent analysis starting")
    try:
        async with async_session() as session:
            # Find the last completed agent run
            last_run_result = await session.execute(
                select(AgentRun.finished_at)
                .where(AgentRun.status == "completed")
                .order_by(AgentRun.finished_at.desc())
                .limit(1)
            )
            last_run_time = last_run_result.scalar_one_or_none()

            # Find nodes with fresh observations since last run
            query = select(SentimentObservation.node_id).distinct()
            if last_run_time:
                query = query.where(SentimentObservation.created_at > last_run_time)

            result = await session.execute(query)
            fresh_node_ids = [row[0] for row in result.all()]

            if not fresh_node_ids:
                logger.info("No nodes with fresh data — skipping scheduled analysis")
                return

            # Import here to avoid circular import
            from app.main import app_state

            logger.info("Running scheduled analysis on %d nodes with fresh data", len(fresh_node_ids))
            await run_analysis(
                node_ids=fresh_node_ids,
                session=session,
                graph=app_state.graph,
                trigger="scheduled",
            )
    except Exception as e:
        logger.exception("Scheduled agent analysis failed: %s", e)


async def scheduled_regime_check():
    """Detect current market regime and store snapshot."""
    from app.db.connection import async_session
    from app.graph_engine.regimes import detect_regime
    from app.models.observations import RegimeSnapshot

    logger.info("Scheduled regime check starting")
    try:
        from app.main import app_state

        result = detect_regime(app_state.graph)
        async with async_session() as session:
            snapshot = RegimeSnapshot(
                state=result.state.value,
                confidence=result.confidence,
                composite_score=result.composite_score,
                contributing_signals=result.contributing_signals,
            )
            session.add(snapshot)
            await session.commit()
            logger.info("Regime: %s (confidence: %.2f, score: %.4f)", result.state.value, result.confidence, result.composite_score)

        # Broadcast regime via WebSocket
        from app.api.websocket import manager
        await manager.broadcast({
            "type": "regime_update",
            "data": {
                "state": result.state.value,
                "confidence": result.confidence,
                "composite_score": result.composite_score,
                "contributing_signals": result.contributing_signals,
            },
        })
    except Exception as e:
        logger.exception("Regime check failed: %s", e)


async def _check_anomalies_and_trigger():
    """Check for anomalies after data fetch and auto-trigger agent if found."""
    from app.agent.orchestrator import run_analysis
    from app.db.connection import async_session
    from app.graph_engine.anomalies import detect_anomalies

    try:
        async with async_session() as session:
            from app.config import settings as _settings
            anomalies = await detect_anomalies(session, lookback_days=30, z_threshold=_settings.anomaly_z_threshold)
            if not anomalies:
                return

            anomalous_nodes = [a.node_id for a in anomalies]
            logger.info(
                "Anomalies detected in %d nodes (z-scores: %s) — triggering agent",
                len(anomalous_nodes),
                ", ".join(f"{a.node_id}={a.z_score}" for a in anomalies[:5]),
            )

            from app.main import app_state

            await run_analysis(
                node_ids=anomalous_nodes,
                session=session,
                graph=app_state.graph,
                trigger="anomaly",
            )
    except Exception as e:
        logger.exception("Anomaly check failed: %s", e)


async def scheduled_edgar_fetch():
    """Fetch SEC EDGAR financials for tracked companies."""
    from app.data_pipeline.edgar import EDGAR_COMPANY_MAP, fetch_all_company_financials
    from app.db.connection import async_session
    from app.models.observations import SentimentObservation

    logger.info("Scheduled EDGAR fetch starting")
    try:
        results = await fetch_all_company_financials()
        async with async_session() as session:
            count = 0
            for result in results:
                for node_id in result.get("nodes", []):
                    growth_info = ""
                    if "revenue_growth_pct" in result:
                        growth_info += f"Revenue growth: {result['revenue_growth_pct']:+.1f}%. "
                    if "eps_growth_pct" in result:
                        growth_info += f"EPS growth: {result['eps_growth_pct']:+.1f}%. "

                    obs = SentimentObservation(
                        node_id=node_id,
                        sentiment=0.0,
                        confidence=0.8,
                        source="edgar_scheduled",
                        evidence=f"{result['ticker']} ({result['company']}): {growth_info or 'Financial data fetched'}",
                        raw_data=result,
                    )
                    session.add(obs)
                    count += 1
            await session.commit()
            logger.info("EDGAR fetch complete: %d observations from %d companies", count, len(results))
        await _check_anomalies_and_trigger()
    except Exception as e:
        logger.exception("Scheduled EDGAR fetch failed: %s", e)


async def scheduled_reddit_fetch():
    """Fetch Reddit posts and store as observations for relevant nodes."""
    from app.data_pipeline.reddit import fetch_reddit_posts
    from app.db.connection import async_session
    from app.models.observations import SentimentObservation

    logger.info("Scheduled Reddit fetch starting")
    try:
        posts = await fetch_reddit_posts()
        if not posts:
            logger.info("No Reddit posts fetched (credentials may not be configured)")
            return

        async with async_session() as session:
            count = 0
            for post in posts:
                for node_id in post["node_ids"]:
                    obs = SentimentObservation(
                        node_id=node_id,
                        sentiment=0.0,  # Raw data — agent will interpret
                        confidence=0.5,
                        source="reddit_scheduled",
                        evidence=f"r/{post['subreddit']}: {post['title']} (score: {post['score']})",
                        raw_data={
                            "title": post["title"],
                            "score": post["score"],
                            "subreddit": post["subreddit"],
                            "url": post["url"],
                            "num_comments": post["num_comments"],
                        },
                    )
                    session.add(obs)
                    count += 1
            await session.commit()
            logger.info("Reddit fetch complete: %d observations stored from %d posts", count, len(posts))
    except Exception as e:
        logger.exception("Scheduled Reddit fetch failed: %s", e)


async def scheduled_weight_update():
    """Recalculate dynamic edge weights from empirical correlations."""
    from app.db.connection import async_session
    from app.graph_engine.correlations import update_dynamic_weights

    logger.info("Scheduled weight update starting")
    try:
        async with async_session() as session:
            from app.main import app_state

            updated = await update_dynamic_weights(session, app_state.graph)
            logger.info("Weight update complete: %d edges updated", updated)
    except Exception as e:
        logger.exception("Scheduled weight update failed: %s", e)


async def scheduled_sentiment_decay():
    """Apply exponential decay to sentiment values based on age."""
    from datetime import timedelta

    from sqlalchemy import select

    from app.db.connection import async_session
    from app.graph_engine.weights import exponential_decay
    from app.models.graph import Node

    logger.info("Running sentiment decay")
    try:
        async with async_session() as session:
            result = await session.execute(select(Node))
            nodes = result.scalars().all()
            now = datetime.utcnow()
            updated = 0
            for node in nodes:
                if not node.composite_sentiment or abs(node.composite_sentiment) < 0.01:
                    continue
                if not node.last_updated:
                    continue
                age_hours = (now - node.last_updated).total_seconds() / 3600
                from app.config import settings as _settings
                if age_hours < _settings.sentiment_decay_skip_hours:
                    continue
                decayed = exponential_decay(node.composite_sentiment, age_hours)
                if abs(decayed) < 0.01:
                    decayed = 0.0
                node.composite_sentiment = decayed
                updated += 1
            await session.commit()
            logger.info("Sentiment decay applied to %d nodes", updated)

            # Update in-memory graph under lock
            from app.main import app_state
            async with app_state.graph_lock:
                for node in nodes:
                    if node.id in app_state.graph:
                        app_state.graph.nodes[node.id]["composite_sentiment"] = node.composite_sentiment or 0.0
    except Exception as e:
        logger.exception("Sentiment decay failed: %s", e)


async def scheduled_prediction_resolution():
    """Resolve expired predictions by comparing predicted vs actual sentiment."""
    from app.db.connection import async_session
    from app.graph_engine.predictions import resolve_expired_predictions

    logger.info("Scheduled prediction resolution starting")
    try:
        async with async_session() as session:
            count = await resolve_expired_predictions(session)
            if count > 0:
                logger.info("Resolved %d expired predictions", count)
    except Exception as e:
        logger.exception("Prediction resolution failed: %s", e)


def setup_scheduler() -> AsyncIOScheduler:
    """Configure all scheduled jobs."""
    from app.config import settings

    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled (set SCHEDULER_ENABLED=true in .env to enable)")
        return scheduler

    scheduler.add_job(
        scheduled_fred_fetch,
        IntervalTrigger(hours=4),
        id="fred_fetch",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_market_fetch,
        IntervalTrigger(hours=1),
        id="market_fetch",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_agent_analysis,
        IntervalTrigger(hours=6),
        id="agent_analysis",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_reddit_fetch,
        IntervalTrigger(hours=2),
        id="reddit_fetch",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_edgar_fetch,
        CronTrigger(hour=6, minute=0),
        id="edgar_fetch",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_weight_update,
        CronTrigger(hour=3, minute=0),
        id="weight_update",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_regime_check,
        IntervalTrigger(hours=2),
        id="regime_check",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_sentiment_decay,
        CronTrigger(hour=2, minute=0),
        id="sentiment_decay",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_prediction_resolution,
        IntervalTrigger(hours=1),
        id="prediction_resolution",
        replace_existing=True,
    )
    return scheduler
