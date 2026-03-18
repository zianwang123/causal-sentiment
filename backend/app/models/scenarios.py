"""Scenario extrapolation engine — DB models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
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
