"""Unit tests for the propagation algorithm."""

import networkx as nx
import pytest

from app.graph_engine.propagation import build_networkx_graph, propagate_signal
from app.models.graph import EdgeDirection


def _simple_graph():
    """A -> B -> C linear chain with positive edges, weight 0.8."""
    nodes = [
        {"id": "A", "label": "A", "composite_sentiment": 0.0},
        {"id": "B", "label": "B", "composite_sentiment": 0.0},
        {"id": "C", "label": "C", "composite_sentiment": 0.0},
    ]
    edges = [
        {"source_id": "A", "target_id": "B", "direction": EdgeDirection.POSITIVE, "base_weight": 0.8, "dynamic_weight": 0.8},
        {"source_id": "B", "target_id": "C", "direction": EdgeDirection.POSITIVE, "base_weight": 0.8, "dynamic_weight": 0.8},
    ]
    return build_networkx_graph(nodes, edges)


def _diamond_graph():
    """A -> B, A -> C, B -> D, C -> D — diamond with interference."""
    nodes = [{"id": n, "label": n, "composite_sentiment": 0.0} for n in "ABCD"]
    edges = [
        {"source_id": "A", "target_id": "B", "direction": EdgeDirection.POSITIVE, "base_weight": 0.5, "dynamic_weight": 0.5},
        {"source_id": "A", "target_id": "C", "direction": EdgeDirection.POSITIVE, "base_weight": 0.5, "dynamic_weight": 0.5},
        {"source_id": "B", "target_id": "D", "direction": EdgeDirection.POSITIVE, "base_weight": 0.5, "dynamic_weight": 0.5},
        {"source_id": "C", "target_id": "D", "direction": EdgeDirection.NEGATIVE, "base_weight": 0.5, "dynamic_weight": 0.5},
    ]
    return build_networkx_graph(nodes, edges)


def test_linear_propagation():
    g = _simple_graph()
    result = propagate_signal(g, "A", 1.0, decay_per_hop=0.3)

    assert "B" in result.impacts
    assert "C" in result.impacts
    # B: 1.0 * 0.8 * 1.0 * 0.7 = 0.56
    assert abs(result.impacts["B"] - 0.56) < 0.01
    # C: 0.56 * 0.8 * 1.0 * 0.7 = 0.3136
    assert abs(result.impacts["C"] - 0.3136) < 0.01


def test_negative_edge():
    nodes = [{"id": "X", "label": "X"}, {"id": "Y", "label": "Y"}]
    edges = [{"source_id": "X", "target_id": "Y", "direction": EdgeDirection.NEGATIVE, "base_weight": 0.6, "dynamic_weight": 0.6}]
    g = build_networkx_graph(nodes, edges)
    result = propagate_signal(g, "X", 0.8, decay_per_hop=0.3)
    # 0.8 * 0.6 * (-1) * 0.7 = -0.336
    assert result.impacts["Y"] < 0
    assert abs(result.impacts["Y"] - (-0.336)) < 0.01


def test_diamond_interference():
    g = _diamond_graph()
    result = propagate_signal(g, "A", 1.0, decay_per_hop=0.3)
    assert "D" in result.impacts
    # Two paths to D, one positive and one negative — should partially cancel
    # Path B: 1.0*0.5*0.7 = 0.35 -> D: 0.35*0.5*0.7 = 0.1225
    # Path C: 1.0*0.5*0.7 = 0.35 -> D: 0.35*0.5*(-1)*0.7 = -0.1225
    # Sum ≈ 0.0
    assert abs(result.impacts["D"]) < 0.01


def test_max_depth_respected():
    # Long chain: A->B->C->D->E->F
    nodes = [{"id": n, "label": n} for n in "ABCDEF"]
    edges = [
        {"source_id": s, "target_id": t, "direction": EdgeDirection.POSITIVE, "base_weight": 0.9, "dynamic_weight": 0.9}
        for s, t in [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "F")]
    ]
    g = build_networkx_graph(nodes, edges)
    result = propagate_signal(g, "A", 1.0, max_depth=3)
    assert "D" in result.impacts
    assert "E" not in result.impacts  # Depth 4 — beyond max_depth=3


def test_clamping():
    nodes = [{"id": "X", "label": "X"}, {"id": "Y", "label": "Y"}]
    edges = [{"source_id": "X", "target_id": "Y", "direction": EdgeDirection.POSITIVE, "base_weight": 1.0, "dynamic_weight": 1.0}]
    g = build_networkx_graph(nodes, edges)
    result = propagate_signal(g, "X", 5.0, decay_per_hop=0.0)  # No decay, signal > 1
    assert result.impacts["Y"] <= 1.0


def test_nonexistent_source():
    g = _simple_graph()
    result = propagate_signal(g, "DOES_NOT_EXIST", 1.0)
    assert len(result.impacts) == 0


def test_mvp_graph_builds():
    from app.graph_engine.topology import MVP_EDGES, MVP_NODES
    g = build_networkx_graph(MVP_NODES, MVP_EDGES)
    assert g.number_of_nodes() == len(MVP_NODES)
    assert g.number_of_edges() == len(MVP_EDGES)

    # Propagate from fed_funds_rate and verify it reaches sp500
    result = propagate_signal(g, "fed_funds_rate", 0.5)
    assert "sp500" in result.impacts
