from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class NodeType(str, enum.Enum):
    MACRO = "macro"
    MONETARY_POLICY = "monetary_policy"
    GEOPOLITICS = "geopolitics"
    RATES_CREDIT = "rates_credit"
    VOLATILITY = "volatility"
    COMMODITIES = "commodities"
    EQUITIES = "equities"
    EQUITY_FUNDAMENTALS = "equity_fundamentals"
    CURRENCIES = "currencies"
    FLOWS_SENTIMENT = "flows_sentiment"
    GLOBAL = "global"


class EdgeDirection(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    COMPLEX = "complex"


class Node(Base):
    __tablename__ = "nodes"

    id = Column(String(64), primary_key=True)
    label = Column(String(128), nullable=False)
    node_type = Column(Enum(NodeType), nullable=False)
    description = Column(Text, default="")
    composite_sentiment = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    evidence = Column(JSONB, default=list)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    metadata_ = Column("metadata", JSONB, default=dict)

    outgoing_edges = relationship("Edge", foreign_keys="Edge.source_id", back_populates="source")
    incoming_edges = relationship("Edge", foreign_keys="Edge.target_id", back_populates="target")


class Edge(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(64), ForeignKey("nodes.id"), nullable=False)
    target_id = Column(String(64), ForeignKey("nodes.id"), nullable=False)
    direction = Column(Enum(EdgeDirection), nullable=False, default=EdgeDirection.POSITIVE)
    base_weight = Column(Float, default=0.5)
    dynamic_weight = Column(Float, default=0.5)
    description = Column(Text, default="")
    transmission_lag_hours = Column(Float, default=0.0)
    metadata_ = Column("metadata", JSONB, default=dict)

    source = relationship("Node", foreign_keys=[source_id], back_populates="outgoing_edges")
    target = relationship("Node", foreign_keys=[target_id], back_populates="incoming_edges")

    @property
    def effective_weight(self) -> float:
        from app.config import settings
        r = settings.edge_weight_base_ratio
        return r * self.base_weight + (1 - r) * self.dynamic_weight
