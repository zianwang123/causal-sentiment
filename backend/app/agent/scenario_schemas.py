"""Tool schemas for the scenario extrapolation engine.

Reuses search_news, fetch_market_prices, validate_consistency from the main agent.
Adds get_graph_topology and submit_scenarios as scenario-specific tools.
"""

from app.agent.schemas import AGENT_TOOLS

# Reuse existing tool schemas by name
_REUSED_TOOLS = {"search_news", "fetch_market_prices", "validate_consistency"}
SCENARIO_TOOLS_BASE = [t for t in AGENT_TOOLS if t["name"] in _REUSED_TOOLS]

# New: get graph topology (nodes + edges, NO sentiments)
GET_GRAPH_TOPOLOGY = {
    "name": "get_graph_topology",
    "description": "Get the causal factor graph structure: all nodes (id, label, type, description) and all edges (source, target, direction, weight). Does NOT include sentiment values — only the structural topology. Use this to understand what nodes exist and how they connect.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

# New: submit structured scenario output
SUBMIT_SCENARIOS = {
    "name": "submit_scenarios",
    "description": "Submit your final structured scenario output. Call this once after you've completed all phases: research, scenario generation, and graph mapping.",
    "input_schema": {
        "type": "object",
        "properties": {
            "research_summary": {
                "type": "string",
                "description": "Summary of what you found during news research (2-3 sentences)",
            },
            "historical_parallels": {
                "type": "string",
                "description": "Historical precedents you identified with market impact data",
            },
            "branches": {
                "type": "array",
                "description": "2-3 scenario branches",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Short scenario title",
                        },
                        "probability": {
                            "type": "number",
                            "description": "Probability estimate 0-1 (branches should sum to ~1.0)",
                        },
                        "narrative": {
                            "type": "string",
                            "description": "2-3 sentence scenario narrative",
                        },
                        "causal_chain": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Step-by-step causal chain: ['event', '-> consequence 1', '-> consequence 2']",
                        },
                        "time_horizon": {
                            "type": "string",
                            "description": "How fast does this play out: 'days', 'weeks', or 'months'",
                        },
                        "invalidation": {
                            "type": "string",
                            "description": "What would make this scenario wrong",
                        },
                        "shocks": {
                            "type": "array",
                            "description": "Mapped shocks to graph nodes",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "node_id": {
                                        "type": "string",
                                        "description": "Graph node ID to shock",
                                    },
                                    "shock_value": {
                                        "type": "number",
                                        "description": "Shock value [-1, +1]",
                                    },
                                    "reasoning": {
                                        "type": "string",
                                        "description": "Why this shock for this node",
                                    },
                                    "original_impact": {
                                        "type": "string",
                                        "description": "Original free-form impact description before mapping",
                                    },
                                },
                                "required": ["node_id", "shock_value", "reasoning"],
                            },
                        },
                        "node_suggestions": {
                            "type": "array",
                            "description": "Suggested new nodes for impacts that don't map to existing nodes",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "suggested_id": {
                                        "type": "string",
                                        "description": "Suggested node ID (snake_case)",
                                    },
                                    "suggested_label": {
                                        "type": "string",
                                        "description": "Human-readable label",
                                    },
                                    "suggested_type": {
                                        "type": "string",
                                        "description": "Node type (macro, geopolitics, commodities, equities, etc.)",
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "What this node represents",
                                    },
                                    "reasoning": {
                                        "type": "string",
                                        "description": "Why this node is needed",
                                    },
                                },
                                "required": ["suggested_id", "suggested_label", "suggested_type", "description"],
                            },
                        },
                        "edge_suggestions": {
                            "type": "array",
                            "description": "Suggested new causal edges (missing links between existing nodes)",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "source_id": {
                                        "type": "string",
                                        "description": "Source node ID",
                                    },
                                    "target_id": {
                                        "type": "string",
                                        "description": "Target node ID",
                                    },
                                    "direction": {
                                        "type": "string",
                                        "enum": ["positive", "negative", "complex"],
                                        "description": "Causal direction",
                                    },
                                    "reasoning": {
                                        "type": "string",
                                        "description": "Why this edge should exist",
                                    },
                                },
                                "required": ["source_id", "target_id", "direction", "reasoning"],
                            },
                        },
                    },
                    "required": ["title", "probability", "narrative", "causal_chain", "time_horizon", "shocks"],
                },
            },
        },
        "required": ["research_summary", "historical_parallels", "branches"],
    },
}

# Full tool list for scenario agent
SCENARIO_TOOLS = SCENARIO_TOOLS_BASE + [GET_GRAPH_TOPOLOGY, SUBMIT_SCENARIOS]
