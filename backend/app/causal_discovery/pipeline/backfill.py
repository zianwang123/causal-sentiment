"""Backfill pipeline — bulk-load historical data into the node_values table.

Converts yfinance DataFrames and FRED observation tuples into row dicts
suitable for bulk INSERT, and provides an async ``run_backfill`` entrypoint
that orchestrates fetching + upserting.
"""
from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pandas as pd
from sqlalchemy import text

from app.causal_discovery.pipeline.fetchers import (
    fetch_fred_series_history,
    fetch_yfinance_history,
)
from app.causal_discovery.pipeline.fetchers_api import (
    fetch_cftc_cot,
    fetch_gdelt_tone,
)
from app.causal_discovery.pipeline.fetchers_csv import (
    fetch_aaii_sentiment,
    fetch_cboe_put_call,
    fetch_gpr_index,
    fetch_shiller_cape,
)
from app.causal_discovery.pipeline.sources import FRED_SOURCES, YFINANCE_SOURCES

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


# ---------------------------------------------------------------------------
# Row converters
# ---------------------------------------------------------------------------

def yfinance_df_to_node_value_rows(
    df: pd.DataFrame,
    ticker_to_node: dict[str, str],
) -> list[dict]:
    """Convert a yfinance Close-price DataFrame to a flat list of row dicts.

    Parameters
    ----------
    df : pd.DataFrame
        Columns = ticker symbols, index = DatetimeIndex, values = Close prices.
    ticker_to_node : dict[str, str]
        Mapping from ticker symbol to graph node_id (e.g. ``{"SPY": "sp500"}``).

    Returns
    -------
    list[dict]
        Each dict has keys ``node_id``, ``ts``, ``value``, ``source``.
        Rows with NaN values are skipped.
    """
    rows: list[dict] = []
    for ticker, node_id in ticker_to_node.items():
        if ticker not in df.columns:
            continue
        series = df[ticker]
        for ts, value in series.items():
            if math.isnan(value):
                continue
            # Ensure the timestamp is a UTC-aware datetime
            if isinstance(ts, pd.Timestamp):
                dt = ts.to_pydatetime()
            else:
                dt = pd.Timestamp(ts).to_pydatetime()
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            rows.append({
                "node_id": node_id,
                "ts": dt,
                "value": float(value),
                "source": "yfinance",
            })
    return rows


def fred_series_to_node_value_rows(
    node_id: str,
    observations: list[tuple[str, float]],
) -> list[dict]:
    """Convert FRED (date_str, value) tuples to row dicts.

    Parameters
    ----------
    node_id : str
        The graph node ID this series maps to.
    observations : list[tuple[str, float]]
        Parsed FRED observations as ``(date_string, numeric_value)`` pairs.

    Returns
    -------
    list[dict]
        Each dict has keys ``node_id``, ``ts``, ``value``, ``source``.
    """
    rows: list[dict] = []
    for date_str, value in observations:
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        rows.append({
            "node_id": node_id,
            "ts": dt,
            "value": float(value),
            "source": "fred",
        })
    return rows


# ---------------------------------------------------------------------------
# Bulk upsert helper
# ---------------------------------------------------------------------------

async def _bulk_upsert(session: AsyncSession, rows: list[dict]) -> int:
    """INSERT rows into node_values with ON CONFLICT DO UPDATE, in batches.

    Returns the total number of rows upserted.
    """
    if not rows:
        return 0

    # Deduplicate: keep last value per (node_id, ts) — PostgreSQL ON CONFLICT
    # cannot handle duplicate keys within the same INSERT statement
    seen: dict[tuple, dict] = {}
    for row in rows:
        key = (row["node_id"], str(row["ts"]))
        seen[key] = row  # last wins
    rows = list(seen.values())
    logger.info("Deduped to %d unique (node_id, ts) rows", len(rows))

    upserted = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        # Build a multi-row VALUES clause with bind parameters
        value_clauses = []
        params: dict = {}
        for j, row in enumerate(batch):
            value_clauses.append(
                f"(:node_id_{j}, :ts_{j}, :value_{j}, :source_{j})"
            )
            params[f"node_id_{j}"] = row["node_id"]
            params[f"ts_{j}"] = row["ts"]
            params[f"value_{j}"] = row["value"]
            params[f"source_{j}"] = row["source"]

        sql = text(
            "INSERT INTO node_values (node_id, ts, value, source) VALUES "
            + ", ".join(value_clauses)
            + " ON CONFLICT (node_id, ts) DO UPDATE SET "
            "value = EXCLUDED.value, source = EXCLUDED.source"
        )
        await session.execute(sql, params)
        upserted += len(batch)

    await session.commit()
    return upserted


