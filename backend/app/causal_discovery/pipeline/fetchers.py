"""Bulk history fetchers for yfinance and FRED data sources.

These fetchers retrieve multi-year daily price/value histories that feed into
the causal discovery pipeline's matrix builder and statistical tests.
"""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import httpx
import pandas as pd
import yfinance as yf

from app.config import settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# yfinance
# ---------------------------------------------------------------------------

# Rate-limit settings to avoid Yahoo Finance 429 errors.
# Yahoo blocks IPs that send too many requests in a short window.
# Downloading one ticker at a time with delays is more reliable than bulk.
_YF_DELAY_BETWEEN_TICKERS: float = 2.0   # seconds between individual downloads
_YF_BATCH_SIZE: int = 5                    # pause longer every N tickers
_YF_BATCH_PAUSE: float = 10.0             # seconds to pause between batches
_YF_MAX_RETRIES: int = 3                   # retries per ticker on failure
_YF_RETRY_BACKOFF_BASE: float = 5.0       # exponential backoff base (5s, 10s, 20s)


def _yfinance_download_single(ticker: str, period: str = "5y") -> pd.Series | None:
    """Download close prices for a single ticker. Returns None on failure."""
    try:
        raw = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        if raw.empty:
            return None
        if isinstance(raw.columns, pd.MultiIndex):
            series = raw["Close"].iloc[:, 0]
        else:
            series = raw["Close"]
        series.name = ticker
        return series
    except Exception as e:
        logger.warning("yfinance download failed for %s: %s", ticker, e)
        return None


def _yfinance_download_sync(
    tickers: list[str],
    period: str = "5y",
) -> pd.DataFrame:
    """Download close prices for multiple tickers sequentially with rate-limit handling.

    Downloads one ticker at a time with delays to avoid Yahoo Finance 429 errors.
    Retries failed tickers with exponential backoff.
    """
    import time

    results: dict[str, pd.Series] = {}
    failed: list[str] = []

    for i, ticker in enumerate(tickers):
        # Batch pause: longer delay every N tickers
        if i > 0 and i % _YF_BATCH_SIZE == 0:
            logger.info("yfinance batch pause (%d/%d tickers done, waiting %.0fs)",
                        i, len(tickers), _YF_BATCH_PAUSE)
            time.sleep(_YF_BATCH_PAUSE)
        elif i > 0:
            time.sleep(_YF_DELAY_BETWEEN_TICKERS)

        series = _yfinance_download_single(ticker, period)
        if series is not None and not series.empty:
            results[ticker] = series
            logger.info("yfinance %s: %d rows", ticker, len(series))
        else:
            failed.append(ticker)
            logger.warning("yfinance %s: failed (will retry)", ticker)

    # Retry failed tickers with exponential backoff
    for retry in range(_YF_MAX_RETRIES):
        if not failed:
            break
        wait = _YF_RETRY_BACKOFF_BASE * (2 ** retry)
        logger.info("yfinance retry %d/%d: waiting %.0fs then retrying %d tickers",
                     retry + 1, _YF_MAX_RETRIES, wait, len(failed))
        time.sleep(wait)

        still_failed = []
        for ticker in failed:
            time.sleep(_YF_DELAY_BETWEEN_TICKERS)
            series = _yfinance_download_single(ticker, period)
            if series is not None and not series.empty:
                results[ticker] = series
                logger.info("yfinance %s: %d rows (retry %d)", ticker, len(series), retry + 1)
            else:
                still_failed.append(ticker)
        failed = still_failed

    if failed:
        logger.warning("yfinance: %d tickers failed via yfinance library, trying direct Yahoo API fallback: %s",
                        len(failed), failed)
        # Fallback: fetch failed tickers directly from Yahoo Finance API with browser headers
        for ticker in list(failed):
            time.sleep(_YF_DELAY_BETWEEN_TICKERS)
            series = _yahoo_direct_download_single(ticker, period)
            if series is not None and not series.empty:
                results[ticker] = series
                failed.remove(ticker)
                logger.info("yahoo direct %s: %d rows (fallback)", ticker, len(series))

    if failed:
        logger.error("yfinance: %d tickers permanently failed (both yfinance and direct): %s", len(failed), failed)

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df.columns = [str(c) for c in df.columns]
    return df


