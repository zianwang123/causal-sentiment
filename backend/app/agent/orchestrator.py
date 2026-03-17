"""LLM agent orchestrator — three-phase reasoning loop (Plan → Analyze → Validate)."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime

import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.llm_client import append_tool_results, chat_with_tools
from app.agent.prompts import (
    ANALYSIS_PROMPT_TEMPLATE,
    PLANNING_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
    VALIDATION_PROMPT,
)
from app.agent.schemas import AGENT_TOOLS
from app.agent.tools import (
    FRED_SERIES_MAP,
    batch_update_sentiment,
    fetch_fred_data,
    fetch_market_prices,
    fetch_sec_filings,
    get_agent_track_record,
    get_analysis_context,
    get_graph_neighborhood,
    record_prediction,
    search_news,
    search_reddit,
    update_sentiment_signal,
    validate_consistency,
)
from app.config import settings
from app.models.observations import AgentRun

logger = logging.getLogger(__name__)

# Phase boundaries (round ranges)
PLANNING_ROUNDS = 3
ANALYSIS_ROUNDS = 25
VALIDATION_ROUNDS = 7
MAX_ROUNDS = PLANNING_ROUNDS + ANALYSIS_ROUNDS + VALIDATION_ROUNDS  # 35


def _get_phase(round_num: int) -> str:
    """Return the current phase name based on round number."""
    if round_num < PLANNING_ROUNDS:
        return "planning"
    elif round_num < PLANNING_ROUNDS + ANALYSIS_ROUNDS:
        return "analysis"
    else:
        return "validation"


def _build_regime_context(graph: nx.DiGraph) -> str:
    """Detect current market regime and return a context string."""
    from app.graph_engine.regimes import detect_regime
    regime = detect_regime(graph)
    guidance = ""
    if regime.state.value == "risk_off":
        guidance = "In risk-off regimes, weight defensive signals more heavily and be more cautious on bullish calls."
    elif regime.state.value == "risk_on":
        guidance = "In risk-on regimes, bullish momentum tends to persist — look for confirmation signals."
    return (
        f"\n\n## Current Market Regime\n"
        f"**{regime.state.value.upper().replace('_', ' ')}** (confidence: {regime.confidence:.0%}, "
        f"composite: {regime.composite_score:+.3f})\n"
        f"Contributing signals: {', '.join(f'{k}={v:+.2f}' for k, v in regime.contributing_signals.items())}\n"
        f"{guidance}"
    )


async def run_analysis(
    node_ids: list[str],
    session: AsyncSession,
    graph: nx.DiGraph,
    trigger: str = "manual",
) -> AgentRun:
    """Run the LLM agent with Plan → Analyze → Validate phases."""
    # Validate API key before creating a "running" AgentRun
    provider = settings.llm_provider
    if provider == "openai" and not settings.openai_api_key:
        agent_run = AgentRun(
            trigger=trigger, status="error", nodes_analyzed=node_ids,
            error="OPENAI_API_KEY not configured", finished_at=datetime.utcnow(),
        )
        session.add(agent_run)
        await session.commit()
        return agent_run
    elif provider == "anthropic" and not settings.anthropic_api_key:
        agent_run = AgentRun(
            trigger=trigger, status="error", nodes_analyzed=node_ids,
            error="ANTHROPIC_API_KEY not configured", finished_at=datetime.utcnow(),
        )
        session.add(agent_run)
        await session.commit()
        return agent_run

    agent_run = AgentRun(
        trigger=trigger,
        status="running",
        nodes_analyzed=node_ids,
    )
    session.add(agent_run)
    await session.commit()

    # Build system prompt with initial regime context
    regime_context = _build_regime_context(graph)
    system_prompt = SYSTEM_PROMPT + regime_context

    # ── AGENT MEMORY: previous runs + track record ────────────────
    memory_context = await _build_memory_context(session)
    if memory_context:
        system_prompt += memory_context

    # ── PRE-FETCH DATA PACKAGE ────────────────────────────────────
    try:
        data_package_text, source_map = await _build_data_package(node_ids, session, graph)
        system_prompt += data_package_text
        logger.info("Pre-fetch succeeded: source_map has %d node entries", len(source_map))
    except Exception as e:
        logger.warning("Data package pre-fetch failed (agent will fetch manually): %s", e)
        source_map = {}

    # Check for portfolio positions to give agent context
    from sqlalchemy import select as sa_select
    from app.models.observations import PortfolioPosition
    portfolio_context = ""
    try:
        port_result = await session.execute(sa_select(PortfolioPosition))
        positions = port_result.scalars().all()
        if positions:
            holdings = ", ".join(f"{p.ticker} ({p.shares} shares @ ${p.entry_price:.2f})" for p in positions)
            portfolio_context = f"\n\n**User Portfolio:** {holdings}\nFlag any sentiment signals particularly relevant to these holdings."
    except Exception:
        pass

    tool_calls_log: list[dict] = []
    nodes_updated: list[str] = []  # Track which nodes get updated for validation

    # Snapshot in-memory graph sentiment state so we can rollback on error (C3 fix)
    graph_snapshot: dict[str, dict] = {}
    for nid in graph.nodes:
        graph_snapshot[nid] = {
            "composite_sentiment": graph.nodes[nid].get("composite_sentiment", 0.0),
            "confidence": graph.nodes[nid].get("confidence", 0.0),
        }

    try:
        # ── PHASE 1: PLANNING ──────────────────────────────────────────
        planning_prompt = PLANNING_PROMPT_TEMPLATE.format(node_ids=", ".join(node_ids)) + portfolio_context
        messages: list[dict] = [{"role": "user", "content": planning_prompt}]

        for round_num in range(PLANNING_ROUNDS):
            phase = "planning"
            llm_response, messages = await chat_with_tools(
                system=system_prompt,
                messages=messages,
                tools=AGENT_TOOLS,
            )

            if llm_response.done or not llm_response.tool_calls:
                break

            results: dict[str, str] = {}
            for tc in llm_response.tool_calls:
                logger.info("[%s round %d] %s(%s)", phase, round_num, tc.name, json.dumps(tc.input)[:200])
                result = await _execute_tool(tc.name, tc.input, session, graph, agent_run_id=agent_run.id, source_map=source_map)
                results[tc.id] = result
                tool_calls_log.append({"tool": tc.name, "input": tc.input, "output": result[:2000] if isinstance(result, str) else str(result)[:2000], "round": round_num, "phase": phase})

            messages = append_tool_results(messages, llm_response.tool_calls, results)
            _broadcast_progress(round_num, phase, llm_response.tool_calls, tool_calls_log)

        # Transition to analysis: refresh regime context and inject analysis prompt
        fresh_regime = _build_regime_context(graph)
        analysis_prompt = ANALYSIS_PROMPT_TEMPLATE.format(node_ids=", ".join(node_ids))
        messages.append({"role": "user", "content": f"[Regime update]{fresh_regime}\n\n{analysis_prompt}"})

        # ── PHASE 2: ANALYSIS ──────────────────────────────────────────
        for round_num in range(PLANNING_ROUNDS, PLANNING_ROUNDS + ANALYSIS_ROUNDS):
            phase = "analysis"
            llm_response, messages = await chat_with_tools(
                system=system_prompt,
                messages=messages,
                tools=AGENT_TOOLS,
            )

            if llm_response.done or not llm_response.tool_calls:
                if llm_response.text:
                    agent_run.summary = llm_response.text
                break

            results = {}
            for tc in llm_response.tool_calls:
                logger.info("[%s round %d] %s(%s)", phase, round_num, tc.name, json.dumps(tc.input)[:200])
                result = await _execute_tool(tc.name, tc.input, session, graph, agent_run_id=agent_run.id, source_map=source_map)
                results[tc.id] = result
                tool_calls_log.append({"tool": tc.name, "input": tc.input, "output": result[:2000] if isinstance(result, str) else str(result)[:2000], "round": round_num, "phase": phase})

                # Track nodes that get sentiment updates
                if tc.name == "update_sentiment_signal" and "node_id" in tc.input:
                    nodes_updated.append(tc.input["node_id"])
                elif tc.name == "batch_update_sentiment" and "updates" in tc.input:
                    nodes_updated.extend(u["node_id"] for u in tc.input["updates"])

            messages = append_tool_results(messages, llm_response.tool_calls, results)
            _broadcast_progress(round_num, phase, llm_response.tool_calls, tool_calls_log)

        # ── PHASE 3: VALIDATION ────────────────────────────────────────
        if nodes_updated:
            fresh_regime = _build_regime_context(graph)
            validation_prompt = VALIDATION_PROMPT.format(
                nodes_updated=", ".join(dict.fromkeys(nodes_updated)),  # unique, ordered
            )
            messages.append({"role": "user", "content": f"[Regime update]{fresh_regime}\n\n{validation_prompt}"})

            for round_num in range(PLANNING_ROUNDS + ANALYSIS_ROUNDS, MAX_ROUNDS):
                phase = "validation"
                llm_response, messages = await chat_with_tools(
                    system=system_prompt,
                    messages=messages,
                    tools=AGENT_TOOLS,
                )

                if llm_response.done or not llm_response.tool_calls:
                    if llm_response.text:
                        # Append validation summary to existing summary
                        existing = agent_run.summary or ""
                        agent_run.summary = existing + ("\n\n---\n**Validation:** " + llm_response.text if existing else llm_response.text)
                    break

                results = {}
                for tc in llm_response.tool_calls:
                    logger.info("[%s round %d] %s(%s)", phase, round_num, tc.name, json.dumps(tc.input)[:200])
                    result = await _execute_tool(tc.name, tc.input, session, graph, agent_run_id=agent_run.id, source_map=source_map)
                    results[tc.id] = result
                    tool_calls_log.append({"tool": tc.name, "input": tc.input, "output": result[:2000] if isinstance(result, str) else str(result)[:2000], "round": round_num, "phase": phase})

                messages = append_tool_results(messages, llm_response.tool_calls, results)
                _broadcast_progress(round_num, phase, llm_response.tool_calls, tool_calls_log)

        agent_run.status = "completed"
        agent_run.tool_calls = tool_calls_log
        agent_run.finished_at = datetime.utcnow()

    except Exception as e:
        logger.exception("Agent run failed")
        # Rollback DB changes
        try:
            await session.rollback()
        except Exception:
            pass
        # Restore in-memory graph state from snapshot to prevent graph/DB divergence
        try:
            from app.main import app_state
            async with app_state.graph_lock:
                for nid, snapshot in graph_snapshot.items():
                    if nid in graph:
                        graph.nodes[nid]["composite_sentiment"] = snapshot["composite_sentiment"]
                        graph.nodes[nid]["confidence"] = snapshot["confidence"]
            logger.info("Restored in-memory graph state from pre-run snapshot")
        except Exception as restore_err:
            logger.error("Failed to restore graph snapshot: %s", restore_err)
        # Persist error state in a fresh session to avoid stale object issues
        try:
            from app.db.connection import async_session
            async with async_session() as err_session:
                from sqlalchemy import update
                from app.models.observations import AgentRun as AgentRunModel
                await err_session.execute(
                    update(AgentRunModel)
                    .where(AgentRunModel.id == agent_run.id)
                    .values(
                        status="error",
                        error=str(e)[:2000],
                        tool_calls=tool_calls_log,
                        finished_at=datetime.utcnow(),
                    )
                )
                await err_session.commit()
            agent_run.status = "error"
            agent_run.error = str(e)[:2000]
            return agent_run
        except Exception as commit_err:
            logger.error("Failed to persist agent error state: %s", commit_err)
            return agent_run

    await session.commit()
    return agent_run


# Track fire-and-forget broadcast tasks to prevent GC and enable cleanup
_broadcast_tasks: set[asyncio.Task] = set()


def _broadcast_done_callback(task: asyncio.Task) -> None:
    """Clean up completed broadcast tasks and log errors."""
    _broadcast_tasks.discard(task)
    if not task.cancelled() and task.exception():
        logger.debug("Broadcast failed: %s", task.exception())


def _broadcast_progress(
    round_num: int,
    phase: str,
    tool_calls: list,
    tool_calls_log: list[dict],
) -> None:
    """Broadcast agent progress via WebSocket (fire-and-forget)."""
    try:
        from app.api.websocket import manager
        task = asyncio.create_task(manager.broadcast({
            "type": "agent_progress",
            "data": {
                "round": round_num + 1,
                "max_rounds": MAX_ROUNDS,
                "phase": phase,
                "tool_calls": [tc.name for tc in tool_calls],
                "total_tool_calls": len(tool_calls_log),
            },
        }))
        _broadcast_tasks.add(task)
        task.add_done_callback(_broadcast_done_callback)
    except Exception as e:
        logger.debug("Failed to broadcast agent progress: %s", e)


async def _execute_tool(
    tool_name: str,
    tool_input: dict,
    session: AsyncSession,
    graph: nx.DiGraph,
    agent_run_id: int | None = None,
    source_map: dict | None = None,
) -> str:
    """Dispatch a tool call to the appropriate implementation."""
    if tool_name in ("update_sentiment_signal", "batch_update_sentiment"):
        logger.info("_execute_tool %s: source_map=%s entries, node=%s",
                    tool_name, len(source_map) if source_map else "None",
                    tool_input.get("node_id", "batch"))
    if tool_name == "fetch_fred_data":
        return await fetch_fred_data(
            series_id=tool_input["series_id"],
            observation_count=tool_input.get("observation_count", 10),
        )
    elif tool_name == "fetch_market_prices":
        return await fetch_market_prices(
            tickers=tool_input.get("tickers"),
        )
    elif tool_name == "fetch_sec_filings":
        return await fetch_sec_filings(
            company=tool_input["company"],
            form_type=tool_input.get("form_type", "10-Q"),
        )
    elif tool_name == "search_news":
        return await search_news(
            query=tool_input["query"],
            max_results=tool_input.get("max_results", 10),
        )
    elif tool_name == "search_reddit":
        return await search_reddit(
            subreddit=tool_input.get("subreddit", "all"),
            query=tool_input.get("query", ""),
            limit=tool_input.get("limit", 10),
        )
    elif tool_name == "update_sentiment_signal":
        # Attach data source provenance from pre-fetch source_map
        node_data_sources = source_map.get(tool_input["node_id"]) if source_map else None
        return await update_sentiment_signal(
            node_id=tool_input["node_id"],
            sentiment=tool_input["sentiment"],
            confidence=tool_input["confidence"],
            evidence=tool_input["evidence"],
            session=session,
            graph=graph,
            sources=tool_input.get("sources"),
            data_freshness=tool_input.get("data_freshness"),
            source_agreement=tool_input.get("source_agreement"),
            signal_strength=tool_input.get("signal_strength"),
            data_sources=node_data_sources,
        )
    elif tool_name == "get_graph_neighborhood":
        return await get_graph_neighborhood(
            node_id=tool_input["node_id"],
            session=session,
            graph=graph,
        )
    elif tool_name == "get_analysis_context":
        return await get_analysis_context(
            session=session,
            graph=graph,
        )
    elif tool_name == "validate_consistency":
        return await validate_consistency(
            node_ids=tool_input["node_ids"],
            session=session,
            graph=graph,
        )
    elif tool_name == "get_agent_track_record":
        return await get_agent_track_record(
            session=session,
            graph=graph,
            node_id=tool_input.get("node_id"),
        )
    elif tool_name == "record_prediction":
        return await record_prediction(
            node_id=tool_input["node_id"],
            predicted_direction=tool_input["predicted_direction"],
            predicted_sentiment=tool_input["predicted_sentiment"],
            reasoning=tool_input["reasoning"],
            session=session,
            graph=graph,
            horizon_hours=tool_input.get("horizon_hours", 168),
            agent_run_id=agent_run_id,
        )
    elif tool_name == "batch_update_sentiment":
        return await batch_update_sentiment(
            updates=tool_input["updates"],
            session=session,
            graph=graph,
            source_map=source_map,
        )
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})


async def _build_data_package(node_ids: list[str], session: AsyncSession, graph: nx.DiGraph) -> tuple[str, dict]:
    """Pre-fetch all available data and build a context string + source map.

    Returns (prompt_text, source_map) where source_map tracks real/mock/missing per node.
    """
    from app.data_pipeline.market import MARKET_TICKER_MAP

    source_map: dict[str, dict] = {}  # {node_id: {source_type: {status, ...}}}

    # 1. Fetch all FRED series
    fred_lines = []
    for series_id, node_id in FRED_SERIES_MAP.items():
        try:
            result = await fetch_fred_data(series_id, 3)
            data = json.loads(result)
            is_mock = "mock_data" in data
            obs = data.get("observations") or data.get("mock_data", [])
            latest = obs[0] if obs else {}
            source_map.setdefault(node_id, {})["fred"] = {
                "status": "mock" if is_mock else "real",
                "series": series_id,
                "latest_value": latest.get("value"),
                "latest_date": latest.get("date"),
            }
            status_tag = "[MOCK]" if is_mock else ""
            fred_lines.append(f"  {series_id} → {node_id}: {latest.get('value', 'N/A')} ({latest.get('date', '?')}) {status_tag}")
        except Exception as e:
            logger.warning("Pre-fetch FRED %s failed: %s", series_id, e)

    # 2. Fetch all market tickers
    market_lines = []
    try:
        result = await fetch_market_prices()
        market_data = json.loads(result)
        prices = market_data.get("prices", {})
        for ticker, node_id in MARKET_TICKER_MAP.items():
            if ticker in prices:
                p = prices[ticker]
                source_map.setdefault(node_id, {})["yfinance"] = {
                    "status": "real",
                    "ticker": ticker,
                    "close": p.get("close"),
                    "change_pct": p.get("change_pct"),
                    "change_5d_pct": p.get("change_5d_pct"),
                    "trend": p.get("trend"),
                }
                trend_str = ""
                if p.get("change_5d_pct") is not None:
                    trend_str = f", 5d: {p['change_5d_pct']:+.2f}% {p.get('trend', '')}"
                    if p.get("high_5d") is not None:
                        trend_str += f", range: {p['low_5d']}-{p['high_5d']}"
                market_lines.append(f"  {ticker} → {node_id}: ${p.get('close', 'N/A')} (1d: {p.get('change_pct', 0):+.2f}%{trend_str})")
    except Exception as e:
        logger.warning("Pre-fetch market failed: %s", e)

    # 3. Fetch RSS headlines
    news_lines = []
    try:
        from app.data_pipeline.news import fetch_all_news_feeds
        articles = await fetch_all_news_feeds()
        news_by_node: dict[str, list] = {}
        for article in articles[:80]:
            for nid in article.node_ids:
                news_by_node.setdefault(nid, []).append(article)

        for nid, arts in news_by_node.items():
            tiers = sorted(set(a.tier for a in arts))
            source_map.setdefault(nid, {})["rss"] = {
                "status": "real",
                "count": len(arts),
                "top_headlines": [a.title[:80] for a in arts[:3]],
                "best_tier": min(tiers) if tiers else 3,
            }

        # Top 20 headlines for the prompt (deduplicated, diverse)
        seen_titles = set()
        for article in articles[:50]:
            if article.title not in seen_titles:
                seen_titles.add(article.title)
                tier_label = {1: "T1", 2: "T2", 3: "T3"}.get(article.tier, "T2")
                nodes_str = ", ".join(article.node_ids[:3])
                news_lines.append(f"  [{tier_label} {article.source}] {article.title[:90]} → {nodes_str}")
            if len(news_lines) >= 20:
                break
    except Exception as e:
        logger.warning("Pre-fetch RSS failed: %s", e)

    # 4. Mark nodes with no data sources
    for nid in node_ids:
        if nid not in source_map:
            source_map[nid] = {"_none": {"status": "inferred"}}

    # Build prompt text
    parts = ["\n\n## Pre-Fetched Data Package\n"]
    parts.append("All data below was fetched moments ago. Use it directly — no need to re-fetch unless you need more detail.\n")
    parts.append("Use `batch_update_sentiment` to update multiple nodes efficiently in one call.\n")

    if fred_lines:
        parts.append(f"\n### FRED Macro Data ({len(fred_lines)} series)\n")
        parts.extend(fred_lines)
        parts.append("")

    if market_lines:
        parts.append(f"\n### Market Prices ({len(market_lines)} tickers)\n")
        parts.extend(market_lines)
        parts.append("")

    if news_lines:
        parts.append(f"\n### Top News Headlines ({len(news_lines)} articles from RSS)\n")
        parts.extend(news_lines)
        parts.append("")

    # Flag nodes with no data
    no_data_nodes = [nid for nid in node_ids if source_map.get(nid, {}).get("_none")]
    if no_data_nodes:
        parts.append(f"\n### Nodes Without Direct Data ({len(no_data_nodes)})\n")
        parts.append(f"  {', '.join(no_data_nodes)}")
        parts.append("  For these, search news or infer from causal neighbors. Mark evidence as 'inferred'.\n")

    prompt = "\n".join(parts)
    logger.info("Data package: %d FRED, %d market, %d news, %d no-data nodes",
                len(fred_lines), len(market_lines), len(news_lines), len(no_data_nodes))
    return prompt, source_map


async def _build_memory_context(session: AsyncSession) -> str:
    """Build memory context from previous runs and prediction track record."""
    from sqlalchemy import select as sa_select, func as sa_func
    from app.models.observations import Prediction
    from datetime import timedelta

    parts: list[str] = []

    # Previous run summaries (last 3 completed runs)
    try:
        result = await session.execute(
            sa_select(AgentRun)
            .where(AgentRun.status == "completed")
            .where(AgentRun.summary.isnot(None))
            .order_by(AgentRun.finished_at.desc())
            .limit(3)
        )
        prev_runs = result.scalars().all()
        if prev_runs:
            lines = []
            now = datetime.utcnow()
            for run in prev_runs:
                ago = now - run.finished_at if run.finished_at else timedelta(0)
                hours_ago = int(ago.total_seconds() / 3600)
                node_count = len(run.nodes_analyzed) if run.nodes_analyzed else 0
                # Truncate summary to keep prompt manageable
                summary = (run.summary or "")[:300]
                if hours_ago < 1:
                    time_label = "< 1 hour ago"
                elif hours_ago < 24:
                    time_label = f"{hours_ago}h ago"
                else:
                    time_label = f"{hours_ago // 24}d ago"
                lines.append(f"- **{time_label}** ({node_count} nodes, {run.trigger}): {summary}")
            parts.append("\n\n## Previous Analyses\n" + "\n".join(lines))
    except Exception:
        pass

    # Prediction track record summary
    try:
        result = await session.execute(
            sa_select(Prediction).where(Prediction.hit.isnot(None)).order_by(Prediction.resolved_at.desc())
        )
        resolved = result.scalars().all()
        if resolved:
            hits = sum(1 for p in resolved if p.hit == 1)
            misses = sum(1 for p in resolved if p.hit == 0)
            total = hits + misses
            hit_rate = hits / total if total > 0 else 0

            recent_lines = []
            for p in resolved[:5]:
                symbol = "correct" if p.hit == 1 else "wrong"
                recent_lines.append(f"{p.node_id} {p.predicted_direction} → {symbol}")

            parts.append(
                f"\n\n## Your Track Record\n"
                f"Overall: {total} resolved predictions, {hit_rate:.0%} hit rate ({hits} correct, {misses} wrong)\n"
                f"Recent: {' · '.join(recent_lines)}\n"
                f"{'Calibration: your hit rate is below 50% — consider being more conservative with predictions.' if hit_rate < 0.5 and total >= 5 else ''}"
            )
    except Exception:
        pass

    return "".join(parts)
