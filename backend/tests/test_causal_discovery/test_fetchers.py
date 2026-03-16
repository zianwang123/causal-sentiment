"""Tests for data fetchers."""
import pandas as pd
import pytest
from app.causal_discovery.pipeline.fetchers import (
    fetch_yfinance_history, parse_fred_observations,
)

@pytest.mark.network
async def test_fetch_yfinance_history_returns_dataframe():
    df = await fetch_yfinance_history(["SPY"], period="1mo")
    assert isinstance(df, pd.DataFrame)
    assert "SPY" in df.columns
    assert len(df) > 15
    assert df.index.dtype.kind == "M"

@pytest.mark.network
async def test_fetch_yfinance_history_multiple_tickers():
    df = await fetch_yfinance_history(["SPY", "QQQ", "GLD"], period="5d")
    assert "SPY" in df.columns
    assert "QQQ" in df.columns
    assert "GLD" in df.columns

def test_parse_fred_observations():
    raw = [
        {"date": "2025-01-02", "value": "4.33"},
        {"date": "2025-01-03", "value": "4.35"},
        {"date": "2025-01-04", "value": "."},
    ]
    result = parse_fred_observations(raw)
    assert len(result) == 2
    assert result[0] == ("2025-01-02", 4.33)
    assert result[1] == ("2025-01-03", 4.35)

def test_parse_fred_observations_empty():
    result = parse_fred_observations([])
    assert result == []
