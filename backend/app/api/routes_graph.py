"""Graph CRUD and query endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator as pydantic_field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_session
from app.graph_engine.weights import compute_centralities
from app.models.graph import Edge, Node
from app.models.observations import SentimentObservation

router = APIRouter(prefix="/api/graph", tags=["graph"])


class NodeOut(BaseModel):
    id: str
    label: str
    node_type: str
    description: str
    composite_sentiment: float
    confidence: float
    evidence: list
    centrality: float = 0.0

    model_config = {"from_attributes": True}


class EdgeOut(BaseModel):
    id: int
    source_id: str
    target_id: str
    direction: str
    base_weight: float
    dynamic_weight: float
    description: str

    model_config = {"from_attributes": True}


class GraphOut(BaseModel):
    nodes: list[NodeOut]
    edges: list[EdgeOut]


@router.get("/full", response_model=GraphOut)
async def get_full_graph(session: AsyncSession = Depends(get_session)):
    """Return the complete graph for 3D visualization."""
    from app.main import app_state

    nodes_result = await session.execute(select(Node))
    nodes = nodes_result.scalars().all()

    edges_result = await session.execute(select(Edge))
    edges = edges_result.scalars().all()

    centralities = compute_centralities(app_state.graph)

    node_list = []
    for n in nodes:
        node_out = NodeOut(
            id=n.id,
            label=n.label,
            node_type=n.node_type.value,
            description=n.description or "",
            composite_sentiment=n.composite_sentiment or 0.0,
            confidence=n.confidence or 0.0,
            evidence=n.evidence or [],
            centrality=centralities.get(n.id, 0.0),
        )
        node_list.append(node_out)

    edge_list = [
        EdgeOut(
            id=e.id,
            source_id=e.source_id,
            target_id=e.target_id,
            direction=e.direction.value,
            base_weight=e.base_weight,
            dynamic_weight=e.dynamic_weight,
            description=e.description or "",
        )
        for e in edges
    ]

    return GraphOut(nodes=node_list, edges=edge_list)


@router.get("/node/{node_id}", response_model=NodeOut)
async def get_node(node_id: str, session: AsyncSession = Depends(get_session)):
    """Get a single node's details."""
    from app.main import app_state

    result = await session.execute(select(Node).where(Node.id == node_id))
    node = result.scalar_one()
    centralities = compute_centralities(app_state.graph)

    return NodeOut(
        id=node.id,
        label=node.label,
        node_type=node.node_type.value,
        description=node.description or "",
        composite_sentiment=node.composite_sentiment or 0.0,
        confidence=node.confidence or 0.0,
        evidence=node.evidence or [],
        centrality=centralities.get(node.id, 0.0),
    )


class SentimentHistoryPoint(BaseModel):
    timestamp: datetime
    sentiment: float
    confidence: float
    source: str


@router.get("/snapshot", response_model=GraphOut)
async def get_graph_snapshot(
    timestamp: datetime,
    session: AsyncSession = Depends(get_session),
):
    """Return graph state at a specific point in time.

    For each node, uses the most recent SentimentObservation before the timestamp
    (from agent source) as the composite_sentiment.
    """
    from app.main import app_state

    nodes_result = await session.execute(select(Node))
    nodes = nodes_result.scalars().all()

    edges_result = await session.execute(select(Edge))
    edges = edges_result.scalars().all()

    centralities = compute_centralities(app_state.graph)

    # For each node, find the most recent agent-sourced observation before timestamp
    # DB uses TIMESTAMP WITHOUT TIME ZONE — strip tzinfo for comparison
    ts_naive = timestamp.replace(tzinfo=None) if timestamp.tzinfo else timestamp
    node_list = []
    for n in nodes:
        # Get most recent sentiment observation at or before timestamp
        obs_result = await session.execute(
            select(SentimentObservation)
            .where(SentimentObservation.node_id == n.id)
            .where(SentimentObservation.created_at <= ts_naive)
            .where(SentimentObservation.source.in_(["agent", "deep_dive"]))
            .order_by(SentimentObservation.created_at.desc())
            .limit(1)
        )
        obs = obs_result.scalar_one_or_none()

        node_list.append(NodeOut(
            id=n.id,
            label=n.label,
            node_type=n.node_type.value,
            description=n.description or "",
            composite_sentiment=obs.sentiment if obs else 0.0,
            confidence=obs.confidence if obs else 0.0,
            evidence=n.evidence or [],
            centrality=centralities.get(n.id, 0.0),
        ))

    edge_list = [
        EdgeOut(
            id=e.id,
            source_id=e.source_id,
            target_id=e.target_id,
            direction=e.direction.value,
            base_weight=e.base_weight,
            dynamic_weight=e.dynamic_weight,
            description=e.description or "",
        )
        for e in edges
    ]

    return GraphOut(nodes=node_list, edges=edge_list)


