"""Scenario extrapolation API endpoints."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_session
from app.models.scenarios import NodeSuggestion, Scenario, ScenarioShock

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


# ── Request / Response models ───────────────────────────────────


class ScenarioTriggerRequest(BaseModel):
    trigger: str
    trigger_type: str = "user_prompt"  # news_event | user_prompt


class ScenarioTriggerResponse(BaseModel):
    id: int
    status: str


class ScenarioBranchOut(BaseModel):
    title: str
    probability: float
    narrative: str
    causal_chain: list[str]
    time_horizon: str
    invalidation: str | None = None
    shocks: list[dict]
    node_suggestions: list[dict] | None = None
    edge_suggestions: list[dict] | None = None


class ScenarioOut(BaseModel):
    id: int
    trigger: str
    trigger_type: str
    status: str
    branches: list[ScenarioBranchOut]
    research_summary: str | None
    historical_parallels: str | None
    selected_branch_idx: int | None
    simulation_result: dict | None
    error: str | None
    created_at: str
    finished_at: str | None

    model_config = {"from_attributes": True}


class ScenarioSummaryOut(BaseModel):
    id: int
    trigger: str
    trigger_type: str
    status: str
    branch_count: int
    created_at: str

    model_config = {"from_attributes": True}


class ApplyBranchRequest(BaseModel):
    branch_idx: int = 0
    shock_overrides: list[dict] | None = None  # [{node_id, shock_value}]


class MultiShockImpact(BaseModel):
    node_id: str
    label: str
    total_impact: float
    contributing_shocks: list[str]
    hops: int


class ApplyBranchResponse(BaseModel):
    scenario_id: int
    branch_idx: int
    branch_title: str
    shocks_applied: int
    impacts: list[MultiShockImpact]
    total_nodes_affected: int


class QuickTriggerOut(BaseModel):
    headline: str
    source: str
    suggested_prompt: str


# ── Endpoints ───────────────────────────────────────────────────


@router.post("", response_model=ScenarioTriggerResponse)
async def trigger_scenario(
    request: ScenarioTriggerRequest,
    session: AsyncSession = Depends(get_session),
):
    """Trigger scenario extrapolation (runs in background, returns immediately)."""
    from app.main import app_state

    task = asyncio.create_task(
        _run_scenario_background(request.trigger, request.trigger_type, app_state)
    )
    task.add_done_callback(_handle_task_error)

    # Return placeholder — real result comes via WebSocket or GET
    return ScenarioTriggerResponse(id=0, status="running")


@router.get("", response_model=list[ScenarioSummaryOut])
async def list_scenarios(
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """List recent scenarios."""
    result = await session.execute(
        select(Scenario).order_by(Scenario.created_at.desc()).limit(limit)
    )
    scenarios = result.scalars().all()
    return [
        ScenarioSummaryOut(
            id=s.id,
            trigger=s.trigger,
            trigger_type=s.trigger_type,
            status=s.status,
            branch_count=len(s.scenarios_json.get("branches", [])) if s.scenarios_json else 0,
            created_at=s.created_at.isoformat() if s.created_at else "",
        )
        for s in scenarios
    ]


@router.get("/quick-triggers", response_model=list[QuickTriggerOut])
async def get_quick_triggers():
    """Get 2-3 scenario-worthy events from current news."""
    from app.agent.scenario_agent import generate_quick_triggers
    from app.main import app_state

    triggers = await generate_quick_triggers(app_state.graph)
    return [QuickTriggerOut(**t) for t in triggers]


@router.get("/{scenario_id}", response_model=ScenarioOut)
async def get_scenario(
    scenario_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get full scenario result with branches."""
    result = await session.execute(
        select(Scenario).where(Scenario.id == scenario_id)
    )
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

    branches = _extract_branches(scenario)

    return ScenarioOut(
        id=scenario.id,
        trigger=scenario.trigger,
        trigger_type=scenario.trigger_type,
        status=scenario.status,
        branches=branches,
        research_summary=scenario.research_summary,
        historical_parallels=scenario.historical_parallels,
        selected_branch_idx=scenario.selected_branch_idx,
        simulation_result=scenario.simulation_result,
        error=scenario.error,
        created_at=scenario.created_at.isoformat() if scenario.created_at else "",
        finished_at=scenario.finished_at.isoformat() if scenario.finished_at else None,
    )


