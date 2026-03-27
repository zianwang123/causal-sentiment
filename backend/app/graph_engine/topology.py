"""Seed graph topology — 111 nodes and 1071 causal edges.

MVP_NODES / MVP_EDGES are the original 52-node graph (kept for reference).
ALL_NODES / ALL_EDGES are the full 111-node graph from MACRO_FACTOR_REPORT.md.
"""

from app.models.graph import EdgeDirection, NodeType
from app.graph_engine.topology_expanded import EXPANDED_NODES, EXPANDED_EDGES

MVP_NODES = [
    # Macro
    {"id": "fed_funds_rate", "label": "Fed Funds Rate", "node_type": NodeType.MACRO, "description": "Federal Reserve target interest rate"},
    {"id": "us_cpi_yoy", "label": "US CPI YoY", "node_type": NodeType.MACRO, "description": "US Consumer Price Index year-over-year change"},
    {"id": "us_gdp_growth", "label": "US GDP Growth", "node_type": NodeType.MACRO, "description": "US real GDP quarter-over-quarter annualized growth rate"},
    {"id": "unemployment_rate", "label": "Unemployment Rate", "node_type": NodeType.MACRO, "description": "US civilian unemployment rate"},
    {"id": "us_pmi", "label": "US PMI", "node_type": NodeType.MACRO, "description": "ISM Manufacturing Purchasing Managers Index"},
    {"id": "pce_deflator", "label": "PCE Deflator", "node_type": NodeType.MACRO, "description": "Personal Consumption Expenditures price index — Fed's preferred inflation gauge"},
    {"id": "consumer_confidence", "label": "Consumer Confidence", "node_type": NodeType.MACRO, "description": "University of Michigan / Conference Board consumer confidence index"},
    {"id": "wage_growth", "label": "Wage Growth", "node_type": NodeType.MACRO, "description": "Average hourly earnings year-over-year growth"},
    # Monetary Policy
    {"id": "fed_balance_sheet", "label": "Fed Balance Sheet", "node_type": NodeType.MONETARY_POLICY, "description": "Total Federal Reserve balance sheet assets"},
    {"id": "rate_expectations", "label": "Rate Expectations", "node_type": NodeType.MONETARY_POLICY, "description": "Fed funds futures implied rate path"},
    {"id": "qe_pace", "label": "QE Pace", "node_type": NodeType.MONETARY_POLICY, "description": "Pace of quantitative easing or tightening (asset purchases/sales per month)"},
    {"id": "global_central_bank_liquidity", "label": "Global CB Liquidity", "node_type": NodeType.MONETARY_POLICY, "description": "Aggregate global central bank balance sheet expansion/contraction"},
    # Geopolitics
    {"id": "geopolitical_risk_index", "label": "Geopolitical Risk", "node_type": NodeType.GEOPOLITICS, "description": "Composite geopolitical risk index based on news coverage"},
    {"id": "trade_policy_tariffs", "label": "Trade Policy / Tariffs", "node_type": NodeType.GEOPOLITICS, "description": "Trade policy sentiment and tariff regime changes"},
    {"id": "us_political_risk", "label": "US Political Risk", "node_type": NodeType.GEOPOLITICS, "description": "Domestic political uncertainty — elections, policy shifts, government shutdowns"},
    {"id": "sanctions_pressure", "label": "Sanctions Pressure", "node_type": NodeType.GEOPOLITICS, "description": "Intensity of international economic sanctions and enforcement"},
    # Rates & Credit
    {"id": "us_2y_yield", "label": "US 2Y Yield", "node_type": NodeType.RATES_CREDIT, "description": "US 2-year Treasury yield"},
    {"id": "us_10y_yield", "label": "US 10Y Yield", "node_type": NodeType.RATES_CREDIT, "description": "US 10-year Treasury yield"},
    {"id": "us_30y_yield", "label": "US 30Y Yield", "node_type": NodeType.RATES_CREDIT, "description": "US 30-year Treasury yield"},
    {"id": "yield_curve_spread", "label": "Yield Curve Spread", "node_type": NodeType.RATES_CREDIT, "description": "10Y minus 2Y Treasury spread"},
    {"id": "ig_credit_spread", "label": "IG Credit Spread", "node_type": NodeType.RATES_CREDIT, "description": "Investment grade corporate bond spread over Treasuries"},
    {"id": "hy_credit_spread", "label": "HY Credit Spread", "node_type": NodeType.RATES_CREDIT, "description": "High yield corporate bond spread over Treasuries"},
    # Volatility
    {"id": "vix", "label": "VIX", "node_type": NodeType.VOLATILITY, "description": "CBOE Volatility Index — S&P 500 implied volatility"},
    {"id": "move_index", "label": "MOVE Index", "node_type": NodeType.VOLATILITY, "description": "Merrill Lynch bond market volatility index"},
    {"id": "put_call_ratio", "label": "Put/Call Ratio", "node_type": NodeType.VOLATILITY, "description": "CBOE equity put/call volume ratio"},
    {"id": "skew_index", "label": "SKEW Index", "node_type": NodeType.VOLATILITY, "description": "CBOE SKEW index — tail risk pricing in S&P 500 options"},
    {"id": "credit_default_swaps", "label": "CDS Spreads", "node_type": NodeType.VOLATILITY, "description": "Investment grade CDS index — market-priced credit risk"},
    # Commodities
    {"id": "wti_crude", "label": "WTI Crude Oil", "node_type": NodeType.COMMODITIES, "description": "West Texas Intermediate crude oil price"},
    {"id": "gold", "label": "Gold", "node_type": NodeType.COMMODITIES, "description": "Gold spot price (USD/oz)"},
    {"id": "copper", "label": "Copper", "node_type": NodeType.COMMODITIES, "description": "Copper futures price — industrial bellwether"},
    {"id": "natural_gas", "label": "Natural Gas", "node_type": NodeType.COMMODITIES, "description": "Henry Hub natural gas spot price"},
    {"id": "silver", "label": "Silver", "node_type": NodeType.COMMODITIES, "description": "Silver spot price (USD/oz) — industrial + precious metal"},
    {"id": "wheat", "label": "Wheat", "node_type": NodeType.COMMODITIES, "description": "Wheat futures price — food inflation bellwether"},
    # Equities
    {"id": "sp500", "label": "S&P 500", "node_type": NodeType.EQUITIES, "description": "S&P 500 index level"},
    {"id": "nasdaq", "label": "NASDAQ", "node_type": NodeType.EQUITIES, "description": "NASDAQ Composite index level"},
    {"id": "tech_sector", "label": "Tech Sector", "node_type": NodeType.EQUITIES, "description": "Technology sector performance (XLK)"},
    {"id": "energy_sector", "label": "Energy Sector", "node_type": NodeType.EQUITIES, "description": "Energy sector performance (XLE)"},
    {"id": "financials_sector", "label": "Financials Sector", "node_type": NodeType.EQUITIES, "description": "Financial sector performance (XLF)"},
    {"id": "russell2000", "label": "Russell 2000", "node_type": NodeType.EQUITIES, "description": "Russell 2000 small-cap index — domestic growth proxy"},
    # Equity Fundamentals
    {"id": "earnings_momentum", "label": "Earnings Momentum", "node_type": NodeType.EQUITY_FUNDAMENTALS, "description": "Aggregate earnings revision and surprise trends"},
    {"id": "pe_valuations", "label": "P/E Valuations", "node_type": NodeType.EQUITY_FUNDAMENTALS, "description": "S&P 500 forward P/E ratio — valuation stretch indicator"},
    {"id": "revenue_growth", "label": "Revenue Growth", "node_type": NodeType.EQUITY_FUNDAMENTALS, "description": "Aggregate S&P 500 revenue growth rate"},
    # Currencies
    {"id": "dxy_index", "label": "DXY Index", "node_type": NodeType.CURRENCIES, "description": "US Dollar Index"},
    {"id": "eurusd", "label": "EUR/USD", "node_type": NodeType.CURRENCIES, "description": "Euro vs US Dollar exchange rate"},
    {"id": "usdjpy", "label": "USD/JPY", "node_type": NodeType.CURRENCIES, "description": "US Dollar vs Japanese Yen exchange rate"},
    {"id": "usdcny", "label": "USD/CNY", "node_type": NodeType.CURRENCIES, "description": "US Dollar vs Chinese Yuan exchange rate"},
    # Flows & Sentiment
    {"id": "retail_sentiment", "label": "Retail Sentiment", "node_type": NodeType.FLOWS_SENTIMENT, "description": "Aggregate retail investor sentiment from social media and surveys"},
    {"id": "fund_flows", "label": "Fund Flows", "node_type": NodeType.FLOWS_SENTIMENT, "description": "Net flows into equity/bond/money market funds — tracks institutional allocation"},
    {"id": "institutional_positioning", "label": "Institutional Positioning", "node_type": NodeType.FLOWS_SENTIMENT, "description": "CFTC COT data — net speculative positioning in futures markets"},
    # Global
    {"id": "china_pmi", "label": "China PMI", "node_type": NodeType.GLOBAL, "description": "China Caixin Manufacturing PMI"},
    {"id": "eu_hicp", "label": "EU HICP", "node_type": NodeType.GLOBAL, "description": "Eurozone Harmonised Index of Consumer Prices — ECB inflation target"},
    {"id": "japan_boj_policy", "label": "BOJ Policy", "node_type": NodeType.GLOBAL, "description": "Bank of Japan monetary policy stance — yield curve control and rate decisions"},
]


