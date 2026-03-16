"""Tests for regime-aware PCMCI+ (RPCMCI) causal discovery."""
import numpy as np
import pandas as pd
import pytest

ruptures = pytest.importorskip("ruptures", reason="ruptures not installed")
tigramite = pytest.importorskip("tigramite", reason="tigramite not installed")

from app.causal_discovery.engine.causal import discover_edges_rpcmci


def _make_regime_data(n: int = 300) -> pd.DataFrame:
    """Synthetic data with 2 variables and different correlation per half.

    First half:  B strongly follows A (coeff 0.8).
    Second half: B is nearly independent of A (coeff 0.05).
    """
    np.random.seed(99)
    mid = n // 2
    a = np.random.randn(n).cumsum()
    b = np.zeros(n)

    # Regime 0 — strong causal link A→B
    for t in range(1, mid):
        b[t] = 0.8 * a[t - 1] + 0.2 * np.random.randn()

    # Regime 1 — weak / no causal link
    for t in range(mid, n):
        b[t] = 0.05 * a[t - 1] + np.random.randn()

    dates = pd.date_range("2023-01-01", periods=n, freq="B")
    return pd.DataFrame({"A": a, "B": b}, index=dates)


class TestRPCMCIReturnsRegimes:
    """Verify the return type and structure of discover_edges_rpcmci."""

    def test_rpcmci_returns_regimes(self):
        df = _make_regime_data(300)
        result = discover_edges_rpcmci(df, max_lag=3, significance_level=0.05)

        # Must be a list
        assert isinstance(result, list)
        assert len(result) >= 1

        for item in result:
            # Each item is a 3-tuple
            assert isinstance(item, tuple)
            assert len(item) == 3

            regime_idx, edges, timerange = item

            # regime_index is an int
            assert isinstance(regime_idx, int)

            # edges is a list (possibly empty)
            assert isinstance(edges, list)

            # timerange is a (start, end) tuple of ints
            assert isinstance(timerange, tuple)
            assert len(timerange) == 2
            start, end = timerange
            assert isinstance(start, int)
            assert isinstance(end, int)
            assert start < end

    def test_rpcmci_edges_have_expected_keys(self):
        df = _make_regime_data(300)
        result = discover_edges_rpcmci(df, max_lag=3, significance_level=0.05)

        for _, edges, _ in result:
            for edge in edges:
                assert "source" in edge
                assert "target" in edge
                assert "weight" in edge
                assert "lag" in edge
                assert "direction" in edge

    def test_rpcmci_timeranges_cover_full_data(self):
        df = _make_regime_data(300)
        result = discover_edges_rpcmci(df, max_lag=3, significance_level=0.05)

        # First regime starts at 0, last regime ends at len(df)
        assert result[0][2][0] == 0
        assert result[-1][2][1] == len(df)

    def test_rpcmci_regime_indices_are_sequential(self):
        df = _make_regime_data(300)
        result = discover_edges_rpcmci(df, max_lag=3, significance_level=0.05)

        indices = [r[0] for r in result]
        # Indices should be monotonically increasing (may have gaps if segments skipped)
        assert indices == sorted(indices)