@router.post("/{scenario_id}/apply", response_model=ApplyBranchResponse)
async def apply_scenario_branch(
    scenario_id: int,
    request: ApplyBranchRequest,
    session: AsyncSession = Depends(get_session),
):
    """Apply a scenario branch to the graph (multi-shock simulate, read-only)."""
    from app.main import app_state
    from app.graph_engine.propagation import propagate_signal
    from app.graph_engine.regimes import detect_regime

    result = await session.execute(
        select(Scenario).where(Scenario.id == scenario_id)
    )
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

    if not scenario.scenarios_json or "branches" not in scenario.scenarios_json:
        raise HTTPException(status_code=400, detail="Scenario has no branches")

    branches = scenario.scenarios_json["branches"]
    if request.branch_idx >= len(branches):
        raise HTTPException(status_code=400, detail=f"Branch {request.branch_idx} does not exist")

    branch = branches[request.branch_idx]
    graph = app_state.graph
    regime = detect_regime(graph)

    # Build shock list (with optional overrides)
    shocks = []
    for shock in branch.get("shocks", []):
        node_id = shock["node_id"]
        shock_value = shock["shock_value"]

        # Apply overrides if provided
        if request.shock_overrides:
            for override in request.shock_overrides:
                if override.get("node_id") == node_id:
                    shock_value = override.get("shock_value", shock_value)
                    break

        shock_value = max(-1.0, min(1.0, shock_value))
        if node_id in graph:
            shocks.append({"node_id": node_id, "shock_value": shock_value})

    # Multi-shock simulate: propagate each shock, merge impacts
    merged_impacts: dict[str, dict] = {}  # node_id -> {total_impact, contributing_shocks, hops}

    for shock in shocks:
        nid = shock["node_id"]
        current = graph.nodes[nid].get("composite_sentiment", 0.0) or 0.0
        delta = shock["shock_value"] - current

        if abs(delta) < 0.001:
            continue

        prop_result = propagate_signal(
            graph, nid, delta, regime=regime.state.value,
        )

        for affected_nid, impact in prop_result.impacts.items():
            if affected_nid in [s["node_id"] for s in shocks]:
                continue  # Skip directly shocked nodes from showing as propagation impacts

            if affected_nid not in merged_impacts:
                merged_impacts[affected_nid] = {
                    "total_impact": 0.0,
                    "contributing_shocks": [],
                    "hops": len(prop_result.paths.get(affected_nid, [])) - 1,
                }

            merged_impacts[affected_nid]["total_impact"] += impact
            merged_impacts[affected_nid]["contributing_shocks"].append(nid)
            # Keep minimum hops
            new_hops = len(prop_result.paths.get(affected_nid, [])) - 1
            if new_hops > 0:
                merged_impacts[affected_nid]["hops"] = min(
                    merged_impacts[affected_nid]["hops"], new_hops
                )

    # Sort by magnitude
    sorted_impacts = sorted(
        merged_impacts.items(), key=lambda x: abs(x[1]["total_impact"]), reverse=True
    )

    impacts = []
    for nid, data in sorted_impacts:
        label = graph.nodes[nid].get("label", nid) if nid in graph else nid
        impacts.append(MultiShockImpact(
            node_id=nid,
            label=label,
            total_impact=round(data["total_impact"], 4),
            contributing_shocks=list(set(data["contributing_shocks"])),
            hops=max(data["hops"], 1),
        ))

    # Save simulation result + selected branch
    simulation_data = {
        "branch_idx": request.branch_idx,
        "shocks": shocks,
        "impacts": [i.model_dump() for i in impacts],
        "total_affected": len(impacts),
    }
    scenario.selected_branch_idx = request.branch_idx
    scenario.simulation_result = simulation_data
    await session.commit()

    return ApplyBranchResponse(
        scenario_id=scenario_id,
        branch_idx=request.branch_idx,
        branch_title=branch.get("title", ""),
        shocks_applied=len(shocks),
        impacts=impacts[:30],  # Cap at 30 for response size
        total_nodes_affected=len(impacts),
    )


