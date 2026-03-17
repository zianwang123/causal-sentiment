"""Tests for node importance ranking."""
import networkx as nx
from app.causal_discovery.engine.importance import rank_nodes_by_importance


def test_central_node_ranks_higher():
    g = nx.DiGraph()
    for i in range(5):
        g.add_edge("hub", f"leaf_{i}", weight=0.5)
    g.add_edge("isolated", "leaf_0", weight=0.5)
    ranking = rank_nodes_by_importance(g)
    hub_rank = next(r for r in ranking if r["node_id"] == "hub")
    iso_rank = next(r for r in ranking if r["node_id"] == "isolated")
    assert hub_rank["score"] > iso_rank["score"]


def test_top_n_filter():
    g = nx.DiGraph()
    for i in range(20):
        g.add_edge(f"a_{i}", f"b_{i}", weight=0.5)
    assert len(rank_nodes_by_importance(g, top_n=5)) == 5
