"""REST API fetchers for alternative data sources.

These fetchers call public JSON APIs and return row dicts suitable for the
node_values table.  Each function returns ``[{node_id, ts, value, source}]``
and fails gracefully (log warning, return empty list) so that one broken
upstream never blocks the backfill.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import httpx

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CFTC Commitments of Traders
# ---------------------------------------------------------------------------

async def fetch_cftc_cot(
    start_date: str = "2020-01-01",
) -> list[dict]:
    """Fetch CFTC Commitments of Traders data from the Socrata API.

    Uses the public CFTC reporting endpoint (no API key required, though
    rate-limited).  Fetches S&P 500 futures positioning and computes
    net speculative = noncommercial long - noncommercial short.

    Source: https://publicreporting.cftc.gov/resource/6dca-aqww.json

    Parameters
    ----------
    start_date : str
        ISO date string — only rows on or after this date are returned.

    Returns
    -------
    list[dict]
        Row dicts with keys ``node_id``, ``ts``, ``value``, ``source``.
    """
    url = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

    # Socrata SoQL query: filter by date and S&P 500 contract
    params = {
        "$where": (
            f"report_date_as_yyyy_mm_dd >= '{start_date}' "
            "AND contract_market_name LIKE '%S&P 500%'"
        ),
        "$order": "report_date_as_yyyy_mm_dd ASC",
        "$limit": 5000,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        rows: list[dict] = []
        for record in data:
            try:
                date_str = record.get("report_date_as_yyyy_mm_dd", "")
                # Parse the date (may include a time component)
                dt = datetime.fromisoformat(
                    date_str.replace("T00:00:00.000", ""),
                ).replace(tzinfo=timezone.utc)

                long_val = float(record.get("ncomm_positions_long_all", 0))
                short_val = float(record.get("ncomm_positions_short_all", 0))
                net_spec = long_val - short_val
            except (ValueError, TypeError, KeyError):
                continue

            rows.append({
                "node_id": "institutional_positioning",
                "ts": dt,
                "value": net_spec,
                "source": "cftc_cot",
            })

        logger.info("CFTC COT: %d rows fetched", len(rows))
        return rows

    except Exception as exc:
        logger.warning("CFTC COT fetch failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# GDELT Global Knowledge Graph — tone analysis
# ---------------------------------------------------------------------------

async def fetch_gdelt_tone(days: int = 365) -> list[dict]:
    """Fetch geopolitical and sanctions risk tone from the GDELT GKG API.

    Makes two queries:
      1. "geopolitical risk conflict military" → node_id="geopolitical_risk"
      2. "sanctions embargo trade restrictions" → node_id="sanctions_risk"

    The GDELT Doc API returns a timeline of average tone values which serve
    as a proxy for global risk sentiment.

    Parameters
    ----------
    days : int
        Number of days of history to request (max ~365 depending on GDELT).

    Returns
    -------
    list[dict]
        Row dicts with keys ``node_id``, ``ts``, ``value``, ``source``.
    """
    base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
    start_date = datetime.now(tz=timezone.utc) - timedelta(days=days)
    start_str = start_date.strftime("%Y%m%d%H%M%S")

    queries = [
        ("geopolitical risk conflict military", "geopolitical_risk"),
        ("sanctions embargo trade restrictions", "sanctions_risk"),
    ]

    all_rows: list[dict] = []
    import asyncio

    for i, (query_text, node_id) in enumerate(queries):
        # Rate-limit: GDELT aggressively 429s back-to-back requests
        if i > 0:
            await asyncio.sleep(3)
        params = {
            "query": query_text,
            "mode": "timelinetone",
            "format": "json",
            "startdatetime": start_str,
            "TIMELINESMOOTH": 5,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(base_url, params=params)
                resp.raise_for_status()
                data = resp.json()

            # The timeline response has a "timeline" array, each entry with
            # "date" and "value" (or similar structure depending on mode).
            timeline = data.get("timeline", [])

            # timelinetone returns [{series, data: [{date, value}]}]
            for series_block in timeline:
                series_data = series_block.get("data", [])
                for point in series_data:
                    try:
                        date_str = str(point.get("date", ""))
                        # GDELT dates are YYYYMMDDHHMMSS format
                        if len(date_str) >= 8:
                            dt = datetime.strptime(
                                date_str[:8], "%Y%m%d",
                            ).replace(tzinfo=timezone.utc)
                        else:
                            continue
                        val = float(point.get("value", 0))
                    except (ValueError, TypeError):
                        continue

                    all_rows.append({
                        "node_id": node_id,
                        "ts": dt,
                        "value": val,
                        "source": "gdelt",
                    })

            logger.info("GDELT %s: %d rows fetched", node_id,
                        sum(1 for r in all_rows if r["node_id"] == node_id))

        except Exception as exc:
            logger.warning("GDELT %s fetch failed: %s", node_id, exc)

    return all_rows
