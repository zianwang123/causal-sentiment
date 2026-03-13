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
from app.models.graph import Node
from app.models.observations import SentimentObservation

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
) -> str:
    """Update a node's sentiment and record the observation."""
    sentiment = clamp_sentiment(sentiment)
    confidence = max(0.0, min(1.0, confidence))

    # Update node in DB
    result = await session.execute(select(Node).where(Node.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        return json.dumps({"error": f"Node '{node_id}' not found in graph"})

    node.composite_sentiment = sentiment
    node.confidence = confidence
    node.evidence = [{"text": evidence, "timestamp": datetime.now(timezone.utc).isoformat(), "sources": sources or []}]

    # Record observation
    obs = SentimentObservation(
        node_id=node_id,
        sentiment=sentiment,
        confidence=confidence,
        source="agent",
        evidence=evidence,
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
