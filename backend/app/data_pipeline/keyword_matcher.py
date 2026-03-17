"""Shared keyword-to-node matching engine.

Used by both the news pipeline and Reddit pipeline to map article/post text
to graph node IDs.  Improvements over naive substring matching:
  - Word-boundary regex (prevents "war" matching "software")
  - Negative keyword exclusions per keyword
  - Multi-word phrases scored higher than single words
  - Headline vs body weighting with confidence scoring
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Keyword definitions
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class KeywordRule:
    """Single keyword matching rule."""
    keyword: str
    node_ids: list[str]
    weight: float = 1.0          # Base importance (longer phrases get higher weight)
    exclude: list[str] = field(default_factory=list)  # Negative keywords


# All rules, longest phrase first for priority scoring
KEYWORD_RULES: list[KeywordRule] = sorted([
    # --- Macro (multi-word phrases first, higher weight) ---
    KeywordRule("federal reserve",  ["fed_funds_rate", "fed_balance_sheet"], weight=2.0),
    KeywordRule("interest rate",    ["fed_funds_rate", "us_2y_yield", "us_10y_yield"], weight=1.5),
    KeywordRule("rate cut",         ["fed_funds_rate", "rate_expectations"], weight=1.8),
    KeywordRule("rate hike",        ["fed_funds_rate", "rate_expectations"], weight=1.8),
    KeywordRule("monetary policy",  ["fed_funds_rate", "fed_balance_sheet"], weight=1.8),
    KeywordRule("balance sheet",    ["fed_balance_sheet"], weight=1.5),
    KeywordRule("pe ratio",         ["pe_valuations"], weight=1.5),
    KeywordRule("price earnings",   ["pe_valuations"], weight=1.5),
    KeywordRule("credit spread",    ["ig_credit_spread", "hy_credit_spread"], weight=1.5),
    KeywordRule("high yield",       ["hy_credit_spread"], weight=1.5),
    KeywordRule("investment grade", ["ig_credit_spread"], weight=1.5),
    KeywordRule("yield curve",      ["yield_curve_spread"], weight=1.5),
    KeywordRule("trade war",        ["trade_policy_tariffs", "geopolitical_risk_index"], weight=1.8),
    KeywordRule("china pmi",        ["china_pmi"], weight=1.8),
    KeywordRule("supply chain",     ["trade_policy_tariffs", "geopolitical_risk_index"], weight=1.3),
    KeywordRule("quantitative easing",  ["fed_balance_sheet"], weight=1.8),
    KeywordRule("quantitative tightening", ["fed_balance_sheet"], weight=1.8),
    KeywordRule("consumer price",   ["us_cpi_yoy"], weight=1.5),
    KeywordRule("core inflation",   ["us_cpi_yoy", "pce_deflator"], weight=1.5),
    KeywordRule("personal consumption", ["pce_deflator"], weight=1.5),
    KeywordRule("crude oil",        ["wti_crude"], weight=1.5),
    KeywordRule("oil price",        ["wti_crude"], weight=1.5),
    KeywordRule("natural gas",      ["natural_gas"], weight=1.5),
    KeywordRule("real estate",      ["us_housing"], weight=1.3, exclude=["star wars"]),

    # --- Single-word keywords (lower weight) ---
    KeywordRule("fed",          ["fed_funds_rate", "rate_expectations"], weight=0.8, exclude=["fedex", "federation", "federated"]),
    KeywordRule("fomc",         ["fed_funds_rate", "rate_expectations"], weight=1.5),
    KeywordRule("inflation",    ["us_cpi_yoy", "pce_deflator"]),
    KeywordRule("cpi",          ["us_cpi_yoy"], weight=1.3),
    KeywordRule("pce",          ["pce_deflator"], weight=1.3),
    KeywordRule("gdp",          ["us_gdp_growth"], weight=1.3),
    KeywordRule("unemployment", ["unemployment_rate"]),
    KeywordRule("payroll",      ["unemployment_rate"], weight=1.2),
    KeywordRule("nonfarm",      ["unemployment_rate"], weight=1.3),
    KeywordRule("jobs",         ["unemployment_rate"], weight=0.8, exclude=["steve jobs", "jobs act"]),
    KeywordRule("treasury",     ["us_10y_yield", "us_30y_yield"]),
    KeywordRule("yield",        ["us_10y_yield", "yield_curve_spread"], weight=0.8),
    KeywordRule("bonds",        ["us_10y_yield", "us_30y_yield"], weight=0.8),
    KeywordRule("credit",       ["ig_credit_spread", "hy_credit_spread"], weight=0.7),
    KeywordRule("oil",          ["wti_crude"], exclude=["oily", "oil painting"]),
    KeywordRule("crude",        ["wti_crude"]),
    KeywordRule("brent",        ["brent_crude"]),
    KeywordRule("gold",         ["gold"], exclude=["golden", "goldfish", "marigold"]),
    KeywordRule("copper",       ["copper"]),
    KeywordRule("vix",          ["vix"], weight=1.3),
    KeywordRule("volatility",   ["vix", "move_index"]),
    KeywordRule("spy",          ["sp500"], weight=1.0, exclude=["espionage", "spying"]),
    KeywordRule("s&p",          ["sp500"], weight=1.2),
    KeywordRule("s&p 500",      ["sp500"], weight=1.5),
    KeywordRule("nasdaq",       ["nasdaq"]),
    KeywordRule("qqq",          ["nasdaq"]),
    KeywordRule("dow jones",    ["sp500"], weight=1.3),
    KeywordRule("tech",         ["tech_sector"], weight=0.7, exclude=["biotech"]),
    KeywordRule("semiconductor", ["tech_sector"], weight=1.0),
    KeywordRule("banks",        ["financials_sector"], weight=0.8, exclude=["river banks", "blood banks"]),
    KeywordRule("banking",      ["financials_sector"]),
    KeywordRule("energy",       ["energy_sector"], weight=0.8),
    KeywordRule("dollar",       ["dxy_index"], exclude=["dollar general", "dollar tree"]),
    KeywordRule("usd",          ["dxy_index"]),
    KeywordRule("dxy",          ["dxy_index"], weight=1.3),
    KeywordRule("euro",         ["eurusd"], exclude=["european", "euronext"]),
    KeywordRule("eurusd",       ["eurusd"], weight=1.5),
    KeywordRule("yen",          ["usdjpy"]),
    KeywordRule("usdjpy",       ["usdjpy"], weight=1.5),
    KeywordRule("yuan",         ["usdcny"]),
    KeywordRule("renminbi",     ["usdcny"]),
    KeywordRule("china",        ["china_pmi"], weight=0.7),
    KeywordRule("tariff",       ["trade_policy_tariffs"]),
    KeywordRule("war",          ["geopolitical_risk_index"], exclude=["software", "warrant", "star wars", "warcraft", "warehouse"]),
    KeywordRule("geopolit",     ["geopolitical_risk_index"]),
    KeywordRule("sanction",     ["sanctions_pressure"]),
    KeywordRule("earnings",     ["earnings_momentum"]),
    KeywordRule("revenue",      ["revenue_growth"], weight=0.8),
    KeywordRule("retail",       ["retail_sentiment"], weight=0.7, exclude=["retail price", "retail store"]),
    KeywordRule("sentiment",    ["retail_sentiment"], weight=0.6),
    KeywordRule("recession",    ["us_gdp_growth", "sp500"], weight=1.3),
    KeywordRule("stagflation",  ["us_gdp_growth", "us_cpi_yoy"], weight=1.5),
    KeywordRule("default",      ["hy_credit_spread"], weight=1.0, exclude=["by default"]),
    KeywordRule("housing",      ["us_housing"]),
    KeywordRule("mortgage",     ["us_housing", "us_10y_yield"]),
    KeywordRule("opec",         ["wti_crude", "brent_crude"], weight=1.5),

    # --- Previously empty nodes (filling coverage gaps) ---
    # us_political_risk
    KeywordRule("congress",     ["us_political_risk"], weight=1.0, exclude=["indian national congress"]),
    KeywordRule("legislation",  ["us_political_risk"]),
    KeywordRule("election",     ["us_political_risk"], weight=0.8),
    KeywordRule("impeach",      ["us_political_risk"], weight=1.3),
    KeywordRule("government shutdown", ["us_political_risk"], weight=1.5),
    # put_call_ratio
    KeywordRule("put call ratio", ["put_call_ratio"], weight=1.5),
    KeywordRule("options sentiment", ["put_call_ratio"], weight=1.3),
    KeywordRule("options volume", ["put_call_ratio"], weight=1.0),
    # skew_index
    KeywordRule("skew index",   ["skew_index"], weight=1.5),
    KeywordRule("tail risk",    ["skew_index"], weight=1.3),
    # credit_default_swaps
    KeywordRule("credit default swap", ["credit_default_swaps"], weight=1.5),
    KeywordRule("cds spread",   ["credit_default_swaps"], weight=1.5),
    # fund_flows
    KeywordRule("fund flows",   ["fund_flows"], weight=1.5),
    KeywordRule("etf flows",    ["fund_flows"], weight=1.3),
    KeywordRule("outflows",     ["fund_flows"], weight=1.0),
    KeywordRule("inflows",      ["fund_flows"], weight=1.0),
    # institutional_positioning
    KeywordRule("institutional positioning", ["institutional_positioning"], weight=1.5),
    KeywordRule("hedge fund",   ["institutional_positioning"], weight=1.0),
    KeywordRule("cot report",   ["institutional_positioning"], weight=1.5),
    KeywordRule("13f filing",   ["institutional_positioning"], weight=1.3),
    # global_central_bank_liquidity
    KeywordRule("global liquidity", ["global_central_bank_liquidity"], weight=1.5),
    KeywordRule("ecb balance sheet", ["global_central_bank_liquidity"], weight=1.3),
    KeywordRule("central bank liquidity", ["global_central_bank_liquidity"], weight=1.5),
    # japan_boj_policy
    KeywordRule("bank of japan", ["japan_boj_policy"], weight=1.8),
    KeywordRule("boj",          ["japan_boj_policy"], weight=1.3),
    KeywordRule("yen intervention", ["japan_boj_policy"], weight=1.5),
    KeywordRule("yield curve control", ["japan_boj_policy"], weight=1.5),
    # eu_hicp
    KeywordRule("eurozone inflation", ["eu_hicp"], weight=1.5),
    KeywordRule("ecb inflation", ["eu_hicp"], weight=1.3),
    KeywordRule("hicp",         ["eu_hicp"], weight=1.5),
    # consumer_confidence
    KeywordRule("consumer confidence", ["consumer_confidence"], weight=1.5),
    KeywordRule("consumer sentiment", ["consumer_confidence"], weight=1.5),
    KeywordRule("michigan sentiment", ["consumer_confidence"], weight=1.8),
    # wage_growth
    KeywordRule("wage growth",  ["wage_growth"], weight=1.5),
    KeywordRule("hourly earnings", ["wage_growth"], weight=1.3),
    KeywordRule("labor cost",   ["wage_growth"], weight=1.0),
    # qe_pace
    KeywordRule("quantitative easing pace", ["qe_pace"], weight=1.5),
    KeywordRule("asset purchases", ["qe_pace", "fed_balance_sheet"], weight=1.0),
], key=lambda r: -len(r.keyword))  # Longest first for priority


# Precompile regex patterns for performance
_COMPILED_PATTERNS: dict[str, re.Pattern] = {}


def _get_pattern(keyword: str) -> re.Pattern:
    """Get or compile a word-boundary regex for a keyword."""
    if keyword not in _COMPILED_PATTERNS:
        escaped = re.escape(keyword)
        _COMPILED_PATTERNS[keyword] = re.compile(r"\b" + escaped + r"\b", re.IGNORECASE)
    return _COMPILED_PATTERNS[keyword]


def _has_exclusion(text: str, exclusions: list[str]) -> bool:
    """Check if any exclusion phrase appears in the text."""
    text_lower = text.lower()
    return any(exc in text_lower for exc in exclusions)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def match_text_to_nodes(
    headline: str,
    body: str = "",
    threshold: float = 0.3,
) -> list[tuple[str, float]]:
    """Match text against keyword rules and return (node_id, confidence) pairs.

    Headline matches score 1.0 * rule weight, body matches score 0.5 * rule weight.
    Multiple keywords matching the same node accumulate (capped at 1.0).
    Only returns nodes with confidence >= threshold.
    """
    node_scores: dict[str, float] = {}
    full_text = headline + " " + body

    for rule in KEYWORD_RULES:
        pattern = _get_pattern(rule.keyword)

        # Check exclusions on the full text
        if rule.exclude and _has_exclusion(full_text, rule.exclude):
            continue

        # Check headline (higher weight)
        in_headline = bool(pattern.search(headline))
        in_body = bool(pattern.search(body)) if body and not in_headline else False

        if not in_headline and not in_body:
            continue

        score = rule.weight * (1.0 if in_headline else 0.5)

        for node_id in rule.node_ids:
            node_scores[node_id] = min(1.0, node_scores.get(node_id, 0.0) + score)

    # Filter by threshold and sort by confidence descending
    results = [
        (node_id, round(conf, 3))
        for node_id, conf in node_scores.items()
        if conf >= threshold
    ]
    results.sort(key=lambda x: -x[1])
    return results


def match_text_to_node_ids(headline: str, body: str = "") -> list[str]:
    """Convenience wrapper that returns just node_id list (for Reddit pipeline compatibility)."""
    return [node_id for node_id, _ in match_text_to_nodes(headline, body)]
