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
                        "probability_reasoning": {
                            "type": "string",
                            "description": "Carry forward from strategist: why this probability",
                        },
                        "narrative": {
                            "type": "string",
                            "description": "2-3 sentence scenario narrative",
                        },
                        "causal_chain": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Deep causal chain with temporal markers and parallel paths. Use format: "
                                "'TRIGGER: event', 'PATH A (domain, mechanism):', "
                                "'IMMEDIATE (0-24h): reaction', '-> SHORT-TERM (1-7d): consequence', "
                                "'-> MEDIUM-TERM (1-4w): second-order', '-> STRUCTURAL (1-6m): regime shift', "
                                "'PATH B (domain):', ..., 'CROSS-DOMAIN SPILLOVER: where Path A enters Path B'. "
                                "Each path minimum 3 hops deep. Label temporal layers explicitly.",
                        },
                        "structural_outcome": {
                            "type": "string",
                            "description": "Carry forward from strategist: the 1-6 month regime shift / new equilibrium",
                        },
                        "time_horizon": {
                            "type": "string",
                            "description": "How fast does this play out: 'days', 'weeks', or 'months'",
                        },
                        "invalidation": {
                            "type": "string",
                            "description": "What would make this scenario wrong",
                        },
                        "key_assumption": {
                            "type": "string",
                            "description": "The critical assumption that must hold for this scenario to play out",
                        },
                        "specific_predictions": {
                            "type": "array",
                            "description": "Carry forward from strategist: predictions with optional ticker/direction/threshold for market-checkable ones",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "prediction": {"type": "string"},
                                    "confidence": {"type": "number"},
                                    "time_window": {"type": "string"},
                                    "ticker": {"type": "string"},
                                    "direction": {"type": "string", "enum": ["above", "below"]},
                                    "threshold": {"type": "number"},
                                },
                                "required": ["prediction", "confidence"],
                            },
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

# Phase 1 Researcher output capture
SUBMIT_RESEARCH = {
    "name": "submit_research",
    "description": "Submit your research findings. Call this once you have a complete situational picture of the triggering event.",
    "input_schema": {
        "type": "object",
        "properties": {
            "trigger": {
                "type": "string",
                "description": "The identified/refined trigger event (use user's trigger if provided, or identify the most scenario-worthy event from news)",
            },
            "facts": {
                "type": "string",
                "description": "Verified facts about the event — what is confirmed vs. speculation",
            },
            "key_actors": {
                "type": "string",
                "description": "Key actors involved with their incentives, capabilities, and constraints",
            },
            "market_reaction": {
                "type": "string",
                "description": "Market reaction so far — what is already priced in",
            },
            "structural_context": {
                "type": "string",
                "description": "Current system vulnerabilities and fragility points this event interacts with",
            },
            "domain_classification": {
                "type": "string",
                "description": "Primary domain(s): geopolitical, monetary, trade, technology, climate, pandemic, corporate",
            },
        },
        "required": ["trigger", "facts", "key_actors", "structural_context", "domain_classification"],
    },
}

# Phase 2 Historian output capture
SUBMIT_HISTORY = {
    "name": "submit_history",
    "description": "Submit your historical analysis. Call this once you have identified 2-3 structural parallels with concrete data.",
    "input_schema": {
        "type": "object",
        "properties": {
            "parallels": {
                "type": "array",
                "description": "2-3 structural parallels from history",
                "items": {
                    "type": "object",
                    "properties": {
                        "event": {
                            "type": "string",
                            "description": "Historical event name and date",
                        },
                        "structural_match": {
                            "type": "string",
                            "description": "What structural conditions from that crisis exist today (leverage, concentration, policy constraints)",
                        },
                        "transmission_mechanism": {
                            "type": "string",
                            "description": "How did the shock propagate through the system? What was the causal chain?",
                        },
                        "duration": {
                            "type": "string",
                            "description": "How long did the impact last? Brief dislocation or regime change?",
                        },
                        "consensus_error": {
                            "type": "string",
                            "description": "What did the consensus get WRONG? What assumption broke?",
                        },
                        "specific_data": {
                            "type": "string",
                            "description": "Specific numbers: spreads, price moves, durations, losses",
                        },
                    },
                    "required": ["event", "structural_match", "transmission_mechanism", "consensus_error", "specific_data"],
                },
            },
        },
        "required": ["parallels"],
    },
}

