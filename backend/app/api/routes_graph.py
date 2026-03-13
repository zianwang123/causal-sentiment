"""Graph CRUD and query endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
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
