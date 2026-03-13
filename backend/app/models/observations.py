from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from .graph import Base


class SentimentObservation(Base):
    __tablename__ = "sentiment_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String(64), ForeignKey("nodes.id"), nullable=False, index=True)
    sentiment = Column(Float, nullable=False)
    confidence = Column(Float, default=0.5)
    source = Column(String(64), nullable=False)
    evidence = Column(Text, default="")
    raw_data = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=func.now(), index=True)


class RegimeSnapshot(Base):
    __tablename__ = "regime_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(32), nullable=False)  # risk_on, risk_off, transitioning
    confidence = Column(Float, default=0.5)
    composite_score = Column(Float, default=0.0)
    contributing_signals = Column(JSONB, default=dict)
    detected_at = Column(DateTime, default=func.now(), index=True)


class PortfolioPosition(Base):
    __tablename__ = "portfolio_positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(16), nullable=False)
    node_id = Column(String(64), ForeignKey("nodes.id"), nullable=True)
    shares = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    entry_date = Column(DateTime, nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class EdgeSuggestion(Base):
    __tablename__ = "edge_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(64), ForeignKey("nodes.id"), nullable=False)
    target_id = Column(String(64), ForeignKey("nodes.id"), nullable=False)
    suggested_direction = Column(String(16), default="positive")  # positive/negative/complex
    suggested_weight = Column(Float, default=0.3)
    correlation = Column(Float, nullable=True)
    llm_reasoning = Column(Text, default="")
    status = Column(String(16), default="pending")  # pending/accepted/rejected
    created_at = Column(DateTime, default=func.now())
    reviewed_at = Column(DateTime, nullable=True)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String(64), ForeignKey("nodes.id"), nullable=False, index=True)
    predicted_direction = Column(String(16), nullable=False)  # bullish, bearish, neutral
    predicted_sentiment = Column(Float, nullable=False)
    horizon_hours = Column(Integer, default=168)  # default 7 days
    reasoning = Column(Text, default="")
    agent_run_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now(), index=True)
    resolved_at = Column(DateTime, nullable=True)
    actual_sentiment = Column(Float, nullable=True)
    hit = Column(Integer, nullable=True)  # 1 = correct direction, 0 = wrong, NULL = unresolved


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trigger = Column(String(32), nullable=False)
    status = Column(String(16), default="running")
    nodes_analyzed = Column(JSONB, default=list)
    tool_calls = Column(JSONB, default=list)
    summary = Column(Text, default="")
    started_at = Column(DateTime, default=func.now())
    finished_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