class AnomalyOut(BaseModel):
    node_id: str
    z_score: float
    latest_value: float
    mean: float
    std: float
    direction: str
    detected_at: datetime


@router.get("/anomalies", response_model=list[AnomalyOut])
async def get_anomalies(
    lookback_days: int = 30,
    z_threshold: float = 2.0,
    session: AsyncSession = Depends(get_session),
):
    """Detect nodes with anomalous recent data (>z_threshold sigma move)."""
    from app.graph_engine.anomalies import detect_anomalies

    anomalies = await detect_anomalies(session, lookback_days, z_threshold)
    return [
        AnomalyOut(
            node_id=a.node_id,
            z_score=a.z_score,
            latest_value=a.latest_value,
            mean=a.mean,
            std=a.std,
            direction=a.direction,
            detected_at=a.detected_at,
        )
        for a in anomalies
    ]


class RegimeOut(BaseModel):
    state: str
    confidence: float
    composite_score: float
    contributing_signals: dict[str, float]


class RegimeHistoryPoint(BaseModel):
    state: str
    confidence: float
    composite_score: float
    contributing_signals: dict[str, float]
    detected_at: str | None


@router.get("/regime", response_model=RegimeOut)
async def get_current_regime():
    """Get the current market regime classification."""
    from app.graph_engine.regimes import detect_regime
    from app.main import app_state

    result = detect_regime(app_state.graph)
    return RegimeOut(
        state=result.state.value,
        confidence=result.confidence,
        composite_score=result.composite_score,
        contributing_signals=result.contributing_signals,
    )


@router.get("/regime/history", response_model=list[RegimeHistoryPoint])
async def get_regime_history_endpoint(
    days: int = 30,
    session: AsyncSession = Depends(get_session),
):
    """Get regime history over time."""
    from app.graph_engine.regimes import get_regime_history

    history = await get_regime_history(session, days)
    return [RegimeHistoryPoint(**h) for h in history]


class ClusterOut(BaseModel):
    clusters: dict[str, list[str]]  # cluster_name -> [node_ids]


@router.get("/clusters", response_model=ClusterOut)
async def get_clusters(session: AsyncSession = Depends(get_session)):
    """Return node cluster assignments based on node types."""
    nodes_result = await session.execute(select(Node))
    nodes = nodes_result.scalars().all()

    clusters: dict[str, list[str]] = {}
    for n in nodes:
        cluster_name = n.node_type.value
        clusters.setdefault(cluster_name, []).append(n.id)

    return ClusterOut(clusters=clusters)


class BacktestResultOut(BaseModel):
    node_id: str
    correlation: float | None = None
    hit_rate: float | None = None
    ic: float | None = None
    n_observations: int = 0
    avg_return_bullish: float | None = None
    avg_return_bearish: float | None = None
    scatter_points: list[list[float]] = []


