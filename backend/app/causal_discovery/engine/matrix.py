"""Daily matrix builder — pivots node_values rows into an aligned DataFrame."""
from __future__ import annotations

import logging
from typing import Any, Sequence

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def build_daily_matrix_from_rows(
    rows: Sequence[dict[str, Any]],
) -> pd.DataFrame:
    """Pivot a list of {node_id, day, value} dicts into a DataFrame.

    Returns a DataFrame with index=day (DatetimeIndex) and columns=node_id.
    """
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    pivoted = df.pivot(index="day", columns="node_id", values="value")
    pivoted.index.name = "day"
    pivoted.columns.name = None
    pivoted = pivoted.sort_index()
    return pivoted


def forward_fill_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Forward-fill NaN values in the matrix (for slow-updating series like CPI)."""
    return df.ffill()


# ---------------------------------------------------------------------------
# Async DB query — requires a running database session
# ---------------------------------------------------------------------------

_TIMESCALE_QUERY = """\
SELECT
    node_id,
    time_bucket('1 day', ts) AS day,
    last(value, ts) AS value
FROM node_values
WHERE ts >= now() - make_interval(days => :days)
{node_filter}
GROUP BY node_id, day
ORDER BY day, node_id
"""

_PLAIN_QUERY = """\
SELECT
    node_id,
    date_trunc('day', ts) AS day,
    value
FROM node_values
WHERE ts >= now() - make_interval(days => :days)
{node_filter}
ORDER BY day, node_id
"""


async def get_daily_matrix(
    session: AsyncSession,
    days: int = 252,
    node_ids: list[str] | None = None,
) -> pd.DataFrame:
    """Query node_values and return an aligned daily matrix.

    Tries TimescaleDB ``time_bucket`` + ``last()`` first, falls back to
    plain ``date_trunc`` if TimescaleDB extensions are not available.
    """
    node_filter = ""
    params: dict[str, Any] = {"days": days}
    if node_ids:
        node_filter = "AND node_id = ANY(:node_ids)"
        params["node_ids"] = node_ids

    for query_template in (_TIMESCALE_QUERY, _PLAIN_QUERY):
        try:
            query = query_template.format(node_filter=node_filter)
            result = await session.execute(text(query), params)
            raw_rows = result.mappings().all()
            rows = [{"node_id": r["node_id"], "day": r["day"], "value": r["value"]} for r in raw_rows]
            df = build_daily_matrix_from_rows(rows)
            df = forward_fill_matrix(df)
            logger.info("Built daily matrix: %d days × %d nodes", len(df), len(df.columns))
            return df
        except Exception:
            if query_template is _TIMESCALE_QUERY:
                logger.info("TimescaleDB functions unavailable, falling back to plain SQL")
                continue
            raise

    # Should not reach here, but return empty DataFrame as safeguard
    return pd.DataFrame()
