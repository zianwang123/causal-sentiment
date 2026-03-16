"""Tests for anchor polarity propagation (bidirectional)."""
import networkx as nx
from app.causal_discovery.engine.anchors import propagate_polarity


def test_positive_edge_preserves_polarity():
    g = nx.DiGraph()
    g.add_edge("sp500", "tech", direction="positive", weight=0.8)
    assert propagate_polarity(g, {"sp500": 1})["tech"] == 1


def test_negative_edge_flips_polarity():
    g = nx.DiGraph()
    g.add_edge("sp500", "vix", direction="negative", weight=0.8)
    assert propagate_polarity(g, {"sp500": 1})["vix"] == -1


def test_transitivity():
    g = nx.DiGraph()
    g.add_edge("sp500", "vix", direction="negative", weight=0.8)
    g.add_edge("vix", "put_call", direction="positive", weight=0.6)
    polarity = propagate_polarity(g, {"sp500": 1})
    assert polarity["vix"] == -1
    assert polarity["put_call"] == -1


def test_unconnected_node_gets_zero():
    g = nx.DiGraph()
    g.add_node("sp500")
    g.add_node("isolated")
    assert propagate_polarity(g, {"sp500": 1}).get("isolated", 0) == 0


def test_backward_propagation():
    """Node pointing TO anchor should get polarity via backward traversal."""
    g = nx.DiGraph()
    # copper → sp500 (negative): copper up → sp500 down
    # From equity perspective: copper up = bad = -1
    g.add_edge("copper", "sp500", direction="negative", weight=0.8)
    polarity = propagate_polarity(g, {"sp500": 1})
    assert polarity["sp500"] == 1
    assert polarity["copper"] == -1  # backward through negative edge


def test_backward_positive_edge():
    """Backward through positive edge preserves polarity."""
    g = nx.DiGraph()
    g.add_edge("tech", "sp500", direction="positive", weight=0.8)
    polarity = propagate_polarity(g, {"sp500": 1})
    assert polarity["tech"] == 1  # tech up → sp500 up, so tech up = good


def test_bidirectional_reaches_all():
    """All nodes in connected component should get polarity."""
    g = nx.DiGraph()
    # A → anchor (positive), B → A (negative), C → B (positive)
    g.add_edge("A", "anchor", direction="positive")
    g.add_edge("B", "A", direction="negative")
    g.add_edge("C", "B", direction="positive")
    polarity = propagate_polarity(g, {"anchor": 1})
    assert polarity["anchor"] == 1
    assert polarity["A"] == 1       # backward positive from anchor
    assert polarity["B"] == -1      # backward negative from A
    assert polarity["C"] == -1      # backward positive from B (preserves B's -1)