def _e(src: str, tgt: str, direction: EdgeDirection, weight: float, desc: str = "") -> dict:
    return {
        "source_id": src,
        "target_id": tgt,
        "direction": direction,
        "base_weight": weight,
        "dynamic_weight": weight,
        "description": desc,
    }


P = EdgeDirection.POSITIVE
N = EdgeDirection.NEGATIVE
C = EdgeDirection.COMPLEX

MVP_EDGES = [
    # Fed funds rate effects
    _e("fed_funds_rate", "us_2y_yield", P, 0.9, "Short-term rates track fed funds closely"),
    _e("fed_funds_rate", "us_10y_yield", P, 0.6, "Long rates respond to fed funds but also term premium"),
    _e("fed_funds_rate", "dxy_index", P, 0.5, "Higher rates attract capital → stronger dollar"),
    _e("fed_funds_rate", "sp500", N, 0.5, "Higher rates → higher discount rate → lower valuations"),
    _e("fed_funds_rate", "gold", N, 0.4, "Higher rates → higher real yields → gold less attractive"),
    _e("fed_funds_rate", "ig_credit_spread", P, 0.3, "Tighter policy → wider spreads"),
    _e("fed_funds_rate", "hy_credit_spread", P, 0.5, "HY more sensitive to rate hikes"),
    # CPI effects
    _e("us_cpi_yoy", "fed_funds_rate", P, 0.7, "Inflation drives Fed tightening"),
    _e("us_cpi_yoy", "rate_expectations", P, 0.8, "Inflation shifts rate path expectations"),
    _e("us_cpi_yoy", "gold", P, 0.4, "Inflation → gold as hedge"),
    _e("us_cpi_yoy", "us_10y_yield", P, 0.5, "Inflation → higher nominal yields"),
    # GDP effects
    _e("us_gdp_growth", "sp500", P, 0.6, "Growth → higher earnings → equities up"),
    _e("us_gdp_growth", "earnings_momentum", P, 0.7, "Growth drives earnings"),
    _e("us_gdp_growth", "copper", P, 0.5, "Growth → industrial demand"),
    _e("us_gdp_growth", "ig_credit_spread", N, 0.4, "Growth → lower default risk → tighter spreads"),
    _e("us_gdp_growth", "hy_credit_spread", N, 0.6, "Growth → lower HY default risk"),
    _e("us_gdp_growth", "unemployment_rate", N, 0.7, "Okun's law"),
    # Unemployment
    _e("unemployment_rate", "retail_sentiment", N, 0.5, "Jobs → consumer confidence"),
    _e("unemployment_rate", "us_cpi_yoy", N, 0.3, "Phillips curve — weak but present"),
    # PMI
    _e("us_pmi", "sp500", P, 0.4, "PMI leading indicator for equities"),
    _e("us_pmi", "copper", P, 0.5, "PMI → industrial activity → copper demand"),
    _e("us_pmi", "wti_crude", P, 0.3, "Manufacturing activity drives energy demand"),
    # Monetary policy
    _e("fed_balance_sheet", "sp500", P, 0.5, "QE → asset price inflation"),
    _e("fed_balance_sheet", "gold", P, 0.4, "Balance sheet expansion → gold hedge"),
    _e("fed_balance_sheet", "us_10y_yield", N, 0.4, "QE suppresses long-term yields"),
    _e("rate_expectations", "us_2y_yield", P, 0.85, "2Y yield = market rate expectations"),
    _e("rate_expectations", "nasdaq", N, 0.6, "Rate expectations hit growth stocks hardest"),
    _e("rate_expectations", "tech_sector", N, 0.6, "Tech valuations sensitive to rate path"),
    # Geopolitics
    _e("geopolitical_risk_index", "gold", P, 0.6, "Geopolitical risk → flight to safety → gold"),
    _e("geopolitical_risk_index", "vix", P, 0.5, "Geopolitical risk → uncertainty → vol"),
    _e("geopolitical_risk_index", "wti_crude", P, 0.5, "Geopolitical risk → supply disruption fear"),
    _e("geopolitical_risk_index", "dxy_index", P, 0.3, "Risk → dollar safe haven bid"),
    _e("trade_policy_tariffs", "china_pmi", N, 0.5, "Tariffs → trade disruption → China slowdown"),
    _e("trade_policy_tariffs", "wti_crude", N, 0.3, "Trade war → less global activity → less oil demand"),
    _e("trade_policy_tariffs", "sp500", N, 0.4, "Tariffs → margin pressure → equities down"),
    # Yield curve
    _e("us_2y_yield", "yield_curve_spread", N, 0.9, "Higher 2Y → flatter/inverted curve"),
    _e("us_10y_yield", "yield_curve_spread", P, 0.9, "Higher 10Y → steeper curve"),
    _e("yield_curve_spread", "financials_sector", P, 0.6, "Steeper curve → bank NIM expansion"),
    _e("yield_curve_spread", "sp500", P, 0.3, "Inversion signals recession risk"),
    # Credit spreads
    _e("ig_credit_spread", "sp500", N, 0.3, "Wider spreads → risk-off → equities weaker"),
    _e("hy_credit_spread", "sp500", N, 0.5, "HY spreads leading indicator for equities"),
    _e("hy_credit_spread", "vix", P, 0.4, "Credit stress → equity vol"),
    # Volatility
    _e("vix", "sp500", N, 0.6, "Vol spikes → equity selloff"),
    _e("vix", "put_call_ratio", P, 0.5, "Fear → more put buying"),
    _e("put_call_ratio", "retail_sentiment", N, 0.3, "High put/call → bearish sentiment"),
    _e("move_index", "us_10y_yield", C, 0.3, "Bond vol → yield uncertainty"),
    # Commodities cross-effects
    _e("wti_crude", "us_cpi_yoy", P, 0.4, "Oil → energy component of CPI"),
    _e("wti_crude", "energy_sector", P, 0.8, "Oil price drives energy stocks directly"),
    _e("copper", "china_pmi", P, 0.4, "Copper demand reflects China manufacturing"),
    _e("gold", "dxy_index", N, 0.5, "Gold and dollar inversely correlated"),
    # Equities interrelations
    _e("sp500", "vix", N, 0.7, "Equity drops → vol spike (leverage effect)"),
    _e("sp500", "retail_sentiment", P, 0.5, "Market performance drives sentiment"),
    _e("nasdaq", "tech_sector", P, 0.9, "NASDAQ heavily weighted to tech"),
    _e("earnings_momentum", "sp500", P, 0.6, "Earnings drive equity returns"),
    _e("earnings_momentum", "nasdaq", P, 0.5, "Tech earnings drive NASDAQ"),
    _e("earnings_momentum", "tech_sector", P, 0.6, "Tech earnings drive sector"),
    # Currencies
    _e("dxy_index", "eurusd", N, 0.9, "Dollar strength → EUR/USD down"),
    _e("dxy_index", "usdjpy", P, 0.7, "Dollar strength → USD/JPY up"),
    _e("dxy_index", "gold", N, 0.5, "Strong dollar → gold weaker"),
    _e("dxy_index", "wti_crude", N, 0.3, "Strong dollar → commodities cheaper"),
    # China / Global
    _e("china_pmi", "copper", P, 0.6, "China growth → industrial metal demand"),
    _e("china_pmi", "wti_crude", P, 0.3, "China growth → energy demand"),
    _e("china_pmi", "sp500", P, 0.2, "China growth → global risk-on"),

    # --- Phase 2 edges: new nodes ---

    # PCE / Wage / Consumer confidence
    _e("pce_deflator", "fed_funds_rate", P, 0.6, "PCE is Fed's preferred inflation gauge → drives rate decisions"),
    _e("pce_deflator", "rate_expectations", P, 0.7, "Core PCE shifts rate path expectations"),
    _e("wage_growth", "us_cpi_yoy", P, 0.5, "Wage-price spiral — labor costs feed into CPI"),
    _e("wage_growth", "pce_deflator", P, 0.5, "Wage growth drives services inflation in PCE"),
    _e("wage_growth", "consumer_confidence", P, 0.4, "Rising wages boost consumer sentiment"),
    _e("unemployment_rate", "wage_growth", N, 0.5, "Tight labor market → wage pressure (Phillips curve)"),
    _e("consumer_confidence", "retail_sentiment", P, 0.7, "Consumer confidence drives retail investor mood"),
    _e("consumer_confidence", "sp500", P, 0.3, "Confidence → spending → earnings → equities"),

    # Monetary policy expansion
    _e("qe_pace", "fed_balance_sheet", P, 0.9, "QE pace directly drives balance sheet size"),
    _e("qe_pace", "us_10y_yield", N, 0.5, "Active QE suppresses long-term yields"),
    _e("qe_pace", "sp500", P, 0.4, "QE → liquidity → risk assets"),
    _e("global_central_bank_liquidity", "sp500", P, 0.4, "Global liquidity lifts all risk assets"),
    _e("global_central_bank_liquidity", "gold", P, 0.5, "Liquidity expansion → currency debasement fear → gold"),
    _e("global_central_bank_liquidity", "dxy_index", C, 0.3, "Depends on relative easing — if Fed eases more, dollar weakens"),

    # Geopolitics expansion
    _e("us_political_risk", "vix", P, 0.4, "Domestic uncertainty → equity volatility"),
    _e("us_political_risk", "dxy_index", N, 0.3, "Political instability → dollar weakens"),
    _e("us_political_risk", "sp500", N, 0.3, "Policy uncertainty → equity risk premium"),
    _e("sanctions_pressure", "wti_crude", P, 0.4, "Sanctions on producers → supply disruption fear"),
    _e("sanctions_pressure", "natural_gas", P, 0.4, "Energy sanctions → gas supply risk"),
    _e("sanctions_pressure", "gold", P, 0.3, "Sanctions → geopolitical hedge → gold"),
    _e("sanctions_pressure", "dxy_index", P, 0.2, "Sanctions strengthen dollar hegemony"),

    # Volatility expansion
    _e("skew_index", "vix", P, 0.4, "Elevated tail risk pricing → broad vol pickup"),
    _e("skew_index", "put_call_ratio", P, 0.3, "Tail risk fear → more OTM put demand"),
    _e("credit_default_swaps", "hy_credit_spread", P, 0.7, "CDS spreads lead cash credit spreads"),
    _e("credit_default_swaps", "ig_credit_spread", P, 0.6, "CDS market prices credit risk ahead of cash bonds"),
    _e("credit_default_swaps", "vix", P, 0.3, "Credit stress → equity vol contagion"),

    # Commodities expansion
    _e("natural_gas", "us_cpi_yoy", P, 0.3, "Natural gas → utilities + heating component of CPI"),
    _e("natural_gas", "energy_sector", P, 0.4, "Gas prices drive gas-weighted energy stocks"),
    _e("silver", "gold", P, 0.6, "Silver tracks gold as precious metal"),
    _e("silver", "copper", P, 0.3, "Silver has industrial demand overlap with copper"),
    _e("wheat", "us_cpi_yoy", P, 0.2, "Wheat → food component of CPI"),
    _e("geopolitical_risk_index", "wheat", P, 0.4, "Geopolitical risk → grain supply disruption"),

    # Russell 2000
    _e("russell2000", "sp500", P, 0.4, "Small-cap breadth confirms broad market trends"),
    _e("us_gdp_growth", "russell2000", P, 0.6, "Small caps more sensitive to domestic growth"),
    _e("fed_funds_rate", "russell2000", N, 0.5, "Small caps more leveraged → more rate sensitive"),
    _e("yield_curve_spread", "russell2000", P, 0.4, "Steeper curve → small cap banks benefit"),

    # Equity fundamentals expansion
    _e("pe_valuations", "sp500", N, 0.3, "Stretched valuations → mean-reversion risk"),
    _e("pe_valuations", "nasdaq", N, 0.4, "Growth/tech more vulnerable to PE compression"),
    _e("revenue_growth", "earnings_momentum", P, 0.7, "Revenue is the top-line driver of earnings"),
    _e("revenue_growth", "sp500", P, 0.4, "Revenue growth signals fundamental health"),
    _e("us_gdp_growth", "revenue_growth", P, 0.6, "Economic growth drives corporate revenue"),

    # USD/CNY
    _e("usdcny", "china_pmi", N, 0.3, "Yuan depreciation hurts Chinese purchasing power"),
    _e("trade_policy_tariffs", "usdcny", P, 0.4, "Tariffs → capital outflow from China → CNY weakens"),
    _e("dxy_index", "usdcny", P, 0.6, "Broad dollar strength lifts USD/CNY"),

    # Fund flows & positioning
    _e("fund_flows", "sp500", P, 0.5, "Net inflows → buying pressure → equities up"),
    _e("fund_flows", "us_10y_yield", N, 0.3, "Flows into bonds → yield compression"),
    _e("institutional_positioning", "sp500", P, 0.4, "Net long positioning supports equities"),
    _e("institutional_positioning", "vix", N, 0.3, "Heavy positioning → crowded trades → vol suppression"),
    _e("retail_sentiment", "fund_flows", P, 0.3, "Retail sentiment drives retail fund allocation"),

    # EU / Japan global
    _e("eu_hicp", "eurusd", C, 0.3, "EU inflation → ECB hawkishness → EUR strength (complex)"),
    _e("eu_hicp", "us_cpi_yoy", P, 0.2, "Global inflation co-moves across developed markets"),
    _e("japan_boj_policy", "usdjpy", N, 0.5, "BOJ hawkish shift → yen strengthens → USD/JPY falls"),
    _e("japan_boj_policy", "us_10y_yield", P, 0.2, "BOJ selling JGBs → global yield spillover"),
    _e("japan_boj_policy", "gold", P, 0.2, "BOJ policy shifts → currency volatility → gold demand"),
]

