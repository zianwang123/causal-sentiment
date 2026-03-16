"""Tests for causal discovery engine — uses synthetic data."""
import numpy as np
import pandas as pd
import pytest

tigramite = pytest.importorskip("tigramite", reason="tigramite not installed")
from app.causal_discovery.engine.causal import discover_edges_pcmci


def _make_causal_data(n=500):
    np.random.seed(42)
    a = np.random.randn(n).cumsum()
    b = np.zeros(n)
    c = np.zeros(n)
    for t in range(1, n):
        b[t] = 0.7 * a[t - 1] + 0.3 * np.random.randn()
        c[t] = 0.5 * b[t - 1] + 0.3 * np.random.randn()
    return pd.DataFrame({"A": a, "B": b, "C": c}, index=pd.date_range("2020-01-01", periods=n, freq="B"))


def test_discover_edges_pcmci_finds_causal_link():
    df = _make_causal_data()
    edges = discover_edges_pcmci(df, max_lag=3, significance_level=0.05)
    edge_pairs = [(e["source"], e["target"]) for e in edges]
    assert ("A", "B") in edge_pairs


def test_discover_edges_returns_weights():
    df = _make_causal_data()
    edges = discover_edges_pcmci(df, max_lag=3)
    for edge in edges:
        assert "weight" in edge and "source" in edge and "target" in edge and "lag" in edge
        assert isinstance(edge["weight"], float)
