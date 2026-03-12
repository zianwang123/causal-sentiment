"""FRED data fetcher — standalone pipeline for scheduled fetching."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

FRED_KEY_SERIES = [
    "FEDFUNDS",
    "CPIAUCSL",
    "GDP",
    "UNRATE",
    "T10Y2Y",
    "DGS2",
    "DGS10",
    "DGS30",
    "VIXCLS",
    "DTWEXBGS",
    "BAMLH0A0HYM2",
    "BAMLC0A0CM",
    "DCOILWTICO",
]


async def fetch_all_fred_series() -> dict[str, list[dict]]:
    """Fetch all key FRED series. Returns {series_id: [{date, value}]}."""
    if not settings.fred_api_key:
        logger.warning("FRED API key not set — skipping FRED fetch")
        return {}

    results = {}
    async with httpx.AsyncClient(timeout=15.0) as client:
        for series_id in FRED_KEY_SERIES:
            try:
                resp = await client.get(
                    "https://api.stlouisfed.org/fred/series/observations",
                    params={
                        "series_id": series_id,
                        "api_key": settings.fred_api_key,
                        "file_type": "json",
                        "sort_order": "desc",
                        "limit": 5,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                results[series_id] = [
                    {"date": obs["date"], "value": obs["value"]}
                    for obs in data.get("observations", [])
                    if obs["value"] != "."
                ]
            except Exception as e:
                logger.error("Failed to fetch FRED series %s: %s", series_id, e)
                results[series_id] = []

    return results
