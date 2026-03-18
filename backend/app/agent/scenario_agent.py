"""Scenario extrapolation engine — 5-phase agent orchestrator.

Phases: News Ingestion -> Historical Research -> Scenario Generation (unconstrained)
        -> Graph Mapping -> Output

Reuses existing tool functions (search_news, fetch_market_prices, validate_consistency)
but NEVER reads stored sentiments, past agent runs, or prediction history.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime

import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.llm_client import append_tool_results, chat_with_tools, simple_completion
from app.agent.scenario_prompts import (
    PHASE1_NEWS_PROMPT,
    PHASE2_HISTORY_PROMPT,
    PHASE3_GENERATE_PROMPT,
    PHASE4_MAP_PROMPT_TEMPLATE,
    QUICK_TRIGGERS_PROMPT,
    SCENARIO_SYSTEM_PROMPT,
)
from app.agent.scenario_schemas import SCENARIO_TOOLS
from app.agent.tools import fetch_market_prices, search_news, validate_consistency
from app.models.scenarios import NodeSuggestion, Scenario, ScenarioShock

logger = logging.getLogger(__name__)

# Phase round budgets
PHASE1_ROUNDS = 3   # News ingestion
PHASE2_ROUNDS = 3   # Historical research
PHASE3_ROUNDS = 5   # Unconstrained generation
PHASE4_ROUNDS = 5   # Graph mapping + output
MAX_ROUNDS = PHASE1_ROUNDS + PHASE2_ROUNDS + PHASE3_ROUNDS + PHASE4_ROUNDS  # 16


def _get_phase(round_num: int) -> str:
    if round_num < PHASE1_ROUNDS:
        return "news"
    elif round_num < PHASE1_ROUNDS + PHASE2_ROUNDS:
        return "history"
    elif round_num < PHASE1_ROUNDS + PHASE2_ROUNDS + PHASE3_ROUNDS:
        return "generation"
    else:
        return "mapping"


def _build_topology_string(graph: nx.DiGraph) -> tuple[str, str, int, int]:
    """Build node list + edge list strings from graph topology only (no sentiments)."""
    node_lines = []
    for nid, data in sorted(graph.nodes(data=True)):
        ntype = data.get("node_type", "unknown")
        label = data.get("label", nid)
        desc = data.get("description", "")
        node_lines.append(f"  - {nid} | {label} | type={ntype} | {desc}")

    edge_lines = []
    for src, tgt, edata in graph.edges(data=True):
        direction = edata.get("direction", "positive")
        weight = edata.get("base_weight", 0.3)
        desc = edata.get("description", "")
        edge_lines.append(f"  - {src} -> {tgt} | {direction} | weight={weight:.2f} | {desc}")

    return (
        "\n".join(node_lines),
        "\n".join(edge_lines),
        graph.number_of_nodes(),
        graph.number_of_edges(),
    )


async def run_scenario_extrapolation(
    trigger: str,
    trigger_type: str,
    session: AsyncSession,
    app_state,
) -> Scenario:
    """Run the scenario extrapolation agent (5-phase loop).

    If trigger is empty, auto-picks the most interesting event from current news.
    """
    from app.config import settings

    graph = app_state.graph

    # Validate API key
    provider = settings.llm_provider
    if provider == "openai" and not settings.openai_api_key:
        scenario = Scenario(
            trigger=trigger or "(auto)", trigger_type=trigger_type, status="error",
            error="OPENAI_API_KEY not configured", finished_at=datetime.utcnow(),
        )
        session.add(scenario)
        await session.commit()
        return scenario
    elif provider == "anthropic" and not settings.anthropic_api_key:
        scenario = Scenario(
            trigger=trigger or "(auto)", trigger_type=trigger_type, status="error",
            error="ANTHROPIC_API_KEY not configured", finished_at=datetime.utcnow(),
        )
        session.add(scenario)
        await session.commit()
        return scenario

    # If no trigger provided, auto-pick from current news
    if not trigger.strip():
        trigger_type = "news_auto"
        trigger = await _auto_pick_trigger(graph)
        if not trigger:
            scenario = Scenario(
                trigger="(no news found)", trigger_type=trigger_type, status="error",
                error="Could not find any scenario-worthy events in current news",
                finished_at=datetime.utcnow(),
            )
            session.add(scenario)
            await session.commit()
            return scenario

    # Create scenario record
    scenario = Scenario(trigger=trigger, trigger_type=trigger_type, status="running")
    session.add(scenario)
    await session.commit()

    tool_calls_log: list[dict] = []
    submitted_result: dict | None = None

    try:
        # Phase 1: News ingestion
        messages: list[dict] = [
            {"role": "user", "content": PHASE1_NEWS_PROMPT.format(trigger=trigger)},
        ]

        for round_num in range(PHASE1_ROUNDS):
            phase = "news"
            llm_response, messages = await chat_with_tools(
                system=SCENARIO_SYSTEM_PROMPT,
                messages=messages,
                tools=SCENARIO_TOOLS,
            )

            if llm_response.done or not llm_response.tool_calls:
                break

            results: dict[str, str] = {}
            for tc in llm_response.tool_calls:
                logger.info("[scenario:%s round %d] %s(%s)", phase, round_num, tc.name, json.dumps(tc.input)[:200])
                result = await _execute_scenario_tool(tc.name, tc.input, session, graph)
                results[tc.id] = result
                tool_calls_log.append({
                    "tool": tc.name, "input": tc.input,
                    "output": result[:2000] if isinstance(result, str) else str(result)[:2000],
                    "round": round_num, "phase": phase,
                })

            messages = append_tool_results(messages, llm_response.tool_calls, results)
            _broadcast_scenario_progress(scenario.id, round_num, phase, tool_calls_log)

        # Phase 2: Historical research
        messages.append({"role": "user", "content": PHASE2_HISTORY_PROMPT})

        for round_num in range(PHASE1_ROUNDS, PHASE1_ROUNDS + PHASE2_ROUNDS):
            phase = "history"
            llm_response, messages = await chat_with_tools(
                system=SCENARIO_SYSTEM_PROMPT,
                messages=messages,
                tools=SCENARIO_TOOLS,
            )

            if llm_response.done or not llm_response.tool_calls:
                break

            results = {}
            for tc in llm_response.tool_calls:
                logger.info("[scenario:%s round %d] %s(%s)", phase, round_num, tc.name, json.dumps(tc.input)[:200])
                result = await _execute_scenario_tool(tc.name, tc.input, session, graph)
                results[tc.id] = result
                tool_calls_log.append({
                    "tool": tc.name, "input": tc.input,
                    "output": result[:2000] if isinstance(result, str) else str(result)[:2000],
                    "round": round_num, "phase": phase,
                })

            messages = append_tool_results(messages, llm_response.tool_calls, results)
            _broadcast_scenario_progress(scenario.id, round_num, phase, tool_calls_log)

        # Phase 3: Unconstrained scenario generation
        messages.append({"role": "user", "content": PHASE3_GENERATE_PROMPT})

        for round_num in range(PHASE1_ROUNDS + PHASE2_ROUNDS, PHASE1_ROUNDS + PHASE2_ROUNDS + PHASE3_ROUNDS):
            phase = "generation"
            llm_response, messages = await chat_with_tools(
                system=SCENARIO_SYSTEM_PROMPT,
                messages=messages,
                tools=SCENARIO_TOOLS,
            )

            if llm_response.done or not llm_response.tool_calls:
                break

            results = {}
            for tc in llm_response.tool_calls:
                logger.info("[scenario:%s round %d] %s(%s)", phase, round_num, tc.name, json.dumps(tc.input)[:200])
                result = await _execute_scenario_tool(tc.name, tc.input, session, graph)
                results[tc.id] = result
                tool_calls_log.append({
                    "tool": tc.name, "input": tc.input,
                    "output": result[:2000] if isinstance(result, str) else str(result)[:2000],
                    "round": round_num, "phase": phase,
                })

            messages = append_tool_results(messages, llm_response.tool_calls, results)
            _broadcast_scenario_progress(scenario.id, round_num, phase, tool_calls_log)

        # Phase 4: Graph mapping
        node_list, edge_list, node_count, edge_count = _build_topology_string(graph)
        map_prompt = PHASE4_MAP_PROMPT_TEMPLATE.format(
            node_count=node_count,
            edge_count=edge_count,
            node_list=node_list,
            edge_list=edge_list,
        )
        messages.append({"role": "user", "content": map_prompt})

        for round_num in range(PHASE1_ROUNDS + PHASE2_ROUNDS + PHASE3_ROUNDS, MAX_ROUNDS):
            phase = "mapping"
            llm_response, messages = await chat_with_tools(
                system=SCENARIO_SYSTEM_PROMPT,
                messages=messages,
                tools=SCENARIO_TOOLS,
            )

            if llm_response.done or not llm_response.tool_calls:
                break

            results = {}
            for tc in llm_response.tool_calls:
                logger.info("[scenario:%s round %d] %s(%s)", phase, round_num, tc.name, json.dumps(tc.input)[:200])

                # Intercept submit_scenarios to capture the result
                if tc.name == "submit_scenarios":
                    submitted_result = tc.input
                    result = json.dumps({"status": "accepted", "message": "Scenarios submitted successfully."})
                else:
                    result = await _execute_scenario_tool(tc.name, tc.input, session, graph)

                results[tc.id] = result
                tool_calls_log.append({
                    "tool": tc.name, "input": tc.input,
                    "output": result[:2000] if isinstance(result, str) else str(result)[:2000],
                    "round": round_num, "phase": phase,
                })

            messages = append_tool_results(messages, llm_response.tool_calls, results)
            _broadcast_scenario_progress(scenario.id, round_num, phase, tool_calls_log)

            # If scenarios were submitted, we're done
            if submitted_result:
                break

        # Save results
        if submitted_result:
            scenario.status = "completed"
            scenario.scenarios_json = submitted_result
            scenario.research_summary = submitted_result.get("research_summary", "")
            scenario.historical_parallels = submitted_result.get("historical_parallels", "")

            # Save individual shocks + suggestions to DB
            await _persist_scenario_details(scenario.id, submitted_result, session, graph)
        else:
            scenario.status = "completed"
            scenario.error = "Agent did not call submit_scenarios — check tool call log"
            # Try to extract from the last text response
            if messages and messages[-1].get("role") == "assistant":
                content = messages[-1].get("content", "")
                if isinstance(content, str):
                    scenario.research_summary = content[:1000]

        scenario.finished_at = datetime.utcnow()

    except Exception as e:
        logger.exception("Scenario agent run failed")
        try:
            await session.rollback()
        except Exception:
            pass
        # Persist error in fresh session
        try:
            from app.db.connection import async_session
            async with async_session() as err_session:
                from sqlalchemy import update
                await err_session.execute(
                    update(Scenario)
                    .where(Scenario.id == scenario.id)
                    .values(
                        status="error",
                        error=str(e)[:2000],
                        finished_at=datetime.utcnow(),
                    )
                )
                await err_session.commit()
            scenario.status = "error"
            scenario.error = str(e)[:2000]
            return scenario
        except Exception as commit_err:
            logger.error("Failed to persist scenario error: %s", commit_err)
            return scenario

    await session.commit()

    # Broadcast completion
    _broadcast_scenario_complete(scenario)

    return scenario


async def _execute_scenario_tool(
    tool_name: str,
    tool_input: dict,
    session: AsyncSession,
    graph: nx.DiGraph,
) -> str:
    """Dispatch scenario tool calls to existing tool functions."""
    if tool_name == "search_news":
        return await search_news(
            query=tool_input["query"],
            max_results=tool_input.get("max_results", 10),
        )
    elif tool_name == "fetch_market_prices":
        return await fetch_market_prices(
            tickers=tool_input.get("tickers"),
        )
    elif tool_name == "validate_consistency":
        return await validate_consistency(
            node_ids=tool_input["node_ids"],
            session=session,
            graph=graph,
        )
    elif tool_name == "get_graph_topology":
        return _get_graph_topology(graph)
    elif tool_name == "submit_scenarios":
        # Handled by the caller (intercepted in the loop)
        return json.dumps({"status": "accepted"})
    else:
        return json.dumps({"error": f"Unknown scenario tool: {tool_name}"})


def _get_graph_topology(graph: nx.DiGraph) -> str:
    """Return graph topology as JSON — nodes + edges, NO sentiments."""
    nodes = []
    for nid, data in graph.nodes(data=True):
        nodes.append({
            "id": nid,
            "label": data.get("label", nid),
            "node_type": data.get("node_type", "unknown"),
            "description": data.get("description", ""),
        })

    edges = []
    for src, tgt, edata in graph.edges(data=True):
        edges.append({
            "source": src,
            "target": tgt,
            "direction": edata.get("direction", "positive"),
            "base_weight": edata.get("base_weight", 0.3),
            "description": edata.get("description", ""),
        })

    return json.dumps({
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    })


async def _persist_scenario_details(
    scenario_id: int,
    result: dict,
    session: AsyncSession,
    graph: nx.DiGraph,
) -> None:
    """Save individual shocks and suggestions from the scenario result.

    Skips shocks/edges referencing nodes that don't exist in the graph
    (the agent may suggest impacts to hypothetical nodes).
    """
    graph_node_ids = set(graph.nodes)
    branches = result.get("branches", [])

    for branch_idx, branch in enumerate(branches):
        # Shocks — only persist for nodes that exist in graph
        for shock in branch.get("shocks", []):
            node_id = shock.get("node_id", "")
            if node_id not in graph_node_ids:
                logger.info("Skipping shock to non-existent node '%s' (branch %d)", node_id, branch_idx)
                continue
            shock_value = max(-1.0, min(1.0, shock.get("shock_value", 0.0)))
            session.add(ScenarioShock(
                scenario_id=scenario_id,
                branch_idx=branch_idx,
                node_id=node_id,
                shock_value=shock_value,
                reasoning=shock.get("reasoning", ""),
                original_impact=shock.get("original_impact", ""),
            ))

        # Node suggestions — these reference hypothetical nodes, no FK issue
        for ns in branch.get("node_suggestions", []):
            session.add(NodeSuggestion(
                scenario_id=scenario_id,
                branch_idx=branch_idx,
                suggested_id=ns["suggested_id"],
                suggested_label=ns["suggested_label"],
                suggested_type=ns.get("suggested_type", "macro"),
                description=ns.get("description", ""),
                reasoning=ns.get("reasoning", ""),
            ))

        # Edge suggestions — only persist if BOTH nodes exist (FK constraint)
        for es in branch.get("edge_suggestions", []):
            src = es.get("source_id", "")
            tgt = es.get("target_id", "")
            if src not in graph_node_ids or tgt not in graph_node_ids:
                logger.info("Skipping edge suggestion %s -> %s (node not in graph)", src, tgt)
                continue
            from app.models.observations import EdgeSuggestion
            session.add(EdgeSuggestion(
                source_id=src,
                target_id=tgt,
                suggested_direction=es.get("direction", "positive"),
                suggested_weight=0.3,
                llm_reasoning=es.get("reasoning", ""),
                status="pending",
            ))


# Track fire-and-forget broadcast tasks
_broadcast_tasks: set[asyncio.Task] = set()


def _broadcast_done_callback(task: asyncio.Task) -> None:
    _broadcast_tasks.discard(task)
    if not task.cancelled() and task.exception():
        logger.debug("Scenario broadcast failed: %s", task.exception())


def _broadcast_scenario_progress(
    scenario_id: int,
    round_num: int,
    phase: str,
    tool_calls_log: list[dict],
) -> None:
    """Broadcast scenario progress via WebSocket."""
    try:
        from app.api.websocket import manager
        task = asyncio.create_task(manager.broadcast({
            "type": "scenario_progress",
            "data": {
                "scenario_id": scenario_id,
                "round": round_num + 1,
                "max_rounds": MAX_ROUNDS,
                "phase": phase,
                "total_tool_calls": len(tool_calls_log),
            },
        }))
        _broadcast_tasks.add(task)
        task.add_done_callback(_broadcast_done_callback)
    except Exception as e:
        logger.debug("Failed to broadcast scenario progress: %s", e)


def _broadcast_scenario_complete(scenario: Scenario) -> None:
    """Broadcast scenario completion via WebSocket."""
    try:
        from app.api.websocket import manager
        branches = []
        if scenario.scenarios_json and "branches" in scenario.scenarios_json:
            for b in scenario.scenarios_json["branches"]:
                branches.append({
                    "title": b.get("title", ""),
                    "probability": b.get("probability", 0),
                    "shock_count": len(b.get("shocks", [])),
                })

        task = asyncio.create_task(manager.broadcast({
            "type": "scenario_complete",
            "data": {
                "scenario_id": scenario.id,
                "status": scenario.status,
                "trigger": scenario.trigger,
                "branch_count": len(branches),
                "branches": branches,
                "error": scenario.error,
            },
        }))
        _broadcast_tasks.add(task)
        task.add_done_callback(_broadcast_done_callback)
    except Exception as e:
        logger.debug("Failed to broadcast scenario complete: %s", e)


async def _auto_pick_trigger(graph: nx.DiGraph) -> str:
    """Auto-pick the most scenario-worthy event from current news.

    Returns a trigger string, or empty string if nothing found.
    """
    try:
        triggers = await generate_quick_triggers(graph)
        if triggers:
            # Pick the first (most impactful) suggestion
            return triggers[0].get("suggested_prompt", triggers[0].get("headline", ""))
    except Exception as e:
        logger.warning("Auto-pick trigger failed: %s", e)
    return ""


async def generate_quick_triggers(graph: nx.DiGraph) -> list[dict]:
    """Scan current RSS headlines and pick 2-3 scenario-worthy events.

    Lightweight: one LLM call, no tool loop.
    """
    try:
        news_result = await search_news(query="markets economy geopolitics", max_results=20)
        news_data = json.loads(news_result)
        articles = news_data.get("articles", [])
        if not articles:
            return []

        headlines_text = "\n".join(
            f"- [{a.get('source', '?')}] {a.get('title', '')}"
            for a in articles[:20]
        )

        response_text = await simple_completion(
            system="You are a financial news analyst. Return ONLY valid JSON, no markdown.",
            user_message=QUICK_TRIGGERS_PROMPT.format(headlines=headlines_text),
        )

        # Parse JSON from response
        response_text = response_text.strip()
        if response_text.startswith("```"):
            # Strip markdown code fence
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        triggers = json.loads(response_text)
        if not isinstance(triggers, list):
            return []

        return [
            {
                "headline": t.get("headline", "")[:80],
                "source": t.get("source", ""),
                "suggested_prompt": t.get("suggested_prompt", ""),
            }
            for t in triggers[:3]
        ]
    except Exception as e:
        logger.warning("Quick trigger generation failed: %s", e)
        return []
