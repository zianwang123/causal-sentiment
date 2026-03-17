"""Tests for scoring functions (z-score, returns, volatility)."""
import pandas as pd
import numpy as np
from app.causal_discovery.engine.scoring import (
    compute_rolling_zscore,
    compute_log_returns,
    compute_rolling_volatility,
    compute_scores,
)


def test_zscore_basic():
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    df = pd.DataFrame({"A": [100.0] * 100}, index=dates)
    zscores = compute_rolling_zscore(df, window=20)
    assert zscores["A"].dropna().abs().max() < 0.01 or zscores["A"].isna().all()


def test_zscore_known_values():
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    df = pd.DataFrame({"A": list(range(100))}, index=dates)
    zscores = compute_rolling_zscore(df, window=20)
    assert zscores["A"].iloc[-1] > 0


def test_zscore_multiple_columns():
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    df = pd.DataFrame({"A": np.random.randn(100).cumsum(), "B": np.random.randn(100).cumsum()}, index=dates)
    zscores = compute_rolling_zscore(df, window=20)
    assert "A" in zscores.columns and "B" in zscores.columns


def test_zscore_clamped():
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    df = pd.DataFrame({"A": [100.0] * 99 + [10000.0]}, index=dates)
    zscores = compute_rolling_zscore(df, window=20, clamp=3.0)
    assert zscores["A"].iloc[-1] <= 3.0


def test_log_returns():
    dates = pd.date_range("2025-01-01", periods=5, freq="B")
    df = pd.DataFrame({"A": [100, 101, 99, 102, 100]}, index=dates)
    ret = compute_log_returns(df)
    assert len(ret) == 5
    assert ret["A"].iloc[0] == 0.0  # first row is NaN → filled with 0
    assert ret["A"].iloc[1] > 0  # 100 → 101 is positive return


def test_log_returns_no_inf():
    dates = pd.date_range("2025-01-01", periods=3, freq="B")
    df = pd.DataFrame({"A": [0, 100, 200]}, index=dates)  # 0 → 100 would be inf
    ret = compute_log_returns(df)
    assert not np.isinf(ret.values).any()


def test_rolling_volatility():
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    # Constant prices → zero volatility
    df = pd.DataFrame({"A": [100.0] * 100}, index=dates)
    vol = compute_rolling_volatility(df, window=20)
    assert vol["A"].iloc[-1] == 0.0


def test_rolling_volatility_increases():
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    np.random.seed(42)
    # Calm then volatile
    calm = np.cumsum(np.random.randn(50) * 0.01) + 100
    wild = np.cumsum(np.random.randn(50) * 0.10) + calm[-1]
    df = pd.DataFrame({"A": np.concatenate([calm, wild])}, index=dates)
    vol = compute_rolling_volatility(df, window=20)
    assert vol["A"].iloc[-1] > vol["A"].iloc[50]  # vol higher in wild period


def test_compute_scores_dispatcher():
    dates = pd.date_range("2025-01-01", periods=50, freq="B")
    df = pd.DataFrame({"A": np.random.randn(50).cumsum() + 100}, index=dates)
    for method in ["zscore", "returns", "volatility"]:
        result = compute_scores(df, method=method)
        assert isinstance(result, pd.DataFrame)
        assert "A" in result.columns


def test_compute_scores_unknown_method():
    df = pd.DataFrame({"A": [1, 2, 3]})
    try:
        compute_scores(df, method="nonexistent")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