@router.get("/backtest/summary", response_model=list[BacktestResultOut])
async def get_backtest_summary(
    lookback_days: int = 90,
    forward_days: int = 5,
    session: AsyncSession = Depends(get_session),
):
    """Run backtest for all nodes with market data, sorted by hit rate."""
    from app.graph_engine.backtest import backtest_all_nodes

    results = await backtest_all_nodes(session, lookback_days, forward_days)
    return [
        BacktestResultOut(
            node_id=r.node_id,
            correlation=r.correlation,
            hit_rate=r.hit_rate,
            ic=r.ic,
            n_observations=r.n_observations,
            avg_return_bullish=r.avg_return_bullish,
            avg_return_bearish=r.avg_return_bearish,
            scatter_points=r.scatter_points,
        )
        for r in results
    ]


@router.get("/backtest/{node_id}", response_model=BacktestResultOut)
async def get_backtest(
    node_id: str,
    lookback_days: int = 90,
    forward_days: int = 5,
    session: AsyncSession = Depends(get_session),
):
    """Backtest sentiment predictions for a single node."""
    from app.graph_engine.backtest import backtest_node

    result = await backtest_node(session, node_id, lookback_days, forward_days)
    return BacktestResultOut(
        node_id=result.node_id,
        correlation=result.correlation,
        hit_rate=result.hit_rate,
        ic=result.ic,
        n_observations=result.n_observations,
        avg_return_bullish=result.avg_return_bullish,
        avg_return_bearish=result.avg_return_bearish,
        scatter_points=result.scatter_points,
    )


