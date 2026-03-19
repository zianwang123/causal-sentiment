"""Scenario extrapolation engine — multi-agent orchestrator.

Architecture: Orchestrator + 3 sub-agents, each with a focused system prompt.
  Phase 1: RESEARCHER — scans news, identifies trigger, builds structural picture
  Phase 2: HISTORIAN — finds structural parallels from history, calibrates magnitudes
  Phase 3: STRATEGIST — deep causal chain reasoning, generates branching scenarios
  Phase 4: MAPPER (orchestrator) — maps free-form impacts to graph nodes

Each sub-agent gets a FRESH conversation with only the context it needs.
Reuses existing tool functions (search_news, fetch_market_prices, validate_consistency)
but NEVER reads stored sentiments, past agent runs, or prediction history.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta

import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.llm_client import append_tool_results, chat_with_tools, simple_completion
from app.agent.scenario_prompts import (
    HISTORIAN_SYSTEM_PROMPT,
    MAPPER_SYSTEM_PROMPT,
    PHASE1_NEWS_PROMPT,
    PHASE2_HISTORY_PROMPT,
    PHASE3_GENERATE_PROMPT,
    PHASE4_MAP_PROMPT_TEMPLATE,
    QUICK_TRIGGERS_PROMPT,
    RESEARCHER_SYSTEM_PROMPT,
    STRATEGIST_SYSTEM_PROMPT,
)
from app.agent.scenario_schemas import (
    HISTORIAN_TOOLS,
    MAPPER_TOOLS,
    RESEARCHER_TOOLS,
    STRATEGIST_TOOLS,
)
from app.agent.tools import fetch_market_prices, search_news, validate_consistency
from app.models.scenarios import NodeSuggestion, Scenario, ScenarioPrediction, ScenarioShock

logger = logging.getLogger(__name__)

# Phase round budgets — each sub-agent gets its own fresh context
PHASE1_ROUNDS = 4   # Researcher: news ingestion + structural assessment
PHASE2_ROUNDS = 5   # Historian: structural parallels + calibration
PHASE3_ROUNDS = 12  # Strategist: deep causal chain reasoning (core value) — higher budget for structured output
PHASE4_ROUNDS = 6   # Mapper: mechanical graph mapping + preview_propagation verification
MAX_ROUNDS = PHASE1_ROUNDS + PHASE2_ROUNDS + PHASE3_ROUNDS + PHASE4_ROUNDS  # 22

# Higher max_tokens for scenario agents — submit tool calls produce large JSON
SCENARIO_MAX_TOKENS = 24576

# Submission tool names (intercepted by orchestrator)
_SUBMIT_TOOLS = {"submit_research", "submit_history", "submit_free_scenarios", "submit_scenarios"}

# Domain-specific trigger keywords — used to inject targeted research guidance in Phase 1
_DOMAIN_KEYWORDS: dict[str, set[str]] = {
    "geopolitical": {
        "war", "invasion", "strike", "assassination", "killed", "death", "coup",
        "military", "missile", "nuclear", "embargo", "blockade",
        "strait", "hormuz", "suez", "taiwan", "nato", "irgc", "hezbollah",
        "houthi", "proxy", "escalation", "retaliation", "regime", "succession",
        "iran", "russia", "israel", "gaza", "ukraine",
    },
    "policy_monetary": {
        "fed", "fomc", "ecb", "boj", "boe", "pboc",
        "qe", "qt", "taper", "pivot",
        "dovish", "hawkish", "transitory",
        "repo", "ldi", "pension",
        "rate cut", "rate hike", "yield curve control", "emergency cut",
        "emergency rate", "balance sheet", "inflation target",
        "forward guidance",
    },
    "trade_tariff": {
        "tariff", "tariffs", "reshoring", "nearshoring", "decoupling",
        "cbam", "wto",
        "trade war", "trade deal", "trade deficit",
        "import duty", "export ban", "carbon border",
        "supply chain", "rare earth", "semiconductor ban",
        "chip ban", "entity list",
    },
    "technology_systemic": {
        "cyberattack", "cyber", "ransomware", "hack", "outage",
        "automation", "displacement", "deepfake", "quantum",
        "cloud outage", "ai disruption", "artificial intelligence",
        "infrastructure attack", "grid failure", "systemic outage",
        "platform monopoly",
    },
    "climate_energy": {
        "climate", "hurricane", "wildfire", "drought", "flood",
        "renewable", "solar", "wind", "lithium", "cobalt", "transition",
        "carbon tax", "carbon price", "stranded asset", "ice ban",
        "ev mandate", "extreme weather", "insurance withdrawal",
        "crop failure", "food crisis", "heat wave",
    },
    "pandemic_health": {
        "pandemic", "epidemic", "outbreak", "pathogen", "virus", "variant",
        "lockdown", "quarantine", "vaccine", "mortality",
        "bird flu", "avian flu", "h5n1", "who emergency",
        "supply shortage",
    },
    "corporate_financial": {
        "default", "bankruptcy", "stablecoin", "depeg",
        "counterparty", "contagion", "liquidation",
        "clearinghouse",
        "bank run", "bank failure", "margin call",
        "commercial real estate", "credit crunch",
        "forced selling", "money market", "prime broker",
        "hedge fund collapse",
    },
}

# Domain-specific Phase 1 research supplements
_DOMAIN_SUPPLEMENTS: dict[str, str] = {
    "geopolitical": """\

## Geopolitical Focus

This trigger involves a geopolitical/military event. In addition to market context:
1. Research the specific actors and their command structures
2. Identify proxy networks and alliance commitments that could activate
3. Assess physical chokepoints or infrastructure at risk
4. Search for the political/military dimensions, not just the market reaction

Example queries: "Iran IRGC command structure", "Strait of Hormuz shipping risk", \
"Middle East proxy forces escalation".

## Cross-Domain Cascade
After tracing the political/military cascade, explicitly identify:
- Which ENERGY chokepoints or supply chains are at risk?
- Which FINANCIAL positions (carry trades, concentrated bets) would unwind?
- Which POLICY responses (sanctions, emergency measures) would create second-order effects?
- Which ALLIANCE structures could fracture, and what would that mean for trade/currency blocs?\
""",
    "policy_monetary": """\

## Monetary Policy Focus

This trigger involves a central bank policy event. In addition to market context:
1. Research the specific policy tool and its transmission mechanism timeline
2. Identify leveraged positions that depend on current rate/liquidity regime
3. Assess forward guidance credibility — has a commitment been broken?
4. Search for carry trade and collateral chain implications, not just rate direction

Example queries: "yen carry trade size estimates", "money market fund T-bill holdings", \
"pension LDI leverage exposure".

## Cross-Domain Cascade
After tracing the monetary transmission mechanism, explicitly identify:
- Which CORPORATE balance sheets break at new rate levels?
- Which SOVEREIGN debt becomes unsustainable (EM countries, fiscal-constrained economies)?
- Which TRADE competitiveness shifts from currency repricing?
- Which REAL ECONOMY sectors slow first (housing, autos, capex)?
- Which POLITICAL pressures build from economic pain?\
""",
    "trade_tariff": """\

## Trade/Tariff Focus

This trigger involves a trade policy or sanctions event. In addition to market context:
1. Research which specific supply chains are affected and substitution timelines
2. Identify the most likely retaliation sequence and its escalation ceiling
3. Assess which countries/companies are caught in the crossfire
4. Search for the supply chain restructuring timeline, not just the headline tariff rate

Example queries: "semiconductor supply chain China alternatives", "rare earth processing \
outside China", "agricultural export retaliation targets".

## Cross-Domain Cascade
After tracing the supply chain cascade, explicitly identify:
- Which SUPPLY CHAINS have no substitutes (cross into TECHNOLOGY constraints)?
- Which CURRENCIES are weaponized in response (cross into MONETARY)?
- Which POLITICAL coalitions fracture (allied countries forced to choose sides)?
- Which CONSUMER prices spike and with what lag (cross into INFLATION/POLICY)?
- Which CORPORATE earnings are exposed (specific sectors, not vague "trade-exposed")?\
""",
    "technology_systemic": """\