# ---------------------------------------------------------------------------
# Yahoo Finance direct API fallback
# ---------------------------------------------------------------------------

# When yfinance gets rate-limited (429), Yahoo blocks the default Python User-Agent.
# Fetching directly with browser-like headers bypasses this. Used as a fallback only.
_YAHOO_BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _yahoo_direct_download_single(ticker: str, period: str = "5y") -> pd.Series | None:
    """Fetch close prices directly from Yahoo Finance chart API with browser headers.

    Fallback for when yfinance is rate-limited (429). Returns a pandas Series
    with DatetimeIndex and close prices, or None on failure.
    """
    import httpx as _httpx
    from datetime import datetime, timezone

    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        r = _httpx.get(url, headers=_YAHOO_BROWSER_HEADERS,
                       params={"interval": "1d", "range": period}, timeout=30)
        if r.status_code != 200:
            logger.warning("Yahoo direct API returned %d for %s", r.status_code, ticker)
            return None

        data = r.json()
        chart = data["chart"]["result"][0]
        timestamps = chart["timestamp"]
        closes = chart["indicators"]["quote"][0]["close"]

        dates = [datetime.fromtimestamp(ts, tz=timezone.utc) for ts in timestamps]
        series = pd.Series(closes, index=pd.DatetimeIndex(dates), name=ticker, dtype=float)
        series = series.dropna()
        return series
    except Exception as e:
        logger.warning("Yahoo direct API failed for %s: %s", ticker, e)
        return None


async def fetch_yfinance_history(
    tickers: list[str],
    period: str = "5y",
) -> pd.DataFrame:
    """Async wrapper for Yahoo Finance data download.

    Tries yfinance library first. If any tickers fail (e.g., 429 rate limit),
    falls back to direct Yahoo Finance chart API with browser-like headers.

    Parameters
    ----------
    tickers : list[str]
        Yahoo Finance ticker symbols (e.g. ``["SPY", "QQQ"]``).
    period : str
        yfinance period string (e.g. ``"5y"``, ``"1mo"``).

    Returns
    -------
    pd.DataFrame
        Columns = tickers, index = DatetimeIndex, values = Close prices.
    """
    return await asyncio.to_thread(_yfinance_download_sync, tickers, period)


# ---------------------------------------------------------------------------
# FRED
# ---------------------------------------------------------------------------

def parse_fred_observations(
    raw_observations: list[dict],
) -> list[tuple[str, float]]:
    """Parse raw FRED API observations into (date_str, value) tuples.

    Filters out entries where the value is ``"."`` (FRED's missing-data
    sentinel).

    Parameters
    ----------
    raw_observations : list[dict]
        List of ``{"date": "YYYY-MM-DD", "value": "..."}`` dicts as returned
        by the FRED ``series/observations`` endpoint.

    Returns
    -------
    list[tuple[str, float]]
        Parsed ``(date_string, numeric_value)`` pairs.
    """
    results: list[tuple[str, float]] = []
    for obs in raw_observations:
        val = obs.get("value", ".")
        if val == ".":
            continue
        try:
            results.append((obs["date"], float(val)))
        except (ValueError, KeyError):
            continue
    return results


async def fetch_fred_series_history(
    series_id: str,
    observation_start: str = "2020-01-01",
) -> list[tuple[str, float]]:
    """Fetch a full observation history for a single FRED series.

    Parameters
    ----------
    series_id : str
        FRED series identifier (e.g. ``"FEDFUNDS"``).
    observation_start : str
        ISO date string for the start of the observation window.

    Returns
    -------
    list[tuple[str, float]]
        Parsed ``(date_string, value)`` pairs, or an empty list if the FRED
        API key is not configured or the request fails.
    """
    if not settings.fred_api_key:
        logger.warning(
            "FRED API key not configured — skipping fetch for %s", series_id,
        )
        return []

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": settings.fred_api_key,
        "file_type": "json",
        "observation_start": observation_start,
        "sort_order": "asc",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return parse_fred_observations(data.get("observations", []))
    except httpx.HTTPError as exc:
        logger.error("FRED API error for %s: %s", series_id, exc)
        return []