# ── Merged topology: expanded (111 nodes, 1071 edges) with MVP overrides ─────
# Expanded data is the primary source. MVP edges override expanded edges where
# both exist (same source+target) because MVP edges have hand-tuned weights.

def _merge():
    """Merge expanded topology with MVP overrides."""
    # Nodes: expanded is authoritative (superset of MVP)
    node_map = {n["id"]: n for n in EXPANDED_NODES}
    # MVP nodes can override descriptions/labels
    for n in MVP_NODES:
        if n["id"] in node_map:
            node_map[n["id"]].update(n)
        else:
            node_map[n["id"]] = n
    all_nodes = list(node_map.values())

    # Edges: start with expanded, then override with MVP (hand-tuned weights)
    edge_map = {}
    for e in EXPANDED_EDGES:
        key = (e["source_id"], e["target_id"])
        edge_map[key] = e
    for e in MVP_EDGES:
        key = (e["source_id"], e["target_id"])
        if key in edge_map:
            # MVP has hand-tuned weight — preserve it, but keep expanded lag/description if MVP lacks them
            merged = {**edge_map[key], **e}
            if e.get("transmission_lag_hours", 0) == 0 and edge_map[key].get("transmission_lag_hours", 0) > 0:
                merged["transmission_lag_hours"] = edge_map[key]["transmission_lag_hours"]
            edge_map[key] = merged
        else:
            edge_map[key] = e
    all_edges = list(edge_map.values())

    return all_nodes, all_edges

ALL_NODES, ALL_EDGES = _merge()