# Phase 3 Strategist output capture (free-form impacts, NO node mappings)
SUBMIT_FREE_SCENARIOS = {
    "name": "submit_free_scenarios",
    "description": "Submit your scenario analysis. Call this once you have generated 2-3 branching scenarios with causal chains, predictions, and free-form impacts. Do NOT include node IDs or shock values — describe impacts in real-world terms.",
    "input_schema": {
        "type": "object",
        "properties": {
            "research_summary": {
                "type": "string",
                "description": "Summary of the situation from research phase (2-3 sentences)",
            },
            "historical_parallels": {
                "type": "string",
                "description": "Key historical parallels and their calibration lessons",
            },
            "branches": {
                "type": "array",
                "description": "2-3 scenario branches with free-form impacts",
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
                        "probability_reasoning": {
                            "type": "string",
                            "description": "WHY this probability — cite the historical base rate for this class of event, "
                                "what evidence shifts it up or down, and why it's not the default 55/30/15. "
                                "E.g., 'Trade wars escalate beyond initial tariffs ~40-50% of the time historically. "
                                "Current evidence (retaliatory measures already announced, election-year politics) "
                                "pushes this toward the upper end → 55%.'",
                        },
                        "narrative": {
                            "type": "string",
                            "description": "2-3 sentence scenario narrative with specific mechanisms",
                        },
                        "causal_chain": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Deep causal chain with temporal markers and parallel paths. Use format: "
                                "'TRIGGER: event', 'PATH A (domain, mechanism):', "
                                "'IMMEDIATE (0-24h): reaction', '-> SHORT-TERM (1-7d): consequence', "
                                "'-> MEDIUM-TERM (1-4w): second-order', '-> STRUCTURAL (1-6m): regime shift', "
                                "'PATH B (domain):', ..., 'CROSS-DOMAIN SPILLOVER: where Path A enters Path B'. "
                                "Each path minimum 3 hops deep.",
                        },
                        "structural_outcome": {
                            "type": "string",
                            "description": "The STRUCTURAL (1-6 month) regime shift or new equilibrium that results. "
                                "What permanently changes? What new behavioral pattern or market structure emerges? "
                                "E.g., 'Permanent reshoring of critical mineral processing creates a 3-5 year "
                                "capex cycle; supply chains bifurcate into US-allied and China-aligned blocs.'",
                        },
                        "specific_predictions": {
                            "type": "array",
                            "description": "3-5 predictions per branch. At least 2 MUST be market-checkable "
                                "(include ticker, direction, threshold). The rest can be qualitative events.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "prediction": {"type": "string", "description": "Observable prediction text"},
                                    "confidence": {"type": "number", "description": "Confidence 0-1"},
                                    "time_window": {"type": "string", "description": "When checkable (e.g., '1-2 weeks')"},
                                    "ticker": {
                                        "type": "string",
                                        "description": "For market-checkable predictions ONLY: ticker symbol "
                                            "(SPY, ^VIX, CL=F, BZ=F, GC=F, DX-Y.NYB, ^TNX, ^TYX, HYG, LQD, "
                                            "^GSPC, IWM, EURUSD=X, USDJPY=X). Omit for qualitative predictions.",
                                    },
                                    "direction": {
                                        "type": "string",
                                        "enum": ["above", "below"],
                                        "description": "For market-checkable predictions: above or below the threshold",
                                    },
                                    "threshold": {
                                        "type": "number",
                                        "description": "For market-checkable predictions: the price/level threshold",
                                    },
                                },
                                "required": ["prediction", "confidence", "time_window"],
                            },
                        },
                        "free_form_impacts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Real-world consequences with magnitudes. Describe impacts as they would actually unfold — NOT as graph node IDs. E.g., 'Oil spikes to $120+ as 2M bpd goes offline' not 'crude_oil: +0.5'",
                        },
                        "time_horizon": {
                            "type": "string",
                            "description": "How fast: 'days', 'weeks', or 'months'",
                        },
                        "invalidation": {
                            "type": "string",
                            "description": "What would make this scenario wrong",
                        },
                        "key_assumption": {
                            "type": "string",
                            "description": "The critical assumption that must hold",
                        },
                    },
                    "required": ["title", "probability", "narrative", "causal_chain", "specific_predictions", "free_form_impacts", "time_horizon"],
                },
            },
        },
        "required": ["research_summary", "historical_parallels", "branches"],
    },
}

