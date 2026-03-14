"""Agent trigger and status endpoints."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

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

    model_config = {"from_attributes": True}


class PredictionSummary(BaseModel):
    total: int
    resolved: int
    pending: int
    hit_rate: float | None
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

    return PredictionSummary(
        total=len(all_preds),
        resolved=len(resolved),
        pending=len(pending),
        hit_rate=round(hits / total_decided, 4) if total_decided > 0 else None,
        by_direction=by_direction,
    )
