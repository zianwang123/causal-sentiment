"""Tests for data source registry."""
from app.causal_discovery.pipeline.sources import (
    YFINANCE_SOURCES, FRED_SOURCES, get_all_sources, get_source_for_node,
)

def test_yfinance_sources_has_sp500():
    assert any(s["node_id"] == "sp500" for s in YFINANCE_SOURCES)

def test_fred_sources_has_fedfunds():
    assert any(s["node_id"] == "fed_funds_rate" for s in FRED_SOURCES)

def test_get_all_sources_returns_both():
    sources = get_all_sources()
    node_ids = {s["node_id"] for s in sources}
    assert "sp500" in node_ids
    assert "fed_funds_rate" in node_ids

def test_get_source_for_node():
    src = get_source_for_node("sp500")
    assert src is not None
    assert src["ticker"] == "SPY"
    assert src["source_type"] == "yfinance"

def test_get_source_for_unknown_node():
    assert get_source_for_node("nonexistent_node") is None

def test_no_duplicate_node_ids():
    sources = get_all_sources()
    node_ids = [s["node_id"] for s in sources]
    assert len(node_ids) == len(set(node_ids))
