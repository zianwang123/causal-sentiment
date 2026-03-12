"""LLM-assisted topology learning — suggest new causal edges from empirical correlations."""

from __future__ import annotations

import json
import logging
from datetime import datetime

import numpy as np
import networkx as nx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.graph_engine.correlations import _get_node_timeseries, _align_timeseries, _pearson_correlation
from app.models.graph import Node
from app.models.observations import EdgeSuggestion

logger = logging.getLogger(__name__)


async def find_correlated_unconnected_pairs(
    session: AsyncSession,
    graph: nx.DiGraph,
    lookback_days: int = 90,
    min_correlation: float = 0.5,
    max_results: int = 10,
) -> list[dict]:
    """Find node pairs with high correlation but no existing edge."""
    nodes_result = await session.execute(select(Node))
    nodes = nodes_result.scalars().all()
    node_ids = [n.id for n in nodes]

    # Fetch all time series
    ts_cache: dict[str, list] = {}
    for nid in node_ids:
        ts_cache[nid] = await _get_node_timeseries(session, nid, lookback_days)

    candidates: list[dict] = []

    for i, nid_a in enumerate(node_ids):
        for nid_b in node_ids[i + 1:]:
            # Skip if edge already exists (either direction)
            if graph.has_edge(nid_a, nid_b) or graph.has_edge(nid_b, nid_a):
                continue

            ts_a = ts_cache.get(nid_a, [])
            ts_b = ts_cache.get(nid_b, [])

            if len(ts_a) < 5 or len(ts_b) < 5:
                continue

            aligned_a, aligned_b = _align_timeseries(ts_a, ts_b)
            corr = _pearson_correlation(aligned_a, aligned_b)

            if corr is not None and abs(corr) >= min_correlation:
                candidates.append({
                    "source_id": nid_a,
                    "target_id": nid_b,
                    "correlation": round(corr, 4),
                    "n_datapoints": len(aligned_a),
                })

    # Sort by absolute correlation descending
    candidates.sort(key=lambda c: abs(c["correlation"]), reverse=True)
    return candidates[:max_results]


async def suggest_edges_with_llm(
    session: AsyncSession,
    graph: nx.DiGraph,
) -> list[EdgeSuggestion]:
    """Use Claude to evaluate correlated but unconnected node pairs and suggest causal edges."""
    candidates = await find_correlated_unconnected_pairs(session, graph)

    if not candidates:
        logger.info("No correlated unconnected pairs found for topology learning")
        return []

    provider = settings.llm_provider
    if provider == "openai" and not settings.openai_api_key:
        logger.warning("Cannot run topology learning without OPENAI_API_KEY")
        return []
    if provider == "anthropic" and not settings.anthropic_api_key:
        logger.warning("Cannot run topology learning without ANTHROPIC_API_KEY")
        return []

    # Get node labels for context
    nodes_result = await session.execute(select(Node))
    nodes = {n.id: n.label for n in nodes_result.scalars().all()}

    # Build prompt
    pairs_text = "\n".join(
        f"- {nodes.get(c['source_id'], c['source_id'])} ({c['source_id']}) <-> "
        f"{nodes.get(c['target_id'], c['target_id'])} ({c['target_id']}): "
        f"r={c['correlation']:+.3f} ({c['n_datapoints']} data points)"
        for c in candidates
    )

    prompt = f"""You are a macro finance expert analyzing a causal factor graph. The following node pairs show statistically significant correlation but have no existing causal edge in the graph.

For each pair, assess:
1. Is there a plausible causal relationship? (not just spurious correlation)
2. What is the likely direction of causation? (which node causes which)
3. What type of relationship? (positive, negative, or complex)
4. How strong should the edge weight be? (0.1 to 0.8)

Correlated pairs without edges:
{pairs_text}

Respond with a JSON array. For pairs with NO plausible causal link, omit them. For plausible causal edges, include:
```json
[
  {{
    "source_id": "causing_node_id",
    "target_id": "affected_node_id",
    "direction": "positive|negative|complex",
    "weight": 0.3,
    "reasoning": "Brief explanation of causal mechanism"
  }}
]
```

Only suggest edges where you are confident in the causal mechanism. Quality over quantity."""

    from app.agent.llm_client import simple_completion

    try:
        response_text = await simple_completion(
            system="You are a macro finance expert. Respond with valid JSON only.",
            user_message=prompt,
        )

        # Extract JSON from response
        start = response_text.find("[")
        end = response_text.rfind("]") + 1
        if start < 0 or end <= 0:
            logger.warning("No JSON array found in topology learning response")
            return []

        suggestions_raw = json.loads(response_text[start:end])
    except Exception as e:
        logger.exception("Topology learning LLM call failed: %s", e)
        return []

    # Create EdgeSuggestion records
    # Build correlation lookup
    corr_lookup = {(c["source_id"], c["target_id"]): c["correlation"] for c in candidates}
    corr_lookup.update({(c["target_id"], c["source_id"]): c["correlation"] for c in candidates})

    suggestions: list[EdgeSuggestion] = []
    for s in suggestions_raw:
        source_id = s.get("source_id", "")
        target_id = s.get("target_id", "")

        # Validate node IDs exist
        if source_id not in nodes or target_id not in nodes:
            continue

        # Check for existing pending suggestion
        existing = await session.execute(
            select(EdgeSuggestion)
            .where(EdgeSuggestion.source_id == source_id)
            .where(EdgeSuggestion.target_id == target_id)
            .where(EdgeSuggestion.status == "pending")
        )
        if existing.scalar_one_or_none():
            continue

        suggestion = EdgeSuggestion(
            source_id=source_id,
            target_id=target_id,
            suggested_direction=s.get("direction", "positive"),
            suggested_weight=min(1.0, max(0.1, s.get("weight", 0.3))),
            correlation=corr_lookup.get((source_id, target_id)),
            llm_reasoning=s.get("reasoning", ""),
            status="pending",
        )
        session.add(suggestion)
        suggestions.append(suggestion)

    await session.commit()
    logger.info("Topology learning created %d edge suggestions", len(suggestions))
    return suggestions