## Technology/Systemic Focus

This trigger involves technology disruption or systemic infrastructure risk. In addition to market context:
1. Research concentration risk — how many systems depend on the affected platform/technology?
2. Identify cascading dependencies (a cloud outage hits payments, logistics, healthcare simultaneously)
3. Assess regulatory response timelines and emergency powers
4. Search for the labor market or productivity implications, not just stock price impact

Example queries: "cloud provider market share concentration", "critical infrastructure \
dependencies", "AI labor displacement timeline estimates".

## Cross-Domain Cascade
After tracing the technology/concentration cascade, explicitly identify:
- Which FINANCIAL systems depend on the affected platform (payments, clearing, trading)?
- Which LABOR markets are disrupted (displacement speed vs. retraining timeline)?
- Which REGULATORY responses create new constraints (emergency powers, breakup pressure)?
- Which NATIONAL SECURITY implications arise (defense, intelligence, critical infrastructure)?
- Which INSURANCE markets face new exposure categories?\
""",
    "climate_energy": """\

## Climate/Energy Transition Focus

This trigger involves climate events or energy transition policy. In addition to market context:
1. Research physical exposure — which regions, crops, or infrastructure are directly affected?
2. Identify stranded asset exposure on bank and insurer balance sheets
3. Assess transition metal supply bottlenecks if the event accelerates green policy
4. Search for the insurance and mortgage market implications, not just commodity prices

Example queries: "flood insurance withdrawal US coastal", "lithium supply deficit projections", \
"stranded fossil fuel asset bank exposure".

## Cross-Domain Cascade
After tracing the physical/energy cascade, explicitly identify:
- Which INSURANCE markets withdraw coverage (cross into FINANCIAL — uninsurable = unlendable)?
- Which FOOD supply chains break from crop/logistics damage (cross into TRADE/POLITICAL)?
- Which ENERGY infrastructure is damaged (cross into INDUSTRIAL production, heating, transport)?
- Which MIGRATION patterns shift from uninhabitable zones (cross into POLITICAL/LABOR)?
- Which SOVEREIGN fiscal positions are strained by disaster response costs?\
""",
    "pandemic_health": """\

## Pandemic/Health Focus

This trigger involves a health emergency or pandemic risk. In addition to market context:
1. Research the pathogen characteristics — transmissibility, mortality, immune escape
2. Identify supply chain nodes most vulnerable to disruption (semiconductors, medical, food)
3. Assess fiscal capacity for stimulus — sovereign debt levels are much higher post-COVID
4. Search for behavioral change implications (voluntary vs mandated), not just lockdown probability

Example queries: "pandemic preparedness stockpile status", "sovereign debt capacity fiscal \
stimulus", "JIT supply chain vulnerability assessment".

## Cross-Domain Cascade
After tracing the behavioral/health cascade, explicitly identify:
- Which SUPPLY CHAINS break first (cross into TRADE — semis, medical, food)?
- Which FISCAL capacity is exhausted (cross into MONETARY — can governments stimulate again)?
- Which LABOR markets are disrupted (cross into CONSUMER spending, wage dynamics)?
- Which POLITICAL responses create moral hazard or social division?
- Which PHARMA/BIOTECH pipelines become relevant (cross into EQUITY sector rotation)?\
""",
    "corporate_financial": """\

## Corporate/Financial Systemic Focus

This trigger involves a corporate failure or financial system stress. In addition to market context:
1. Research counterparty exposure — who is the failing entity's prime broker, clearinghouse, creditors?
2. Identify collateral chains that could create forced-selling cascades
3. Assess deposit flight risk and the speed of social-media-accelerated bank runs
4. Search for regulatory intervention threshold and available tools (FDIC, Fed 13(3), etc.)

Example queries: "CRE loan maturity wall", "stablecoin reserve composition", \
"prime broker concentrated exposure hedge funds".

