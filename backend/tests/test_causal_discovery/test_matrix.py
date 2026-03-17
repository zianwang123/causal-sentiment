"""Tests for matrix builder — uses synthetic data, no DB."""
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from app.causal_discovery.engine.matrix import build_daily_matrix_from_rows, forward_fill_matrix


def test_build_daily_matrix_from_rows():
    rows = [
        {"node_id": "sp500", "day": datetime(2025, 1, 2, tzinfo=timezone.utc), "value": 480.0},
        {"node_id": "sp500", "day": datetime(2025, 1, 3, tzinfo=timezone.utc), "value": 482.0},
        {"node_id": "vix", "day": datetime(2025, 1, 2, tzinfo=timezone.utc), "value": 13.2},
        {"node_id": "vix", "day": datetime(2025, 1, 3, tzinfo=timezone.utc), "value": 12.8},
    ]
    df = build_daily_matrix_from_rows(rows)
    assert df.shape == (2, 2)
    assert "sp500" in df.columns
    assert "vix" in df.columns
    assert df.loc[df.index[0], "sp500"] == 480.0


def test_forward_fill_matrix():
    dates = pd.date_range("2025-01-01", periods=5, freq="B")
    df = pd.DataFrame({"sp500": [480, 482, 479, 481, 483], "cpi": [3.1, np.nan, np.nan, np.nan, np.nan]}, index=dates)
    filled = forward_fill_matrix(df)
    assert filled["cpi"].isna().sum() == 0
    assert filled.loc[dates[4], "cpi"] == 3.1
