"""Agent trigger and status endpoints."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.orchestrator import run_analysis
from app.db.connection import get_session
from app.models.observations import AgentRun, Prediction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent", tags=["agent"])


class LLMConfigOut(BaseModel):
    provider: str
    anthropic_model: str
    openai_model: str
    has_anthropic_key: bool
    has_openai_key: bool


class LLMConfigUpdate(BaseModel):
    provider: str | None = None
    anthropic_model: str | None = None
    openai_model: str | None = None


@router.get("/llm-config", response_model=LLMConfigOut)
async def get_llm_config():
    """Get current LLM provider configuration."""
    from app.config import settings
    return LLMConfigOut(
        provider=settings.llm_provider,
        anthropic_model=settings.anthropic_model,
        openai_model=settings.openai_model,
        has_anthropic_key=bool(settings.anthropic_api_key),
        has_openai_key=bool(settings.openai_api_key),
    )


@router.post("/llm-config", response_model=LLMConfigOut)
async def update_llm_config(update: LLMConfigUpdate):
    """Switch LLM provider or model at runtime."""
    from app.config import settings
    if update.provider and update.provider in ("anthropic", "openai"):
        settings.llm_provider = update.provider
    if update.anthropic_model:
        settings.anthropic_model = update.anthropic_model
    if update.openai_model:
        settings.openai_model = update.openai_model
    return LLMConfigOut(
        provider=settings.llm_provider,
        anthropic_model=settings.anthropic_model,
        openai_model=settings.openai_model,
        has_anthropic_key=bool(settings.anthropic_api_key),
        has_openai_key=bool(settings.openai_api_key),
    )


class AnalysisRequest(BaseModel):
    node_ids: list[str] | None = None
    trigger: str = "manual"


class AgentRunOut(BaseModel):
    id: int
    trigger: str
    status: str
    nodes_analyzed: list
    tool_calls: list | None = None
    summary: str | None
    started_at: datetime
    finished_at: datetime | None
    error: str | None

    model_config = {"from_attributes": True}


@router.post("/analyze", response_model=AgentRunOut)
async def trigger_analysis(
    request: AnalysisRequest,
    session: AsyncSession = Depends(get_session),
):
    """Trigger a Claude agent analysis run (returns immediately, runs in background)."""
    from app.main import app_state

    node_ids = request.node_ids
    if not node_ids:
        node_ids = list(app_state.graph.nodes())

    # Run analysis in background so progress bar works via WebSocket
    task = asyncio.create_task(_run_analysis_background(node_ids, request.trigger, app_state))
    task.add_done_callback(_handle_notification_error)

    # Return a placeholder response immediately
    return AgentRunOut(
        id=0,
        trigger=request.trigger,
        status="running",
        nodes_analyzed=node_ids,
        tool_calls=None,
        summary=None,
        started_at=datetime.utcnow(),
        finished_at=None,
        error=None,
    )


@router.get("/runs", response_model=list[AgentRunOut])
async def list_runs(limit: int = 20, session: AsyncSession = Depends(get_session)):
    """List recent agent runs."""
    result = await session.execute(
        select(AgentRun).order_by(AgentRun.started_at.desc()).limit(limit)
    )
    return [_run_to_out(r) for r in result.scalars().all()]


def _run_to_out(r: AgentRun) -> AgentRunOut:
    return AgentRunOut(
        id=r.id,
        trigger=r.trigger,
        status=r.status,
        nodes_analyzed=r.nodes_analyzed or [],
        tool_calls=r.tool_calls,
        summary=r.summary,
        started_at=r.started_at,
        finished_at=r.finished_at,
        error=r.error,
    )


async def _run_analysis_background(node_ids: list[str], trigger: str, app_state):
    """Run agent analysis in background with its own DB session."""
    from app.api.websocket import manager
    from app.db.connection import async_session

    try:
        async with async_session() as session:
            agent_run = await run_analysis(
                node_ids=node_ids,
                session=session,
                graph=app_state.graph,
                trigger=trigger,
            )
            # Notify WebSocket clients: analysis complete + updated graph
            await manager.broadcast({
                "type": "agent_complete",
                "data": {
                    "id": agent_run.id,
                    "status": agent_run.status,
                    "summary": agent_run.summary,
                    "error": agent_run.error,
                },
            })
            await _notify_graph_update(app_state)
    except Exception as e:
        logger.exception("Background analysis failed: %s", e)
        # Still notify frontend so it doesn't get stuck
        try:
            await manager.broadcast({
                "type": "agent_complete",
                "data": {
                    "id": 0,
                    "status": "error",
                    "summary": None,
                    "error": str(e),
                },
            })
        except Exception as notify_err:
            logger.error("Failed to send error notification to frontend: %s", notify_err)


def _handle_notification_error(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    exc = task.exception()
    if exc:
        logger.error("WebSocket notification failed: %s", exc)


async def _notify_graph_update(app_state):
    """Push graph update to all WebSocket clients."""
    from app.api.websocket import manager
    from app.db.connection import async_session
    from app.api.routes_graph import get_full_graph

    async with async_session() as session:
        graph_data = await get_full_graph(session)
        await manager.broadcast({"type": "graph_update", "data": graph_data.model_dump()})


# ── Prediction endpoints ────────────────────────────────────────


class PredictionOut(BaseModel):
    id: int
    node_id: str
    predicted_direction: str
    predicted_sentiment: float
    horizon_hours: int
    reasoning: str
    created_at: datetime
    resolved_at: datetime | None
    actual_sentiment: float | None
    hit: int | None
    magnitude_score: float | None = None

    model_config = {"from_attributes": True}


class PredictionSummary(BaseModel):
    total: int
    resolved: int
    pending: int
    hit_rate: float | None
    mean_magnitude_score: float | None = None
    by_direction: dict


@router.get("/predictions", response_model=list[PredictionOut])
async def list_predictions(
    limit: int = 20,
    status: str | None = None,
    node_id: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """List predictions with optional filters."""
    query = select(Prediction).order_by(Prediction.created_at.desc())
    if status == "pending":
        query = query.where(Prediction.resolved_at.is_(None))
    elif status == "resolved":
        query = query.where(Prediction.resolved_at.isnot(None))
    if node_id:
        query = query.where(Prediction.node_id == node_id)
    query = query.limit(limit)

    result = await session.execute(query)
    return [PredictionOut.model_validate(p) for p in result.scalars().all()]


@router.get("/predictions/summary", response_model=PredictionSummary)
async def get_prediction_summary(
    session: AsyncSession = Depends(get_session),
):
    """Aggregate prediction stats."""
    result = await session.execute(select(Prediction))
    all_preds = result.scalars().all()

    resolved = [p for p in all_preds if p.resolved_at is not None]
    pending = [p for p in all_preds if p.resolved_at is None]
    hits = sum(1 for p in resolved if p.hit == 1)
    misses = sum(1 for p in resolved if p.hit == 0)
    total_decided = hits + misses

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

    mag_scores = [p.magnitude_score for p in resolved if p.magnitude_score is not None]
    mean_mag = round(sum(mag_scores) / len(mag_scores), 4) if mag_scores else None

    return PredictionSummary(
        total=len(all_preds),
        resolved=len(resolved),
        pending=len(pending),
        hit_rate=round(hits / total_decided, 4) if total_decided > 0 else None,
        mean_magnitude_score=mean_mag,
        by_direction=by_direction,
    )


# ── Morning Brief ─────────────────────────────────────────────


class MorningBriefResponse(BaseModel):
    generated_at: str
    overnight_movers: list[dict]
    resolved_predictions: list[dict]
    prediction_summary: dict
    regime: dict
    top_propagation_paths: list[dict]
    narrative: str


@router.post("/morning-brief", response_model=MorningBriefResponse)
async def generate_morning_brief(
    session: AsyncSession = Depends(get_session),
):
    """Generate a morning intelligence brief: overnight movers, predictions, regime, narrative."""
    from app.main import app_state
    from app.graph_engine.anomalies import detect_anomalies
    from app.graph_engine.regimes import detect_regime, get_regime_history
    from app.graph_engine.propagation import propagate_signal
    from app.config import settings

    graph = app_state.graph
    now = datetime.utcnow()
    yesterday = now - timedelta(hours=24)

    # 1. Overnight movers (>1σ in last 24h)
    anomalies = await detect_anomalies(session, lookback_days=1, z_threshold=1.0)
    movers = [
        {
            "node_id": a.node_id,
            "label": graph.nodes[a.node_id].get("label", a.node_id) if a.node_id in graph else a.node_id,
            "direction": a.direction,
            "z_score": round(a.z_score, 2),
            "latest_value": round(a.latest_value, 4) if a.latest_value else None,
        }
        for a in anomalies[:10]
    ]

    # 2. Predictions resolved in last 24h
    result = await session.execute(
        select(Prediction)
        .where(Prediction.resolved_at >= yesterday)
        .order_by(Prediction.resolved_at.desc())
    )
    resolved_preds = result.scalars().all()
    resolved_list = [
        {
            "node_id": p.node_id,
            "predicted_direction": p.predicted_direction,
            "predicted_sentiment": round(p.predicted_sentiment, 3),
            "actual_sentiment": round(p.actual_sentiment, 3) if p.actual_sentiment is not None else None,
            "hit": p.hit,
            "reasoning": (p.reasoning or "")[:120],
        }
        for p in resolved_preds
    ]
    hits = sum(1 for p in resolved_preds if p.hit == 1)
    misses = sum(1 for p in resolved_preds if p.hit == 0)

    # 3. Regime
    regime = detect_regime(graph)
    history = await get_regime_history(session, days=1)
    regime_changed = False
    from_state = None
    if len(history) >= 2:
        prev = history[-2]["state"]
        if prev and prev != regime.state.value:
            regime_changed = True
            from_state = prev

    sorted_signals = sorted(
        regime.contributing_signals.items(), key=lambda x: abs(x[1]), reverse=True
    )
    top_drivers = [s[0] for s in sorted_signals[:5]]

    # 4. Propagation paths for top 3 movers
    paths_list = []
    for a in anomalies[:3]:
        if a.node_id not in graph:
            continue
        try:
            prop = propagate_signal(graph, a.node_id, a.z_score * 0.1, regime=regime.state.value)
            top_impacts = sorted(prop.impacts.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
            paths_list.append({
                "source": a.node_id,
                "source_label": graph.nodes[a.node_id].get("label", a.node_id) if a.node_id in graph else a.node_id,
                "impacts": [
                    {
                        "node_id": nid,
                        "label": graph.nodes[nid].get("label", nid) if nid in graph else nid,
                        "impact": round(imp, 4),
                        "hops": len(prop.paths.get(nid, [])) - 1 if nid in prop.paths else 0,
                    }
                    for nid, imp in top_impacts
                ],
            })
        except Exception:
            pass

    # 5. LLM narrative
    narrative = await _generate_brief_narrative(
        movers, resolved_list, hits, misses, regime, regime_changed, from_state,
        top_drivers, paths_list, settings,
    )

    # 6. Broadcast via WebSocket
    brief_data = {
        "generated_at": now.isoformat(),
        "overnight_movers": movers,
        "resolved_predictions": resolved_list,
        "prediction_summary": {
            "total": len(resolved_preds),
            "hits": hits,
            "misses": misses,
            "hit_rate": round(hits / (hits + misses), 3) if (hits + misses) > 0 else None,
        },
        "regime": {
            "state": regime.state.value,
            "confidence": regime.confidence,
            "composite_score": regime.composite_score,
            "changed": regime_changed,
            "from_state": from_state,
            "top_drivers": top_drivers,
        },
        "top_propagation_paths": paths_list,
        "narrative": narrative,
    }

    from app.api.websocket import manager
    await manager.broadcast({"type": "morning_brief", "data": brief_data})

    return MorningBriefResponse(**brief_data)


async def _generate_brief_narrative(
    movers, resolved, hits, misses, regime, regime_changed, from_state,
    top_drivers, paths, settings,
) -> str:
    """Generate LLM narrative for the morning brief."""
    # Build context
    movers_desc = ", ".join(
        f"{m['label']} ({m['direction']} {m['z_score']:+.1f}σ)" for m in movers[:5]
    ) or "No significant overnight moves."

    pred_desc = f"{hits} hits, {misses} misses" if (hits + misses) > 0 else "No predictions resolved."

    regime_desc = f"{regime.state.value.replace('_', ' ').upper()} (confidence {regime.confidence:.0%})"
    if regime_changed:
        regime_desc += f" — shifted from {from_state}"

    drivers_desc = ", ".join(top_drivers[:3])

    paths_desc = ""
    for p in paths[:2]:
        impacts = ", ".join(f"{i['label']} ({i['impact']:+.3f})" for i in p["impacts"][:3])
        paths_desc += f"  {p['source_label']} → {impacts}\n"

    prompt = (
        f"You are a macro strategist writing a daily morning brief. Be concise (4-6 sentences).\n\n"
        f"OVERNIGHT MOVERS: {movers_desc}\n"
        f"PREDICTIONS: {pred_desc}\n"
        f"REGIME: {regime_desc}\n"
        f"KEY DRIVERS: {drivers_desc}\n"
        f"PROPAGATION PATHS:\n{paths_desc}\n\n"
        f"Summarize the overnight developments, highlight the most important moves, "
        f"note any prediction outcomes, describe the current regime, and suggest what to watch today. "
        f"Write in flowing prose, no bullet points."
    )

    try:
        if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            response = client.messages.create(
                model=settings.anthropic_model,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        elif settings.openai_api_key:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model=settings.openai_model,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content or ""
        else:
            return (
                f"Morning brief: {movers_desc}. "
                f"Predictions: {pred_desc}. "
                f"Regime: {regime_desc}. "
                f"Watch: {drivers_desc}."
            )
    except Exception as e:
        logger.error("Morning brief LLM error: %s", e)
        return (
            f"Morning brief: {movers_desc}. "
            f"Predictions: {pred_desc}. "
            f"Regime: {regime_desc}."
        )


# ── Automation Toggles ─────────────────────────────────────────


class AutomationItem(BaseModel):
    id: str
    label: str
    description: str
    enabled: bool
    schedule: str | None = None


class AutomationsResponse(BaseModel):
    automations: list[AutomationItem]


class ToggleRequest(BaseModel):
    automation_id: str
    enabled: bool


@router.get("/automations", response_model=AutomationsResponse)
async def get_automations():
    """List all automation toggles with current status."""
    from app.data_pipeline.scheduler import scheduler

    # Scheduler is "enabled" if it has data-fetching jobs (not counting morning_brief)
    data_jobs = [j for j in scheduler.get_jobs() if j.id != "morning_brief"]
    scheduler_enabled = scheduler.running and len(data_jobs) > 0

    return AutomationsResponse(automations=[
        AutomationItem(
            id="scheduler",
            label="Background Scheduler",
            description="FRED, market, Reddit, news fetching + agent analysis + weight updates",
            enabled=scheduler_enabled,
            schedule="Multiple intervals (1h-6h)",
        ),
        AutomationItem(
            id="morning_brief",
            label="Morning Brief",
            description="Daily intelligence summary: overnight movers, predictions, regime, narrative",
            enabled=_is_morning_brief_scheduled(),
            schedule="Daily 7:00 AM UTC",
        ),
    ])


@router.post("/automations/toggle", response_model=AutomationsResponse)
async def toggle_automation(req: ToggleRequest):
    """Toggle an automation on or off at runtime."""
    from app.data_pipeline.scheduler import scheduler, setup_scheduler

    if req.automation_id == "scheduler":
        if req.enabled:
            # Enable: add data-fetching jobs (not morning_brief — that's separate)
            data_jobs = [j for j in scheduler.get_jobs() if j.id != "morning_brief"]
            if not data_jobs:
                from app.config import settings
                original = settings.scheduler_enabled
                settings.scheduler_enabled = True
                setup_scheduler()
                settings.scheduler_enabled = original
                # Remove morning_brief if setup_scheduler added it (it shouldn't, but be safe)
                # Morning brief is managed independently
            if not scheduler.running:
                scheduler.start()
            logger.info("Scheduler enabled at runtime")
        else:
            # Disable: remove data jobs only, preserve morning_brief
            has_morning_brief = scheduler.get_job("morning_brief") is not None
            for job in scheduler.get_jobs():
                if job.id != "morning_brief":
                    scheduler.remove_job(job.id)
            logger.info("Scheduler disabled at runtime (morning_brief preserved: %s)", has_morning_brief)

    elif req.automation_id == "morning_brief":
        if req.enabled:
            _add_morning_brief_job()
            logger.info("Morning brief job enabled")
        else:
            _remove_morning_brief_job()
            logger.info("Morning brief job disabled")

    return await get_automations()


def _is_morning_brief_scheduled() -> bool:
    """Check if the morning brief job exists in the scheduler."""
    from app.data_pipeline.scheduler import scheduler
    return scheduler.get_job("morning_brief") is not None


def _add_morning_brief_job():
    """Add the morning brief scheduled job."""
    from apscheduler.triggers.cron import CronTrigger
    from app.data_pipeline.scheduler import scheduler, scheduled_morning_brief

    if scheduler.get_job("morning_brief"):
        return  # Already exists
    scheduler.add_job(
        scheduled_morning_brief,
        CronTrigger(hour=7, minute=0),
        id="morning_brief",
        replace_existing=True,
    )
    if not scheduler.running:
        scheduler.start()


def _remove_morning_brief_job():
    """Remove the morning brief scheduled job."""
    from app.data_pipeline.scheduler import scheduler
    if scheduler.get_job("morning_brief"):
        scheduler.remove_job("morning_brief")
