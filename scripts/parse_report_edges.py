#!/usr/bin/env python3
"""Parse MACRO_FACTOR_REPORT.md edge matrix tables into topology_expanded.py.

Reads the Markdown tables in the "Causal Edge Matrix" section and generates
a Python module with EXPANDED_NODES and EXPANDED_EDGES suitable for import
by topology.py.

Usage:
    python scripts/parse_report_edges.py
"""

import re
import sys
from pathlib import Path

REPORT_PATH = Path(__file__).parent.parent / "MACRO_FACTOR_REPORT.md"
OUTPUT_PATH = Path(__file__).parent.parent / "backend" / "app" / "graph_engine" / "topology_expanded.py"

# ── Name-to-ID mapping (111 factors) ──────────────────────────────────────────
# Maps the human-readable target names used in report edge tables to node IDs.
# Existing 52 nodes use their current IDs; new 59 nodes get descriptive IDs.

NAME_TO_ID = {
    # Category 1: US Macroeconomic Fundamentals (14)
    "Federal Funds Rate": "fed_funds_rate",
    "US CPI Year-over-Year": "us_cpi_yoy",
    "US GDP Growth": "us_gdp_growth",
    "Unemployment Rate": "unemployment_rate",
    "US Manufacturing PMI": "us_pmi",
    "Manufacturing PMI": "us_pmi",
    "PCE Deflator": "pce_deflator",
    "Consumer Confidence": "consumer_confidence",
    "Wage Growth": "wage_growth",
    "Initial Jobless Claims": "initial_jobless_claims",
    "Jobless Claims": "initial_jobless_claims",
    "JOLTS Job Openings": "jolts_job_openings",
    "Labor Force Participation Rate": "labor_force_participation",
    "Labor Force Participation": "labor_force_participation",
    "US Services PMI": "us_services_pmi",
    "Services PMI": "us_services_pmi",
    "US Fiscal Deficit": "us_fiscal_deficit",
    "Fiscal Deficit": "us_fiscal_deficit",
    "US Productivity Growth": "us_productivity",
    "Productivity": "us_productivity",
    # Category 2: Monetary Policy (7)
    "Fed Balance Sheet": "fed_balance_sheet",
    "Rate Expectations": "rate_expectations",
    "Rate Expectations (Fed Funds Futures)": "rate_expectations",
    "QE/QT Pace": "qe_pace",
    "QE Pace": "qe_pace",
    "Global Central Bank Liquidity": "global_central_bank_liquidity",
    "Global CB Liquidity": "global_central_bank_liquidity",
    "ECB Policy Rate": "ecb_policy_rate",
    "PBOC Policy": "pboc_policy",
    "Term Premium": "term_premium",
    # Category 3: Geopolitics (6)
    "Geopolitical Risk Index": "geopolitical_risk_index",
    "Geopolitical Risk": "geopolitical_risk_index",
    "Trade Policy / Tariffs": "trade_policy_tariffs",
    "Trade Policy Uncertainty": "trade_policy_tariffs",
    "Trade Policy": "trade_policy_tariffs",
    "US Political Risk": "us_political_risk",
    "Sanctions Pressure": "sanctions_pressure",
    "Sanctions Regime": "sanctions_pressure",
    "Sanctions": "sanctions_pressure",
    "Climate / Energy Transition Policy": "climate_policy",
    "Climate Policy": "climate_policy",
    "Tech / AI Regulation": "tech_regulation",
    "Tech Regulation": "tech_regulation",
    # Category 4: Rates & Credit (10)
    "US 2Y Yield": "us_2y_yield",
    "2Y Treasury Yield": "us_2y_yield",
    "2-Year Treasury Yield": "us_2y_yield",
    "US 10Y Yield": "us_10y_yield",
    "10Y Treasury Yield": "us_10y_yield",
    "10-Year Treasury Yield": "us_10y_yield",
    "US 30Y Yield": "us_30y_yield",
    "30Y Treasury Yield": "us_30y_yield",
    "30-Year Treasury Yield": "us_30y_yield",
    "Yield Curve Spread": "yield_curve_spread",
    "Yield Curve Spread (10Y-2Y)": "yield_curve_spread",
    "IG Credit Spread": "ig_credit_spread",
    "Investment Grade Credit Spread": "ig_credit_spread",
    "HY Credit Spread": "hy_credit_spread",
    "High Yield Credit Spread": "hy_credit_spread",
    "US 10Y Real Yield (TIPS)": "us_real_yield",
    "Real Yield (TIPS)": "us_real_yield",
    "Real Yield": "us_real_yield",
    "10Y Breakeven Inflation": "breakeven_inflation",
    "Breakeven Inflation": "breakeven_inflation",
    "Breakevens": "breakeven_inflation",
    "5Y5Y Forward Inflation": "forward_inflation_5y5y",
    "EM Sovereign Spread (EMBI)": "em_sovereign_spread",
    "EM Sovereign Spread": "em_sovereign_spread",
    # Category 5: Volatility (6)
    "VIX": "vix",
    "MOVE Index": "move_index",
    "Put/Call Ratio": "put_call_ratio",
    "SKEW Index": "skew_index",
    "SKEW": "skew_index",
    "Credit Default Swaps": "credit_default_swaps",
    "CDS Spreads": "credit_default_swaps",
    "CDS Spreads (IG CDX)": "credit_default_swaps",
    "FX Implied Volatility": "fx_volatility",
    "FX Volatility": "fx_volatility",
    # Category 6: Commodities (10)
    "WTI Crude Oil": "wti_crude",
    "Brent Crude Oil": "wti_crude",
    "Gold": "gold",
    "Copper": "copper",
    "Natural Gas": "natural_gas",
    "Silver": "silver",
    "Wheat": "wheat",
    "Soybeans": "soybeans",
    "Iron Ore": "iron_ore",
    "Lithium": "lithium",
    "Uranium": "uranium",
    # Category 7: Equities (14)
    "S&P 500": "sp500",
    "NASDAQ": "nasdaq",
    "NASDAQ Composite": "nasdaq",
    "Tech Sector": "tech_sector",
    "Energy Sector": "energy_sector",
    "Financials Sector": "financials_sector",
    "Financials": "financials_sector",
    "Russell 2000": "russell2000",
    "Healthcare Sector": "healthcare_sector",
    "Healthcare": "healthcare_sector",
    "REITs": "reits",
    "Regional Banks": "regional_banks",
    "EM Equities": "em_equities",
    "Europe Equities": "europe_equities",
    "China Equities": "china_equities",
    "Japan Equities (Nikkei)": "japan_equities",
    "Japan Equities": "japan_equities",
    "Semiconductors": "semiconductors",
    # Category 8: Equity Fundamentals (5)
    "Earnings Momentum": "earnings_momentum",
    "P/E Valuations": "pe_valuations",
    "PE Valuations": "pe_valuations",
    "PE Valuations (Shiller CAPE)": "pe_valuations",
    "Revenue Growth": "revenue_growth",
    "Equity Risk Premium": "equity_risk_premium",
    "Corporate Buybacks": "corporate_buybacks",
    "Buybacks": "corporate_buybacks",
    # Category 9: Currencies (7)
    "US Dollar Index (DXY)": "dxy_index",
    "US Dollar Index": "dxy_index",
    "DXY": "dxy_index",
    "EUR/USD": "eurusd",
    "USD/JPY": "usdjpy",
    "USD/CNY": "usdcny",
    "GBP/USD": "gbpusd",
    "EM FX Basket": "em_fx_basket",
    "Bitcoin": "bitcoin",
    # Category 10: Flows & Sentiment (5)
    "Retail Sentiment": "retail_sentiment",
    "Retail Sentiment (AAII Survey)": "retail_sentiment",
    "Fund Flows": "fund_flows",
    "Fund Flows (ICI Weekly)": "fund_flows",
    "Institutional Positioning (COT)": "institutional_positioning",
    "Institutional Positioning": "institutional_positioning",
    "Institutional Positioning (CFTC COT)": "institutional_positioning",
    "Margin Debt / Leverage": "margin_debt",
    "Margin Debt": "margin_debt",
    "Margin Debt (FINRA)": "margin_debt",
    "ETF Flows": "etf_flows",
    # Category 11: Global (8)
    "China PMI": "china_pmi",
    "China PMI (Caixin Manufacturing)": "china_pmi",
    "EU HICP": "eu_hicp",
    "EU HICP (Eurozone Inflation)": "eu_hicp",
    "BOJ Policy": "japan_boj_policy",
    "China Credit Impulse": "china_credit_impulse",
    "China Property Sector": "china_property",
    "China Property Market": "china_property",
    "China Property": "china_property",
    "EU Periphery Spreads (Italy-Germany)": "eu_periphery_spreads",
    "EU Periphery Spreads": "eu_periphery_spreads",
    "EU Periphery Spreads (BTP-Bund)": "eu_periphery_spreads",
    "Global Trade Volume": "global_trade_volume",
    "India Growth": "india_growth",
    "India Growth Rate": "india_growth",
    # Category 12: Housing / Real Estate (4)
    "US Housing Starts": "housing_starts",
    "Housing Starts": "housing_starts",
    "US Home Prices (Case-Shiller)": "home_prices",
    "Home Prices (Case-Shiller)": "home_prices",
    "Home Prices": "home_prices",
    "30-Year Mortgage Rate": "mortgage_rate",
    "Mortgage Rate (30Y Fixed)": "mortgage_rate",
    "Mortgage Rate": "mortgage_rate",
    "Commercial Real Estate Stress": "cre_stress",
    "CRE Stress": "cre_stress",
    # Category 13: Financial System / Banking (4)
    "Financial Conditions Index": "financial_conditions_index",
    "Financial Conditions Index (FCI)": "financial_conditions_index",
    "Financial Conditions": "financial_conditions_index",
    "FCI": "financial_conditions_index",
    "Bank Lending Standards": "bank_lending_standards",
    "Lending Standards": "bank_lending_standards",
    "Bank Reserves at the Fed": "bank_reserves",
    "Bank Reserves": "bank_reserves",
    "Repo / SOFR Rate": "repo_sofr_rate",
    "Repo/SOFR Rate": "repo_sofr_rate",
    "Repo/SOFR": "repo_sofr_rate",
    # Category 14: Money Markets / Funding (3)
    "TED Spread (SOFR-Treasury)": "ted_spread",
    "TED Spread": "ted_spread",
    "Money Market Fund Flows": "mmf_flows",
    "MMF Flows": "mmf_flows",
    "Commercial Paper Spread": "commercial_paper_spread",
    "CP Spread": "commercial_paper_spread",
    # Category 15: Fiscal Policy / Sovereign (3)
    "US Debt-to-GDP": "us_debt_to_gdp",
    "Debt-to-GDP Ratio": "us_debt_to_gdp",
    "Debt-to-GDP": "us_debt_to_gdp",
    "Debt/GDP": "us_debt_to_gdp",
    "Treasury Issuance / Supply": "treasury_issuance",
    "Treasury Issuance": "treasury_issuance",
    "US Government Spending": "government_spending",
    "Government Spending": "government_spending",
    # Category 16: Supply Chain / Trade Infrastructure (3)
    "Supply Chain Pressure Index": "supply_chain_pressure",
    "Supply Chain Pressure": "supply_chain_pressure",
    "Baltic Dry Index": "baltic_dry_index",
    "Container Shipping Rates": "container_shipping_rates",
    "Container Shipping Rates (Freightos/Drewry)": "container_shipping_rates",
    # Category 17: Private Credit / Alternatives (2)
    "Private Credit / CLO Conditions": "private_credit",
    "Private Credit": "private_credit",
    "IPO / Equity Issuance": "ipo_issuance",
    "IPO Issuance": "ipo_issuance",
    # Short aliases commonly used in edge table target columns
    "CPI": "us_cpi_yoy",
    "GDP Growth": "us_gdp_growth",
    "GDP": "us_gdp_growth",
    "Fed Funds Rate": "fed_funds_rate",
    # Misc aliases used in edge tables
    "Recession Probability": "yield_curve_spread",  # proxy — yield curve IS the recession indicator
    "Mining Equities": "energy_sector",  # proxy
    "Lumber/Timber": "housing_starts",  # proxy — not a standalone factor
    "Quits Rate → GDP": "us_gdp_growth",  # proxy
}

