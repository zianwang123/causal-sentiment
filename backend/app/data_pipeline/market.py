"""Market data pipeline using yfinance."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone

import yfinance as yf

logger = logging.getLogger(__name__)

# Ticker → graph node ID mapping
MARKET_TICKER_MAP: dict[str, str] = {
    "SPY": "sp500",
    "QQQ": "nasdaq",
    "IWM": "russell2000",
    "XLK": "tech_sector",
    "XLE": "energy_sector",
    "XLF": "financials_sector",
    "GLD": "gold",
    "SLV": "silver",
    "USO": "wti_crude",
    "UNG": "natural_gas",
    "HG=F": "copper",
    "ZW=F": "wheat",
    "DX-Y.NYB": "dxy_index",
}


def _fetch_sync(tickers: list[str], period: str = "5d") -> dict[str, dict]:
    """Synchronous yfinance fetch — run via asyncio.to_thread."""
    results: dict[str, dict] = {}
    for ticker in tickers:
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                data = yf.download(ticker, period=period, interval="1d", progress=False)
                if data.empty:
                    break  # No data available, not a transient error
                # Handle multi-level columns from yfinance
                if hasattr(data.columns, "levels") and len(data.columns.levels) > 1:
                    data.columns = data.columns.droplevel(1)
                last = data.iloc[-1]
                prev = data.iloc[-2] if len(data) > 1 else data.iloc[-1]
                close = float(last["Close"])
                prev_close = float(prev["Close"])
                change_pct = ((close - prev_close) / prev_close) * 100 if prev_close else 0.0
                results[ticker] = {
                    "close": round(close, 4),
                    "prev_close": round(prev_close, 4),
                    "change_pct": round(change_pct, 4),
                    "date": str(data.index[-1].date()),
                }
                break  # Success
            except Exception as e:
                if attempt == max_attempts - 1:
                    logger.warning("Failed to fetch %s after %d attempts: %s", ticker, max_attempts, e)
                else:
                    delay = 1.0 * (2 ** attempt)
                    logger.warning("Fetch %s attempt %d/%d failed, retrying in %.1fs: %s", ticker, attempt + 1, max_attempts, delay, e)
                    time.sleep(delay)
    return results


async def fetch_all_market_prices(
    tickers: list[str] | None = None,
) -> dict[str, dict]:
    """Fetch market prices for all tracked tickers."""
    if tickers is None:
        tickers = list(MARKET_TICKER_MAP.keys())
    return await asyncio.to_thread(_fetch_sync, tickers)


async def fetch_market_prices_for_agent(tickers: list[str] | None = None) -> list[dict]:
    """Fetch market prices and return in agent-friendly format."""
    prices = await fetch_all_market_prices(tickers)
    results = []
    for ticker, data in prices.items():
        node_id = MARKET_TICKER_MAP.get(ticker, ticker)
        results.append({
            "ticker": ticker,
            "node_id": node_id,
            **data,
        })
    return results
