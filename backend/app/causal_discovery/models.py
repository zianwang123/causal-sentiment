"""SQLAlchemy models for causal discovery — TimescaleDB hypertable + graph snapshots."""
from __future__ import annotations
import logging
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, UniqueConstraint, text, func, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncConnection
from app.models.graph import Base

logger = logging.getLogger(__name__)


class NodeValue(Base):
    __tablename__ = "node_values"
    node_id = Column(String(64), nullable=False, primary_key=True)
    ts = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    value = Column(Float(precision=53), nullable=False)
    source = Column(String(64), nullable=False)


class DiscoveredGraph(Base):
    """A snapshot of a discovered causal graph.

    Each row is one complete graph produced by a causal discovery algorithm at a
    point in time. Stores the full node list and edge list as JSONB so the entire
    graph can be loaded in one query. Multiple snapshots with the same `run_name`
    form a time-series of evolving graphs for comparison.
    """
    __tablename__ = "discovered_graphs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_name = Column(String(128), nullable=False, index=True)  # groups snapshots into a series
    algorithm = Column(String(64), nullable=False)               # 'pcmci', 'varlingam', etc.
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    data_start = Column(DateTime(timezone=True), nullable=True)  # earliest data used
    data_end = Column(DateTime(timezone=True), nullable=True)    # latest data used
    node_count = Column(Integer, default=0)
    edge_count = Column(Integer, default=0)
    parameters = Column(JSONB, default=dict)                     # algorithm params
    nodes = Column(JSONB, nullable=False, default=list)          # [{id, zscore, polarity, display_sentiment}]
    edges = Column(JSONB, nullable=False, default=list)          # [{source, target, weight, lag, direction}]
    metadata_ = Column("metadata", JSONB, default=dict)          # run time, notes, etc.


class CausalAnchor(Base):
    """Anchor nodes for polarity propagation, configurable per scoring method."""
    __tablename__ = "causal_anchors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String(64), nullable=False)
    scoring = Column(String(32), nullable=False)
    polarity = Column(Integer, nullable=False)  # +1 or -1
    created_at = Column(DateTime(timezone=True), default=func.now())
    __table_args__ = (UniqueConstraint("node_id", "scoring", name="uq_anchor_node_scoring"),)


# Default anchors by scoring method — mirrors _ANCHORS_BY_SCORING in api/routes.py
_DEFAULT_ANCHORS_BY_SCORING: dict[str, dict[str, int]] = {
    "zscore": {
        "sp500": +1,
        "nasdaq": +1,
        "russell2000": +1,
        "us_gdp_growth": +1,
        "unemployment_rate": -1,
        "dxy_index": -1,
        "us_10y_yield": -1,
        "vix": -1,
        "wti_crude": -1,
    },
    "returns": {
        "sp500": +1,
        "nasdaq": +1,
        "russell2000": +1,
        "us_gdp_growth": +1,
        "unemployment_rate": -1,
        "dxy_index": -1,
        "us_10y_yield": -1,
        "vix": -1,
        "wti_crude": -1,
    },
    "volatility": {
        "sp500": -1,
        "nasdaq": -1,
        "russell2000": -1,
        "vix": -1,
        "us_10y_yield": -1,
        "gold": +1,
        "dxy_index": -1,
        "hy_credit_spread": -1,
        "wti_crude": -1,
    },
}


async def seed_default_anchors(conn: AsyncConnection) -> None:
    """Seed default anchors if the table is empty."""
    result = await conn.execute(
        select(func.count()).select_from(CausalAnchor.__table__)
    )
    count = result.scalar()
    if count and count > 0:
        logger.info("causal_anchors already has %d rows, skipping seed", count)
        return

    rows = []
    for scoring, anchors in _DEFAULT_ANCHORS_BY_SCORING.items():
        for node_id, polarity in anchors.items():
            rows.append({"node_id": node_id, "scoring": scoring, "polarity": polarity})

    if rows:
        await conn.execute(CausalAnchor.__table__.insert().values(rows))
        logger.info("Seeded %d default causal anchors", len(rows))


async def create_hypertable_if_needed(conn: AsyncConnection) -> None:
    try:
        await conn.execute(text("""
            SELECT create_hypertable('node_values', 'ts', if_not_exists => TRUE, migrate_data => TRUE);
        """))
        logger.info("node_values hypertable ready")
    except Exception as e:
        logger.warning("Could not create hypertable (TimescaleDB may not be installed): %s", e)


async def create_node_values_index(conn: AsyncConnection) -> None:
    try:
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_node_values_node_ts ON node_values (node_id, ts DESC);
        """))
    except Exception as e:
        logger.warning("Could not create index: %s", e)
