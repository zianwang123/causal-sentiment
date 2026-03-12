"""SEC EDGAR data pipeline — free, no API key needed."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Major S&P 500 companies tracked: ticker -> (CIK, sector node mappings)
EDGAR_COMPANY_MAP: dict[str, dict] = {
    "AAPL":  {"cik": "0000320193", "name": "Apple Inc", "nodes": ["tech_sector", "earnings_momentum", "nasdaq"]},
    "MSFT":  {"cik": "0000789019", "name": "Microsoft Corp", "nodes": ["tech_sector", "earnings_momentum", "nasdaq"]},
    "AMZN":  {"cik": "0001018724", "name": "Amazon.com", "nodes": ["tech_sector", "earnings_momentum", "nasdaq"]},
    "GOOGL": {"cik": "0001652044", "name": "Alphabet Inc", "nodes": ["tech_sector", "earnings_momentum", "nasdaq"]},
    "META":  {"cik": "0001326801", "name": "Meta Platforms", "nodes": ["tech_sector", "earnings_momentum", "nasdaq"]},
    "NVDA":  {"cik": "0001045810", "name": "NVIDIA Corp", "nodes": ["tech_sector", "earnings_momentum", "nasdaq"]},
    "JPM":   {"cik": "0000019617", "name": "JPMorgan Chase", "nodes": ["financials_sector", "earnings_momentum"]},
    "GS":    {"cik": "0000886982", "name": "Goldman Sachs", "nodes": ["financials_sector", "earnings_momentum"]},
    "XOM":   {"cik": "0000034088", "name": "Exxon Mobil", "nodes": ["energy_sector", "earnings_momentum"]},
    "JNJ":   {"cik": "0000200406", "name": "Johnson & Johnson", "nodes": ["earnings_momentum", "sp500"]},
}

# SEC requires a descriptive User-Agent
def _user_agent() -> str:
    ua = settings.sec_edgar_user_agent
    if ua:
        return ua
    return "CausalSentiment/1.0 (causal-sentiment-engine)"

HEADERS = {
    "Accept": "application/json",
}


async def fetch_recent_filings(
    form_type: str = "10-Q",
    days: int = 30,
) -> list[dict]:
    """Search EDGAR full-text search for recent filings."""
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    url = "https://efts.sec.gov/LATEST/search-index"
    params = {
        "q": "*",
        "dateRange": "custom",
        "startdt": start_date,
        "enddt": end_date,
        "forms": form_type,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            resp = await client.get(
                url,
                params=params,
                headers={**HEADERS, "User-Agent": _user_agent()},
            )
            resp.raise_for_status()
            data = resp.json()
            hits = data.get("hits", {}).get("hits", [])
            return [
                {
                    "filing_type": h.get("_source", {}).get("form_type", form_type),
                    "company": h.get("_source", {}).get("entity_name", "Unknown"),
                    "filed_date": h.get("_source", {}).get("file_date", ""),
                    "accession": h.get("_source", {}).get("file_num", ""),
                }
                for h in hits[:20]
            ]
        except Exception as e:
            logger.error("EDGAR search failed: %s", e)
            return []


async def fetch_company_financials(ticker: str) -> dict | None:
    """Fetch XBRL company facts from SEC (revenue, EPS, net income)."""
    company = EDGAR_COMPANY_MAP.get(ticker.upper())
    if not company:
        return None

    cik = company["cik"]
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            resp = await client.get(
                url,
                headers={**HEADERS, "User-Agent": _user_agent()},
            )
            resp.raise_for_status()
            data = resp.json()

            facts = data.get("facts", {}).get("us-gaap", {})
            result: dict = {
                "ticker": ticker.upper(),
                "company": company["name"],
                "cik": cik,
                "nodes": company["nodes"],
                "financials": {},
            }

            # Extract key metrics
            for metric_key, label in [
                ("Revenues", "revenue"),
                ("RevenueFromContractWithCustomerExcludingAssessedTax", "revenue"),
                ("NetIncomeLoss", "net_income"),
                ("EarningsPerShareBasic", "eps"),
                ("EarningsPerShareDiluted", "eps_diluted"),
            ]:
                if metric_key in facts:
                    units = facts[metric_key].get("units", {})
                    # Get USD or USD/shares values
                    values = units.get("USD", units.get("USD/shares", []))
                    if values:
                        # Get most recent 10-Q and 10-K filings
                        recent = [
                            v for v in values
                            if v.get("form") in ("10-Q", "10-K")
                        ]
                        recent.sort(key=lambda x: x.get("end", ""), reverse=True)
                        if recent and label not in result["financials"]:
                            latest = recent[:4]  # Last 4 quarters
                            result["financials"][label] = [
                                {
                                    "period": v.get("end", ""),
                                    "value": v.get("val"),
                                    "form": v.get("form"),
                                }
                                for v in latest
                            ]

            # Compute YoY growth if we have enough data
            if "revenue" in result["financials"] and len(result["financials"]["revenue"]) >= 2:
                vals = result["financials"]["revenue"]
                if vals[0]["value"] and vals[-1]["value"] and vals[-1]["value"] != 0:
                    growth = (vals[0]["value"] - vals[-1]["value"]) / abs(vals[-1]["value"])
                    result["revenue_growth_pct"] = round(growth * 100, 2)

            if "eps" in result["financials"] and len(result["financials"]["eps"]) >= 2:
                vals = result["financials"]["eps"]
                if vals[0]["value"] is not None and vals[-1]["value"] is not None and vals[-1]["value"] != 0:
                    growth = (vals[0]["value"] - vals[-1]["value"]) / abs(vals[-1]["value"])
                    result["eps_growth_pct"] = round(growth * 100, 2)

            return result

        except Exception as e:
            logger.error("EDGAR company facts failed for %s: %s", ticker, e)
            return None


async def fetch_all_company_financials() -> list[dict]:
    """Fetch financials for all tracked companies."""
    import asyncio

    results = []
    for ticker in EDGAR_COMPANY_MAP:
        result = await fetch_company_financials(ticker)
        if result:
            results.append(result)
        await asyncio.sleep(0.15)  # SEC rate limit: 10 req/sec
    return results
