"""Economic calendar — upcoming macro events for scenario analysis.

Provides a forward-looking calendar of scheduled macro releases so the
scenario agent knows what catalysts are coming. Uses:
1. Hardcoded FOMC dates (public, known years in advance)
2. Rule-based recurring releases (CPI, NFP, GDP, PCE, ISM)
3. Optional: FRED releases API for precise dates (uses FRED_API_KEY)
"""

from __future__ import annotations

import asyncio
import calendar
import logging
from datetime import date, datetime, timedelta

import httpx

logger = logging.getLogger(__name__)

# ── FOMC meeting dates (announcement day) ────────────────────────────

FOMC_DATES: dict[int, list[str]] = {
    2025: [
        "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
        "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
    ],
    2026: [
        "2026-01-28", "2026-03-18", "2026-05-06", "2026-06-17",
        "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09",
    ],
    2027: [
        "2027-01-27", "2027-03-17", "2027-05-05", "2027-06-16",
        "2027-07-28", "2027-09-15", "2027-10-27", "2027-12-15",
    ],
}


def _first_friday(year: int, month: int) -> date:
    """Return the first Friday of the given month."""
    cal = calendar.Calendar(firstweekday=0)
    for day in cal.itermonthdays2(year, month):
        if day[0] != 0 and day[1] == 4:  # 4 = Friday
            return date(year, month, day[0])
    return date(year, month, 7)  # fallback


def _compute_upcoming_recurring(today: date, days_ahead: int) -> list[dict]:
    """Generate approximate dates for recurring macro releases."""
    events: list[dict] = []
    end = today + timedelta(days=days_ahead)

    # Iterate month-by-month from current to end
    current = today.replace(day=1)
    while current <= end:
        y, m = current.year, current.month

        # NFP / Jobs Report — first Friday of month
        nfp_date = _first_friday(y, m)
        if today <= nfp_date <= end:
            events.append({
                "name": "Nonfarm Payrolls (NFP)",
                "date": nfp_date.isoformat(),
                "type": "employment",
                "description": "Monthly jobs report — key driver of Fed policy expectations",
            })

        # CPI — typically 10th-14th of month
        cpi_date = date(y, m, 12)  # approximate mid-range
        if today <= cpi_date <= end:
            events.append({
                "name": "CPI Release",
                "date": cpi_date.isoformat(),
                "type": "inflation",
                "description": "Consumer Price Index — primary inflation gauge, directly impacts Fed path",
            })

        # PCE — typically 25th-30th of month
        pce_date = date(y, m, min(28, calendar.monthrange(y, m)[1]))
        if today <= pce_date <= end:
            events.append({
                "name": "PCE Price Index",
                "date": pce_date.isoformat(),
                "type": "inflation",
                "description": "Personal Consumption Expenditures — the Fed's preferred inflation measure",
            })

        # ISM Manufacturing — 1st business day of month
        ism_date = date(y, m, 1)
        if ism_date.weekday() == 5:  # Saturday
            ism_date = date(y, m, 3)
        elif ism_date.weekday() == 6:  # Sunday
            ism_date = date(y, m, 2)
        if today <= ism_date <= end:
            events.append({
                "name": "ISM Manufacturing PMI",
                "date": ism_date.isoformat(),
                "type": "activity",
                "description": "Manufacturing activity survey — leading indicator of economic direction",
            })

        # GDP (advance) — quarterly, end of month following quarter end
        if m in (1, 4, 7, 10):
            gdp_date = date(y, m, min(28, calendar.monthrange(y, m)[1]))
            if today <= gdp_date <= end:
                events.append({
                    "name": "GDP (Advance Estimate)",
                    "date": gdp_date.isoformat(),
                    "type": "growth",
                    "description": "First estimate of quarterly GDP growth",
                })

        # Advance to next month
        if m == 12:
            current = date(y + 1, 1, 1)
        else:
            current = date(y, m + 1, 1)

    return events


def _get_fomc_events(today: date, days_ahead: int) -> list[dict]:
    """Return upcoming FOMC meetings from the hardcoded calendar."""
    events: list[dict] = []
    end = today + timedelta(days=days_ahead)

    for year, dates in FOMC_DATES.items():
        for d_str in dates:
            d = date.fromisoformat(d_str)
            if today <= d <= end:
                events.append({
                    "name": "FOMC Meeting (Rate Decision)",
                    "date": d.isoformat(),
                    "type": "monetary_policy",
                    "description": "Federal Reserve rate decision — highest-impact scheduled macro event",
                })
    return events


async def _fetch_fred_releases(days_ahead: int) -> list[dict]:
    """Optionally fetch precise release dates from FRED API."""
    try:
        from app.config import settings
        api_key = settings.fred_api_key
        if not api_key:
            return []
    except Exception:
        return []

    today = datetime.utcnow().date()
    end = today + timedelta(days=days_ahead)

    url = "https://api.stlouisfed.org/fred/releases/dates"
    params = {
        "api_key": api_key,
        "file_type": "json",
        "realtime_start": today.isoformat(),
        "realtime_end": end.isoformat(),
        "include_release_dates_with_no_data": "false",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        events: list[dict] = []
        for item in data.get("release_dates", []):
            events.append({
                "name": item.get("release_name", "Unknown Release"),
                "date": item.get("date", ""),
                "type": "fred_release",
                "description": f"FRED release ID {item.get('release_id', '?')}",
            })
        return events
    except Exception as e:
        logger.debug("FRED releases API failed (non-fatal): %s", e)
        return []


async def get_economic_calendar(days_ahead: int = 30) -> list[dict]:
    """Return upcoming macro events in the next N days.

    Merges:
    1. Hardcoded FOMC dates
    2. Rule-based recurring releases (CPI, NFP, GDP, PCE, ISM)
    3. Optional FRED releases API (if FRED_API_KEY is configured)

    Returns list of {name, date, type, description} sorted by date.
    """
    days_ahead = max(1, min(days_ahead, 90))
    today = datetime.utcnow().date()

    # Gather from all sources
    fomc_events = _get_fomc_events(today, days_ahead)
    recurring_events = _compute_upcoming_recurring(today, days_ahead)

    # Optionally fetch from FRED (non-blocking, non-fatal)
    fred_events = await _fetch_fred_releases(days_ahead)

    # Merge and deduplicate (prefer FRED precise dates over rule-based)
    all_events = fomc_events + recurring_events + fred_events

    # Deduplicate by (name-prefix, date) — FRED names may differ slightly
    seen: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for ev in all_events:
        key = (ev["name"][:20].lower(), ev["date"])
        if key not in seen:
            seen.add(key)
            deduped.append(ev)

    # Sort by date
    deduped.sort(key=lambda e: e["date"])
    return deduped