# ── Lag string to hours mapping ──────────────────────────────────────────────

LAG_TO_HOURS = {
    "hours": 4.0,
    "hours-days": 12.0,
    "days": 24.0,
    "days-weeks": 72.0,
    "weeks": 168.0,
    "weeks-months": 504.0,
    "months": 720.0,
    "months-quarters": 1440.0,
    "quarters": 2160.0,
}

# ── Node definitions (all 111) ───────────────────────────────────────────────
# category_name: list of (id, label, description)

NODE_DEFS = {
    "macro": [
        ("fed_funds_rate", "Fed Funds Rate", "Federal Reserve target interest rate"),
        ("us_cpi_yoy", "US CPI YoY", "US Consumer Price Index year-over-year change"),
        ("us_gdp_growth", "US GDP Growth", "US real GDP quarter-over-quarter annualized growth rate"),
        ("unemployment_rate", "Unemployment Rate", "US civilian unemployment rate"),
        ("us_pmi", "US Manufacturing PMI", "ISM Manufacturing Purchasing Managers Index"),
        ("pce_deflator", "PCE Deflator", "Personal Consumption Expenditures price index — Fed's preferred inflation gauge"),
        ("consumer_confidence", "Consumer Confidence", "University of Michigan / Conference Board consumer confidence index"),
        ("wage_growth", "Wage Growth", "Average hourly earnings year-over-year growth"),
        ("initial_jobless_claims", "Initial Jobless Claims", "Weekly initial unemployment insurance claims — highest-frequency labor market indicator"),
        ("jolts_job_openings", "JOLTS Job Openings", "Job Openings and Labor Turnover Survey — Beveridge Curve anchor"),
        ("labor_force_participation", "Labor Force Participation", "Civilian labor force participation rate — explains why unemployment rate lies"),
        ("us_services_pmi", "US Services PMI", "ISM Services PMI — 80% of US GDP"),
        ("us_fiscal_deficit", "US Fiscal Deficit", "Federal budget deficit as % of GDP"),
        ("us_productivity", "US Productivity Growth", "Nonfarm business labor productivity — speed limit of non-inflationary growth"),
    ],
    "monetary_policy": [
        ("fed_balance_sheet", "Fed Balance Sheet", "Total Federal Reserve balance sheet assets"),
        ("rate_expectations", "Rate Expectations", "Fed funds futures implied rate path"),
        ("qe_pace", "QE/QT Pace", "Pace of quantitative easing or tightening (asset purchases/sales per month)"),
        ("global_central_bank_liquidity", "Global CB Liquidity", "Aggregate global central bank balance sheet expansion/contraction"),
        ("ecb_policy_rate", "ECB Policy Rate", "European Central Bank main refinancing rate"),
        ("pboc_policy", "PBOC Policy", "People's Bank of China monetary policy stance — RRR, LPR, liquidity injections"),
        ("term_premium", "Term Premium", "Compensation for uncertainty about holding long-duration bonds"),
    ],
    "geopolitics": [
        ("geopolitical_risk_index", "Geopolitical Risk", "Composite geopolitical risk index based on news coverage"),
        ("trade_policy_tariffs", "Trade Policy / Tariffs", "Trade policy sentiment and tariff regime changes"),
        ("us_political_risk", "US Political Risk", "Domestic political uncertainty — elections, policy shifts, government shutdowns"),
        ("sanctions_pressure", "Sanctions Pressure", "Intensity of international economic sanctions and enforcement"),
        ("climate_policy", "Climate / Energy Transition", "Carbon pricing, green subsidies, energy transition regulatory regime"),
        ("tech_regulation", "Tech / AI Regulation", "Technology regulation — chip export controls, antitrust, AI Act"),
    ],
    "rates_credit": [
        ("us_2y_yield", "US 2Y Yield", "US 2-year Treasury yield"),
        ("us_10y_yield", "US 10Y Yield", "US 10-year Treasury yield"),
        ("us_30y_yield", "US 30Y Yield", "US 30-year Treasury yield"),
        ("yield_curve_spread", "Yield Curve Spread", "10Y minus 2Y Treasury spread"),
        ("ig_credit_spread", "IG Credit Spread", "Investment grade corporate bond spread over Treasuries"),
        ("hy_credit_spread", "HY Credit Spread", "High yield corporate bond spread over Treasuries"),
        ("us_real_yield", "US 10Y Real Yield", "10Y TIPS yield — the real discount rate"),
        ("breakeven_inflation", "Breakeven Inflation", "10Y breakeven inflation rate — market inflation expectations"),
        ("forward_inflation_5y5y", "5Y5Y Forward Inflation", "5-year, 5-year forward inflation expectation — Fed's preferred anchoring measure"),
        ("em_sovereign_spread", "EM Sovereign Spread", "JP Morgan EMBI+ spread — aggregate EM credit risk"),
    ],
    "volatility": [
        ("vix", "VIX", "CBOE Volatility Index — S&P 500 implied volatility"),
        ("move_index", "MOVE Index", "Merrill Lynch bond market volatility index"),
        ("put_call_ratio", "Put/Call Ratio", "CBOE equity put/call volume ratio"),
        ("skew_index", "SKEW Index", "CBOE SKEW index — tail risk pricing in S&P 500 options"),
        ("credit_default_swaps", "CDS Spreads", "Investment grade CDS index — market-priced credit risk"),
        ("fx_volatility", "FX Implied Volatility", "G10 FX implied volatility — currency market stress"),
    ],
    "commodities": [
        ("wti_crude", "Brent Crude Oil", "Brent/WTI crude oil price"),
        ("gold", "Gold", "Gold spot price (USD/oz)"),
        ("copper", "Copper", "Copper futures price — industrial bellwether"),
        ("natural_gas", "Natural Gas", "Henry Hub natural gas spot price"),
        ("silver", "Silver", "Silver spot price (USD/oz) — industrial + precious metal"),
        ("wheat", "Wheat", "Wheat futures price — food inflation bellwether"),
        ("soybeans", "Soybeans", "Soybean futures — US-China agricultural trade barometer"),
        ("iron_ore", "Iron Ore", "Iron ore price — highest-fidelity indicator of China construction activity"),
        ("lithium", "Lithium", "Lithium price — EV supply chain and green energy transition health"),
        ("uranium", "Uranium", "Uranium price — nuclear renaissance and AI power demand"),
    ],
    "equities": [
        ("sp500", "S&P 500", "S&P 500 index level"),
        ("nasdaq", "NASDAQ", "NASDAQ Composite index level"),
        ("tech_sector", "Tech Sector", "Technology sector performance (XLK)"),
        ("energy_sector", "Energy Sector", "Energy sector performance (XLE)"),
        ("financials_sector", "Financials Sector", "Financial sector performance (XLF)"),
        ("russell2000", "Russell 2000", "Russell 2000 small-cap index — domestic growth proxy"),
        ("healthcare_sector", "Healthcare Sector", "Healthcare sector — defensive with distinct policy drivers"),
        ("reits", "REITs", "Real estate investment trusts — liquid CRE proxy"),
        ("regional_banks", "Regional Banks", "KRE regional bank ETF — CRE exposure, small business lending"),
        ("em_equities", "EM Equities", "MSCI Emerging Markets equity index"),
        ("europe_equities", "Europe Equities", "Euro Stoxx 50 — European equity benchmark"),
        ("china_equities", "China Equities", "CSI 300 / Hang Seng — Chinese equity markets"),
        ("japan_equities", "Japan Equities", "Nikkei 225 — Japanese equity benchmark, carry trade barometer"),
        ("semiconductors", "Semiconductors", "SOX semiconductor index — AI capex + chip war nexus"),
    ],
    "equity_fundamentals": [
        ("earnings_momentum", "Earnings Momentum", "Aggregate earnings revision and surprise trends"),
        ("pe_valuations", "P/E Valuations", "S&P 500 forward P/E ratio — valuation stretch indicator"),
        ("revenue_growth", "Revenue Growth", "Aggregate S&P 500 revenue growth rate"),
        ("equity_risk_premium", "Equity Risk Premium", "Earnings yield minus real yield — equity attractiveness vs bonds"),
        ("corporate_buybacks", "Corporate Buybacks", "S&P 500 aggregate share buyback activity — ~$1T/year"),
    ],
    "currencies": [
        ("dxy_index", "DXY Index", "US Dollar Index"),
        ("eurusd", "EUR/USD", "Euro vs US Dollar exchange rate"),
        ("usdjpy", "USD/JPY", "US Dollar vs Japanese Yen exchange rate"),
        ("usdcny", "USD/CNY", "US Dollar vs Chinese Yuan exchange rate"),
        ("gbpusd", "GBP/USD", "British Pound vs US Dollar — fiscal credibility barometer"),
        ("em_fx_basket", "EM FX Basket", "Aggregate emerging market currency basket"),
        ("bitcoin", "Bitcoin", "Bitcoin price — $1T+ asset class, institutional adoption via ETFs"),
    ],
    "flows_sentiment": [
        ("retail_sentiment", "Retail Sentiment", "Aggregate retail investor sentiment from social media and surveys"),
        ("fund_flows", "Fund Flows", "Net flows into equity/bond/money market funds"),
        ("institutional_positioning", "Institutional Positioning", "CFTC COT data — net speculative positioning in futures markets"),
        ("margin_debt", "Margin Debt", "FINRA margin debt — leverage amplifier ($936B peak Oct 2021)"),
        ("etf_flows", "ETF Flows", "ETF creation/redemption flows — passive investing structural force"),
    ],
    "global": [
        ("china_pmi", "China PMI", "China Caixin Manufacturing PMI"),
        ("eu_hicp", "EU HICP", "Eurozone Harmonised Index of Consumer Prices"),
        ("japan_boj_policy", "BOJ Policy", "Bank of Japan monetary policy stance"),
        ("china_credit_impulse", "China Credit Impulse", "Change in total social financing as % of GDP — leads global PMIs by 6-9 months"),
        ("china_property", "China Property Sector", "China property market health — ~30% of GDP"),
        ("eu_periphery_spreads", "EU Periphery Spreads", "Italy-Germany 10Y spread — Eurozone fragmentation risk"),
        ("global_trade_volume", "Global Trade Volume", "WTO/CPB world trade monitor — goods crossing borders"),
        ("india_growth", "India Growth", "India GDP growth — 5th largest economy, fastest-growing major economy"),
    ],
    "housing": [
        ("housing_starts", "US Housing Starts", "New residential construction starts — most rate-sensitive leading indicator"),
        ("home_prices", "US Home Prices", "Case-Shiller home price index — $45T asset class, wealth effect driver"),
        ("mortgage_rate", "30-Year Mortgage Rate", "30Y fixed mortgage rate — direct Fed-to-consumer transmission"),
        ("cre_stress", "Commercial Real Estate Stress", "CRE vacancy, valuations, loan delinquency — slow-motion crisis"),
    ],
    "financial_system": [
        ("financial_conditions_index", "Financial Conditions Index", "Chicago Fed NFCI — aggregate of 105 financial indicators"),
        ("bank_lending_standards", "Bank Lending Standards", "Fed SLOOS — most reliable predictor of credit availability"),
        ("bank_reserves", "Bank Reserves", "Reserves at the Fed — money market plumbing health"),
        ("repo_sofr_rate", "Repo / SOFR Rate", "Secured Overnight Financing Rate — financial system heartbeat"),
    ],
    "money_markets": [
        ("ted_spread", "TED Spread", "SOFR minus T-bill — fastest indicator of counterparty/funding stress"),
        ("mmf_flows", "Money Market Fund Flows", "$6T+ force that can destabilize banking via deposit competition"),
        ("commercial_paper_spread", "Commercial Paper Spread", "CP rates — how large corporations fund daily operations"),
    ],
    "fiscal_policy": [
        ("us_debt_to_gdp", "US Debt-to-GDP", "Federal debt as % of GDP — structural constraint on future policy"),
        ("treasury_issuance", "Treasury Issuance", "Net new Treasury supply — marginal price setter for risk-free rate"),
        ("government_spending", "US Government Spending", "Federal spending change — fiscal impulse to GDP"),
    ],
    "supply_chain": [
        ("supply_chain_pressure", "Supply Chain Pressure Index", "NY Fed GSCPI — aggregate supply chain stress"),
        ("baltic_dry_index", "Baltic Dry Index", "Bulk commodity shipping costs — purest demand signal"),
        ("container_shipping_rates", "Container Shipping Rates", "Freightos/Drewry container rates — consumer goods trade costs"),
    ],
    "private_credit": [
        ("private_credit", "Private Credit / CLO", "$1.5T+ opaque market — fastest-growing, least monitored"),
        ("ipo_issuance", "IPO / Equity Issuance", "IPO activity — risk appetite and capital formation proxy"),
    ],
}