@router.post("/quick-triggers", response_model=list[QuickTriggerOut])
async def refresh_quick_triggers():
    """Refresh quick triggers from current news (POST alias for GET)."""
    return await get_quick_triggers()


@router.get("/hypothetical")
async def get_hypothetical_state():
    """Get current hypothetical node/edge state."""
    from app.main import app_state
    return {
        "hypothetical_node_ids": list(app_state.hypothetical_node_ids),
        "hypothetical_edge_keys": [list(k) for k in app_state.hypothetical_edge_keys],
        "count": len(app_state.hypothetical_node_ids),
    }


# ── Evolve Graph ────────────────────────────────────────────────


class EvolveRequest(BaseModel):
    branch_idx: int = 0


class EvolveResponse(BaseModel):
    nodes_added: list[dict]
    edges_added: list[dict]
    hypothetical_count: int


@router.post("/{scenario_id}/evolve", response_model=EvolveResponse)
async def evolve_graph(
    scenario_id: int,
    request: EvolveRequest,
    session: AsyncSession = Depends(get_session),
):
    """Add hypothetical nodes/edges from a scenario branch to the in-memory graph.

    These are temporary — removed when the user runs a full analysis.
    """
    from app.main import app_state
    from app.models.graph import NodeType

    result = await session.execute(
        select(Scenario).where(Scenario.id == scenario_id)
    )
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

    if not scenario.scenarios_json or "branches" not in scenario.scenarios_json:
        raise HTTPException(status_code=400, detail="Scenario has no branches")

    branches = scenario.scenarios_json["branches"]
    if request.branch_idx >= len(branches):
        raise HTTPException(status_code=400, detail=f"Branch {request.branch_idx} does not exist")

    branch = branches[request.branch_idx]
    graph = app_state.graph
    nodes_added = []
    edges_added = []

    async with app_state.graph_lock:
        # Add suggested nodes
        for ns in branch.get("node_suggestions", []):
            nid = ns.get("suggested_id", "")
            if not nid or nid in graph:
                continue  # Skip if already exists
            graph.add_node(
                nid,
                label=ns.get("suggested_label", nid),
                node_type=ns.get("suggested_type", "macro"),
                description=ns.get("description", ""),
                composite_sentiment=0.0,
                confidence=0.0,
                hypothetical=True,
            )
            app_state.hypothetical_node_ids.add(nid)
            nodes_added.append({
                "id": nid,
                "label": ns.get("suggested_label", nid),
                "type": ns.get("suggested_type", "macro"),
            })

        # Add suggested edges (only if both nodes exist)
        for es in branch.get("edge_suggestions", []):
            src = es.get("source_id", "")
            tgt = es.get("target_id", "")
            if not src or not tgt:
                continue
            if src not in graph or tgt not in graph:
                continue
            if graph.has_edge(src, tgt):
                continue  # Already exists
            graph.add_edge(
                src, tgt,
                direction=es.get("direction", "positive"),
                base_weight=0.3,
                dynamic_weight=0.3,
                description=es.get("reasoning", ""),
                hypothetical=True,
            )
            app_state.hypothetical_edge_keys.add((src, tgt))
            edges_added.append({
                "source": src,
                "target": tgt,
                "direction": es.get("direction", "positive"),
            })

    # Broadcast graph update
    try:
        from app.api.websocket import manager
        from app.api.routes_graph import get_full_graph
        from app.db.connection import async_session as async_session_factory
        async with async_session_factory() as graph_session:
            graph_data = await get_full_graph(graph_session)
            await manager.broadcast({"type": "graph_update", "data": graph_data.model_dump()})
    except Exception as e:
        logger.warning("Failed to broadcast after evolve: %s", e)

    return EvolveResponse(
        nodes_added=nodes_added,
        edges_added=edges_added,
        hypothetical_count=len(app_state.hypothetical_node_ids),
    )