# ---------------------------------------------------------------------------
# Main backfill entrypoint
# ---------------------------------------------------------------------------

async def run_backfill(
    session: AsyncSession,
    yfinance_period: str = "5y",
    fred_start: str = "2020-01-01",
) -> dict:
    """Fetch all registered data sources and bulk-upsert into node_values.

    Parameters
    ----------
    session : AsyncSession
        SQLAlchemy async session for DB writes.
    yfinance_period : str
        yfinance period string (e.g. ``"5y"``, ``"1mo"``).
    fred_start : str
        ISO date for FRED observation start.

    Returns
    -------
    dict
        Summary with keys ``yfinance_rows``, ``fred_rows``, ``total_upserted``,
        ``errors``.
    """
    errors: list[str] = []
    all_rows: list[dict] = []

    # --- yfinance -----------------------------------------------------------
    ticker_to_node = {s["ticker"]: s["node_id"] for s in YFINANCE_SOURCES}
    tickers = list(ticker_to_node.keys())

    try:
        yf_df = await fetch_yfinance_history(tickers, period=yfinance_period)
        yf_rows = yfinance_df_to_node_value_rows(yf_df, ticker_to_node)
        all_rows.extend(yf_rows)
        logger.info("yfinance: %d rows from %d tickers", len(yf_rows), len(tickers))
    except Exception as exc:
        msg = f"yfinance fetch failed: {exc}"
        logger.error(msg)
        errors.append(msg)
        yf_rows = []

    # --- FRED ---------------------------------------------------------------
    fred_rows: list[dict] = []
    for src in FRED_SOURCES:
        try:
            observations = await fetch_fred_series_history(
                src["series_id"], observation_start=fred_start,
            )
            rows = fred_series_to_node_value_rows(src["node_id"], observations)
            fred_rows.extend(rows)
            logger.info(
                "FRED %s (%s): %d observations",
                src["series_id"], src["node_id"], len(rows),
            )
        except Exception as exc:
            msg = f"FRED {src['series_id']} failed: {exc}"
            logger.error(msg)
            errors.append(msg)

    all_rows.extend(fred_rows)

    # --- CSV download sources -----------------------------------------------
    csv_rows: list[dict] = []

    csv_fetchers = [
        ("Shiller CAPE", fetch_shiller_cape, {"start_date": fred_start}),
        ("GPR Index", fetch_gpr_index, {"start_date": fred_start}),
        ("CBOE put/call", fetch_cboe_put_call, {}),
        ("AAII sentiment", fetch_aaii_sentiment, {}),
    ]
    for label, fetcher, kwargs in csv_fetchers:
        try:
            rows = await fetcher(**kwargs)
            csv_rows.extend(rows)
            logger.info("%s: %d rows", label, len(rows))
        except Exception as exc:
            msg = f"{label} fetch failed: {exc}"
            logger.error(msg)
            errors.append(msg)

    all_rows.extend(csv_rows)

    # --- REST API sources ---------------------------------------------------
    api_rows: list[dict] = []

    api_fetchers = [
        ("CFTC COT", fetch_cftc_cot, {"start_date": fred_start}),
        ("GDELT tone", fetch_gdelt_tone, {}),
    ]
    for label, fetcher, kwargs in api_fetchers:
        try:
            rows = await fetcher(**kwargs)
            api_rows.extend(rows)
            logger.info("%s: %d rows", label, len(rows))
        except Exception as exc:
            msg = f"{label} fetch failed: {exc}"
            logger.error(msg)
            errors.append(msg)

    all_rows.extend(api_rows)

    # --- Bulk upsert --------------------------------------------------------
    total_upserted = 0
    if all_rows:
        try:
            total_upserted = await _bulk_upsert(session, all_rows)
            logger.info("Backfill complete: %d rows upserted", total_upserted)
        except Exception as exc:
            msg = f"Bulk upsert failed: {exc}"
            logger.error(msg)
            errors.append(msg)

    return {
        "yfinance_rows": len(yf_rows),
        "fred_rows": len(fred_rows),
        "csv_rows": len(csv_rows),
        "api_rows": len(api_rows),
        "total_upserted": total_upserted,
        "errors": errors,
    }