# New: fetch historical price summary for the Historian
FETCH_HISTORICAL_PRICES = {
    "name": "fetch_historical_prices",
    "description": "Fetch historical price summary for a ticker over a date range. "
        "Returns summary statistics (open, close, high, low, total return, max drawdown, "
        "peak/trough dates, annualized volatility) — NOT raw daily bars. "
        "Use this to verify historical parallels with actual market data. Max 1 year per request.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Ticker symbol (e.g., 'SPY', '^VIX', 'CL=F', 'GLD', 'BZ=F', '^GSPC', 'DX-Y.NYB', 'HYG')",
            },
            "start_date": {
                "type": "string",
                "description": "Start date in ISO format (YYYY-MM-DD)",
            },
            "end_date": {
                "type": "string",
                "description": "End date in ISO format (YYYY-MM-DD)",
            },
        },
        "required": ["ticker", "start_date", "end_date"],
    },
}

# New: preview propagation cascade for the Mapper
PREVIEW_PROPAGATION = {
    "name": "preview_propagation",
    "description": "Preview the cascade effects of proposed shocks through the causal graph. "
        "Pass the shocks you plan to assign for a branch, and see which nodes are affected "
        "by propagation and by how much. Use this to verify that the cascade matches the "
        "strategist's narrative before submitting. If the propagation doesn't reflect the "
        "expected impacts, adjust your shock values.",
    "input_schema": {
        "type": "object",
        "properties": {
            "shocks": {
                "type": "array",
                "description": "Proposed shocks for a branch",
                "items": {
                    "type": "object",
                    "properties": {
                        "node_id": {"type": "string", "description": "Graph node ID"},
                        "shock_value": {"type": "number", "description": "Shock value [-1, +1]"},
                    },
                    "required": ["node_id", "shock_value"],
                },
            },
        },
        "required": ["shocks"],
    },
}

# Per-phase tool lists for multi-agent scenario engine
_NEWS_TOOLS = [t for t in AGENT_TOOLS if t["name"] in {"search_news", "fetch_market_prices"}]

RESEARCHER_TOOLS = _NEWS_TOOLS + [SUBMIT_RESEARCH]
HISTORIAN_TOOLS = _NEWS_TOOLS + [FETCH_HISTORICAL_PRICES, SUBMIT_HISTORY]
STRATEGIST_TOOLS = _NEWS_TOOLS + [SUBMIT_FREE_SCENARIOS]
MAPPER_TOOLS = [
    t for t in AGENT_TOOLS if t["name"] == "validate_consistency"
] + [GET_GRAPH_TOPOLOGY, PREVIEW_PROPAGATION, SUBMIT_SCENARIOS]

# Full tool list for scenario agent (backward compatibility)
SCENARIO_TOOLS = SCENARIO_TOOLS_BASE + [GET_GRAPH_TOPOLOGY, SUBMIT_SCENARIOS]
