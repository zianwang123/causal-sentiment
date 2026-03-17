"""CSV/Excel download fetchers for alternative data sources.

These fetchers download spreadsheet files from public URLs and parse them
into row dicts suitable for the node_values table.  Each function returns
``[{node_id, ts, value, source}]`` and fails gracefully (log warning,
return empty list) so that one broken upstream never blocks the backfill.
"""
from __future__ import annotations

import io
import logging
from datetime import datetime, timezone

import httpx
import pandas as pd

logger = logging.getLogger(__name__)

# Browser-like headers to avoid 403 from sites that block default Python UA.
_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


# ---------------------------------------------------------------------------
# Shiller CAPE
# ---------------------------------------------------------------------------

async def fetch_shiller_cape(
    start_date: str = "2000-01-01",
) -> list[dict]:
    """Download Shiller's IE data Excel and extract the CAPE ratio.

    Source: http://www.econ.yale.edu/~shiller/data/ie_data.xls
    The "Data" sheet contains monthly rows with CAPE in the column
    typically labeled "CAPE" or located at a known column offset.

    Returns
    -------
    list[dict]
        Row dicts with keys ``node_id``, ``ts``, ``value``, ``source``.
    """
    url = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=_BROWSER_HEADERS)
            resp.raise_for_status()

        # Parse the "Data" sheet.  Shiller's layout has a header row around
        # row 7 (0-indexed), with columns: Date, P, D, E, CPI, ... CAPE.
        # Read with header=None and locate the CAPE column manually.
        xls = pd.read_excel(
            io.BytesIO(resp.content),
            sheet_name="Data",
            header=None,
            engine="xlrd",
        )

        # Find the header row — look for a cell containing "CAPE"
        cape_col = None
        header_row = None
        for idx, row in xls.iterrows():
            for col_idx, cell in enumerate(row):
                if isinstance(cell, str) and "CAPE" in cell.upper():
                    cape_col = col_idx
                    header_row = idx
                    break
            if cape_col is not None:
                break

        if cape_col is None or header_row is None:
            logger.warning("Shiller CAPE: could not locate CAPE column header")
            return []

        # The date is in column 0 as a fractional year (e.g. 2023.01)
        date_col = 0
        data = xls.iloc[header_row + 1:]

        cutoff = pd.Timestamp(start_date, tz=timezone.utc)
        rows: list[dict] = []

        for _, row in data.iterrows():
            try:
                date_val = float(row.iloc[date_col])
                cape_val = float(row.iloc[cape_col])
            except (ValueError, TypeError):
                continue

            # Convert fractional year to datetime
            year = int(date_val)
            month = round((date_val - year) * 100) or 1
            month = max(1, min(12, month))
            dt = datetime(year, month, 1, tzinfo=timezone.utc)

            if pd.Timestamp(dt) < cutoff:
                continue

            rows.append({
                "node_id": "pe_valuations",
                "ts": dt,
                "value": cape_val,
                "source": "shiller_cape",
            })

        logger.info("Shiller CAPE: %d rows fetched", len(rows))
        return rows

    except Exception as exc:
        logger.warning("Shiller CAPE fetch failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Geopolitical Risk Index (GPR)
# ---------------------------------------------------------------------------

async def fetch_gpr_index(
    start_date: str = "2000-01-01",
) -> list[dict]:
    """Download the daily Geopolitical Risk Index from Matteo Iacoviello.

    Source: https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls

    Returns
    -------
    list[dict]
        Row dicts with keys ``node_id``, ``ts``, ``value``, ``source``.
    """
    url = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=_BROWSER_HEADERS)
            resp.raise_for_status()

        df = pd.read_excel(io.BytesIO(resp.content), engine="xlrd")

        # The sheet typically has a "date" column and a "GPRD" or "GPR" column.
        # Normalize column names to lowercase for flexible matching.
        df.columns = [str(c).strip().lower() for c in df.columns]

        if df.empty:
            logger.warning("GPR data: downloaded file is empty")
            return None

        # Find date column
        date_col = None
        for c in df.columns:
            if "date" in c:
                date_col = c
                break
        if date_col is None:
            # Fall back to first column
            date_col = df.columns[0]

        # Find GPR value column — prefer "gprd" (daily), then "gpr"
        gpr_col = None
        for candidate in ["gprd", "gpr_daily", "gpr"]:
            if candidate in df.columns:
                gpr_col = candidate
                break
        if gpr_col is None:
            # Pick the first numeric column that isn't the date
            for c in df.columns:
                if c != date_col and pd.api.types.is_numeric_dtype(df[c]):
                    gpr_col = c
                    break
        if gpr_col is None:
            logger.warning("GPR Index: could not locate GPR value column")
            return []

        cutoff = pd.Timestamp(start_date, tz=timezone.utc)
        rows: list[dict] = []

        for _, row in df.iterrows():
            try:
                dt = pd.Timestamp(row[date_col])
                if dt.tzinfo is None:
                    dt = dt.tz_localize(timezone.utc)
                val = float(row[gpr_col])
            except (ValueError, TypeError):
                continue

            if dt < cutoff:
                continue

            rows.append({
                "node_id": "geopolitical_risk_index",
                "ts": dt.to_pydatetime(),
                "value": val,
                "source": "gpr_iacoviello",
            })

        logger.info("GPR Index: %d rows fetched", len(rows))
        return rows

    except Exception as exc:
        logger.warning("GPR Index fetch failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# CBOE Put/Call Ratio
# ---------------------------------------------------------------------------

async def fetch_cboe_put_call() -> list[dict]:
    """Fetch CBOE equity put/call ratio.

    The CBOE occasionally changes download URLs and formats.  This function
    tries the most commonly-available endpoint and returns an empty list on
    any failure so the rest of the backfill is not blocked.

    Returns
    -------
    list[dict]
        Row dicts with keys ``node_id``, ``ts``, ``value``, ``source``.
    """
    # CBOE provides put/call ratio data. Try multiple known URLs since they
    # change periodically. The totalpc.csv endpoint is the most stable.
    urls = [
        "https://cdn.cboe.com/api/global/us_options/market_statistics/daily/totalpc.csv",
        "https://www.cboe.com/us/options/market_statistics/daily/totalpc.csv",
    ]
    try:
        resp = None
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for url in urls:
                try:
                    resp = await client.get(url, headers=_BROWSER_HEADERS)
                    resp.raise_for_status()
                    break
                except httpx.HTTPError:
                    continue
        if resp is None or resp.status_code != 200:
            logger.warning("CBOE put/call: all URLs failed")
            return []

        # Try to parse as CSV
        df = pd.read_csv(io.StringIO(resp.text))
        df.columns = [str(c).strip().lower() for c in df.columns]

        if df.empty:
            logger.warning("Put/Call data: downloaded file is empty")
            return None

        # Look for date and put/call columns
        date_col = None
        for c in df.columns:
            if "date" in c:
                date_col = c
                break
        if date_col is None:
            date_col = df.columns[0]

        pc_col = None
        for candidate in ["p/c ratio", "put/call", "put_call", "total p/c ratio",
                          "equity p/c ratio", "ratio"]:
            for c in df.columns:
                if candidate in c:
                    pc_col = c
                    break
            if pc_col is not None:
                break

        if pc_col is None:
            logger.warning("CBOE put/call: could not locate ratio column")
            return []

        rows: list[dict] = []
        for _, row in df.iterrows():
            try:
                dt = pd.Timestamp(row[date_col])
                if dt.tzinfo is None:
                    dt = dt.tz_localize(timezone.utc)
                val = float(row[pc_col])
            except (ValueError, TypeError):
                continue
            rows.append({
                "node_id": "put_call_ratio",
                "ts": dt.to_pydatetime(),
                "value": val,
                "source": "cboe",
            })

        logger.info("CBOE put/call: %d rows fetched", len(rows))
        return rows

    except Exception as exc:
        logger.warning("CBOE put/call fetch failed (URL may have changed): %s", exc)
        return []


# ---------------------------------------------------------------------------
# AAII Investor Sentiment
# ---------------------------------------------------------------------------

async def fetch_aaii_sentiment() -> list[dict]:
    """Fetch AAII investor sentiment survey data.

    AAII provides a weekly survey of individual investor sentiment (bullish,
    bearish, neutral percentages).  The public Excel download may require AAII
    membership; this function fails gracefully if it cannot be downloaded.

    We compute the bull-bear spread (bullish% - bearish%) as the sentiment
    signal.

    Returns
    -------
    list[dict]
        Row dicts with keys ``node_id``, ``ts``, ``value``, ``source``.
    """
    url = "https://www.aaii.com/files/surveys/sentiment.xls"
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=_BROWSER_HEADERS)
            resp.raise_for_status()

        df = pd.read_excel(io.BytesIO(resp.content), engine="xlrd")
        df.columns = [str(c).strip().lower() for c in df.columns]

        if df.empty:
            logger.warning("AAII sentiment data: downloaded file is empty")
            return None

        # Find date column
        date_col = None
        for c in df.columns:
            if "date" in c:
                date_col = c
                break
        if date_col is None:
            date_col = df.columns[0]

        # Find bullish and bearish columns
        bull_col = None
        bear_col = None
        for c in df.columns:
            c_lower = c.lower()
            if "bull" in c_lower and bull_col is None:
                bull_col = c
            if "bear" in c_lower and bear_col is None:
                bear_col = c

        if bull_col is None or bear_col is None:
            logger.warning(
                "AAII sentiment: could not locate bullish/bearish columns "
                "(found columns: %s)", list(df.columns),
            )
            return []

        rows: list[dict] = []
        for _, row in df.iterrows():
            try:
                dt = pd.Timestamp(row[date_col])
                if dt.tzinfo is None:
                    dt = dt.tz_localize(timezone.utc)
                bull = float(row[bull_col])
                bear = float(row[bear_col])
                spread = bull - bear  # bull-bear spread
            except (ValueError, TypeError):
                continue

            rows.append({
                "node_id": "retail_sentiment",
                "ts": dt.to_pydatetime(),
                "value": spread,
                "source": "aaii",
            })

        logger.info("AAII sentiment: %d rows fetched", len(rows))
        return rows

    except Exception as exc:
        logger.warning("AAII sentiment fetch failed (may require membership): %s", exc)
        return []