## Cross-Domain Cascade
After tracing the counterparty/financial cascade, explicitly identify:
- Which COUNTERPARTIES are exposed (cross into FINANCIAL SYSTEM — prime brokers, clearinghouses)?
- Which REGULATORY responses change the rules (cross into POLICY — bailout debates, new regulations)?
- Which CONSUMER confidence effects materialize (cross into REAL ECONOMY — spending, hiring)?
- Which POLITICAL responses emerge (bailout politics, populist backlash)?
- Which CREDIT channels tighten (cross into CORPORATE/SME lending → real economy slowdown)?\
""",
}


def _build_vulnerability_context(graph: nx.DiGraph) -> str:
    """Extract structural vulnerability signals from graph state.

    Reports which areas of the system are fragile WITHOUT exposing specific
    sentiment values (preserves the isolation principle — agent sees direction
    and structural weight, not exact numbers).
    """
    try:
        from app.graph_engine.regimes import detect_regime

        regime = detect_regime(graph)

        extreme_nodes = []
        for nid, data in graph.nodes(data=True):
            sentiment = data.get("composite_sentiment", 0.0) or 0.0
            if abs(sentiment) > 0.7:
                direction = "extremely bullish" if sentiment > 0 else "extremely bearish"
                extreme_nodes.append(f"  - {data.get('label', nid)}: {direction}")

        high_weight_edges = []
        for src, tgt, edata in graph.edges(data=True):
            eff_weight = 0.6 * edata.get("base_weight", 0.3) + 0.4 * edata.get("dynamic_weight", 0.3)
            if eff_weight > 0.5:
                src_label = graph.nodes[src].get("label", src)
                tgt_label = graph.nodes[tgt].get("label", tgt)
                high_weight_edges.append((eff_weight, f"  - {src_label} → {tgt_label} (weight: {eff_weight:.2f})"))
        high_weight_edges.sort(key=lambda x: x[0], reverse=True)

        parts = [f"Current regime: {regime.state.value} (confidence: {regime.confidence:.0%})"]

        if extreme_nodes:
            parts.append(f"\nNodes at extreme sentiment (potential fragility points):\n" + "\n".join(extreme_nodes[:10]))

        if high_weight_edges:
            parts.append(f"\nHighest-weight transmission channels (strongest causal links):\n" + "\n".join(e[1] for e in high_weight_edges[:8]))

        return "\n".join(parts)
    except Exception as e:
        logger.debug("Failed to build vulnerability context: %s", e)
        return ""


def _classify_trigger_domains(trigger: str) -> list[str]:
    """Classify the trigger text into one or more domains."""
    trigger_lower = trigger.lower()
    trigger_words = set(trigger_lower.split())

    domain_scores: dict[str, int] = {}
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if " " in kw:
                if kw in trigger_lower:
                    score += 2
            else:
                if kw in trigger_words:
                    score += 1
        if score > 0:
            domain_scores[domain] = score

    return sorted(domain_scores.keys(), key=lambda d: domain_scores[d], reverse=True)


def _build_topology_string(graph: nx.DiGraph) -> tuple[str, str, int, int]:
    """Build node list + edge list strings from graph topology only (no sentiments)."""
    node_lines = []
    for nid, data in sorted(graph.nodes(data=True)):
        ntype = data.get("node_type", "unknown")
        label = data.get("label", nid)
        desc = data.get("description", "")
        node_lines.append(f"  - {nid} | {label} | type={ntype} | {desc}")

    edge_lines = []
    for src, tgt, edata in graph.edges(data=True):
        direction = edata.get("direction", "positive")
        weight = edata.get("base_weight", 0.3)
        desc = edata.get("description", "")
        edge_lines.append(f"  - {src} -> {tgt} | {direction} | weight={weight:.2f} | {desc}")

    return (
        "\n".join(node_lines),
        "\n".join(edge_lines),
        graph.number_of_nodes(),
        graph.number_of_edges(),
    )


# ── Cross-branch coherence check ─────────────────────────────────────────


def _check_branch_coherence(scenario_brief: dict) -> list[str]:
    """Check cross-branch coherence — flag branches with very similar impact sets.

    Returns a list of warning strings (empty if coherent).
    """
    warnings: list[str] = []
    branches = scenario_brief.get("branches", [])

    # Build word sets from free_form_impacts per branch
    branch_words: list[set[str]] = []
    for b in branches:
        words: set[str] = set()
        for impact in b.get("free_form_impacts", []):
            if isinstance(impact, str):
                words.update(re.findall(r"\w+", impact.lower()))
        branch_words.append(words)

    for i in range(len(branches)):
        for j in range(i + 1, len(branches)):
            wi, wj = branch_words[i], branch_words[j]
            if not wi or not wj:
                continue
            intersection = wi & wj
            union = wi | wj
            jaccard = len(intersection) / len(union) if union else 0.0
            if jaccard > 0.8:
                title_i = branches[i].get("title", f"Branch {chr(65 + i)}")
                title_j = branches[j].get("title", f"Branch {chr(65 + j)}")
                warnings.append(
                    f"'{title_i}' and '{title_j}' have very similar impact sets "
                    f"(Jaccard={jaccard:.2f}). Consider differentiating them more."
                )

    return warnings


# ── Sub-agent runner ──────────────────────────────────────────────────────


async def _run_sub_agent(
    system_prompt: str,
    user_message: str,
    tools: list[dict],
    max_rounds: int,
    phase_name: str,
    scenario_id: int,
    global_round_offset: int,
    tool_calls_log: list[dict],
    session: AsyncSession,
    graph: nx.DiGraph,
) -> dict | None:
    """Run a sub-agent loop with fresh conversation context.

    Returns the intercepted submission tool input (dict), or None if the agent
    finished without calling a submission tool.
    """
    messages: list[dict] = [{"role": "user", "content": user_message}]
    submitted: dict | None = None
    # Convergence detection: track recent tool calls to avoid redundant searches
    _recent_calls: list[tuple[str, set[str]]] = []
    _CONVERGENCE_TOOLS = {"search_news", "fetch_market_prices"}

    for local_round in range(max_rounds):
        global_round = global_round_offset + local_round
        llm_response, messages = await chat_with_tools(
            system=system_prompt,
            messages=messages,
            tools=tools,
            max_tokens=SCENARIO_MAX_TOKENS,
        )

        if llm_response.done or not llm_response.tool_calls:
            break

        results: dict[str, str] = {}
        for tc in llm_response.tool_calls:
            logger.info("[scenario:%s round %d] %s(%s)", phase_name, local_round, tc.name, json.dumps(tc.input)[:200])

            # Intercept submission tools
            if tc.name in _SUBMIT_TOOLS:
                submitted = tc.input
                result = json.dumps({"status": "accepted", "message": f"{tc.name} received."})
            elif tc.name in _CONVERGENCE_TOOLS:
                # Check for redundant searches (Jaccard > 0.7 on input words)
                input_words = set(re.findall(r"\w+", json.dumps(tc.input).lower()))
                is_redundant = False
                for prev_name, prev_words in _recent_calls:
                    if prev_name == tc.name and prev_words and input_words:
                        intersection = input_words & prev_words
                        union = input_words | prev_words
                        if union and len(intersection) / len(union) > 0.7:
                            is_redundant = True
                            break
                _recent_calls.append((tc.name, input_words))
                if len(_recent_calls) > 8:
                    _recent_calls.pop(0)

                if is_redundant:
                    result = json.dumps({
                        "warning": "You've already searched for very similar terms. "
                        "Synthesize what you have and proceed to your submission tool."
                    })
                    logger.info("[scenario:%s] Convergence nudge for %s", phase_name, tc.name)
                else:
                    result = await _execute_scenario_tool(tc.name, tc.input, session, graph)
            else:
                result = await _execute_scenario_tool(tc.name, tc.input, session, graph)

            results[tc.id] = result
            tool_calls_log.append({
                "tool": tc.name, "input": tc.input,
                "output": result[:2000] if isinstance(result, str) else str(result)[:2000],
                "round": global_round, "phase": phase_name,
            })

        messages = append_tool_results(messages, llm_response.tool_calls, results)
        _broadcast_scenario_progress(scenario_id, global_round, phase_name, tool_calls_log)

        if submitted:
            break

    # If no submission tool was called, try to extract text from last assistant message
    if not submitted:
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                if isinstance(content, str) and content.strip():
                    # Return as a text-only brief
                    submitted = {"_text_brief": content}
                elif isinstance(content, list):
                    # Anthropic format: list of content blocks
                    for block in content:
                        if hasattr(block, "text") and block.text:
                            submitted = {"_text_brief": block.text}
                            break
                break

    return submitted


def _format_research_brief(research: dict) -> str:
    """Format researcher output as a brief for downstream agents."""
    if "_text_brief" in research:
        return research["_text_brief"]

    parts = [f"## Research Brief\n"]
    parts.append(f"**Trigger:** {research.get('trigger', 'Unknown')}\n")
    if research.get("facts"):
        parts.append(f"**Facts:** {research['facts']}\n")
    if research.get("key_actors"):
        parts.append(f"**Key Actors:** {research['key_actors']}\n")
    if research.get("market_reaction"):
        parts.append(f"**Market Reaction (priced in):** {research['market_reaction']}\n")
    if research.get("structural_context"):
        parts.append(f"**Structural Context:** {research['structural_context']}\n")
    if research.get("domain_classification"):
        parts.append(f"**Domains:** {research['domain_classification']}\n")
    return "\n".join(parts)


def _format_historical_brief(history: dict) -> str:
    """Format historian output as a brief for the strategist."""
    if "_text_brief" in history:
        return history["_text_brief"]

    parts = ["## Historical Parallels\n"]
    for i, p in enumerate(history.get("parallels", []), 1):
        parts.append(f"### Parallel {i}: {p.get('event', 'Unknown')}")
        if p.get("structural_match"):
            parts.append(f"**Structural Match:** {p['structural_match']}")
        if p.get("transmission_mechanism"):
            parts.append(f"**Transmission:** {p['transmission_mechanism']}")
        if p.get("duration"):
            parts.append(f"**Duration:** {p['duration']}")
        if p.get("consensus_error"):
            parts.append(f"**Consensus Error:** {p['consensus_error']}")
        if p.get("specific_data"):
            parts.append(f"**Data:** {p['specific_data']}")
        parts.append("")
    return "\n".join(parts)


def _build_mapper_input(scenario_brief: dict, graph: nx.DiGraph) -> str:
    """Build the Phase 4 user message: scenario brief + graph topology + mapping instructions."""
    node_list, edge_list, node_count, edge_count = _build_topology_string(graph)

    # Format the free-form branches for the mapper
    branches_text = ""
    for i, branch in enumerate(scenario_brief.get("branches", [])):
        branches_text += f"\n### Branch {chr(65 + i)}: {branch.get('title', 'Untitled')} ({branch.get('probability', 0) * 100:.0f}%)\n"
        branches_text += f"**Narrative:** {branch.get('narrative', '')}\n"
        if branch.get("free_form_impacts"):
            branches_text += "**Impacts:**\n"
            for impact in branch["free_form_impacts"]:
                branches_text += f"  - {impact}\n"
        if branch.get("causal_chain"):
            branches_text += "**Causal chain:** " + " | ".join(branch["causal_chain"][:5]) + "\n"

    map_prompt = PHASE4_MAP_PROMPT_TEMPLATE.format(
        node_count=node_count,
        edge_count=edge_count,
        node_list=node_list,
        edge_list=edge_list,
    )

    return f"""## Scenario Brief (from strategist — map these to graph nodes)

{branches_text}

{map_prompt}

