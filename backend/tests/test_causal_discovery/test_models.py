"""Tests for causal_discovery models."""
from datetime import datetime, timezone
from app.causal_discovery.models import NodeValue


def test_node_value_creation():
    nv = NodeValue(
        node_id="sp500",
        ts=datetime(2025, 1, 2, tzinfo=timezone.utc),
        value=480.12,
        source="yfinance",
    )
    assert nv.node_id == "sp500"
    assert nv.value == 480.12
    assert nv.source == "yfinance"
    assert nv.ts.year == 2025


def test_node_value_table_name():
    assert NodeValue.__tablename__ == "node_values"


def test_node_value_inherits_base():
    from app.models.graph import Base
    assert issubclass(NodeValue, Base)
