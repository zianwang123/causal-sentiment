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
    # Equities
    "SPY": "sp500",
    "QQQ": "nasdaq",
    "IWM": "russell2000",
    "XLK": "tech_sector",
    "XLE": "energy_sector",
    "XLF": "financials_sector",
    # Commodities
    "GLD": "gold",
    "SLV": "silver",
    "USO": "wti_crude",
    "UNG": "natural_gas",
    "HG=F": "copper",
    "ZW=F": "wheat",
    # Currencies
    "DX-Y.NYB": "dxy_index",
    "EURUSD=X": "eurusd",
    "USDJPY=X": "usdjpy",
    "USDCNY=X": "usdcny",
    # Volatility & credit indices
    "^VIX": "vix",
    "^MOVE": "move_index",
    "^SKEW": "skew_index",
    "HYG": "hy_credit_spread",
    "LQD": "ig_credit_spread",
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
                # 5-day context for richer agent reasoning
                high_5d = float(data["High"].max())
                low_5d = float(data["Low"].min())
                first_close = float(data["Close"].iloc[0])
                change_5d_pct = ((close - first_close) / first_close) * 100 if first_close else 0.0
                results[ticker] = {
                    "close": round(close, 4),
                    "prev_close": round(prev_close, 4),
                    "change_pct": round(change_pct, 4),
                    "date": str(data.index[-1].date()),
                    "high_5d": round(high_5d, 4),
                    "low_5d": round(low_5d, 4),
                    "change_5d_pct": round(change_5d_pct, 4),
                    "trend": "up" if close > first_close else "down",
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


def _fetch_historical_sync(ticker: str, start: str, end: str) -> dict:
    """Synchronous yfinance historical fetch — returns summary stats, not raw bars."""
    from datetime import date as date_type

    try:
        start_dt = date_type.fromisoformat(start)
        end_dt = date_type.fromisoformat(end)
    except ValueError:
        return {"error": "Invalid date format — use YYYY-MM-DD"}

    if (end_dt - start_dt).days > 366:
        return {"error": "Max 1 year of data per request"}
    if end_dt <= start_dt:
        return {"error": "end_date must be after start_date"}

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            data = yf.download(ticker, start=start, end=end, interval="1d", progress=False)
            if data.empty:
                return {"error": f"No data available for {ticker} in {start} to {end}"}

            # Handle multi-level columns from yfinance
            if hasattr(data.columns, "levels") and len(data.columns.levels) > 1:
                data.columns = data.columns.droplevel(1)

            closes = data["Close"]
            opens = data["Open"]
            highs = data["High"]
            lows = data["Low"]

            period_open = float(opens.iloc[0])
            period_close = float(closes.iloc[-1])
            period_high = float(highs.max())
            period_low = float(lows.min())
            total_return_pct = ((period_close - period_open) / period_open) * 100 if period_open else 0.0

            # Max drawdown from rolling peak
            rolling_max = closes.cummax()
            drawdown = (closes - rolling_max) / rolling_max
            max_drawdown_pct = float(drawdown.min()) * 100

            # Peak and trough dates
            peak_date = str(closes.idxmax().date()) if len(closes) > 0 else ""
            trough_date = str(closes.idxmin().date()) if len(closes) > 0 else ""

            # Annualized volatility
            daily_returns = closes.pct_change().dropna()
            volatility_ann = float(daily_returns.std() * (252 ** 0.5) * 100) if len(daily_returns) > 1 else 0.0

            return {
                "ticker": ticker,
                "start": start,
                "end": end,
                "trading_days": len(data),
                "period_open": round(period_open, 4),
                "period_close": round(period_close, 4),
                "period_high": round(period_high, 4),
                "period_low": round(period_low, 4),
                "total_return_pct": round(total_return_pct, 2),
                "max_drawdown_pct": round(max_drawdown_pct, 2),
                "peak_date": peak_date,
                "trough_date": trough_date,
                "volatility_annualized_pct": round(volatility_ann, 2),
            }
        except Exception as e:
            if attempt == max_attempts - 1:
                logger.warning("Failed to fetch historical %s after %d attempts: %s", ticker, max_attempts, e)
                return {"error": f"Failed to fetch {ticker}: {e}"}
            delay = 1.0 * (2 ** attempt)
            time.sleep(delay)

    return {"error": f"Failed to fetch {ticker} after retries"}


async def fetch_historical_prices_summary(
    ticker: str, start_date: str, end_date: str
) -> dict:
    """Fetch historical prices and return summary stats."""
    return await asyncio.to_thread(_fetch_historical_sync, ticker, start_date, end_date)


def _fetch_options_summary_sync(ticker: str) -> dict:
    """Synchronous yfinance options fetch — returns positioning summary."""
    try:
        t = yf.Ticker(ticker)
        expirations = t.options
        if not expirations:
            return {"ticker": ticker, "error": f"No options data available for {ticker}"}

        near_exp = expirations[0]
        chain_near = t.option_chain(near_exp)
        calls = chain_near.calls
        puts = chain_near.puts

        # Put/Call ratio (volume-based)
        call_vol = float(calls["volume"].sum()) if "volume" in calls.columns and not calls["volume"].isna().all() else 0
        put_vol = float(puts["volume"].sum()) if "volume" in puts.columns and not puts["volume"].isna().all() else 0
        pc_ratio = round(put_vol / call_vol, 3) if call_vol > 0 else None

        # Implied volatility (weighted average by open interest)
        call_iv = None
        put_iv = None
        if "impliedVolatility" in calls.columns and "openInterest" in calls.columns:
            c_oi = calls["openInterest"].fillna(0)
            if c_oi.sum() > 0:
                call_iv = round(float((calls["impliedVolatility"] * c_oi).sum() / c_oi.sum()), 4)
        if "impliedVolatility" in puts.columns and "openInterest" in puts.columns:
            p_oi = puts["openInterest"].fillna(0)
            if p_oi.sum() > 0:
                put_iv = round(float((puts["impliedVolatility"] * p_oi).sum() / p_oi.sum()), 4)

        # Key strike levels (highest OI)
        top_call_strike = None
        top_put_strike = None
        if not calls.empty and "openInterest" in calls.columns:
            valid_calls = calls.dropna(subset=["openInterest"])
            if not valid_calls.empty:
                top_call_strike = float(valid_calls.loc[valid_calls["openInterest"].idxmax(), "strike"])
        if not puts.empty and "openInterest" in puts.columns:
            valid_puts = puts.dropna(subset=["openInterest"])
            if not valid_puts.empty:
                top_put_strike = float(valid_puts.loc[valid_puts["openInterest"].idxmax(), "strike"])

        # IV term structure (near vs. next month)
        iv_term = None
        if len(expirations) >= 2:
            try:
                chain_next = t.option_chain(expirations[1])
                near_iv_avg = float(calls["impliedVolatility"].mean()) if not calls.empty else None
                next_iv_avg = float(chain_next.calls["impliedVolatility"].mean()) if not chain_next.calls.empty else None
                if near_iv_avg and next_iv_avg:
                    iv_term = {
                        "near_month_iv": round(near_iv_avg, 4),
                        "near_expiry": near_exp,
                        "next_month_iv": round(next_iv_avg, 4),
                        "next_expiry": expirations[1],
                        "contango": next_iv_avg > near_iv_avg,
                        "term_slope": round(next_iv_avg - near_iv_avg, 4),
                    }
            except Exception:
                pass  # Term structure is a bonus, not critical

        return {
            "ticker": ticker,
            "near_expiry": near_exp,
            "put_call_ratio": pc_ratio,
            "avg_call_iv": call_iv,
            "avg_put_iv": put_iv,
            "highest_oi_call_strike": top_call_strike,
            "highest_oi_put_strike": top_put_strike,
            "iv_term_structure": iv_term,
        }
    except Exception as e:
        return {"ticker": ticker, "error": f"Failed to fetch options: {e}"}


async def fetch_options_summary(ticker: str) -> dict:
    """Fetch options positioning summary for a ticker (IV, put/call ratio, key strikes)."""
    return await asyncio.to_thread(_fetch_options_summary_sync, ticker)


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