IMPORTANT: For each branch, take the free-form impacts above and:
1. Find the best matching node in the graph
2. Assign a shock_value [-1, +1] calibrated against historical anchors
3. Include the original free-form impact as `original_impact` in each shock
4. Carry forward from the scenario brief: title, probability, probability_reasoning, narrative, \
causal_chain, structural_outcome, specific_predictions, time_horizon, invalidation, key_assumption.
5. Call `preview_propagation` with your proposed shocks to verify cascades match the narrative. \
Adjust shock values if needed (e.g., if a node the strategist identified as affected doesn't \
appear in the propagation, add a direct shock to it).
6. Use `research_summary` and `historical_parallels` from the scenario brief.
7. Call `submit_scenarios` with the final mapped result."""


# ── Main orchestrator ──────────────────────────────────────────────────────


async def run_scenario_extrapolation(
    trigger: str,
    trigger_type: str,
    session: AsyncSession,
    app_state,
    parent_context: str | None = None,
    parent_scenario_id: int | None = None,
    parent_branch_idx: int | None = None,
) -> Scenario:
    """Run the multi-agent scenario extrapolation.

    Phase 1: Researcher scans news, builds structural picture
    Phase 2: Historian finds structural parallels, calibrates magnitudes
    Phase 3: Strategist generates branching scenarios with deep causal chains
    Phase 4: Mapper maps free-form impacts to graph nodes
    """
    from app.config import settings

    graph = app_state.graph

    # Validate API key
    provider = settings.llm_provider
    if provider == "openai" and not settings.openai_api_key:
        scenario = Scenario(
            trigger=trigger or "(auto)", trigger_type=trigger_type, status="error",
            error="OPENAI_API_KEY not configured", finished_at=datetime.utcnow(),
        )
        session.add(scenario)
        await session.commit()
        return scenario
    elif provider == "anthropic" and not settings.anthropic_api_key:
        scenario = Scenario(
            trigger=trigger or "(auto)", trigger_type=trigger_type, status="error",
            error="ANTHROPIC_API_KEY not configured", finished_at=datetime.utcnow(),
        )
        session.add(scenario)
        await session.commit()
        return scenario

    # If no trigger provided, auto-pick from current news
    if not trigger.strip():
        trigger_type = "news_auto"
        trigger = await _auto_pick_trigger(graph)
        if not trigger:
            scenario = Scenario(
                trigger="(no news found)", trigger_type=trigger_type, status="error",
                error="Could not find any scenario-worthy events in current news",
                finished_at=datetime.utcnow(),
            )
            session.add(scenario)
            await session.commit()
            return scenario

    # Create scenario record
    scenario = Scenario(
        trigger=trigger, trigger_type=trigger_type, status="running",
        parent_scenario_id=parent_scenario_id,
        parent_branch_idx=parent_branch_idx,
    )
    session.add(scenario)
    await session.commit()

    tool_calls_log: list[dict] = []
    submitted_result: dict | None = None

    try:
        # ── Pre-fetch: current date + market snapshot for context ────
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        snapshot_text = f"## Current Date: {current_date}\n"
        try:
            snapshot_raw = await fetch_market_prices(tickers=["SPY", "^VIX", "CL=F", "DX-Y.NYB", "^TNX"])
            snapshot_data = json.loads(snapshot_raw) if isinstance(snapshot_raw, str) else snapshot_raw
            if isinstance(snapshot_data, dict):
                snapshot_text += "\n## Current Market Context\n"
                for ticker, data in snapshot_data.items():
                    if isinstance(data, dict) and "close" in data:
                        chg = data.get("change_pct", 0)
                        chg5 = data.get("change_5d_pct", 0)
                        snapshot_text += f"- {ticker}: {data['close']} ({chg:+.2f}% 1d, {chg5:+.2f}% 5d)\n"
        except Exception as e:
            logger.debug("[scenario] Market snapshot fetch failed (non-fatal): %s", e)
            snapshot_text += "(Market data unavailable)\n"

        # ── Phase 1: Researcher ──────────────────────────────────────
        phase1_content = f"{snapshot_text}\n{PHASE1_NEWS_PROMPT.format(trigger=trigger)}"
        if parent_context:
            phase1_content = f"## Parent Scenario Context (ASSUMED OUTCOME)\n\n{parent_context}\n\n---\n\n{phase1_content}"
        detected_domains = _classify_trigger_domains(trigger)
        for domain in detected_domains[:2]:
            supplement = _DOMAIN_SUPPLEMENTS.get(domain, "")
            if supplement:
                phase1_content += supplement

        vulnerability_context = _build_vulnerability_context(graph)
        if vulnerability_context:
            phase1_content += f"\n\n## Current System State (Structural Context)\n{vulnerability_context}"

        research_brief = await _run_sub_agent(
            system_prompt=RESEARCHER_SYSTEM_PROMPT,
            user_message=phase1_content,
            tools=RESEARCHER_TOOLS,
            max_rounds=PHASE1_ROUNDS,
            phase_name="research",
            scenario_id=scenario.id,
            global_round_offset=0,
            tool_calls_log=tool_calls_log,
            session=session,
            graph=graph,
        )

        if not research_brief:
            research_brief = {"_text_brief": f"Trigger: {trigger}. No structured research available."}

        research_text = _format_research_brief(research_brief)
        logger.info("[scenario] Phase 1 complete — research brief: %d chars", len(research_text))

        # ── Phase 2: Historian ───────────────────────────────────────
        historian_input = f"Current date: {current_date}\n\n{research_text}\n\n{PHASE2_HISTORY_PROMPT}"

        history_brief = await _run_sub_agent(
            system_prompt=HISTORIAN_SYSTEM_PROMPT,
            user_message=historian_input,
            tools=HISTORIAN_TOOLS,
            max_rounds=PHASE2_ROUNDS,
            phase_name="history",
            scenario_id=scenario.id,
            global_round_offset=PHASE1_ROUNDS,
            tool_calls_log=tool_calls_log,
            session=session,
            graph=graph,
        )

        if not history_brief:
            history_brief = {"_text_brief": "No historical parallels identified."}

        history_text = _format_historical_brief(history_brief)
        logger.info("[scenario] Phase 2 complete — history brief: %d chars", len(history_text))

        # ── Phase 3: Strategist ──────────────────────────────────────
        try:
            track_record = await _build_scenario_track_record(session)
        except Exception as e:
            logger.warning("[scenario] Track record query failed (non-fatal): %s", e)
            track_record = ""
        strategist_input = f"Current date: {current_date}\n\n{snapshot_text}\n\n{research_text}\n\n{history_text}"
        if track_record:
            strategist_input += f"\n\n{track_record}"
        strategist_input += f"\n\n{PHASE3_GENERATE_PROMPT}"

        scenario_brief = await _run_sub_agent(
            system_prompt=STRATEGIST_SYSTEM_PROMPT,
            user_message=strategist_input,
            tools=STRATEGIST_TOOLS,
            max_rounds=PHASE3_ROUNDS,
            phase_name="generation",
            scenario_id=scenario.id,
            global_round_offset=PHASE1_ROUNDS + PHASE2_ROUNDS,
            tool_calls_log=tool_calls_log,
            session=session,
            graph=graph,
        )

        if not scenario_brief or "_text_brief" in (scenario_brief or {}):
            # Strategist didn't call submit_free_scenarios — try to work with text
            logger.warning("[scenario] Strategist did not call submit_free_scenarios")
            scenario.status = "completed"
            scenario.error = "Strategist did not produce structured scenarios — check tool call log"
            text = (scenario_brief or {}).get("_text_brief", "")
            scenario.research_summary = text[:1000] if text else ""
            scenario.finished_at = datetime.utcnow()
            await session.commit()
            _broadcast_scenario_complete(scenario)
            return scenario

        logger.info("[scenario] Phase 3 complete — %d branches", len(scenario_brief.get("branches", [])))

        # ── Cross-branch coherence check ─────────────────────────────
        coherence_warnings = _check_branch_coherence(scenario_brief)
        for w in coherence_warnings:
            logger.warning("[scenario] Coherence: %s", w)

        # ── Phase 4: Mapper (orchestrator) ───────────────────────────
        mapper_input = _build_mapper_input(scenario_brief, graph)

        mapper_result = await _run_sub_agent(
            system_prompt=MAPPER_SYSTEM_PROMPT,
            user_message=mapper_input,
            tools=MAPPER_TOOLS,
            max_rounds=PHASE4_ROUNDS,
            phase_name="mapping",
            scenario_id=scenario.id,
            global_round_offset=PHASE1_ROUNDS + PHASE2_ROUNDS + PHASE3_ROUNDS,
            tool_calls_log=tool_calls_log,
            session=session,
            graph=graph,
        )

        if mapper_result and "_text_brief" not in mapper_result:
            submitted_result = mapper_result
        else:
            # Mapper didn't call submit_scenarios — try to build from strategist output
            logger.warning("[scenario] Mapper did not call submit_scenarios — using strategist output directly")
            submitted_result = _fallback_from_strategist(scenario_brief)

        # Save results — enrich with original sub-agent briefs if mapper's versions are thin
        if submitted_result:
            if not submitted_result.get("research_summary") and research_text:
                submitted_result["research_summary"] = research_text[:2000]
            if not submitted_result.get("historical_parallels") and history_text:
                submitted_result["historical_parallels"] = history_text[:2000]

            # Enrich branches with Strategist fields the Mapper may have dropped
            strategist_branches = (scenario_brief or {}).get("branches", [])
            for i, branch in enumerate(submitted_result.get("branches", [])):
                if i < len(strategist_branches):
                    sb = strategist_branches[i]
                    if not branch.get("probability_reasoning") and sb.get("probability_reasoning"):
                        branch["probability_reasoning"] = sb["probability_reasoning"]
                    if not branch.get("structural_outcome") and sb.get("structural_outcome"):
                        branch["structural_outcome"] = sb["structural_outcome"]

            scenario.status = "completed"
            scenario.scenarios_json = submitted_result
            scenario.research_summary = submitted_result.get("research_summary", "")
            scenario.historical_parallels = submitted_result.get("historical_parallels", "")
            await _persist_scenario_details(scenario.id, submitted_result, session, graph)
            # Extract predictions in a fresh session to avoid greenlet issues
            # from the long-running agent session (connection may have gone stale)
            try:
                from app.db.connection import async_session as session_factory
                async with session_factory() as pred_session:
                    await _extract_and_store_predictions(scenario.id, submitted_result, pred_session)
                    await pred_session.commit()
            except Exception as e:
                logger.warning("[scenario] Prediction extraction failed (non-fatal): %s", e)
        else:
            scenario.status = "completed"
            scenario.error = "No structured output produced — check tool call log"

        scenario.finished_at = datetime.utcnow()

    except Exception as e:
        logger.exception("Scenario agent run failed")
        try:
            await session.rollback()
        except Exception:
            pass
        try:
            from app.db.connection import async_session
            async with async_session() as err_session:
                from sqlalchemy import update
                await err_session.execute(
                    update(Scenario)
                    .where(Scenario.id == scenario.id)
                    .values(
                        status="error",
                        error=str(e)[:2000],
                        finished_at=datetime.utcnow(),
                    )
                )
                await err_session.commit()
            scenario.status = "error"
            scenario.error = str(e)[:2000]
            return scenario
        except Exception as commit_err:
            logger.error("Failed to persist scenario error: %s", commit_err)
            return scenario

    await session.commit()
    _broadcast_scenario_complete(scenario)
    return scenario


def _fallback_from_strategist(scenario_brief: dict) -> dict:
    """Build a submit_scenarios-compatible result from strategist output.

    When Phase 4 mapper fails to call submit_scenarios, we can still produce
    usable output by converting free_form_impacts to empty shocks.
    """
    branches = []
    for b in scenario_brief.get("branches", []):
        branches.append({
            "title": b.get("title", ""),
            "probability": b.get("probability", 0),
            "probability_reasoning": b.get("probability_reasoning", ""),
            "narrative": b.get("narrative", ""),
            "causal_chain": b.get("causal_chain", []),
            "structural_outcome": b.get("structural_outcome", ""),
            "specific_predictions": b.get("specific_predictions"),
            "time_horizon": b.get("time_horizon", "weeks"),
            "invalidation": b.get("invalidation"),
            "key_assumption": b.get("key_assumption"),
            "shocks": [],  # No node mapping available
            "node_suggestions": [],
            "edge_suggestions": [],
        })
    return {
        "research_summary": scenario_brief.get("research_summary", ""),
        "historical_parallels": scenario_brief.get("historical_parallels", ""),
        "branches": branches,
    }


# ── Tool execution ──────────────────────────────────────────────────────


async def _execute_scenario_tool(
    tool_name: str,
    tool_input: dict,
    session: AsyncSession,
    graph: nx.DiGraph,
) -> str:
    """Dispatch scenario tool calls to existing tool functions."""
    if tool_name == "search_news":
        return await search_news(
            query=tool_input["query"],
            max_results=tool_input.get("max_results", 10),
        )
    elif tool_name == "fetch_market_prices":
        return await fetch_market_prices(
            tickers=tool_input.get("tickers"),
        )
    elif tool_name == "validate_consistency":
        return await validate_consistency(
            node_ids=tool_input["node_ids"],
            session=session,
            graph=graph,
        )
    elif tool_name == "get_graph_topology":
        return _get_graph_topology(graph)
    elif tool_name == "fetch_historical_prices":
        from app.data_pipeline.market import fetch_historical_prices_summary
        ticker = tool_input.get("ticker", "")
        start_date = tool_input.get("start_date", "")
        end_date = tool_input.get("end_date", "")
        if not ticker or not start_date or not end_date:
            return json.dumps({"error": "ticker, start_date, and end_date are required"})
        try:
            result = await fetch_historical_prices_summary(ticker, start_date, end_date)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": f"Failed to fetch historical prices: {e}"})
    elif tool_name == "preview_propagation":
        return _preview_propagation(tool_input.get("shocks", []), graph)
    elif tool_name == "get_economic_calendar":
        from app.data_pipeline.calendar import get_economic_calendar
        days = min(tool_input.get("days_ahead", 30), 90)
        try:
            events = await get_economic_calendar(days)
            return json.dumps({"events": events, "count": len(events)})
        except Exception as e:
            return json.dumps({"error": f"Failed to fetch economic calendar: {e}"})
    elif tool_name == "fetch_options_summary":
        from app.data_pipeline.market import fetch_options_summary
        ticker = tool_input.get("ticker", "")
        if not ticker:
            return json.dumps({"error": "ticker is required"})
        try:
            result = await fetch_options_summary(ticker)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": f"Failed to fetch options summary: {e}"})
    elif tool_name in _SUBMIT_TOOLS:
        return json.dumps({"status": "accepted"})
    else:
        return json.dumps({"error": f"Unknown scenario tool: {tool_name}"})


def _preview_propagation(shocks: list[dict], graph: nx.DiGraph) -> str:
    """Preview cascade effects of proposed shocks through the graph.

    Uses the shared merge_multi_shock_impacts function with non-linear
    interaction model (stress multiplier + sigmoid compression).
    """
    from app.graph_engine.propagation import merge_multi_shock_impacts
    try:
        from app.graph_engine.regimes import detect_regime
        regime = detect_regime(graph)
        regime_val = regime.state.value
    except Exception:
        regime_val = None

    merged, stress_multiplier = merge_multi_shock_impacts(shocks, graph, regime_val)

    # Sort by magnitude, take top 15
    sorted_impacts = sorted(merged.items(), key=lambda x: abs(x[1]["total_impact"]), reverse=True)[:15]

    preview = []
    for nid, data in sorted_impacts:
        label = graph.nodes[nid].get("label", nid) if nid in graph else nid
        preview.append({
            "node_id": nid,
            "label": label,
            "impact": round(data["total_impact"], 4),
            "contributing_shocks": list(set(data["contributing_shocks"])),
            "hops": max(data["hops"], 1),
        })

    result: dict = {
        "preview": preview,
        "total_affected": len(merged),
        "showing_top": len(preview),
    }
    if stress_multiplier > 1.0:
        result["non_linear_note"] = (
            f"Stress multiplier: {stress_multiplier:.2f} applied "
            f"({len(shocks)} simultaneous shocks). "
            f"Sigmoid compression active for impacts >0.8."
        )

    return json.dumps(result)


def _get_graph_topology(graph: nx.DiGraph) -> str:
    """Return graph topology as JSON — nodes + edges, NO sentiments."""
    nodes = []
    for nid, data in graph.nodes(data=True):
        nodes.append({
            "id": nid,
            "label": data.get("label", nid),
            "node_type": data.get("node_type", "unknown"),
            "description": data.get("description", ""),
        })

    edges = []
    for src, tgt, edata in graph.edges(data=True):
        edges.append({
            "source": src,
            "target": tgt,
            "direction": edata.get("direction", "positive"),
            "base_weight": edata.get("base_weight", 0.3),
            "description": edata.get("description", ""),
        })

    return json.dumps({
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    })


# ── Prediction extraction & track record ──────────────────────────────

# Mapping of common terms to yfinance tickers for market prediction parsing
_MARKET_TERM_TICKERS: dict[str, str] = {
    "brent": "BZ=F", "brent crude": "BZ=F",
    "wti": "CL=F", "wti crude": "CL=F", "oil": "CL=F", "crude": "CL=F", "crude oil": "CL=F",
    "s&p": "^GSPC", "s&p 500": "^GSPC", "sp500": "^GSPC", "s&p500": "^GSPC",
    "spy": "SPY", "spx": "^GSPC",
    "nasdaq": "^IXIC", "qqq": "QQQ",
    "vix": "^VIX",
    "gold": "GC=F",
    "silver": "SI=F",
    "dxy": "DX-Y.NYB", "dollar index": "DX-Y.NYB", "usd index": "DX-Y.NYB",
    "10-year": "^TNX", "10y": "^TNX", "10-year yield": "^TNX", "10yr": "^TNX",
    "30-year": "^TYX", "30y": "^TYX", "30-year yield": "^TYX", "30yr": "^TYX",
    "2-year": "^TWO", "2y": "^TWO", "2-year yield": "^TWO",
    "natural gas": "NG=F",
    "copper": "HG=F",
    "euro": "EURUSD=X", "eurusd": "EURUSD=X",
    "yen": "USDJPY=X", "usdjpy": "USDJPY=X",
    "hyg": "HYG", "high yield": "HYG",
    "bitcoin": "BTC-USD", "btc": "BTC-USD",
}

# Normalize LLM-invented tickers to valid yfinance tickers
_TICKER_NORMALIZE: dict[str, str] = {
    "US10Y": "^TNX", "US 10Y": "^TNX", "US10YR": "^TNX",
    "US30Y": "^TYX", "US 30Y": "^TYX", "US30YR": "^TYX",
    "US2Y": "^TWO", "US 2Y": "^TWO", "US2YR": "^TWO",
    "XAUUSD": "GC=F", "XAU/USD": "GC=F", "XAU": "GC=F", "GOLD": "GC=F",
    "XAGUSD": "SI=F", "XAG/USD": "SI=F",
    "USOIL": "CL=F", "WTIUSD": "CL=F", "WTI": "CL=F",
    "BRENT": "BZ=F", "BRTUSD": "BZ=F",
    "DXY": "DX-Y.NYB",
    "SPX": "^GSPC", "ES": "^GSPC",
    "NDX": "^IXIC", "NQ": "^IXIC",
    "VIX": "^VIX",
    "MOVE": "^MOVE",
    "HYG": "HYG", "LQD": "LQD",
    "SPY": "SPY", "QQQ": "QQQ", "IWM": "IWM",
    "EURUSD": "EURUSD=X", "EUR/USD": "EURUSD=X",
    "USDJPY": "USDJPY=X", "USD/JPY": "USDJPY=X",
}


def _normalize_ticker(ticker: str) -> str:
    """Normalize LLM-output ticker to valid yfinance ticker."""
    if not ticker:
        return ticker
    # Try exact match first (case-insensitive)
    upper = ticker.upper().strip()
    if upper in _TICKER_NORMALIZE:
        return _TICKER_NORMALIZE[upper]
    # Already a valid yfinance ticker (has ^ or = or -)
    if any(c in ticker for c in "^=-"):
        return ticker
    return ticker


def _parse_time_window(text: str, base_time: datetime) -> datetime | None:
    """Parse a time_window string into an absolute expiry datetime.

    Uses the upper bound of ranges (e.g., "1-2 weeks" → 2 weeks).
    Returns None for unparseable strings.
    """
    if not text:
        return None

    text = text.lower().strip()

    # Hours: "24h", "48h", "24-72h", "24-72 hours"
    m = re.search(r"(\d+)\s*-\s*(\d+)\s*(?:h|hour)s?", text)
    if m:
        return base_time + timedelta(hours=int(m.group(2)))
    m = re.search(r"(\d+)\s*h(?:our)?s?", text)
    if m:
        return base_time + timedelta(hours=int(m.group(1)))

    # Days: "3 days", "3-5 days", "5 business days"
    m = re.search(r"(\d+)\s*-\s*(\d+)\s*(?:business\s+)?days?", text)
    if m:
        days = int(m.group(2))
        if "business" in text:
            days = int(days * 7 / 5)  # rough conversion
        return base_time + timedelta(days=days)
    m = re.search(r"(\d+)\s*(?:business\s+)?days?", text)
    if m:
        days = int(m.group(1))
        if "business" in text:
            days = int(days * 7 / 5)
        return base_time + timedelta(days=days)

    # Weeks: "1 week", "1-2 weeks"
    m = re.search(r"(\d+)\s*-\s*(\d+)\s*weeks?", text)
    if m:
        return base_time + timedelta(weeks=int(m.group(2)))
    m = re.search(r"(\d+)\s*weeks?", text)
    if m:
        return base_time + timedelta(weeks=int(m.group(1)))

    # Months: "1 month", "1-3 months"
    m = re.search(r"(\d+)\s*-\s*(\d+)\s*months?", text)
    if m:
        return base_time + timedelta(days=int(m.group(2)) * 30)
    m = re.search(r"(\d+)\s*months?", text)
    if m:
        return base_time + timedelta(days=int(m.group(1)) * 30)

    return None


def _parse_market_prediction(text: str) -> tuple[str | None, float | None, str | None]:
    """Extract ticker, threshold value, and direction from a prediction string.

    Returns (ticker, threshold, direction) or (None, None, None) if not market-related.
    """
    text_lower = text.lower()

    # Find direction keyword
    direction_match = re.search(r"\b(above|below|over|under|exceeds?|drops?\s+below|falls?\s+below|rises?\s+above|breaks?)\b", text_lower)
    if not direction_match:
        return None, None, None

    direction_word = direction_match.group(1)
    direction = "above" if direction_word in ("above", "over", "exceeds", "exceed", "rises above", "rise above", "breaks", "break") else "below"

    # Find threshold value — just find a number after the direction word
    after_direction = text_lower[direction_match.end():]
    value_match = re.search(r"\$?\s*([\d,]+(?:\.\d+)?)", after_direction)
    if not value_match:
        # Try before direction
        before_direction = text_lower[:direction_match.start()]
        value_match = re.search(r"\$?\s*([\d,]+(?:\.\d+)?)\s*$", before_direction)
        if not value_match:
            return None, None, None

    try:
        threshold = float(value_match.group(1).replace(",", ""))
    except ValueError:
        return None, None, None

    # Find matching ticker
    ticker = None
    for term, t in _MARKET_TERM_TICKERS.items():
        if term in text_lower:
            ticker = t
            break

    if not ticker:
        return None, None, None

    return ticker, threshold, direction


async def _extract_and_store_predictions(
    scenario_id: int, result: dict, session: AsyncSession
) -> int:
    """Extract predictions from scenario branches and store for resolution.

    Reads from `specific_predictions` per branch. Each prediction may have optional
    structured ticker/direction/threshold fields (from schema enforcement) or just
    free-text prediction text (falls back to regex parsing).
    """
    base_time = datetime.utcnow()
    count = 0

    for branch_idx, branch in enumerate(result.get("branches", [])):
        branch_title = branch.get("title", "")

        for pred in branch.get("specific_predictions") or []:
            pred_text = pred.get("prediction", "")
            if not pred_text:
                continue

            confidence = pred.get("confidence", 0.5)
            time_window = pred.get("time_window", "")

            # Prefer structured fields from schema, fall back to regex parsing
            ticker = pred.get("ticker") or None
            threshold_value = pred.get("threshold") or None
            threshold_direction = pred.get("direction") or None

            if not ticker:
                # Regex fallback for predictions without structured fields
                ticker, threshold_value, threshold_direction = _parse_market_prediction(pred_text)

            # Normalize LLM-invented tickers to valid yfinance tickers
            if ticker:
                ticker = _normalize_ticker(ticker)

            session.add(ScenarioPrediction(
                scenario_id=scenario_id,
                branch_idx=branch_idx,
                branch_title=branch_title,
                prediction_text=pred_text,
                confidence=confidence,
                time_window=time_window,
                expires_at=_parse_time_window(time_window, base_time),
                ticker=ticker,
                threshold_value=threshold_value,
                threshold_direction=threshold_direction,
            ))
            count += 1

    if count > 0:
        logger.info("[scenario] Extracted %d predictions from scenario %d", count, scenario_id)

    return count


async def _build_scenario_track_record(session: AsyncSession) -> str:
    """Build a track record summary from resolved scenario predictions.

    Returns empty string if no resolved predictions exist yet (skip gracefully).
    Uses a fresh session to avoid greenlet issues from the long-running agent session.
    """
    from sqlalchemy import select
    from app.db.connection import async_session as session_factory

    async with session_factory() as fresh_session:
        result = await fresh_session.execute(
            select(ScenarioPrediction).where(
                ScenarioPrediction.resolution_type == "market_resolved",
                ScenarioPrediction.hit.isnot(None),
            )
        )
        # Materialize all fields we need while session is open to avoid lazy-load greenlet errors
        resolved = [
            {
                "hit": r.hit,
                "confidence": r.confidence,
                "prediction_text": r.prediction_text,
                "actual_value": r.actual_value,
                "resolved_at": r.resolved_at,
            }
            for r in result.scalars().all()
        ]

    if not resolved:
        return ""

    total = len(resolved)
    hits = sum(1 for p in resolved if p["hit"] is True)
    hit_rate = hits / total if total > 0 else 0.0

    # Calibration by confidence bucket
    buckets: dict[str, list] = {"low (0-0.3)": [], "medium (0.3-0.6)": [], "high (0.6-1.0)": []}
    for p in resolved:
        if p["confidence"] < 0.3:
            buckets["low (0-0.3)"].append(p["hit"])
        elif p["confidence"] < 0.6:
            buckets["medium (0.3-0.6)"].append(p["hit"])
        else:
            buckets["high (0.6-1.0)"].append(p["hit"])

    parts = [
        "## Your Scenario Prediction Track Record",
        f"Total market-resolved predictions: {total}",
        f"Overall hit rate: {hit_rate:.0%} ({hits}/{total})",
        "",
        "### Calibration by confidence bucket:",
    ]

    for bucket_name, outcomes in buckets.items():
        if not outcomes:
            continue
        bucket_hits = sum(1 for o in outcomes if o is True)
        bucket_rate = bucket_hits / len(outcomes) if outcomes else 0.0
        avg_confidence_label = bucket_name.split("(")[1].rstrip(")")
        parts.append(f"- Confidence {bucket_name}: {bucket_rate:.0%} hit rate ({bucket_hits}/{len(outcomes)})")

        # Flag systematic bias
        # For "high" bucket, expected hit rate should be 60-100%
        if "high" in bucket_name and bucket_rate < 0.5 and len(outcomes) >= 3:
            parts.append(f"  ⚠ You're OVERCONFIDENT in high-confidence predictions — actual hit rate is {bucket_rate:.0%}")
        elif "low" in bucket_name and bucket_rate > 0.5 and len(outcomes) >= 3:
            parts.append(f"  ⚠ You're UNDERCONFIDENT in low-confidence predictions — actual hit rate is {bucket_rate:.0%}")

    # Last 5 resolved predictions
    recent = sorted(resolved, key=lambda p: p["resolved_at"] or datetime.min, reverse=True)[:5]
    if recent:
        parts.append("")
        parts.append("### Recent resolved predictions:")
        for p in recent:
            status = "HIT" if p["hit"] else "MISS"
            parts.append(f"- [{status}] \"{p['prediction_text'][:80]}\" (confidence: {p['confidence']:.0%}, actual: {p['actual_value']})")

    parts.append("")
    parts.append("Use this track record to calibrate your probability assignments and confidence levels. "
                 "If you've been overconfident, lower your confidence. If your tail risks never materialize, "
                 "consider whether your probabilities are too high for those branches.")

    return "\n".join(parts)


# ── Persistence ──────────────────────────────────────────────────────


async def _persist_scenario_details(
    scenario_id: int,
    result: dict,
    session: AsyncSession,
    graph: nx.DiGraph,
) -> None:
    """Save individual shocks and suggestions from the scenario result."""
    graph_node_ids = set(graph.nodes)
    branches = result.get("branches", [])

    for branch_idx, branch in enumerate(branches):
        for shock in branch.get("shocks", []):
            node_id = shock.get("node_id", "")
            if node_id not in graph_node_ids:
                logger.info("Skipping shock to non-existent node '%s' (branch %d)", node_id, branch_idx)
                continue
            shock_value = max(-1.0, min(1.0, shock.get("shock_value", 0.0)))
            session.add(ScenarioShock(
                scenario_id=scenario_id,
                branch_idx=branch_idx,
                node_id=node_id,
                shock_value=shock_value,
                reasoning=shock.get("reasoning", ""),
                original_impact=shock.get("original_impact", ""),
            ))

        for ns in branch.get("node_suggestions", []):
            session.add(NodeSuggestion(
                scenario_id=scenario_id,
                branch_idx=branch_idx,
                suggested_id=ns.get("suggested_id", ""),
                suggested_label=ns.get("suggested_label", ""),
                suggested_type=ns.get("suggested_type", "macro"),
                description=ns.get("description", ""),
                reasoning=ns.get("reasoning", ""),
            ))

        # Collect suggested node IDs from this branch so edge suggestions
        # can reference them (not just existing graph nodes).
        suggested_node_ids = {
            ns.get("suggested_id", "")
            for ns in branch.get("node_suggestions", [])
            if ns.get("suggested_id")
        }
        valid_node_ids = graph_node_ids | suggested_node_ids

        for es in branch.get("edge_suggestions", []):
            src = es.get("source_id", "")
            tgt = es.get("target_id", "")
            if src not in valid_node_ids or tgt not in valid_node_ids:
                logger.info("Skipping edge suggestion %s -> %s (node not in graph or suggestions)", src, tgt)
                continue
            # Only persist to DB if both endpoints are real graph nodes
            # (FK constraint on EdgeSuggestion). Edges referencing suggested
            # nodes are still preserved in scenarios_json for frontend display.
            if src not in graph_node_ids or tgt not in graph_node_ids:
                logger.info("Edge suggestion %s -> %s references suggested node — kept in JSON only", src, tgt)
                continue
            from app.models.observations import EdgeSuggestion
            session.add(EdgeSuggestion(
                source_id=src,
                target_id=tgt,
                suggested_direction=es.get("direction", "positive"),
                suggested_weight=0.3,
                llm_reasoning=es.get("reasoning", ""),
                status="pending",
            ))


# ── Broadcasting ──────────────────────────────────────────────────────


_broadcast_tasks: set[asyncio.Task] = set()


def _broadcast_done_callback(task: asyncio.Task) -> None:
    _broadcast_tasks.discard(task)
    if not task.cancelled() and task.exception():
        logger.debug("Scenario broadcast failed: %s", task.exception())


def _broadcast_scenario_progress(
    scenario_id: int,
    round_num: int,
    phase: str,
    tool_calls_log: list[dict],
) -> None:
    """Broadcast scenario progress via WebSocket."""
    try:
        from app.api.websocket import manager
        task = asyncio.create_task(manager.broadcast({
            "type": "scenario_progress",
            "data": {
                "scenario_id": scenario_id,
                "round": round_num + 1,
                "max_rounds": MAX_ROUNDS,
                "phase": phase,
                "total_tool_calls": len(tool_calls_log),
            },
        }))
        _broadcast_tasks.add(task)
        task.add_done_callback(_broadcast_done_callback)
    except Exception as e:
        logger.debug("Failed to broadcast scenario progress: %s", e)


def _broadcast_scenario_complete(scenario: Scenario) -> None:
    """Broadcast scenario completion via WebSocket."""
    try:
        from app.api.websocket import manager
        branches = []
        if scenario.scenarios_json and "branches" in scenario.scenarios_json:
            for b in scenario.scenarios_json["branches"]:
                branches.append({
                    "title": b.get("title", ""),
                    "probability": b.get("probability", 0),
                    "shock_count": len(b.get("shocks", [])),
                })

        task = asyncio.create_task(manager.broadcast({
            "type": "scenario_complete",
            "data": {
                "scenario_id": scenario.id,
                "status": scenario.status,
                "trigger": scenario.trigger,
                "branch_count": len(branches),
                "branches": branches,
                "error": scenario.error,
            },
        }))
        _broadcast_tasks.add(task)
        task.add_done_callback(_broadcast_done_callback)
    except Exception as e:
        logger.debug("Failed to broadcast scenario complete: %s", e)


# ── Quick triggers ────────────────────────────────────────────────────

# 12 domain-aligned queries covering the full macro-analyst spectrum.
# Includes domains beyond the graph (engine suggests new nodes for gaps).
_QUICK_TRIGGER_QUERIES = [
    "geopolitics conflict war sanctions military escalation",
    "central banks monetary policy rate decision FOMC ECB BOJ",
    "tariffs trade war supply chain reshoring sanctions",
    "AI disruption technology cyber attack outage systemic",
    "energy crisis oil gas climate transition renewable",
    "bank failure credit crisis contagion default bankruptcy",
    "pandemic outbreak virus health emergency supply chain",
    "labor shortage strike immigration wage automation",
    "government debt fiscal deficit downgrade sovereign crisis",
    "housing market mortgage commercial real estate crisis",
    "China economy emerging markets currency crisis capital flight",
    "food prices agriculture drought famine water crisis",
]


async def _auto_pick_trigger(graph: nx.DiGraph) -> str:
    """Auto-pick a scenario-worthy event from current news.

    Randomly selects from the LLM's top 5 triggers to ensure topic diversity
    across multiple auto-generated scenarios.
    """
    import random
    try:
        triggers = await generate_quick_triggers(graph)
        if triggers:
            pick = random.choice(triggers[:5])
            return pick.get("suggested_prompt", pick.get("headline", ""))
    except Exception as e:
        logger.warning("Auto-pick trigger failed: %s", e)
    return ""


async def _fetch_recent_trigger_topics() -> str:
    """Fetch recent scenario triggers to avoid topic repetition."""
    try:
        from app.db.connection import async_session as session_factory
        from sqlalchemy import select

        async with session_factory() as session:
            result = await session.execute(
                select(Scenario.trigger, Scenario.created_at)
                .where(Scenario.status.in_(["completed", "running"]))
                .order_by(Scenario.created_at.desc())
                .limit(5)
            )
            recent = result.all()
            if not recent:
                return ""

            lines = []
            for trigger, created_at in recent:
                date_str = created_at.strftime("%b %d") if created_at else "?"
                lines.append(f'- "{trigger[:80]}" ({date_str})')
            return "\n".join(lines)
    except Exception as e:
        logger.debug("Failed to fetch recent triggers (non-fatal): %s", e)
        return ""


async def generate_quick_triggers(graph: nx.DiGraph) -> list[dict]:
    """Scan current news across 12 domains and pick 5 scenario-worthy events.

    Uses diverse queries to avoid topic concentration, then lets the LLM
    rank by structural scenario potential with a diversity mandate.
    """
    try:
        # Fetch news from all 12 domain queries concurrently (3 articles each)
        fetch_tasks = [
            search_news(query=q, max_results=3)
            for q in _QUICK_TRIGGER_QUERIES
        ]
        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        # Collect and deduplicate articles
        seen_titles: set[str] = set()
        all_articles: list[dict] = []
        for r in results:
            if isinstance(r, Exception):
                continue
            try:
                data = json.loads(r) if isinstance(r, str) else r
                for a in data.get("articles", []):
                    title = a.get("title", "")
                    dedup_key = title[:50].lower().strip()
                    if dedup_key and dedup_key not in seen_titles:
                        seen_titles.add(dedup_key)
                        all_articles.append(a)
            except (json.JSONDecodeError, AttributeError):
                continue

        if not all_articles:
            return []

        headlines_text = "\n".join(
            f"- [{a.get('source', '?')}] {a.get('title', '')}"
            for a in all_articles[:40]  # Cap at 40 to stay within prompt limits
        )

        # Fetch recent topics to inject as avoidance list
        recent_topics = await _fetch_recent_trigger_topics()

        prompt_text = QUICK_TRIGGERS_PROMPT.format(
            headlines=headlines_text,
            recent_topics=recent_topics or "(none)",
        )

        logger.info("[quick_triggers] Calling simple_completion with %d headlines from %d domains",
                     min(len(all_articles), 40), len(_QUICK_TRIGGER_QUERIES))
        response_text = await simple_completion(
            system="You are a financial news analyst. Return ONLY valid JSON, no markdown.",
            user_message=prompt_text,
        )
        logger.info("[quick_triggers] LLM response (%d chars): %s", len(response_text), response_text[:300])

        response_text = response_text.strip()
        # Strip markdown code fences (Claude often wraps JSON in ```json...```)
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            start = 1
            end = len(lines) - 1 if lines[-1].strip().startswith("```") else len(lines)
            response_text = "\n".join(lines[start:end]).strip()
        # Also try extracting JSON array from surrounding text
        if not response_text.startswith("["):
            bracket_start = response_text.find("[")
            bracket_end = response_text.rfind("]")
            if bracket_start >= 0 and bracket_end > bracket_start:
                response_text = response_text[bracket_start:bracket_end + 1]

        triggers = json.loads(response_text)
        if not isinstance(triggers, list):
            return []

        return [
            {
                "headline": t.get("headline", "")[:80],
                "source": t.get("source", ""),
                "suggested_prompt": t.get("suggested_prompt", ""),
                "vulnerability": t.get("vulnerability", ""),
            }
            for t in triggers[:5]
            if isinstance(t, dict)
        ]
    except Exception as e:
        logger.exception("Quick trigger generation failed: %s", e)
        return []
