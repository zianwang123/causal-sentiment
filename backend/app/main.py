"""FastAPI application entry point."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import networkx as nx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text

from app.api.routes_agent import router as agent_router
from app.api.routes_graph import router as graph_router, annotations_router
from app.api.routes_portfolio import router as portfolio_router
from app.api.routes_scenario import router as scenario_router
from app.api.websocket import websocket_endpoint
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.db.connection import async_session, engine
from app.graph_engine.propagation import build_networkx_graph
from app.graph_engine.topology import ALL_EDGES, ALL_NODES
from app.causal_discovery.api.routes import router as causal_router
from app.causal_discovery.models import create_hypertable_if_needed, create_node_values_index, seed_default_anchors
from app.models.graph import Base, Edge, Node
from app.models.scenarios import Scenario, ScenarioPrediction, ScenarioShock  # noqa: F401 — register with Base.metadata

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class AppState:
    graph: nx.DiGraph = field(default_factory=nx.DiGraph)
    graph_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    # Hypothetical nodes/edges added by scenario "Evolve Graph" — removed on analysis run
    hypothetical_node_ids: set = field(default_factory=set)
    hypothetical_edge_keys: set = field(default_factory=set)  # set of (source_id, target_id)


app_state = AppState()


async def seed_graph_if_empty():
    """Seed the database with nodes and edges, adding any missing ones incrementally."""
    async with async_session() as session:
        # Check what already exists
        nodes_result = await session.execute(select(Node))
        existing_nodes = {n.id: n for n in nodes_result.scalars().all()}

        edges_result = await session.execute(select(Edge))
        existing_edges = {
            (e.source_id, e.target_id) for e in edges_result.scalars().all()
        }

        # Insert missing nodes
        new_node_count = 0
        for node_data in ALL_NODES:
            if node_data["id"] not in existing_nodes:
                session.add(Node(**node_data))
                new_node_count += 1

        if new_node_count > 0:
            await session.flush()  # Ensure new nodes have PKs before edges reference them

        # Insert missing edges
        new_edge_count = 0
        for edge_data in ALL_EDGES:
            key = (edge_data["source_id"], edge_data["target_id"])
            if key not in existing_edges:
                session.add(Edge(**edge_data))
                new_edge_count += 1

        if new_node_count > 0 or new_edge_count > 0:
            await session.commit()
            logger.info("Seeded %d new nodes and %d new edges", new_node_count, new_edge_count)
        else:
            logger.info("Graph up to date (%d nodes, %d edges)", len(existing_nodes), len(existing_edges))

        # Build in-memory NetworkX graph from full DB state
        all_nodes_result = await session.execute(select(Node))
        all_edges_result = await session.execute(select(Edge))
        nodes = [
            {
                "id": n.id,
                "label": n.label,
                "node_type": n.node_type,
                "description": n.description,
                "composite_sentiment": n.composite_sentiment or 0.0,
                "confidence": n.confidence or 0.0,
            }
            for n in all_nodes_result.scalars().all()
        ]
        edges = [
            {
                "source_id": e.source_id,
                "target_id": e.target_id,
                "direction": e.direction,
                "base_weight": e.base_weight,
                "dynamic_weight": e.dynamic_weight,
                "transmission_lag_hours": e.transmission_lag_hours,
            }
            for e in all_edges_result.scalars().all()
        ]
        app_state.graph = build_networkx_graph(nodes, edges)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables + auto-fix schema drift
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Sync Postgres enum types — ALTER TYPE ADD VALUE must run outside a transaction
    # (PostgreSQL requires each ADD VALUE to auto-commit independently)
    from sqlalchemy.pool import NullPool
    autocommit_engine = create_async_engine(
        settings.database_url, isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    async with autocommit_engine.connect() as ac:
        # Existing enum values are UPPERCASE (MACRO, MONETARY_POLICY, etc.)
        # SQLAlchemy sends NodeType.name (UPPERCASE) to Postgres
        for new_val in ("HOUSING", "FINANCIAL_SYSTEM", "MONEY_MARKETS", "FISCAL_POLICY", "SUPPLY_CHAIN", "PRIVATE_CREDIT"):
            try:
                await ac.execute(text(f"ALTER TYPE nodetype ADD VALUE IF NOT EXISTS '{new_val}'"))
            except Exception:
                pass  # Value already exists or enum doesn't exist yet (first run)
    await autocommit_engine.dispose()

    async with engine.begin() as conn:
        # Detect and fix column mismatches (e.g., upstream added a column to a model
        # but create_all doesn't alter existing tables — only creates new ones)
        from app.db.schema_sync import sync_schemas
        await sync_schemas(conn)
        # Causal discovery: convert node_values to hypertable + create index
        await create_hypertable_if_needed(conn)
        await create_node_values_index(conn)
        await seed_default_anchors(conn)
    await seed_graph_if_empty()
    logger.info("Graph loaded: %d nodes, %d edges", app_state.graph.number_of_nodes(), app_state.graph.number_of_edges())

    # Clean up orphaned scenarios from crashed/restarted runs
    try:
        from app.models.scenarios import Scenario
        async with async_session() as session:
            from sqlalchemy import update
            result = await session.execute(
                update(Scenario)
                .where(Scenario.status == "running")
                .where(Scenario.created_at < datetime.utcnow() - timedelta(minutes=25))
                .values(status="error", error="Orphaned — server restarted during generation")
            )
            if result.rowcount > 0:
                logger.info("Cleaned up %d orphaned scenario(s)", result.rowcount)
            await session.commit()
    except Exception as e:
        logger.warning("Failed to clean up orphaned scenarios: %s", e)

    # Start scheduler
    from app.data_pipeline.scheduler import setup_scheduler
    sched = setup_scheduler()
    sched.start()
    logger.info("Scheduler started with %d jobs", len(sched.get_jobs()))

    yield

    # Shutdown
    sched.shutdown(wait=True)
    await engine.dispose()


app = FastAPI(
    title="Causal Sentiment Engine",
    description="Agentic sentiment analysis for quant finance — causal factor graph with Claude-powered analysis",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(graph_router)
app.include_router(agent_router)
app.include_router(portfolio_router)
app.include_router(annotations_router)
app.include_router(causal_router)
app.include_router(scenario_router)
app.add_api_websocket_route("/ws", websocket_endpoint)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "graph_nodes": app_state.graph.number_of_nodes(),
        "graph_edges": app_state.graph.number_of_edges(),
    }