def resolve_target(name: str) -> str | None:
    """Resolve a target name from the report to a node ID."""
    name = name.strip()
    if name in NAME_TO_ID:
        return NAME_TO_ID[name]
    # Try fuzzy matching — strip parenthetical suffixes
    base = re.sub(r"\s*\(.*\)$", "", name).strip()
    if base in NAME_TO_ID:
        return NAME_TO_ID[base]
    return None


def parse_lag(lag_str: str) -> float:
    """Convert lag string to hours."""
    lag_str = lag_str.strip().lower()
    if lag_str in LAG_TO_HOURS:
        return LAG_TO_HOURS[lag_str]
    # Handle compound like "months-quarters"
    for key in sorted(LAG_TO_HOURS.keys(), key=len, reverse=True):
        if key in lag_str:
            return LAG_TO_HOURS[key]
    return 24.0  # default: days


def parse_direction(dir_str: str) -> str:
    """Convert direction symbol to EdgeDirection value."""
    d = dir_str.strip()
    if d == "+":
        return "POSITIVE"
    elif d in ("−", "-", "–"):
        return "NEGATIVE"
    elif d in ("±", "+/-", "+-"):
        return "COMPLEX"
    return "POSITIVE"


def parse_report():
    """Parse edge matrix tables from the report."""
    content = REPORT_PATH.read_text()
    lines = content.split("\n")

    # Find the "Causal Edge Matrix" section
    matrix_start = None
    matrix_end = None
    for i, line in enumerate(lines):
        if "## Causal Edge Matrix" in line:
            matrix_start = i
        elif matrix_start and line.startswith("## ") and i > matrix_start + 5:
            matrix_end = i
            break
    if matrix_end is None:
        matrix_end = len(lines)

    if matrix_start is None:
        print("ERROR: Could not find '## Causal Edge Matrix' section")
        sys.exit(1)

    matrix_lines = lines[matrix_start:matrix_end]

    edges = []
    current_source = None
    current_source_id = None
    in_table = False
    unresolved = set()

    for i, line in enumerate(matrix_lines):
        # Detect source factor header: **Name** (N edges)
        header_match = re.match(r"\*\*(.+?)\*\*(?:\s*\(.*?\))?\s*$", line.strip())
        if header_match:
            source_name = header_match.group(1).strip()
            current_source_id = resolve_target(source_name)
            if current_source_id is None:
                unresolved.add(f"SOURCE: {source_name}")
            current_source = source_name
            in_table = False
            continue

        # Detect table header
        if "| Target | Dir | Lag | Mechanism |" in line:
            in_table = True
            continue

        # Skip separator line
        if in_table and re.match(r"\|[-\s|]+\|$", line.strip()):
            continue

        # Parse data row: | Target | Dir | Lag | Mechanism |
        if in_table and line.strip().startswith("|") and current_source_id:
            parts = line.split("|")
            if len(parts) >= 5:
                target_name = parts[1].strip()
                direction = parts[2].strip()
                lag = parts[3].strip()
                mechanism = parts[4].strip()
                # Some mechanism text may contain | characters
                if len(parts) > 5:
                    mechanism = "|".join(parts[4:-1]).strip()

                target_id = resolve_target(target_name)
                if target_id is None:
                    unresolved.add(f"TARGET: {target_name} (from {current_source})")
                    continue

                if target_id == current_source_id:
                    continue  # skip self-loops

                edges.append({
                    "source_id": current_source_id,
                    "target_id": target_id,
                    "direction": parse_direction(direction),
                    "lag_hours": parse_lag(lag),
                    "description": mechanism.rstrip(" |"),
                })

        # End of table (blank line or next section)
        if in_table and not line.strip():
            in_table = False

    if unresolved:
        print(f"\nWARNING: {len(unresolved)} unresolved names:")
        for name in sorted(unresolved):
            print(f"  {name}")

    # Deduplicate edges (keep first occurrence)
    seen = set()
    unique_edges = []
    for e in edges:
        key = (e["source_id"], e["target_id"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    return unique_edges


def generate_output(edges):
    """Generate topology_expanded.py."""
    # Build nodes list
    all_nodes = []
    for category, nodes in NODE_DEFS.items():
        for node_id, label, desc in nodes:
            all_nodes.append((node_id, label, category, desc))

    # Verify all edge source/target IDs exist in node list
    node_ids = {n[0] for n in all_nodes}
    for e in edges:
        if e["source_id"] not in node_ids:
            print(f"WARNING: Edge source '{e['source_id']}' not in node list")
        if e["target_id"] not in node_ids:
            print(f"WARNING: Edge target '{e['target_id']}' not in node list")

    output = '''"""Expanded topology — 111 factors, 1080+ edges with temporal lags.

Auto-generated by scripts/parse_report_edges.py from MACRO_FACTOR_REPORT.md.
Do not edit manually — regenerate from the report.
"""

from app.models.graph import EdgeDirection, NodeType

P = EdgeDirection.POSITIVE
N = EdgeDirection.NEGATIVE
C = EdgeDirection.COMPLEX

EXPANDED_NODES = [
'''
    for node_id, label, category, desc in all_nodes:
        nt = f"NodeType.{category.upper()}"
        output += f'    {{"id": "{node_id}", "label": "{label}", "node_type": {nt}, "description": "{desc}"}},\n'

    output += "]\n\nEXPANDED_EDGES = [\n"

    for e in edges:
        d = e["direction"][0]  # P, N, or C
        desc_escaped = e["description"].replace('"', '\\"').replace("'", "\\'")
        output += (
            f'    {{"source_id": "{e["source_id"]}", "target_id": "{e["target_id"]}", '
            f'"direction": {d}, "base_weight": 0.5, "dynamic_weight": 0.5, '
            f'"transmission_lag_hours": {e["lag_hours"]}, '
            f'"description": "{desc_escaped}"}},\n'
        )

    output += "]\n"

    return output


def main():
    print(f"Reading report from {REPORT_PATH}")
    edges = parse_report()
    print(f"Parsed {len(edges)} unique edges")

    # Count nodes
    total_nodes = sum(len(nodes) for nodes in NODE_DEFS.values())
    print(f"Defined {total_nodes} nodes across {len(NODE_DEFS)} categories")

    output = generate_output(edges)
    OUTPUT_PATH.write_text(output)
    print(f"Written to {OUTPUT_PATH}")
    print(f"  {total_nodes} nodes, {len(edges)} edges")


if __name__ == "__main__":
    main()
