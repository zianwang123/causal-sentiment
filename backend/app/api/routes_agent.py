"""Agent trigger and status endpoints."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.orchestrator import run_analysis
from app.db.connection import get_session
from app.models.observations import AgentRun

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
    started_at: str
    finished_at: str | None
    error: str | None

    model_config = {"from_attributes": True}


@router.post("/analyze", response_model=AgentRunOut)
async def trigger_analysis(
    request: AnalysisRequest,
    session: AsyncSession = Depends(get_session),
):
    """Trigger a Claude agent analysis run."""
    from app.main import app_state

    node_ids = request.node_ids
    if not node_ids:
        node_ids = list(app_state.graph.nodes())

    agent_run = await run_analysis(
        node_ids=node_ids,
        session=session,
        graph=app_state.graph,
        trigger=request.trigger,
    )

    # Notify WebSocket clients
    asyncio.create_task(_notify_graph_update(app_state))

    return _run_to_out(agent_run)


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
        started_at=str(r.started_at),
        finished_at=str(r.finished_at) if r.finished_at else None,
        error=r.error,
    )


async def _notify_graph_update(app_state):
    """Push graph update to all WebSocket clients."""
    from app.api.websocket import manager
    from app.db.connection import async_session
    from app.api.routes_graph import get_full_graph

    async with async_session() as session:
        graph_data = await get_full_graph(session)
        await manager.broadcast({"type": "graph_update", "data": graph_data.model_dump()})
