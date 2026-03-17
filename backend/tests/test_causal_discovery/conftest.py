"""Shared fixtures for causal_discovery tests."""
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_daily_matrix():
    """A small aligned daily matrix for testing (100 days x 5 nodes)."""
    np.random.seed(42)
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    return pd.DataFrame({
        "sp500": np.random.randn(100).cumsum() + 500,
        "vix": np.random.randn(100).cumsum() + 15,
        "gold": np.random.randn(100).cumsum() + 2000,
        "us_10y_yield": np.random.randn(100).cumsum() * 0.1 + 4.0,
        "eurusd": np.random.randn(100).cumsum() * 0.01 + 1.08,
    }, index=dates)
