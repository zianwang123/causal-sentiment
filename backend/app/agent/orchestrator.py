"""LLM agent orchestrator — supports Claude and GPT with tool-use loop."""

from __future__ import annotations

import json
import logging
from datetime import datetime

import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.llm_client import append_tool_results, chat_with_tools
from app.agent.prompts import ANALYSIS_PROMPT_TEMPLATE, SYSTEM_PROMPT
from app.agent.schemas import AGENT_TOOLS
from app.agent.tools import (
    fetch_fred_data,
    fetch_market_prices,
    fetch_sec_filings,
    get_graph_neighborhood,
    search_news,
    search_reddit,
    update_sentiment_signal,
)
from app.config import settings
from app.models.observations import AgentRun

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 20


async def run_analysis(
    node_ids: list[str],
    session: AsyncSession,
    graph: nx.DiGraph,
    trigger: str = "manual",
) -> AgentRun:
    """Run the LLM agent to analyze and update sentiment for given nodes."""
    agent_run = AgentRun(
        trigger=trigger,
        status="running",
        nodes_analyzed=node_ids,
    )
    session.add(agent_run)
    await session.commit()

    # Check that the active provider has an API key
    provider = settings.llm_provider
    if provider == "openai" and not settings.openai_api_key:
        agent_run.status = "error"
        agent_run.error = "OPENAI_API_KEY not configured"
        agent_run.finished_at = datetime.utcnow()
        await session.commit()
        return agent_run
    elif provider == "anthropic" and not settings.anthropic_api_key:
        agent_run.status = "error"
        agent_run.error = "ANTHROPIC_API_KEY not configured"
        agent_run.finished_at = datetime.utcnow()
        await session.commit()
        return agent_run

    # Detect current regime and inject into system prompt
    from app.graph_engine.regimes import detect_regime
    regime = detect_regime(graph)
    regime_context = (
        f"\n\n## Current Market Regime\n"
        f"**{regime.state.value.upper().replace('_', ' ')}** (confidence: {regime.confidence:.0%}, "
        f"composite: {regime.composite_score:+.3f})\n"
        f"Contributing signals: {', '.join(f'{k}={v:+.2f}' for k, v in regime.contributing_signals.items())}\n"
        f"{'In risk-off regimes, weight defensive signals more heavily and be more cautious on bullish calls.' if regime.state.value == 'risk_off' else ''}"
        f"{'In risk-on regimes, bullish momentum tends to persist — look for confirmation signals.' if regime.state.value == 'risk_on' else ''}"
    )
    system_prompt = SYSTEM_PROMPT + regime_context

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

    user_prompt = ANALYSIS_PROMPT_TEMPLATE.format(node_ids=", ".join(node_ids)) + portfolio_context
    messages: list[dict] = [{"role": "user", "content": user_prompt}]
    tool_calls_log: list[dict] = []

    try:
        for round_num in range(MAX_TOOL_ROUNDS):
            llm_response, messages = await chat_with_tools(
                system=system_prompt,
                messages=messages,
                tools=AGENT_TOOLS,
            )

            # Check if we're done (no tool calls)
            if llm_response.done:
                if llm_response.text:
                    agent_run.summary = llm_response.text
                break

            if not llm_response.tool_calls:
                # No tool calls and not explicitly done — treat as done
                if llm_response.text:
                    agent_run.summary = llm_response.text
                break

            # Execute tool calls
            results: dict[str, str] = {}
            for tc in llm_response.tool_calls:
                logger.info("Agent tool call [round %d]: %s(%s)", round_num, tc.name, json.dumps(tc.input)[:200])
                tool_calls_log.append({"tool": tc.name, "input": tc.input, "round": round_num})

                result = await _execute_tool(tc.name, tc.input, session, graph)
                results[tc.id] = result

            messages = append_tool_results(messages, llm_response.tool_calls, results)

        agent_run.status = "completed"
        agent_run.tool_calls = tool_calls_log
        agent_run.finished_at = datetime.utcnow()

    except Exception as e:
        logger.exception("Agent run failed")
        agent_run.status = "error"
        agent_run.error = str(e)
        agent_run.finished_at = datetime.utcnow()

    await session.commit()
    return agent_run


async def _execute_tool(
    tool_name: str,
    tool_input: dict,
    session: AsyncSession,
    graph: nx.DiGraph,
) -> str:
    """Dispatch a tool call to the appropriate implementation."""
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
        return await update_sentiment_signal(
            node_id=tool_input["node_id"],
            sentiment=tool_input["sentiment"],
            confidence=tool_input["confidence"],
            evidence=tool_input["evidence"],
            session=session,
            graph=graph,
        )
    elif tool_name == "get_graph_neighborhood":
        return await get_graph_neighborhood(
            node_id=tool_input["node_id"],
            session=session,
            graph=graph,
        )
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