@router.post("/reset-evolve")
async def reset_evolve():
    """Remove all hypothetical nodes/edges from the graph."""
    from app.main import app_state

    removed_nodes = 0
    removed_edges = 0

    async with app_state.graph_lock:
        # Remove hypothetical edges first (before removing nodes)
        for src, tgt in list(app_state.hypothetical_edge_keys):
            if app_state.graph.has_edge(src, tgt):
                app_state.graph.remove_edge(src, tgt)
                removed_edges += 1
        app_state.hypothetical_edge_keys.clear()

        # Remove hypothetical nodes
        for nid in list(app_state.hypothetical_node_ids):
            if nid in app_state.graph:
                app_state.graph.remove_node(nid)
                removed_nodes += 1
        app_state.hypothetical_node_ids.clear()

    # Broadcast updated graph
    try:
        from app.api.websocket import manager
        from app.api.routes_graph import get_full_graph
        from app.db.connection import async_session as async_session_factory
        async with async_session_factory() as session:
            graph_data = await get_full_graph(session)
            await manager.broadcast({"type": "graph_update", "data": graph_data.model_dump()})
    except Exception as e:
        logger.warning("Failed to broadcast after reset-evolve: %s", e)

    return {"removed_nodes": removed_nodes, "removed_edges": removed_edges}


# ── Helpers ─────────────────────────────────────────────────────


def _extract_branches(scenario: Scenario) -> list[ScenarioBranchOut]:
    """Extract branch data from scenario JSON."""
    if not scenario.scenarios_json or "branches" not in scenario.scenarios_json:
        return []

    branches = []
    for b in scenario.scenarios_json["branches"]:
        branches.append(ScenarioBranchOut(
            title=b.get("title", "Untitled"),
            probability=b.get("probability", 0),
            narrative=b.get("narrative", ""),
            causal_chain=b.get("causal_chain", []),
            time_horizon=b.get("time_horizon", "weeks"),
            invalidation=b.get("invalidation"),
            shocks=b.get("shocks", []),
            node_suggestions=b.get("node_suggestions"),
            edge_suggestions=b.get("edge_suggestions"),
        ))
    return branches


async def _run_scenario_background(trigger: str, trigger_type: str, app_state):
    """Run scenario agent in background with its own DB session."""
    from app.agent.scenario_agent import run_scenario_extrapolation
    from app.api.websocket import manager
    from app.db.connection import async_session

    try:
        async with async_session() as session:
            scenario = await asyncio.wait_for(
                run_scenario_extrapolation(
                    trigger=trigger,
                    trigger_type=trigger_type,
                    session=session,
                    app_state=app_state,
                ),
                timeout=600.0,  # 10-minute timeout
            )
            # Broadcast completion (scenario_agent already broadcasts, but ensure)
            await manager.broadcast({
                "type": "scenario_complete",
                "data": {
                    "scenario_id": scenario.id,
                    "status": scenario.status,
                    "trigger": scenario.trigger,
                    "error": scenario.error,
                },
            })
    except Exception as e:
        logger.exception("Background scenario failed: %s", e)
        try:
            await manager.broadcast({
                "type": "scenario_complete",
                "data": {
                    "scenario_id": 0,
                    "status": "error",
                    "trigger": trigger,
                    "error": str(e),
                },
            })
        except Exception as notify_err:
            logger.error("Failed to send scenario error to frontend: %s", notify_err)


def _handle_task_error(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    exc = task.exception()
    if exc:
        logger.error("Scenario background task error: %s", exc)
