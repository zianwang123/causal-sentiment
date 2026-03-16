"""Tests for backfill logic — uses mock data, no DB or network calls."""
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from app.causal_discovery.pipeline.backfill import (
    yfinance_df_to_node_value_rows,
    fred_series_to_node_value_rows,
)

def test_yfinance_df_to_node_value_rows():
    dates = pd.date_range("2025-01-02", periods=3, freq="B")
    df = pd.DataFrame({"SPY": [480.0, 482.0, 479.0]}, index=dates)
    ticker_to_node = {"SPY": "sp500"}
    rows = yfinance_df_to_node_value_rows(df, ticker_to_node)
    assert len(rows) == 3
    assert rows[0]["node_id"] == "sp500"
    assert rows[0]["value"] == 480.0
    assert rows[0]["source"] == "yfinance"
    assert isinstance(rows[0]["ts"], datetime)

def test_yfinance_df_skips_nan():
    dates = pd.date_range("2025-01-02", periods=3, freq="B")
    df = pd.DataFrame({"SPY": [480.0, np.nan, 479.0]}, index=dates)
    rows = yfinance_df_to_node_value_rows(df, {"SPY": "sp500"})
    assert len(rows) == 2

def test_fred_series_to_node_value_rows():
    observations = [("2025-01-02", 4.33), ("2025-01-03", 4.35)]
    rows = fred_series_to_node_value_rows("fed_funds_rate", observations)
    assert len(rows) == 2
    assert rows[0]["node_id"] == "fed_funds_rate"
    assert rows[0]["value"] == 4.33
    assert rows[0]["source"] == "fred"
