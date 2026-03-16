"""Tests for the DoWhy edge validation engine."""
import networkx as nx
import numpy as np
import pandas as pd
import pytest

dowhy = pytest.importorskip("dowhy", reason="dowhy not installed")

from app.causal_discovery.engine.validation import validate_edges


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_causal_and_spurious(n: int = 500, seed: int = 42) -> tuple[pd.DataFrame, nx.DiGraph, list[dict]]:
    """Create synthetic data where x->y is causal and z->y is spurious.

    x is an independent random walk.
    y = 0.8 * x + noise  (true causal link).
    z is an independent random walk with no real effect on y.
    The DAG and edge list include both x->y and z->y so we can verify that
    the validator distinguishes them.
    """
    rng = np.random.default_rng(seed)

    x = rng.standard_normal(n).cumsum()
    noise = rng.standard_normal(n) * 0.3
    y = 0.8 * x + noise
    z = rng.standard_normal(n).cumsum()  # independent of y

    dates = pd.date_range("2023-01-01", periods=n, freq="B")
    df = pd.DataFrame({"x": x, "y": y, "z": z}, index=dates)

    dag = nx.DiGraph()
    dag.add_edge("x", "y")
    dag.add_edge("z", "y")

    edges = [
        {"source": "x", "target": "y", "weight": 1.0, "lag": 0},
        {"source": "z", "target": "y", "weight": 1.0, "lag": 0},
    ]
    return df, dag, edges


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_validate_edges_basic():
    """x->y should pass validation; z->y should fail (spurious)."""
    df, dag, edges = _make_causal_and_spurious(n=500)

    result = validate_edges(edges, df, dag)

    assert len(result) == 2

    # Find the two edges
    xy = next(e for e in result if e["source"] == "x" and e["target"] == "y")
    zy = next(e for e in result if e["source"] == "z" and e["target"] == "y")

    # x->y should have validation populated and pass
    assert xy["validation"] is not None
    assert xy["validation"]["refutation_passed"] is True
    assert xy["validation"]["arrow_strength"] > 0.01
    assert xy["validation"]["ci_test_p_value"] < 0.05

    # z->y should have validation populated but fail refutation
    assert zy["validation"] is not None
    assert zy["validation"]["refutation_passed"] is False


def test_validate_edges_graceful_failure():
    """Too-few-rows data should return validation=None, not crash."""
    rng = np.random.default_rng(99)
    # Only 5 rows — way below _MIN_ROWS threshold
    df = pd.DataFrame({
        "a": rng.standard_normal(5),
        "b": rng.standard_normal(5),
    }, index=pd.date_range("2023-01-01", periods=5, freq="B"))

    dag = nx.DiGraph()
    dag.add_edge("a", "b")

    edges = [{"source": "a", "target": "b", "weight": 1.0, "lag": 0}]

    result = validate_edges(edges, df, dag)

    assert len(result) == 1
    assert result[0]["validation"] is None
    # Original edge data is preserved
    assert result[0]["source"] == "a"
    assert result[0]["target"] == "b"
