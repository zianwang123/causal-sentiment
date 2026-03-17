"""Market regime detection — risk-on / risk-off classification."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum

import networkx as nx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class RegimeState(str, Enum):
    RISK_ON = "risk_on"
    RISK_OFF = "risk_off"
    TRANSITIONING = "transitioning"


@dataclass
class RegimeResult:
    state: RegimeState
    confidence: float
    composite_score: float
    contributing_signals: dict[str, float]


# Bellwether nodes and their weights for regime detection.
# Negative weight means the node's sentiment is inverted for risk-on scoring
# (e.g., high VIX sentiment = bearish = risk-off, so weight is negative).
REGIME_INDICATORS: dict[str, float] = {
    "vix": -0.25,               # High VIX = risk-off
    "hy_credit_spread": -0.15,  # Widening spreads = risk-off
    "yield_curve_spread": 0.10, # Steepening = risk-on (generally)
    "sp500": 0.20,              # Rising equities = risk-on
    "gold": -0.10,              # Rising gold = flight to safety = risk-off
    "dxy_index": -0.05,         # Strong dollar = risk-off (capital flight to USD)
    "ig_credit_spread": -0.10,  # Widening IG spreads = risk-off
    "put_call_ratio": -0.05,    # High put/call = risk-off
}


def detect_regime(graph: nx.DiGraph) -> RegimeResult:
    """Classify current market regime from bellwether node sentiments."""
    contributing: dict[str, float] = {}
    composite = 0.0
    total_weight = 0.0

    for node_id, weight in REGIME_INDICATORS.items():
        if node_id not in graph:
            continue
        sentiment = graph.nodes[node_id].get("composite_sentiment", 0.0) or 0.0
        contribution = sentiment * weight
        composite += contribution
        total_weight += abs(weight)
        contributing[node_id] = round(sentiment, 4)

    # Normalize by total weight
    if total_weight > 0:
        composite /= total_weight

    # Classify
    if composite > 0.2:
        state = RegimeState.RISK_ON
    elif composite < -0.2:
        state = RegimeState.RISK_OFF
    else:
        state = RegimeState.TRANSITIONING

    # Confidence: how far from the thresholds (scaled 0-1)
    confidence = min(1.0, abs(composite) / 0.5)

    return RegimeResult(
        state=state,
        confidence=round(confidence, 3),
        composite_score=round(composite, 4),
        contributing_signals=contributing,
    )


async def get_regime_history(
    session: AsyncSession,
    days: int = 30,
) -> list[dict]:
    """Get regime history from DB."""
    from app.models.observations import RegimeSnapshot

    cutoff = datetime.now(UTC) - timedelta(days=days)
    result = await session.execute(
        select(RegimeSnapshot)
        .where(RegimeSnapshot.detected_at >= cutoff)
        .order_by(RegimeSnapshot.detected_at.asc())
    )
    snapshots = result.scalars().all()
    return [
        {
            "state": s.state,
            "confidence": s.confidence,
            "composite_score": s.composite_score,
            "contributing_signals": s.contributing_signals,
            "detected_at": s.detected_at.isoformat() if s.detected_at else None,
        }
        for s in snapshots
    ]
