"""Scenario extrapolation engine — DB models."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from .graph import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trigger = Column(Text, nullable=False)
    trigger_type = Column(String(32), default="user_prompt")  # news_event | user_prompt
    status = Column(String(32), default="running")  # running | completed | error
    scenarios_json = Column(JSONB, default=dict)  # Full branching result
    research_summary = Column(Text, default="")
    historical_parallels = Column(Text, default="")
    selected_branch_idx = Column(Integer, nullable=True)
    simulation_result = Column(JSONB, nullable=True)
    error = Column(Text, nullable=True)
    parent_scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=True)
    parent_branch_idx = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    finished_at = Column(DateTime, nullable=True)


class ScenarioShock(Base):
    __tablename__ = "scenario_shocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    branch_idx = Column(Integer, nullable=False)
    node_id = Column(String(64), nullable=False)  # mapped graph node
    shock_value = Column(Float, nullable=False)  # [-1, 1]
    reasoning = Column(Text, default="")
    original_impact = Column(Text, default="")  # free-form impact before mapping
    created_at = Column(DateTime, default=func.now())


class ScenarioPrediction(Base):
    """Individual predictions extracted from scenario branches for resolution tracking."""
    __tablename__ = "scenario_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    branch_idx = Column(Integer, nullable=False)
    branch_title = Column(String(256), default="")
    prediction_text = Column(Text, nullable=False)  # raw event description
    confidence = Column(Float, nullable=False)  # 0-1
    time_window = Column(String(64), default="")  # raw string e.g. "1-2 weeks"
    expires_at = Column(DateTime, nullable=True)  # parsed expiry (None if unparseable)
    ticker = Column(String(32), nullable=True)  # extracted ticker if market-related
    threshold_value = Column(Float, nullable=True)  # e.g. 120.0
    threshold_direction = Column(String(8), nullable=True)  # "above" or "below"
    resolution_type = Column(String(16), default="pending")  # pending|market_resolved|unresolvable
    resolved_at = Column(DateTime, nullable=True)
    actual_value = Column(Float, nullable=True)  # market price at resolution
    hit = Column(Boolean, nullable=True)  # True=correct, False=wrong, None=unresolved
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("ix_scenario_predictions_scenario_id", "scenario_id"),
        Index("ix_scenario_predictions_pending", "resolved_at", "expires_at",
              postgresql_where=Column("resolved_at").is_(None)),
    )


class NodeSuggestion(Base):
    __tablename__ = "node_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    branch_idx = Column(Integer, default=0)
    suggested_id = Column(String(64), nullable=False)
    suggested_label = Column(String(128), nullable=False)
    suggested_type = Column(String(32), default="macro")
    description = Column(Text, default="")
    reasoning = Column(Text, default="")
    status = Column(String(16), default="pending")  # pending | accepted | rejected
    created_at = Column(DateTime, default=func.now())