@router.get("/sentiment/history/{node_id}", response_model=list[SentimentHistoryPoint])
async def get_sentiment_history(
    node_id: str,
    days: int = 30,
    session: AsyncSession = Depends(get_session),
):
    """Return sentiment observation history for a node."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await session.execute(
        select(SentimentObservation)
        .where(SentimentObservation.node_id == node_id)
        .where(SentimentObservation.created_at >= cutoff)
        .order_by(SentimentObservation.created_at.asc())
    )
    observations = result.scalars().all()

    # Deduplicate by second-level timestamp (lightweight-charts requires strictly increasing times)
    seen_seconds: dict[int, SentimentObservation] = {}
    for o in observations:
        ts_key = int(o.created_at.timestamp()) if o.created_at else 0
        seen_seconds[ts_key] = o  # last one wins (data is asc-ordered)

    deduped = sorted(seen_seconds.values(), key=lambda o: o.created_at)
    return [
        SentimentHistoryPoint(
            timestamp=o.created_at,
            sentiment=o.sentiment,
            confidence=o.confidence,
            source=o.source or "",
        )
        for o in deduped
    ]


class RawDataPoint(BaseModel):
    source: str
    timestamp: datetime
    data: dict


@router.get("/raw-data/{node_id}", response_model=list[RawDataPoint])
async def get_raw_data(
    node_id: str,
    limit: int = 5,
    session: AsyncSession = Depends(get_session),
):
    """Return recent raw observation data (FRED values, market prices, etc.) for a node."""
    result = await session.execute(
        select(SentimentObservation)
        .where(SentimentObservation.node_id == node_id)
        .where(
            SentimentObservation.source.in_(
                ["fred_scheduled", "market_scheduled", "edgar_scheduled"]
            )
        )
        .where(SentimentObservation.raw_data.isnot(None))
        .order_by(SentimentObservation.created_at.desc())
        .limit(limit)
    )
    obs = result.scalars().all()
    return [
        RawDataPoint(source=o.source, timestamp=o.created_at, data=o.raw_data or {})
        for o in obs
    ]


class EdgeSuggestionOut(BaseModel):
    id: int
    source_id: str
    target_id: str
    suggested_direction: str
    suggested_weight: float
    correlation: float | None = None
    llm_reasoning: str
    status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TopologySuggestResponse(BaseModel):
    suggestions: list[EdgeSuggestionOut]
    message: str | None = None


@router.post("/topology/suggest", response_model=TopologySuggestResponse)
async def suggest_topology(session: AsyncSession = Depends(get_session)):
    """Trigger LLM-assisted topology learning to suggest new edges."""
    from app.graph_engine.topology_learning import find_correlated_unconnected_pairs, suggest_edges_with_llm
    from app.main import app_state

    # Pre-check: are there enough candidates?
    # Count how many nodes have sufficient observation data
    from app.graph_engine.correlations import _get_node_timeseries
    all_node_ids = list(app_state.graph.nodes())
    nodes_with_data = 0
    for nid in all_node_ids:
        ts = await _get_node_timeseries(session, nid, 90)
        if len(ts) >= 3:
            nodes_with_data += 1

    candidates = await find_correlated_unconnected_pairs(session, app_state.graph)
    if not candidates:
        return TopologySuggestResponse(
            suggestions=[],
            message=f"Not enough correlated pairs found. {nodes_with_data}/{len(all_node_ids)} nodes have 3+ observations. Run more analyses across different time windows to build history.",
        )

    suggestions = await suggest_edges_with_llm(session, app_state.graph)
    return TopologySuggestResponse(
        suggestions=[EdgeSuggestionOut.model_validate(s) for s in suggestions],
        message=f"Generated {len(suggestions)} suggestion(s)." if suggestions else "LLM found no plausible causal links among the correlated pairs.",
    )


@router.get("/topology/suggestions", response_model=list[EdgeSuggestionOut])
async def list_suggestions(
    status: str = "pending",
    session: AsyncSession = Depends(get_session),
):
    """List edge suggestions filtered by status."""
    from app.models.observations import EdgeSuggestion

    result = await session.execute(
        select(EdgeSuggestion)
        .where(EdgeSuggestion.status == status)
        .order_by(EdgeSuggestion.created_at.desc())
    )
    return [EdgeSuggestionOut.model_validate(s) for s in result.scalars().all()]


@router.post("/topology/suggestions/{suggestion_id}/accept")
async def accept_suggestion(
    suggestion_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Accept a suggested edge — creates it in the DB and in-memory graph."""
    from app.main import app_state
    from app.models.graph import Edge, EdgeDirection
    from app.models.observations import EdgeSuggestion

    result = await session.execute(
        select(EdgeSuggestion).where(EdgeSuggestion.id == suggestion_id)
    )
    suggestion = result.scalar_one_or_none()
    if not suggestion:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Suggestion not found")

    if suggestion.status != "pending":
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Suggestion already {suggestion.status}")

    # Create the edge
    direction_map = {
        "positive": EdgeDirection.POSITIVE,
        "negative": EdgeDirection.NEGATIVE,
        "complex": EdgeDirection.COMPLEX,
    }
    new_edge = Edge(
        source_id=suggestion.source_id,
        target_id=suggestion.target_id,
        direction=direction_map.get(suggestion.suggested_direction, EdgeDirection.POSITIVE),
        base_weight=suggestion.suggested_weight,
        dynamic_weight=suggestion.suggested_weight,
        description=f"LLM-suggested: {suggestion.llm_reasoning[:200]}",
    )
    session.add(new_edge)

    suggestion.status = "accepted"
    suggestion.reviewed_at = datetime.utcnow()

    await session.commit()

    # Add to in-memory graph
    app_state.graph.add_edge(
        suggestion.source_id,
        suggestion.target_id,
        direction=suggestion.suggested_direction,
        base_weight=suggestion.suggested_weight,
        dynamic_weight=suggestion.suggested_weight,
        effective_weight=suggestion.suggested_weight,
    )

    # Invalidate centrality cache since topology changed
    from app.graph_engine.weights import invalidate_centrality_cache
    invalidate_centrality_cache()

    return {"status": "accepted", "edge_id": new_edge.id}


