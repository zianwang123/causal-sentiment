"""Data source registry mapping graph node IDs to external data sources.

Each entry defines the external ticker/series that feeds a node in the causal
graph.  Two primary source types:
  - yfinance: daily OHLCV via the yfinance library
  - fred: daily/monthly observations via the FRED API

Note: wti_crude and dxy_index are covered by yfinance (USO, DX-Y.NYB) so they
do NOT have redundant FRED backup entries.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# yfinance sources — 21 tickers
# ---------------------------------------------------------------------------
YFINANCE_SOURCES: list[dict] = [
    {"node_id": "sp500", "ticker": "SPY", "source_type": "yfinance",
     "description": "S&P 500 ETF"},
    {"node_id": "nasdaq", "ticker": "QQQ", "source_type": "yfinance",
     "description": "Nasdaq-100 ETF"},
    {"node_id": "russell2000", "ticker": "IWM", "source_type": "yfinance",
     "description": "Russell 2000 small-cap ETF"},
    {"node_id": "tech_sector", "ticker": "XLK", "source_type": "yfinance",
     "description": "Technology sector ETF"},
    {"node_id": "energy_sector", "ticker": "XLE", "source_type": "yfinance",
     "description": "Energy sector ETF"},
    {"node_id": "financials_sector", "ticker": "XLF", "source_type": "yfinance",
     "description": "Financials sector ETF"},
    {"node_id": "gold", "ticker": "GLD", "source_type": "yfinance",
     "description": "Gold ETF"},
    {"node_id": "silver", "ticker": "SLV", "source_type": "yfinance",
     "description": "Silver ETF"},
    {"node_id": "wti_crude", "ticker": "USO", "source_type": "yfinance",
     "description": "WTI crude oil ETF"},
    {"node_id": "brent_crude", "ticker": "BZ=F", "source_type": "yfinance",
     "description": "Brent crude oil futures"},
    {"node_id": "natural_gas", "ticker": "UNG", "source_type": "yfinance",
     "description": "Natural gas ETF"},
    {"node_id": "copper", "ticker": "HG=F", "source_type": "yfinance",
     "description": "Copper futures"},
    {"node_id": "wheat", "ticker": "ZW=F", "source_type": "yfinance",
     "description": "Wheat futures"},
    {"node_id": "dxy_index", "ticker": "DX-Y.NYB", "source_type": "yfinance",
     "description": "US Dollar Index"},
    {"node_id": "eurusd", "ticker": "EURUSD=X", "source_type": "yfinance",
     "description": "EUR/USD exchange rate"},
    {"node_id": "usdjpy", "ticker": "USDJPY=X", "source_type": "yfinance",
     "description": "USD/JPY exchange rate"},
    {"node_id": "usdcny", "ticker": "USDCNY=X", "source_type": "yfinance",
     "description": "USD/CNY exchange rate"},
    {"node_id": "vix", "ticker": "^VIX", "source_type": "yfinance",
     "description": "CBOE Volatility Index"},
    {"node_id": "move_index", "ticker": "^MOVE", "source_type": "yfinance",
     "description": "ICE BofA MOVE Index (bond volatility)"},
    {"node_id": "skew_index", "ticker": "^SKEW", "source_type": "yfinance",
     "description": "CBOE Skew Index"},
    {"node_id": "gbpusd", "ticker": "GBPUSD=X", "source_type": "yfinance",
     "description": "GBP/USD exchange rate"},
]

# ---------------------------------------------------------------------------
# FRED sources — 17 series
# ---------------------------------------------------------------------------
FRED_SOURCES: list[dict] = [
    {"node_id": "fed_funds_rate", "series_id": "FEDFUNDS",
     "source_type": "fred", "description": "Federal funds effective rate"},
    {"node_id": "us_2y_yield", "series_id": "DGS2",
     "source_type": "fred", "description": "2-year Treasury yield"},
    {"node_id": "us_10y_yield", "series_id": "DGS10",
     "source_type": "fred", "description": "10-year Treasury yield"},
    {"node_id": "us_30y_yield", "series_id": "DGS30",
     "source_type": "fred", "description": "30-year Treasury yield"},
    {"node_id": "yield_curve_spread", "series_id": "T10Y2Y",
     "source_type": "fred", "description": "10Y minus 2Y Treasury spread"},
    {"node_id": "ig_credit_spread", "series_id": "BAMLC0A0CM",
     "source_type": "fred",
     "description": "ICE BofA investment-grade corporate spread"},
    {"node_id": "hy_credit_spread", "series_id": "BAMLH0A0HYM2",
     "source_type": "fred",
     "description": "ICE BofA high-yield corporate spread"},
    {"node_id": "us_cpi_yoy", "series_id": "CPIAUCSL",
     "source_type": "fred", "description": "CPI for all urban consumers"},
    {"node_id": "us_gdp_growth", "series_id": "GDP",
     "source_type": "fred", "description": "US nominal GDP"},
    {"node_id": "unemployment_rate", "series_id": "UNRATE",
     "source_type": "fred", "description": "Civilian unemployment rate"},
    {"node_id": "consumer_confidence", "series_id": "UMCSENT",
     "source_type": "fred",
     "description": "University of Michigan consumer sentiment"},
    {"node_id": "pce_deflator", "series_id": "PCEPILFE",
     "source_type": "fred",
     "description": "Core PCE price index (ex food & energy)"},
    {"node_id": "wage_growth", "series_id": "CES0500000003",
     "source_type": "fred",
     "description": "Average hourly earnings, private sector"},
    {"node_id": "fed_balance_sheet", "series_id": "WALCL",
     "source_type": "fred",
     "description": "Federal Reserve total assets"},
    {"node_id": "us_political_risk", "series_id": "USEPUINDXD",
     "source_type": "fred",
     "description": "US Economic Policy Uncertainty Index (daily)"},
    {"node_id": "ecb_policy_rate", "series_id": "ECBDFR",
     "source_type": "fred", "description": "ECB deposit facility rate"},
    {"node_id": "japan_boj_policy", "series_id": "IRLTLT01JPM156N",
     "source_type": "fred", "description": "Japan 10-year government bond yield (BOJ policy proxy)"},
]


# ---------------------------------------------------------------------------
# CSV download sources — 4 sources
# ---------------------------------------------------------------------------
CSV_SOURCES: list[dict] = [
    {"node_id": "pe_valuations", "source_type": "csv_shiller",
     "description": "Shiller CAPE ratio (monthly, from Yale)"},
    {"node_id": "geopolitical_risk_index", "source_type": "csv_gpr",
     "description": "Geopolitical Risk Index (daily, Caldara-Iacoviello)"},
    {"node_id": "put_call_ratio", "source_type": "csv_cboe",
     "description": "CBOE equity put/call ratio (daily)"},
    {"node_id": "retail_sentiment", "source_type": "csv_aaii",
     "description": "AAII investor sentiment survey (weekly)"},
]

# ---------------------------------------------------------------------------
# REST API sources — 3 sources
# ---------------------------------------------------------------------------
API_SOURCES: list[dict] = [
    {"node_id": "institutional_positioning", "source_type": "api_cftc",
     "description": "CFTC Commitments of Traders (weekly)"},
    {"node_id": "geopolitical_risk", "source_type": "api_gdelt",
     "description": "GDELT geopolitical risk tone (daily)"},
    {"node_id": "sanctions_risk", "source_type": "api_gdelt",
     "description": "GDELT sanctions risk tone (daily)"},
]


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def get_all_sources() -> list[dict]:
    """Return the combined list of all data source definitions."""
    return YFINANCE_SOURCES + FRED_SOURCES + CSV_SOURCES + API_SOURCES


def get_source_for_node(node_id: str) -> dict | None:
    """Look up the source definition for a given graph node ID.

    Returns ``None`` if the node has no registered data source.
    """
    for src in get_all_sources():
        if src["node_id"] == node_id:
            return src
    return None
