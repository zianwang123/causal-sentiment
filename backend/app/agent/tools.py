"""Tool implementations for the Claude agent."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import httpx
import networkx as nx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.data_pipeline.market import MARKET_TICKER_MAP, fetch_market_prices_for_agent
from app.data_pipeline.reddit import search_reddit_for_agent
from app.graph_engine.propagation import propagate_signal
from app.graph_engine.weights import clamp_sentiment
from app.models.graph import Edge, Node
from app.models.observations import Prediction, SentimentObservation

logger = logging.getLogger(__name__)

FRED_SERIES_MAP = {
    "FEDFUNDS": "fed_funds_rate",
    "CPIAUCSL": "us_cpi_yoy",
    "GDP": "us_gdp_growth",
    "UNRATE": "unemployment_rate",
    "MANEMP": "us_pmi",
    "T10Y2Y": "yield_curve_spread",
    "DGS2": "us_2y_yield",
    "DGS10": "us_10y_yield",
    "DGS30": "us_30y_yield",
    "VIXCLS": "vix",
    "DTWEXBGS": "dxy_index",
    "BAMLH0A0HYM2": "hy_credit_spread",
    "BAMLC0A0CM": "ig_credit_spread",
    "DCOILWTICO": "wti_crude",
}


async def fetch_fred_data(series_id: str, observation_count: int = 10) -> str:
    """Fetch data from FRED API."""
    if not settings.fred_api_key:
        return json.dumps({
            "error": "FRED API key not configured. Set FRED_API_KEY environment variable.",
            "series_id": series_id,
            "mock_data": _mock_fred_data(series_id),
        })

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": settings.fred_api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": observation_count,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            observations = [
                {"date": obs["date"], "value": obs["value"]}
                for obs in data.get("observations", [])
                if obs["value"] != "."
            ]
            return json.dumps({"series_id": series_id, "observations": observations})
        except Exception as e:
            logger.error("FRED API error for %s: %s", series_id, e)
            return json.dumps({"error": str(e), "series_id": series_id})


def _mock_fred_data(series_id: str) -> list[dict]:
    """Return mock FRED data for development without API key."""
    mock = {
        "FEDFUNDS": [{"date": "2026-02-01", "value": "4.33"}],
        "CPIAUCSL": [{"date": "2026-01-01", "value": "315.6"}],
        "GDP": [{"date": "2025-10-01", "value": "23800.0"}],
        "UNRATE": [{"date": "2026-02-01", "value": "4.1"}],
        "T10Y2Y": [{"date": "2026-03-11", "value": "0.25"}],
        "VIXCLS": [{"date": "2026-03-11", "value": "18.5"}],
        "DTWEXBGS": [{"date": "2026-03-11", "value": "120.3"}],
    }
    return mock.get(series_id, [{"date": "2026-03-11", "value": "100.0"}])


async def fetch_market_prices(tickers: list[str] | None = None) -> str:
    """Fetch recent market prices for ETFs and futures."""
    try:
        results = await fetch_market_prices_for_agent(tickers)
        if not results:
            return json.dumps({"error": "No market data returned. Markets may be closed."})
        return json.dumps({"prices": results})
    except Exception as e:
        logger.error("Market data fetch error: %s", e)
        return json.dumps({"error": str(e), "available_tickers": list(MARKET_TICKER_MAP.keys())})


async def search_news(query: str, max_results: int = 10) -> str:
    """Search for financial news using NewsAPI."""
    if not settings.newsapi_key:
        return json.dumps({
            "note": "NewsAPI key not configured. Returning mock headlines.",
            "query": query,
            "articles": _mock_news(query),
        })

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": settings.newsapi_key,
        "sortBy": "publishedAt",
        "pageSize": max_results,
        "language": "en",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            articles = [
                {
                    "title": a["title"],
                    "source": a["source"]["name"],
                    "published_at": a["publishedAt"],
                    "description": a.get("description", ""),
                }
                for a in data.get("articles", [])[:max_results]
            ]
            return json.dumps({"query": query, "articles": articles})
        except Exception as e:
            logger.error("NewsAPI error for '%s': %s", query, e)
            return json.dumps({"error": str(e), "query": query})


def _mock_news(query: str) -> list[dict]:
    """Mock news for development."""
    return [
        {
            "title": f"Markets react to latest {query} developments",
            "source": "Mock Financial Times",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "description": f"Analysts are closely watching {query} for signals about the economic outlook.",
        },
        {
            "title": f"What {query} means for investors in 2026",
            "source": "Mock Reuters",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "description": f"A deep dive into how {query} is shaping market expectations.",
        },
    ]


async def fetch_sec_filings(company: str, form_type: str = "10-Q") -> str:
    """Fetch SEC EDGAR filings and financial data for a company."""
    from app.data_pipeline.edgar import EDGAR_COMPANY_MAP, fetch_company_financials

    ticker = company.upper()
    if ticker not in EDGAR_COMPANY_MAP:
        return json.dumps({
            "error": f"Company '{company}' not tracked. Available: {', '.join(EDGAR_COMPANY_MAP.keys())}",
        })

    try:
        result = await fetch_company_financials(ticker)
        if not result:
            return json.dumps({"error": f"No EDGAR data returned for {ticker}"})
        return json.dumps(result, default=str)
    except Exception as e:
        logger.error("SEC EDGAR fetch error for %s: %s", ticker, e)
        return json.dumps({"error": str(e), "company": ticker})


async def search_reddit(subreddit: str = "all", query: str = "", limit: int = 10) -> str:
    """Search Reddit for social sentiment on financial topics."""
    try:
        results = await search_reddit_for_agent(subreddit, query, limit)
        if not results:
            return json.dumps({"note": "No Reddit results found or Reddit not configured.", "query": query})
        return json.dumps({"subreddit": subreddit, "query": query, "posts": results})
    except Exception as e:
        logger.error("Reddit search error: %s", e)
        return json.dumps({"error": str(e), "query": query})


async def update_sentiment_signal(
    node_id: str,
    sentiment: float,
    confidence: float,
    evidence: str,
    session: AsyncSession,
    graph: nx.DiGraph,
    sources: list[str] | None = None,
    data_freshness: float | None = None,
    source_agreement: float | None = None,
    signal_strength: float | None = None,
) -> str:
    """Update a node's sentiment and record the observation."""
    sentiment = clamp_sentiment(sentiment)

    # Compute confidence from decomposition if provided, otherwise use raw value
    if data_freshness is not None and source_agreement is not None and signal_strength is not None:
        data_freshness = max(0.0, min(1.0, data_freshness))
        source_agreement = max(0.0, min(1.0, source_agreement))
        signal_strength = max(0.0, min(1.0, signal_strength))
        confidence = 0.3 * data_freshness + 0.4 * source_agreement + 0.3 * signal_strength
    confidence = max(0.0, min(1.0, confidence))

    # Update node in DB
    result = await session.execute(select(Node).where(Node.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        return json.dumps({"error": f"Node '{node_id}' not found in graph"})

    node.composite_sentiment = sentiment
    node.confidence = confidence
    evidence_entry = {"text": evidence, "timestamp": datetime.now(timezone.utc).isoformat(), "sources": sources or []}
    if data_freshness is not None:
        evidence_entry["confidence_breakdown"] = {
            "data_freshness": round(data_freshness, 2),
            "source_agreement": round(source_agreement, 2),
            "signal_strength": round(signal_strength, 2),
        }
    node.evidence = [evidence_entry]

    # Record observation
    raw_data = {}
    if data_freshness is not None:
        raw_data["confidence_breakdown"] = {
            "data_freshness": round(data_freshness, 2),
            "source_agreement": round(source_agreement, 2),
            "signal_strength": round(signal_strength, 2),
        }
    obs = SentimentObservation(
        node_id=node_id,
        sentiment=sentiment,
        confidence=confidence,
        source="agent",
        evidence=evidence,
        raw_data=raw_data if raw_data else None,
    )
    session.add(obs)

    # Update in-memory graph
    if node_id in graph:
        graph.nodes[node_id]["composite_sentiment"] = sentiment
        graph.nodes[node_id]["confidence"] = confidence

    # Run propagation (regime-aware)
    from app.graph_engine.regimes import detect_regime
    regime = detect_regime(graph)
    prop_result = propagate_signal(graph, node_id, sentiment, regime=regime.state.value)

    # Update propagated nodes in DB
    for target_id, impact in prop_result.impacts.items():
        target_result = await session.execute(select(Node).where(Node.id == target_id))
        target_node = target_result.scalar_one_or_none()
        if target_node:
            # Blend existing with propagated signal
            blend = settings.propagation_blend_ratio
            blended = (1 - blend) * (target_node.composite_sentiment or 0.0) + blend * impact
            target_node.composite_sentiment = clamp_sentiment(blended)
            if target_id in graph:
                graph.nodes[target_id]["composite_sentiment"] = target_node.composite_sentiment

    await session.commit()

    return json.dumps({
        "status": "updated",
        "node_id": node_id,
        "sentiment": sentiment,
        "confidence": confidence,
        "propagated_to": len(prop_result.impacts),
        "impacts": {k: round(v, 4) for k, v in list(prop_result.impacts.items())[:10]},
    })


async def get_graph_neighborhood(node_id: str, session: AsyncSession, graph: nx.DiGraph) -> str:
    """Get a node and its immediate neighbors."""
    if node_id not in graph:
        return json.dumps({"error": f"Node '{node_id}' not found"})

    node_data = dict(graph.nodes[node_id])
    # Convert enums to strings for JSON serialization
    for k, v in node_data.items():
        if hasattr(v, "value"):
            node_data[k] = v.value

    neighbors = []
    for _, target, edge_data in graph.out_edges(node_id, data=True):
        target_data = dict(graph.nodes[target])
        edge_info = dict(edge_data)
        for d in [target_data, edge_info]:
            for k, v in d.items():
                if hasattr(v, "value"):
                    d[k] = v.value
        neighbors.append({
            "node_id": target,
            "label": target_data.get("label", target),
            "sentiment": target_data.get("composite_sentiment", 0.0),
            "edge_weight": edge_info.get("effective_weight", 0.5),
            "edge_direction": edge_info.get("direction", "positive"),
        })

    for source, _, edge_data in graph.in_edges(node_id, data=True):
        source_data = dict(graph.nodes[source])
        edge_info = dict(edge_data)
        for d in [source_data, edge_info]:
            for k, v in d.items():
                if hasattr(v, "value"):
                    d[k] = v.value
        neighbors.append({
            "node_id": source,
            "label": source_data.get("label", source),
            "sentiment": source_data.get("composite_sentiment", 0.0),
            "edge_weight": edge_info.get("effective_weight", 0.5),
            "edge_direction": edge_info.get("direction", "positive"),
            "relationship": "incoming",
        })

    return json.dumps({
        "node": {"id": node_id, **node_data},
        "neighbors": neighbors,
    }, default=str)


async def get_analysis_context(session: AsyncSession, graph: nx.DiGraph) -> str:
    """Return a graph-wide state summary for the agent's planning phase."""
    from app.graph_engine.anomalies import detect_anomalies
    from app.graph_engine.regimes import detect_regime

    # Current regime
    regime = detect_regime(graph)

    # Anomalies (last 30 days, 2σ)
    anomalies = await detect_anomalies(session, lookback_days=30, z_threshold=2.0)
    anomaly_summary = [
        {"node_id": a.node_id, "z_score": a.z_score, "direction": a.direction}
        for a in anomalies[:15]
    ]

    # Data freshness: last observation time per node
    from datetime import timedelta
    cutoff_24h = datetime.utcnow() - timedelta(hours=24)
    cutoff_6h = datetime.utcnow() - timedelta(hours=6)

    result = await session.execute(
        select(SentimentObservation.node_id, SentimentObservation.created_at, SentimentObservation.source)
        .order_by(SentimentObservation.created_at.desc())
    )
    rows = result.all()

    # Track latest observation per node
    latest_by_node: dict[str, datetime] = {}
    for node_id, created_at, source in rows:
        if node_id not in latest_by_node:
            latest_by_node[node_id] = created_at

    # Stale nodes (no observation in 24h)
    all_node_ids = list(graph.nodes)
    stale_nodes = [
        nid for nid in all_node_ids
        if nid not in latest_by_node or latest_by_node[nid] < cutoff_24h
    ]

    # Recently changed nodes (observation in last 6h)
    recent_nodes = []
    for nid in all_node_ids:
        if nid in latest_by_node and latest_by_node[nid] >= cutoff_6h:
            sentiment = graph.nodes[nid].get("composite_sentiment", 0.0) or 0.0
            recent_nodes.append({"node_id": nid, "sentiment": round(sentiment, 3)})

    # Node priority ranking: centrality × staleness indicator
    centrality = nx.degree_centrality(graph)
    priority = []
    for nid in all_node_ids:
        c = centrality.get(nid, 0.0)
        is_stale = 1.0 if nid in stale_nodes else 0.0
        is_anomalous = 1.0 if any(a.node_id == nid for a in anomalies) else 0.0
        score = c * 0.4 + is_stale * 0.3 + is_anomalous * 0.3
        if score > 0.1:
            priority.append({"node_id": nid, "priority_score": round(score, 3)})
    priority.sort(key=lambda x: x["priority_score"], reverse=True)

    return json.dumps({
        "regime": {
            "state": regime.state.value,
            "confidence": regime.confidence,
            "composite_score": regime.composite_score,
        },
        "anomalies": anomaly_summary,
        "stale_nodes": stale_nodes[:20],
        "recently_updated": recent_nodes[:15],
        "priority_nodes": priority[:20],
        "total_nodes": len(all_node_ids),
        "total_stale": len(stale_nodes),
    }, default=str)


async def validate_consistency(
    node_ids: list[str],
    session: AsyncSession,
    graph: nx.DiGraph,
) -> str:
    """Check for logical contradictions among recently-updated nodes."""
    contradictions = []

    for node_id in node_ids:
        if node_id not in graph:
            continue

        node_sentiment = graph.nodes[node_id].get("composite_sentiment", 0.0) or 0.0
        node_label = graph.nodes[node_id].get("label", node_id)

        # Check outgoing edges
        for _, target, edge_data in graph.out_edges(node_id, data=True):
            if target not in node_ids and target not in [n for n, _ in graph.in_edges(node_id)]:
                continue  # Only check nodes we've analyzed or direct neighbors

            target_sentiment = graph.nodes[target].get("composite_sentiment", 0.0) or 0.0
            target_label = graph.nodes[target].get("label", target)
            direction = edge_data.get("direction", "positive")
            if hasattr(direction, "value"):
                direction = direction.value

            # Check alignment
            if direction == "positive":
                # Same direction expected
                if node_sentiment * target_sentiment < -0.04:  # Opposite signs, both non-trivial
                    contradictions.append({
                        "type": "direction_mismatch",
                        "source": {"id": node_id, "label": node_label, "sentiment": round(node_sentiment, 3)},
                        "target": {"id": target, "label": target_label, "sentiment": round(target_sentiment, 3)},
                        "edge_direction": direction,
                        "explanation": f"{node_label} ({node_sentiment:+.2f}) has POSITIVE edge to {target_label} ({target_sentiment:+.2f}), but they have opposite signs. Expected same direction.",
                    })
            elif direction == "negative":
                # Opposite direction expected
                if node_sentiment * target_sentiment > 0.04:  # Same signs, both non-trivial
                    contradictions.append({
                        "type": "direction_mismatch",
                        "source": {"id": node_id, "label": node_label, "sentiment": round(node_sentiment, 3)},
                        "target": {"id": target, "label": target_label, "sentiment": round(target_sentiment, 3)},
                        "edge_direction": direction,
                        "explanation": f"{node_label} ({node_sentiment:+.2f}) has NEGATIVE edge to {target_label} ({target_sentiment:+.2f}), but they have the same sign. Expected opposite direction.",
                    })

        # Check incoming edges too
        for source, _, edge_data in graph.in_edges(node_id, data=True):
            if source not in node_ids:
                continue

            source_sentiment = graph.nodes[source].get("composite_sentiment", 0.0) or 0.0
            source_label = graph.nodes[source].get("label", source)
            direction = edge_data.get("direction", "positive")
            if hasattr(direction, "value"):
                direction = direction.value

            if direction == "positive":
                if source_sentiment * node_sentiment < -0.04:
                    contradictions.append({
                        "type": "direction_mismatch",
                        "source": {"id": source, "label": source_label, "sentiment": round(source_sentiment, 3)},
                        "target": {"id": node_id, "label": node_label, "sentiment": round(node_sentiment, 3)},
                        "edge_direction": direction,
                        "explanation": f"{source_label} ({source_sentiment:+.2f}) has POSITIVE edge to {node_label} ({node_sentiment:+.2f}), but they have opposite signs.",
                    })
            elif direction == "negative":
                if source_sentiment * node_sentiment > 0.04:
                    contradictions.append({
                        "type": "direction_mismatch",
                        "source": {"id": source, "label": source_label, "sentiment": round(source_sentiment, 3)},
                        "target": {"id": node_id, "label": node_label, "sentiment": round(node_sentiment, 3)},
                        "edge_direction": direction,
                        "explanation": f"{source_label} ({source_sentiment:+.2f}) has NEGATIVE edge to {node_label} ({node_sentiment:+.2f}), but they have the same sign.",
                    })

    # Deduplicate by source-target pair
    seen = set()
    unique = []
    for c in contradictions:
        key = (c["source"]["id"], c["target"]["id"])
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return json.dumps({
        "contradictions_found": len(unique),
        "contradictions": unique[:15],
        "nodes_checked": len(node_ids),
        "status": "consistent" if not unique else "contradictions_detected",
    })


async def record_prediction(
    node_id: str,
    predicted_direction: str,
    predicted_sentiment: float,
    reasoning: str,
    session: AsyncSession,
    graph: nx.DiGraph,
    horizon_hours: int = 168,
) -> str:
    """Record a falsifiable prediction for future backtesting."""
    if node_id not in graph:
        return json.dumps({"error": f"Node '{node_id}' not found"})

    predicted_direction = predicted_direction.lower()
    if predicted_direction not in ("bullish", "bearish", "neutral"):
        return json.dumps({"error": "predicted_direction must be 'bullish', 'bearish', or 'neutral'"})

    predicted_sentiment = max(-1.0, min(1.0, predicted_sentiment))

    prediction = Prediction(
        node_id=node_id,
        predicted_direction=predicted_direction,
        predicted_sentiment=predicted_sentiment,
        horizon_hours=horizon_hours,
        reasoning=reasoning,
    )
    session.add(prediction)
    await session.flush()

    return json.dumps({
        "status": "recorded",
        "prediction_id": prediction.id,
        "node_id": node_id,
        "predicted_direction": predicted_direction,
        "predicted_sentiment": predicted_sentiment,
        "horizon": f"{horizon_hours}h",
        "note": "This prediction will be evaluated against actual outcomes for backtesting.",
    })


async def get_agent_track_record(
    session: AsyncSession,
    graph: nx.DiGraph,
    node_id: str | None = None,
) -> str:
    """Get the agent's prediction track record — hit rate, accuracy, recent results."""
    from sqlalchemy import func as sa_func

    query = select(Prediction).where(Prediction.resolved_at.isnot(None))
    if node_id:
        query = query.where(Prediction.node_id == node_id)

    result = await session.execute(query.order_by(Prediction.resolved_at.desc()))
    resolved = result.scalars().all()

    # Also get pending count
    pending_query = select(sa_func.count()).select_from(Prediction).where(Prediction.resolved_at.is_(None))
    if node_id:
        pending_query = pending_query.where(Prediction.node_id == node_id)
    pending_count = (await session.execute(pending_query)).scalar() or 0

    if not resolved:
        return json.dumps({
            "total_resolved": 0,
            "pending": pending_count,
            "message": "No resolved predictions yet. Track record will build as predictions expire.",
        })

    # Aggregate stats
    total = len(resolved)
    hits = sum(1 for p in resolved if p.hit == 1)
    misses = sum(1 for p in resolved if p.hit == 0)
    inconclusive = sum(1 for p in resolved if p.hit is None)
    hit_rate = hits / (hits + misses) if (hits + misses) > 0 else None

    # Per-direction breakdown
    by_direction: dict[str, dict] = {}
    for p in resolved:
        d = p.predicted_direction
        if d not in by_direction:
            by_direction[d] = {"total": 0, "hits": 0, "misses": 0}
        by_direction[d]["total"] += 1
        if p.hit == 1:
            by_direction[d]["hits"] += 1
        elif p.hit == 0:
            by_direction[d]["misses"] += 1

    for d_stats in by_direction.values():
        denom = d_stats["hits"] + d_stats["misses"]
        d_stats["hit_rate"] = round(d_stats["hits"] / denom, 3) if denom > 0 else None

    # Avg sentiment error
    errors = [
        abs(p.predicted_sentiment - p.actual_sentiment)
        for p in resolved
        if p.actual_sentiment is not None
    ]
    avg_error = round(sum(errors) / len(errors), 4) if errors else None

    # Last 5 resolved with details
    recent = []
    for p in resolved[:5]:
        hit_symbol = "?" if p.hit is None else ("correct" if p.hit == 1 else "wrong")
        recent.append({
            "node_id": p.node_id,
            "predicted": f"{p.predicted_direction} ({p.predicted_sentiment:+.2f})",
            "actual_sentiment": round(p.actual_sentiment, 3) if p.actual_sentiment is not None else None,
            "result": hit_symbol,
            "reasoning": p.reasoning[:120] if p.reasoning else "",
            "created": p.created_at.isoformat(),
        })

    return json.dumps({
        "total_resolved": total,
        "pending": pending_count,
        "hits": hits,
        "misses": misses,
        "inconclusive": inconclusive,
        "hit_rate": round(hit_rate, 3) if hit_rate is not None else None,
        "avg_sentiment_error": avg_error,
        "by_direction": by_direction,
        "recent_predictions": recent,
    })