@router.post("/topology/suggestions/{suggestion_id}/reject")
async def reject_suggestion(
    suggestion_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Reject a suggested edge."""
    from app.models.observations import EdgeSuggestion

    result = await session.execute(
        select(EdgeSuggestion).where(EdgeSuggestion.id == suggestion_id)
    )
    suggestion = result.scalar_one_or_none()
    if not suggestion:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Suggestion not found")

    suggestion.status = "rejected"
    suggestion.reviewed_at = datetime.utcnow()
    await session.commit()

    return {"status": "rejected"}


# ── REGIME NARRATOR ──────────────────────────────────────────────────

class RegimeNarrativeOut(BaseModel):
    narrative: str
    regime: str
    confidence: float
    composite_score: float
    top_drivers: list[str]


@router.post("/regime/narrative", response_model=RegimeNarrativeOut)
async def generate_regime_narrative(
    session: AsyncSession = Depends(get_session),
):
    """Generate an LLM narrative explaining the current market regime."""
    from app.main import app_state
    from app.graph_engine.regimes import detect_regime, get_regime_history
    from app.config import settings

    graph = app_state.graph
    regime = detect_regime(graph)

    # Get recent regime history for transition detection
    history = await get_regime_history(session, days=7)

    # Find top drivers (highest absolute contributing signals)
    sorted_signals = sorted(
        regime.contributing_signals.items(),
        key=lambda x: abs(x[1]),
        reverse=True,
    )
    top_drivers = [s[0] for s in sorted_signals[:3]]

    # Detect regime transition
    transition_info = ""
    if len(history) >= 2:
        prev_state = history[-2]["state"] if len(history) >= 2 else None
        if prev_state and prev_state != regime.state.value:
            transition_info = f"The regime recently shifted from {prev_state} to {regime.state.value}."

    # Build prompt for Claude
    signal_desc = ", ".join(
        f"{node_id} ({sentiment:+.2f})"
        for node_id, sentiment in sorted_signals
    )
    prompt = (
        f"You are a macro strategist. Write a concise 2-3 sentence narrative about the current market regime.\n\n"
        f"Regime: {regime.state.value.replace('_', ' ').upper()} (confidence: {regime.confidence:.0%}, composite: {regime.composite_score:+.3f})\n"
        f"Contributing signals: {signal_desc}\n"
        f"{transition_info}\n\n"
        f"Be specific about which indicators are driving the regime. Mention what to watch for next. "
        f"No bullet points, just flowing prose. Maximum 3 sentences."
    )

    # Call LLM
    try:
        if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            response = client.messages.create(
                model=settings.anthropic_model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            narrative = response.content[0].text
        elif settings.openai_api_key:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model=settings.openai_model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            narrative = response.choices[0].message.content or ""
        else:
            # Fallback: generate a simple narrative without LLM
            drivers_str = ", ".join(top_drivers)
            narrative = (
                f"Market is in {regime.state.value.replace('_', ' ')} mode "
                f"(confidence {regime.confidence:.0%}, composite {regime.composite_score:+.3f}). "
                f"Key drivers: {drivers_str}. {transition_info}"
            )
    except Exception as e:
        # Fallback on LLM error
        drivers_str = ", ".join(top_drivers)
        narrative = (
            f"Market is in {regime.state.value.replace('_', ' ')} mode "
            f"(confidence {regime.confidence:.0%}). "
            f"Key drivers: {drivers_str}."
        )

    return RegimeNarrativeOut(
        narrative=narrative,
        regime=regime.state.value,
        confidence=regime.confidence,
        composite_score=regime.composite_score,
        top_drivers=top_drivers,
    )


# ── WHAT-IF SHOCK SIMULATOR ──────────────────────────────────────────

class SimulateRequest(BaseModel):
    node_id: str
    hypothetical_sentiment: float


class SimulationImpact(BaseModel):
    node_id: str
    label: str
    impact: float
    path: list[str]
    hops: int


class SimulateResponse(BaseModel):
    source_node: str
    source_label: str
    initial_signal: float
    current_sentiment: float
    shock_delta: float
    regime: str
    impacts: list[SimulationImpact]
    total_nodes_affected: int


@router.post("/simulate", response_model=SimulateResponse)
async def simulate_shock(req: SimulateRequest):
    """Run a read-only what-if shock propagation. No DB writes."""
    from fastapi import HTTPException
    from app.main import app_state
    from app.graph_engine.propagation import propagate_signal
    from app.graph_engine.regimes import detect_regime

    graph = app_state.graph
    if req.node_id not in graph:
        raise HTTPException(status_code=404, detail=f"Node '{req.node_id}' not found")

    sentiment = max(-1.0, min(1.0, req.hypothetical_sentiment))
    current = graph.nodes[req.node_id].get("composite_sentiment", 0.0) or 0.0
    shock_delta = sentiment - current

    regime = detect_regime(graph)
    result = propagate_signal(
        graph,
        req.node_id,
        shock_delta,
        regime=regime.state.value,
    )

    impacts = []
    for node_id, impact in sorted(result.impacts.items(), key=lambda x: abs(x[1]), reverse=True):
        if node_id == req.node_id:
            continue
        label = graph.nodes[node_id].get("label", node_id) if node_id in graph else node_id
        path = result.paths.get(node_id, [req.node_id, node_id])
        impacts.append(SimulationImpact(
            node_id=node_id,
            label=label,
            impact=round(impact, 4),
            path=path,
            hops=len(path) - 1,
        ))

    source_label = graph.nodes[req.node_id].get("label", req.node_id)
    return SimulateResponse(
        source_node=req.node_id,
        source_label=source_label,
        initial_signal=round(sentiment, 4),
        current_sentiment=round(current, 4),
        shock_delta=round(shock_delta, 4),
        regime=regime.state.value,
        impacts=impacts,
        total_nodes_affected=len(impacts),
    )


# ── ANALYST ANNOTATIONS ──────────────────────────────────────────────

annotations_router = APIRouter(prefix="/api/annotations", tags=["annotations"])


class AnnotationCreate(BaseModel):
    node_id: str
    text: str
    pinned: bool = False

    @pydantic_field_validator("text")
    @classmethod
    def text_not_too_long(cls, v: str) -> str:
        if len(v) > 10000:
            raise ValueError("Annotation text must be 10,000 characters or fewer")
        return v


class AnnotationUpdate(BaseModel):
    text: str | None = None
    pinned: bool | None = None


class AnnotationOut(BaseModel):
    id: int
    node_id: str
    text: str
    pinned: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@annotations_router.get("", response_model=list[AnnotationOut])
async def list_annotations(
    node_id: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """List annotations, optionally filtered by node_id."""
    from app.models.observations import Annotation

    query = select(Annotation).order_by(Annotation.pinned.desc(), Annotation.created_at.desc())
    if node_id:
        query = query.where(Annotation.node_id == node_id)
    result = await session.execute(query)
    return [AnnotationOut.model_validate(a) for a in result.scalars().all()]


@annotations_router.post("", response_model=AnnotationOut)
async def create_annotation(
    body: AnnotationCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new annotation on a node."""
    from app.models.observations import Annotation

    annotation = Annotation(
        node_id=body.node_id,
        text=body.text,
        pinned=body.pinned,
    )
    session.add(annotation)
    await session.commit()
    await session.refresh(annotation)
    return AnnotationOut.model_validate(annotation)


@annotations_router.put("/{annotation_id}", response_model=AnnotationOut)
async def update_annotation(
    annotation_id: int,
    body: AnnotationUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update an annotation's text or pin status."""
    from fastapi import HTTPException
    from app.models.observations import Annotation

    result = await session.execute(select(Annotation).where(Annotation.id == annotation_id))
    annotation = result.scalar_one_or_none()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    if body.text is not None:
        annotation.text = body.text
    if body.pinned is not None:
        annotation.pinned = body.pinned
    annotation.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(annotation)
    return AnnotationOut.model_validate(annotation)


@annotations_router.delete("/{annotation_id}")
async def delete_annotation(
    annotation_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete an annotation."""
    from fastapi import HTTPException
    from app.models.observations import Annotation

    result = await session.execute(select(Annotation).where(Annotation.id == annotation_id))
    annotation = result.scalar_one_or_none()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    await session.delete(annotation)
    await session.commit()
    return {"status": "deleted"}
