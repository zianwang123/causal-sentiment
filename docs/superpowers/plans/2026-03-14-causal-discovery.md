# Causal Discovery Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained `causal_discovery` module that fetches historical financial data, stores it in a TimescaleDB hypertable, computes z-scores, discovers causal edges using PCMCI/VARLiNGAM, infers display polarity via anchor propagation, and exposes the discovered graph via REST API.

**Architecture:** Feature module pattern — all code lives under `backend/app/causal_discovery/` with own models, pipeline, engine, and API. Only ~3 lines added to `main.py`. Reuses existing DB connection, propagation engine, and frontend Graph3D component.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy + asyncpg, TimescaleDB hypertable, yfinance, FRED API (httpx), tigramite (PCMCI+), lingam (VARLiNGAM), NetworkX, numpy/scipy/pandas.

**Spec:** `backend/app/causal_discovery/README.md`

**Skills to invoke during execution:**
- `superpowers:subagent-driven-development` — REQUIRED for execution (fresh agent per task, reads this plan file)
- `superpowers:executing-plans` — alternative if subagents unavailable (sequential, same session)
- `superpowers:test-driven-development` — each task follows TDD: write failing test → implement → verify
- `superpowers:systematic-debugging` — invoke when any test fails unexpectedly; diagnose root cause, don't hack around it
- `superpowers:verification-before-completion` — invoke at the end of each chunk before claiming it's done; run ALL tests, check output
- `superpowers:using-git-worktrees` — invoke before starting execution to create isolated workspace on `feature/causal-discovery` branch
- `superpowers:finishing-a-development-branch` — invoke after all 7 chunks pass to verify, commit, and create PR
- `superpowers:requesting-code-review` — invoke after completing major chunks (3, 5, 7) for quality review

**Research context:** Full research log at `research/RESEARCH_LOG.md`. Use the `research-log` skill (MCP search or targeted Read) to recall design decisions, algorithm comparisons, or rationale. Key entries: "Computational Causal Graph Discovery", "Data Pipeline Gap Analysis", "Computationally Generated Network: Scoring Without LLM", "Database Schema for node_values", "Implementation Architecture".

**Data sources for this plan (verified working, no API keys needed):**
- **yfinance** — all 20 tickers tested and confirmed working (SPY, QQQ, GLD, EURUSD=X, ^MOVE, ^SKEW, BZ=F, ^VIX, USDCNY=X, USDJPY=X, USO, UNG, HG=F, ZW=F, DX-Y.NYB, IWM, XLK, XLE, XLF, SLV). 5-year backfill confirmed: 1,256 rows per ticker.
- **FRED** — requires API key (not currently configured). Code supports it but will skip gracefully if `FRED_API_KEY` is empty. Not a blocker.
- **Other sources** (CBOE, ECB, BOJ, GDELT) — deferred to future phases.

**Critical engineering constraints:**
- Dependencies install via `pip install -r requirements.txt` in Docker (python:3.12-slim). No conda in the container. `graph-tool` is deferred (optional, conda-only).
- Existing tests (`pytest tests/`) must continue to pass at every phase.
- The `Base` class from `app.models.graph` is used for all SQLAlchemy models. New models must inherit from it so `Base.metadata.create_all` picks them up.
- Hypertable creation requires raw SQL via `text()` after `create_all` (SQLAlchemy doesn't know about TimescaleDB extensions).
- yfinance is synchronous — must use `asyncio.to_thread()` (same pattern as existing `market.py`).
- Tests that require network access (yfinance downloads) must be marked with `@pytest.mark.network` and skipped in CI. Pure unit tests must work offline.
- Scheduler for incremental daily updates is implemented but **disabled by default** (same pattern as existing `SCHEDULER_ENABLED=false`). Enabled via env var when ready.

**Deferred to future phases (not in this plan):**
- Frontend components (`CausalGraph3D.tsx`, `CausalPanel.tsx`)
- FRED and other API-key-required data sources
- GitHub Actions CI configuration for new tests
- graph-tool / DoWhy integration
- Incremental scheduler activation

---

## Chunk 1: Foundation (Database + Model + Package Structure)

### Task 1.1: Create package structure with `__init__.py` files

**Files:**
- Create: `backend/app/causal_discovery/__init__.py`
- Create: `backend/app/causal_discovery/pipeline/__init__.py`
- Create: `backend/app/causal_discovery/engine/__init__.py`
- Create: `backend/app/causal_discovery/api/__init__.py`

- [ ] **Step 1: Create all `__init__.py` files**

```python
# All four files are empty — just make the directories into Python packages
```

- [ ] **Step 2: Verify the package is importable**

Run: `cd backend && python -c "import app.causal_discovery; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Verify existing tests still pass**

Run: `cd backend && pytest tests/ -q --tb=short`
Expected: All tests pass, no regressions.

- [ ] **Step 4: Commit**

```bash
git add backend/app/causal_discovery/
git commit -m "feat(causal-discovery): create package structure"
```

### Task 1.2: Create NodeValue SQLAlchemy model

**Files:**
- Create: `backend/app/causal_discovery/models.py`
- Test: `backend/tests/test_causal_discovery/__init__.py` (create dir)
- Test: `backend/tests/test_causal_discovery/test_models.py`

- [ ] **Step 1: Create test directory and conftest**

```bash
mkdir -p backend/tests/test_causal_discovery
touch backend/tests/test_causal_discovery/__init__.py
```

Create shared test fixtures:

```python
# backend/tests/test_causal_discovery/conftest.py
"""Shared fixtures for causal_discovery tests."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_daily_matrix():
    """A small aligned daily matrix for testing (100 days × 5 nodes)."""
    np.random.seed(42)
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    return pd.DataFrame({
        "sp500": np.random.randn(100).cumsum() + 500,
        "vix": np.random.randn(100).cumsum() + 15,
        "gold": np.random.randn(100).cumsum() + 2000,
        "us_10y_yield": np.random.randn(100).cumsum() * 0.1 + 4.0,
        "eurusd": np.random.randn(100).cumsum() * 0.01 + 1.08,
    }, index=dates)
```

- [ ] **Step 2: Write failing test for NodeValue model**

```python
# backend/tests/test_causal_discovery/test_models.py
"""Tests for causal_discovery models."""

from datetime import datetime, timezone

from app.causal_discovery.models import NodeValue


def test_node_value_creation():
    """NodeValue can be instantiated with required fields."""
    nv = NodeValue(
        node_id="sp500",
        ts=datetime(2025, 1, 2, tzinfo=timezone.utc),
        value=480.12,
        source="yfinance",
    )
    assert nv.node_id == "sp500"
    assert nv.value == 480.12
    assert nv.source == "yfinance"
    assert nv.ts.year == 2025


def test_node_value_table_name():
    """Table name is 'node_values'."""
    assert NodeValue.__tablename__ == "node_values"


def test_node_value_inherits_base():
    """NodeValue inherits from the shared Base class."""
    from app.models.graph import Base
    assert issubclass(NodeValue, Base)
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd backend && pytest tests/test_causal_discovery/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.causal_discovery.models'` or `ImportError`

- [ ] **Step 4: Write NodeValue model**

```python
# backend/app/causal_discovery/models.py
"""SQLAlchemy models for causal discovery — TimescaleDB hypertable."""

from __future__ import annotations

import logging

from sqlalchemy import Column, DateTime, Float, String, Text, text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.models.graph import Base

logger = logging.getLogger(__name__)


class NodeValue(Base):
    """Raw numerical time-series data for causal discovery.

    One row = one observation: which node, when (real observation time), what value, from where.
    Designed as a TimescaleDB hypertable on `ts` for efficient time-range queries.
    """

    __tablename__ = "node_values"

    node_id = Column(String(64), nullable=False, primary_key=True)
    ts = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    value = Column(Float, nullable=False)
    source = Column(String(64), nullable=False)


async def create_hypertable_if_needed(conn: AsyncConnection) -> None:
    """Convert node_values to a TimescaleDB hypertable if not already done.

    Must be called AFTER Base.metadata.create_all (table must exist first).
    Safe to call multiple times — TimescaleDB raises a notice if already a hypertable.
    """
    try:
        await conn.execute(
            text("""
                SELECT create_hypertable('node_values', 'ts',
                    if_not_exists => TRUE,
                    migrate_data => TRUE
                );
            """)
        )
        logger.info("node_values hypertable ready")
    except Exception as e:
        # TimescaleDB extension might not be available (e.g., plain Postgres in CI)
        logger.warning("Could not create hypertable (TimescaleDB may not be installed): %s", e)


async def create_node_values_index(conn: AsyncConnection) -> None:
    """Create index for fast node+time lookups if it doesn't exist."""
    try:
        await conn.execute(
            text("""
                CREATE INDEX IF NOT EXISTS idx_node_values_node_ts
                ON node_values (node_id, ts DESC);
            """)
        )
    except Exception as e:
        logger.warning("Could not create index: %s", e)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd backend && pytest tests/test_causal_discovery/test_models.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 6: Verify existing tests still pass**

Run: `cd backend && pytest tests/ -q --tb=short`
Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add backend/app/causal_discovery/models.py backend/tests/test_causal_discovery/
git commit -m "feat(causal-discovery): add NodeValue model with hypertable support"
```

### Task 1.3: Add causal discovery settings to config.py

**Files:**
- Modify: `backend/app/config.py` (add settings block)

- [ ] **Step 1: Add causal discovery settings**

Add after the existing `centrality_cache_ttl` line in `Settings`:

```python
    # Causal Discovery
    causal_zscore_window: int = 90
    causal_backfill_years: int = 5
    causal_max_display_nodes: int = 100
    causal_discovery_algorithm: str = "pcmci"  # "pcmci" or "varlingam"
    causal_min_edge_weight: float = 0.1
    causal_anchor_nodes: str = "sp500,nasdaq,us_gdp_growth,unemployment_rate"  # comma-separated
```

Note: `causal_anchor_nodes` is a comma-separated string (not a list) because pydantic-settings loads from env vars which are always strings. Parse with `.split(",")` at usage site.

- [ ] **Step 2: Verify existing tests still pass**

Run: `cd backend && pytest tests/ -q --tb=short`
Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add backend/app/config.py
git commit -m "feat(causal-discovery): add configuration settings"
```

### Task 1.4: Register model and hypertable in main.py

**Files:**
- Modify: `backend/app/main.py` (add ~5 lines)

- [ ] **Step 1: Write test that NodeValue table is created on startup**

This is an integration concern — we verify by checking that the import doesn't break existing startup.

- [ ] **Step 2: Add imports and hypertable creation to main.py lifespan**

Add this import at the top of `main.py` (after existing imports):

```python
from app.causal_discovery.models import create_hypertable_if_needed, create_node_values_index
```

In the `lifespan` function, find the existing block:

```python
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

Add two lines AFTER `create_all` but INSIDE the same `async with` block (do NOT delete or replace the existing `create_all` line):

```python
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Causal discovery: convert node_values to hypertable + create index
        await create_hypertable_if_needed(conn)
        await create_node_values_index(conn)
```

- [ ] **Step 3: Verify existing tests still pass**

Run: `cd backend && pytest tests/ -q --tb=short`
Expected: All tests pass. The `create_hypertable_if_needed` gracefully handles non-TimescaleDB environments (CI uses plain Postgres).

- [ ] **Step 4: Commit**

```bash
git add backend/app/main.py
git commit -m "feat(causal-discovery): register NodeValue table in app lifespan"
```

---

## Chunk 2: Data Source Registry + Fetchers

### Task 2.1: Create data source registry (sources.py)

**Files:**
- Create: `backend/app/causal_discovery/pipeline/sources.py`
- Test: `backend/tests/test_causal_discovery/test_sources.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_causal_discovery/test_sources.py
"""Tests for data source registry."""

from app.causal_discovery.pipeline.sources import (
    YFINANCE_SOURCES,
    FRED_SOURCES,
    get_all_sources,
    get_source_for_node,
)


def test_yfinance_sources_has_sp500():
    assert any(s["node_id"] == "sp500" for s in YFINANCE_SOURCES)


def test_fred_sources_has_fedfunds():
    assert any(s["node_id"] == "fed_funds_rate" for s in FRED_SOURCES)


def test_get_all_sources_returns_both():
    sources = get_all_sources()
    node_ids = {s["node_id"] for s in sources}
    assert "sp500" in node_ids
    assert "fed_funds_rate" in node_ids


def test_get_source_for_node():
    src = get_source_for_node("sp500")
    assert src is not None
    assert src["ticker"] == "SPY"
    assert src["source_type"] == "yfinance"


def test_get_source_for_unknown_node():
    src = get_source_for_node("nonexistent_node")
    assert src is None


def test_no_duplicate_node_ids():
    sources = get_all_sources()
    node_ids = [s["node_id"] for s in sources]
    assert len(node_ids) == len(set(node_ids)), f"Duplicate node_ids found: {[n for n in node_ids if node_ids.count(n) > 1]}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_causal_discovery/test_sources.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: Write sources.py**

```python
# backend/app/causal_discovery/pipeline/sources.py
"""Data source registry — maps node_ids to tickers/series for fetching."""

from __future__ import annotations

# yfinance sources: ticker → node_id
# Each entry: {node_id, ticker, source_type, description}
YFINANCE_SOURCES: list[dict] = [
    # Equities
    {"node_id": "sp500", "ticker": "SPY", "source_type": "yfinance", "description": "S&P 500 ETF"},
    {"node_id": "nasdaq", "ticker": "QQQ", "source_type": "yfinance", "description": "NASDAQ 100 ETF"},
    {"node_id": "russell2000", "ticker": "IWM", "source_type": "yfinance", "description": "Russell 2000 ETF"},
    {"node_id": "tech_sector", "ticker": "XLK", "source_type": "yfinance", "description": "Tech Sector ETF"},
    {"node_id": "energy_sector", "ticker": "XLE", "source_type": "yfinance", "description": "Energy Sector ETF"},
    {"node_id": "financials_sector", "ticker": "XLF", "source_type": "yfinance", "description": "Financials Sector ETF"},
    # Commodities
    {"node_id": "gold", "ticker": "GLD", "source_type": "yfinance", "description": "Gold ETF"},
    {"node_id": "silver", "ticker": "SLV", "source_type": "yfinance", "description": "Silver ETF"},
    {"node_id": "wti_crude", "ticker": "USO", "source_type": "yfinance", "description": "WTI Crude Oil ETF"},
    {"node_id": "brent_crude", "ticker": "BZ=F", "source_type": "yfinance", "description": "Brent Crude Futures"},
    {"node_id": "natural_gas", "ticker": "UNG", "source_type": "yfinance", "description": "Natural Gas ETF"},
    {"node_id": "copper", "ticker": "HG=F", "source_type": "yfinance", "description": "Copper Futures"},
    {"node_id": "wheat", "ticker": "ZW=F", "source_type": "yfinance", "description": "Wheat Futures"},
    # Currencies
    {"node_id": "dxy_index", "ticker": "DX-Y.NYB", "source_type": "yfinance", "description": "US Dollar Index"},
    {"node_id": "eurusd", "ticker": "EURUSD=X", "source_type": "yfinance", "description": "EUR/USD"},
    {"node_id": "usdjpy", "ticker": "USDJPY=X", "source_type": "yfinance", "description": "USD/JPY"},
    {"node_id": "usdcny", "ticker": "USDCNY=X", "source_type": "yfinance", "description": "USD/CNY"},
    # Volatility
    {"node_id": "vix", "ticker": "^VIX", "source_type": "yfinance", "description": "CBOE VIX"},
    {"node_id": "move_index", "ticker": "^MOVE", "source_type": "yfinance", "description": "ICE BofA MOVE Index"},
    {"node_id": "skew_index", "ticker": "^SKEW", "source_type": "yfinance", "description": "CBOE SKEW Index"},
]

# FRED sources: series_id → node_id
FRED_SOURCES: list[dict] = [
    # Rates
    {"node_id": "fed_funds_rate", "series_id": "FEDFUNDS", "source_type": "fred", "description": "Effective Federal Funds Rate"},
    {"node_id": "us_2y_yield", "series_id": "DGS2", "source_type": "fred", "description": "2-Year Treasury Yield"},
    {"node_id": "us_10y_yield", "series_id": "DGS10", "source_type": "fred", "description": "10-Year Treasury Yield"},
    {"node_id": "us_30y_yield", "series_id": "DGS30", "source_type": "fred", "description": "30-Year Treasury Yield"},
    {"node_id": "yield_curve_spread", "series_id": "T10Y2Y", "source_type": "fred", "description": "10Y-2Y Spread"},
    # Credit
    {"node_id": "ig_credit_spread", "series_id": "BAMLC0A0CM", "source_type": "fred", "description": "IG Credit Spread"},
    {"node_id": "hy_credit_spread", "series_id": "BAMLH0A0HYM2", "source_type": "fred", "description": "HY Credit Spread"},
    # Macro
    {"node_id": "us_cpi_yoy", "series_id": "CPIAUCSL", "source_type": "fred", "description": "CPI All Urban Consumers"},
    {"node_id": "us_gdp_growth", "series_id": "GDP", "source_type": "fred", "description": "Nominal GDP"},
    {"node_id": "unemployment_rate", "series_id": "UNRATE", "source_type": "fred", "description": "Unemployment Rate"},
    {"node_id": "consumer_confidence", "series_id": "UMCSENT", "source_type": "fred", "description": "U. Michigan Consumer Sentiment"},
    {"node_id": "pce_deflator", "series_id": "PCEPILFE", "source_type": "fred", "description": "Core PCE Price Index"},
    {"node_id": "wage_growth", "series_id": "CES0500000003", "source_type": "fred", "description": "Avg Hourly Earnings"},
    # Monetary policy
    {"node_id": "fed_balance_sheet", "series_id": "WALCL", "source_type": "fred", "description": "Fed Total Assets"},
    # Geopolitics / policy uncertainty
    {"node_id": "us_political_risk", "series_id": "USEPUINDXD", "source_type": "fred", "description": "Economic Policy Uncertainty (Daily)"},
    # Note: wti_crude and dxy_index are already covered by yfinance (USO, DX-Y.NYB).
    # FRED versions omitted to avoid duplicate node_ids. Add them back if yfinance
    # sources become unreliable, using node_ids "wti_crude" and "dxy_index" (replacing yfinance).
]


def get_all_sources() -> list[dict]:
    """Return all registered data sources."""
    return YFINANCE_SOURCES + FRED_SOURCES


def get_source_for_node(node_id: str) -> dict | None:
    """Look up the data source for a given node_id."""
    for source in get_all_sources():
        if source["node_id"] == node_id:
            return source
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_causal_discovery/test_sources.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/causal_discovery/pipeline/sources.py backend/tests/test_causal_discovery/test_sources.py
git commit -m "feat(causal-discovery): add data source registry with yfinance + FRED mappings"
```

### Task 2.2: Create yfinance bulk fetcher

**Files:**
- Create: `backend/app/causal_discovery/pipeline/fetchers.py`
- Test: `backend/tests/test_causal_discovery/test_fetchers.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_causal_discovery/test_fetchers.py
"""Tests for data fetchers."""

import pandas as pd
import pytest

from app.causal_discovery.pipeline.fetchers import (
    fetch_yfinance_history,
    parse_fred_observations,
)


@pytest.mark.network
async def test_fetch_yfinance_history_returns_dataframe():
    """Fetch real SPY data and verify structure."""
    df = await fetch_yfinance_history(["SPY"], period="1mo")
    assert isinstance(df, pd.DataFrame)
    assert "SPY" in df.columns
    assert len(df) > 15  # ~20 trading days in a month
    assert df.index.dtype.kind == "M"  # datetime index


@pytest.mark.network
async def test_fetch_yfinance_history_multiple_tickers():
    """Multiple tickers return multiple columns."""
    df = await fetch_yfinance_history(["SPY", "QQQ", "GLD"], period="5d")
    assert "SPY" in df.columns
    assert "QQQ" in df.columns
    assert "GLD" in df.columns


def test_parse_fred_observations():
    """Parse FRED API response into {date: value} series."""
    raw = [
        {"date": "2025-01-02", "value": "4.33"},
        {"date": "2025-01-03", "value": "4.35"},
        {"date": "2025-01-04", "value": "."},  # FRED missing value
    ]
    result = parse_fred_observations(raw)
    assert len(result) == 2
    assert result[0] == ("2025-01-02", 4.33)
    assert result[1] == ("2025-01-03", 4.35)


def test_parse_fred_observations_empty():
    result = parse_fred_observations([])
    assert result == []
```

Note: Tests marked `@pytest.mark.network` make real network calls (yfinance). Run them locally with `pytest -m network`. Skip in CI with `pytest -m "not network"`. The `parse_fred_observations` tests are pure unit tests and always run.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_causal_discovery/test_fetchers.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: Write fetchers.py**

```python
# backend/app/causal_discovery/pipeline/fetchers.py
"""Data fetchers for causal discovery — yfinance and FRED bulk historical data."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import httpx
import pandas as pd
import yfinance as yf

from app.config import settings

logger = logging.getLogger(__name__)


def _yfinance_download_sync(tickers: list[str], period: str = "5y") -> pd.DataFrame:
    """Synchronous yfinance download — returns daily close prices as a DataFrame.

    Columns = ticker symbols, index = dates.
    """
    if len(tickers) == 1:
        data = yf.download(tickers[0], period=period, interval="1d", progress=False)
        if data.empty:
            return pd.DataFrame()
        # Handle multi-level columns
        if hasattr(data.columns, "levels") and len(data.columns.levels) > 1:
            data.columns = data.columns.droplevel(1)
        return data[["Close"]].rename(columns={"Close": tickers[0]})

    data = yf.download(tickers, period=period, interval="1d", progress=False, group_by="ticker")
    if data.empty:
        return pd.DataFrame()

    result = pd.DataFrame(index=data.index)
    for ticker in tickers:
        try:
            if ticker in data.columns.get_level_values(0):
                result[ticker] = data[ticker]["Close"]
        except (KeyError, TypeError):
            logger.warning("No data for ticker %s", ticker)
    return result


async def fetch_yfinance_history(tickers: list[str], period: str = "5y") -> pd.DataFrame:
    """Async wrapper for yfinance bulk download. Returns DataFrame: columns=tickers, index=dates."""
    return await asyncio.to_thread(_yfinance_download_sync, tickers, period)


def parse_fred_observations(raw_observations: list[dict]) -> list[tuple[str, float]]:
    """Parse FRED API observations into (date_str, value) tuples.

    Filters out FRED's missing-value sentinel '.'.
    """
    results = []
    for obs in raw_observations:
        if obs["value"] == ".":
            continue
        try:
            results.append((obs["date"], float(obs["value"])))
        except (ValueError, KeyError):
            continue
    return results


async def fetch_fred_series_history(
    series_id: str,
    observation_start: str = "2020-01-01",
) -> list[tuple[str, float]]:
    """Fetch full history for a single FRED series.

    Returns list of (date_str, value) tuples.
    """
    if not settings.fred_api_key:
        logger.warning("FRED API key not set — skipping %s", series_id)
        return []

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(
                "https://api.stlouisfed.org/fred/series/observations",
                params={
                    "series_id": series_id,
                    "api_key": settings.fred_api_key,
                    "file_type": "json",
                    "sort_order": "asc",
                    "observation_start": observation_start,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return parse_fred_observations(data.get("observations", []))
        except Exception as e:
            logger.error("Failed to fetch FRED series %s: %s", series_id, e)
            return []
```

- [ ] **Step 4: Add pandas + pytest-asyncio to requirements and configure pytest**

```bash
cd backend
grep -q "pandas" requirements.txt || echo "pandas>=2.2.0" >> requirements.txt
grep -q "pytest-asyncio" requirements.txt || echo "pytest-asyncio>=0.23.0" >> requirements.txt
pip install pandas pytest-asyncio
```

Create `backend/pyproject.toml` (or add to existing) for pytest configuration:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
markers = [
    "network: tests that require network access (yfinance, FRED API calls)",
]
```

Note: `pandas` is a new dependency. It's needed for the matrix operations (aligned daily DataFrame). The existing project uses numpy/scipy but not pandas. Adding it is safe — it doesn't conflict with anything. The `asyncio_mode = "auto"` setting means `@pytest.mark.asyncio` is not needed on every async test — pytest-asyncio detects them automatically.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd backend && pytest tests/test_causal_discovery/test_fetchers.py -v`
Expected: All 4 tests PASS. The yfinance tests make real network calls and take 5-10 seconds.

- [ ] **Step 6: Verify existing tests still pass**

Run: `cd backend && pytest tests/ -q --tb=short`
Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add backend/app/causal_discovery/pipeline/fetchers.py backend/tests/test_causal_discovery/test_fetchers.py backend/requirements.txt
git commit -m "feat(causal-discovery): add yfinance + FRED bulk history fetchers"
```

---

## Chunk 3: Backfill Pipeline (Fetchers → DB)

### Task 3.1: Create backfill job

**Files:**
- Create: `backend/app/causal_discovery/pipeline/backfill.py`
- Test: `backend/tests/test_causal_discovery/test_backfill.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_causal_discovery/test_backfill.py
"""Tests for backfill logic — uses mock data, no DB or network calls."""

import pandas as pd
import numpy as np
from datetime import datetime, timezone

from app.causal_discovery.pipeline.backfill import (
    yfinance_df_to_node_value_rows,
    fred_series_to_node_value_rows,
)


def test_yfinance_df_to_node_value_rows():
    """Convert a yfinance DataFrame into NodeValue-compatible row dicts."""
    dates = pd.date_range("2025-01-02", periods=3, freq="B")
    df = pd.DataFrame({"SPY": [480.0, 482.0, 479.0]}, index=dates)
    ticker_to_node = {"SPY": "sp500"}

    rows = yfinance_df_to_node_value_rows(df, ticker_to_node)
    assert len(rows) == 3
    assert rows[0]["node_id"] == "sp500"
    assert rows[0]["value"] == 480.0
    assert rows[0]["source"] == "yfinance"
    assert isinstance(rows[0]["ts"], datetime)


def test_yfinance_df_skips_nan():
    """NaN values (missing data) are skipped."""
    dates = pd.date_range("2025-01-02", periods=3, freq="B")
    df = pd.DataFrame({"SPY": [480.0, np.nan, 479.0]}, index=dates)
    ticker_to_node = {"SPY": "sp500"}

    rows = yfinance_df_to_node_value_rows(df, ticker_to_node)
    assert len(rows) == 2


def test_fred_series_to_node_value_rows():
    """Convert FRED (date, value) tuples into row dicts."""
    observations = [("2025-01-02", 4.33), ("2025-01-03", 4.35)]
    rows = fred_series_to_node_value_rows("fed_funds_rate", observations)
    assert len(rows) == 2
    assert rows[0]["node_id"] == "fed_funds_rate"
    assert rows[0]["value"] == 4.33
    assert rows[0]["source"] == "fred"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_causal_discovery/test_backfill.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: Write backfill.py**

```python
# backend/app/causal_discovery/pipeline/backfill.py
"""Historical data backfill — fetches years of data and stores in node_values."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.causal_discovery.models import NodeValue
from app.causal_discovery.pipeline.fetchers import (
    fetch_fred_series_history,
    fetch_yfinance_history,
)
from app.causal_discovery.pipeline.sources import FRED_SOURCES, YFINANCE_SOURCES

logger = logging.getLogger(__name__)


def yfinance_df_to_node_value_rows(
    df: pd.DataFrame,
    ticker_to_node: dict[str, str],
) -> list[dict]:
    """Convert a yfinance DataFrame (columns=tickers, index=dates) into row dicts."""
    rows = []
    for ticker, node_id in ticker_to_node.items():
        if ticker not in df.columns:
            continue
        for ts, value in df[ticker].items():
            if pd.isna(value):
                continue
            rows.append({
                "node_id": node_id,
                "ts": ts.to_pydatetime().replace(tzinfo=timezone.utc) if ts.tzinfo is None else ts.to_pydatetime(),
                "value": float(value),
                "source": "yfinance",
            })
    return rows


def fred_series_to_node_value_rows(
    node_id: str,
    observations: list[tuple[str, float]],
) -> list[dict]:
    """Convert FRED (date_str, value) tuples into row dicts."""
    rows = []
    for date_str, value in observations:
        ts = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        rows.append({
            "node_id": node_id,
            "ts": ts,
            "value": value,
            "source": "fred",
        })
    return rows


async def run_backfill(
    session: AsyncSession,
    yfinance_period: str = "5y",
    fred_start: str = "2020-01-01",
) -> dict:
    """Run full historical backfill for all registered sources.

    Returns summary: {yfinance_rows: int, fred_rows: int, errors: list[str]}.
    """
    summary = {"yfinance_rows": 0, "fred_rows": 0, "errors": []}

    # --- yfinance backfill ---
    tickers = [s["ticker"] for s in YFINANCE_SOURCES]
    ticker_to_node = {s["ticker"]: s["node_id"] for s in YFINANCE_SOURCES}

    logger.info("Backfilling yfinance: %d tickers, period=%s", len(tickers), yfinance_period)
    try:
        df = await fetch_yfinance_history(tickers, period=yfinance_period)
        rows = yfinance_df_to_node_value_rows(df, ticker_to_node)
        # Bulk upsert in batches of 1000 for performance (~25K rows total)
        BATCH_SIZE = 1000
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i : i + BATCH_SIZE]
            await session.execute(
                text("""
                    INSERT INTO node_values (node_id, ts, value, source)
                    VALUES (:node_id, :ts, :value, :source)
                    ON CONFLICT (node_id, ts) DO UPDATE SET value = EXCLUDED.value, source = EXCLUDED.source
                """),
                batch,
            )
        summary["yfinance_rows"] = len(rows)
        logger.info("yfinance backfill: %d rows", len(rows))
    except Exception as e:
        logger.exception("yfinance backfill failed: %s", e)
        summary["errors"].append(f"yfinance: {e}")

    # --- FRED backfill ---
    logger.info("Backfilling FRED: %d series, start=%s", len(FRED_SOURCES), fred_start)
    for source in FRED_SOURCES:
        try:
            observations = await fetch_fred_series_history(source["series_id"], fred_start)
            rows = fred_series_to_node_value_rows(source["node_id"], observations)
            if rows:
                await session.execute(
                    text("""
                        INSERT INTO node_values (node_id, ts, value, source)
                        VALUES (:node_id, :ts, :value, :source)
                        ON CONFLICT (node_id, ts) DO UPDATE SET value = EXCLUDED.value, source = EXCLUDED.source
                    """),
                    rows,
                )
            summary["fred_rows"] += len(rows)
            logger.info("FRED %s (%s): %d rows", source["series_id"], source["node_id"], len(rows))
        except Exception as e:
            logger.exception("FRED backfill failed for %s: %s", source["series_id"], e)
            summary["errors"].append(f"fred/{source['series_id']}: {e}")

    await session.commit()
    logger.info("Backfill complete: %d yfinance + %d FRED rows, %d errors",
                summary["yfinance_rows"], summary["fred_rows"], len(summary["errors"]))
    return summary
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_causal_discovery/test_backfill.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/causal_discovery/pipeline/backfill.py backend/tests/test_causal_discovery/test_backfill.py
git commit -m "feat(causal-discovery): add backfill pipeline with yfinance + FRED history"
```

### Task 3.2: Create API route to trigger backfill

**Files:**
- Create: `backend/app/causal_discovery/api/routes.py`
- Modify: `backend/app/main.py` (add router)

- [ ] **Step 1: Write routes.py with backfill endpoint**

```python
# backend/app/causal_discovery/api/routes.py
"""API routes for causal discovery module."""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks
from sqlalchemy import text

from app.db.connection import async_session

router = APIRouter(prefix="/api/causal", tags=["causal-discovery"])

logger = logging.getLogger(__name__)

# Track backfill status in memory
_backfill_status = {"running": False, "last_result": None}


async def _run_backfill_task():
    """Background task for backfill."""
    from app.causal_discovery.pipeline.backfill import run_backfill

    _backfill_status["running"] = True
    try:
        async with async_session() as session:
            result = await run_backfill(session)
            _backfill_status["last_result"] = result
    except Exception as e:
        _backfill_status["last_result"] = {"error": str(e)}
    finally:
        _backfill_status["running"] = False


@router.post("/backfill")
async def trigger_backfill(background_tasks: BackgroundTasks):
    """Trigger historical data backfill (runs in background)."""
    if _backfill_status["running"]:
        return {"status": "already_running"}
    background_tasks.add_task(_run_backfill_task)
    return {"status": "started"}


@router.get("/backfill/status")
async def backfill_status():
    """Check backfill progress."""
    return _backfill_status


@router.get("/sources")
async def list_sources():
    """List all registered data sources."""
    from app.causal_discovery.pipeline.sources import get_all_sources
    return get_all_sources()


@router.get("/stats")
async def data_stats():
    """Get row counts and date ranges per node."""
    async with async_session() as session:
        result = await session.execute(
            text("""
                SELECT node_id, COUNT(*) as row_count,
                       MIN(ts) as first_date, MAX(ts) as last_date
                FROM node_values
                GROUP BY node_id
                ORDER BY row_count DESC
            """)
        )
        rows = result.fetchall()
        return [
            {
                "node_id": r.node_id,
                "row_count": r.row_count,
                "first_date": str(r.first_date),
                "last_date": str(r.last_date),
            }
            for r in rows
        ]
```

- [ ] **Step 2: Register router in main.py**

Add after the existing router registrations in `main.py`:

```python
from app.causal_discovery.api.routes import router as causal_router
```

And:

```python
app.include_router(causal_router)
```

- [ ] **Step 3: Verify existing tests still pass**

Run: `cd backend && pytest tests/ -q --tb=short`
Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/app/causal_discovery/api/routes.py backend/app/main.py
git commit -m "feat(causal-discovery): add API routes for backfill + data stats"
```

### Task 3.3: End-to-end backfill integration test

- [ ] **Step 1: Verify the full stack works**

With Docker running:

```bash
# Trigger backfill
curl -X POST http://localhost:8000/api/causal/backfill

# Check status (wait for it to finish)
curl http://localhost:8000/api/causal/backfill/status

# Check data stats
curl http://localhost:8000/api/causal/stats
```

Expected: `stats` shows rows for each node_id, spanning ~5 years of history for yfinance sources. FRED sources will only have data if FRED_API_KEY is set.

- [ ] **Step 2: Verify data integrity**

```bash
# Check total row count
curl http://localhost:8000/api/causal/stats | python3 -m json.tool | head -30
```

Expected: Each yfinance node has ~1,250 rows (252 trading days × 5 years). FRED nodes have varying counts depending on frequency (daily rates: ~1,250, monthly CPI: ~60).

- [ ] **Step 3: Commit with integration test note**

```bash
git commit --allow-empty -m "test(causal-discovery): verify end-to-end backfill against running DB"
```

---

## Chunk 4: Matrix Builder + Z-Score Engine

### Task 4.1: Create matrix builder

**Files:**
- Create: `backend/app/causal_discovery/engine/matrix.py`
- Test: `backend/tests/test_causal_discovery/test_matrix.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_causal_discovery/test_matrix.py
"""Tests for matrix builder — uses synthetic data, no DB."""

import pandas as pd
import numpy as np
from datetime import datetime, timezone

from app.causal_discovery.engine.matrix import (
    build_daily_matrix_from_rows,
    forward_fill_matrix,
)


def test_build_daily_matrix_from_rows():
    """Convert raw rows into a pivot DataFrame."""
    rows = [
        {"node_id": "sp500", "day": datetime(2025, 1, 2, tzinfo=timezone.utc), "value": 480.0},
        {"node_id": "sp500", "day": datetime(2025, 1, 3, tzinfo=timezone.utc), "value": 482.0},
        {"node_id": "vix", "day": datetime(2025, 1, 2, tzinfo=timezone.utc), "value": 13.2},
        {"node_id": "vix", "day": datetime(2025, 1, 3, tzinfo=timezone.utc), "value": 12.8},
    ]
    df = build_daily_matrix_from_rows(rows)
    assert df.shape == (2, 2)
    assert "sp500" in df.columns
    assert "vix" in df.columns
    assert df.loc[df.index[0], "sp500"] == 480.0


def test_forward_fill_matrix():
    """Forward-fill NaN values in the matrix (for sparse series like monthly CPI)."""
    dates = pd.date_range("2025-01-01", periods=5, freq="B")
    df = pd.DataFrame({
        "sp500": [480, 482, 479, 481, 483],
        "cpi": [3.1, np.nan, np.nan, np.nan, np.nan],
    }, index=dates)
    filled = forward_fill_matrix(df)
    assert filled["cpi"].isna().sum() == 0
    assert filled.loc[dates[4], "cpi"] == 3.1  # Forward-filled from day 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_causal_discovery/test_matrix.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: Write matrix.py**

```python
# backend/app/causal_discovery/engine/matrix.py
"""Build aligned daily matrix from node_values table."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def build_daily_matrix_from_rows(rows: list[dict]) -> pd.DataFrame:
    """Convert list of {node_id, day, value} dicts into a pivot DataFrame.

    Rows = trading days, columns = node_ids, values = last observation per day.
    """
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    pivot = df.pivot(index="day", columns="node_id", values="value")
    pivot.sort_index(inplace=True)
    return pivot


def forward_fill_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Forward-fill NaN values (carry last known value for sparse series)."""
    return df.ffill()


async def get_daily_matrix(
    session: AsyncSession,
    days: int = 252,
    node_ids: list[str] | None = None,
) -> pd.DataFrame:
    """Query node_values and return an aligned daily matrix.

    Uses TimescaleDB time_bucket + last() for alignment.
    Falls back to plain SQL if TimescaleDB functions aren't available.
    """
    try:
        # Try TimescaleDB-native query first
        query = """
            SELECT node_id,
                   time_bucket('1 day', ts) AS day,
                   last(value, ts) AS value
            FROM node_values
            WHERE ts >= NOW() - make_interval(days => :days)
        """
        if node_ids:
            query += " AND node_id = ANY(:node_ids)"
        query += " GROUP BY node_id, day ORDER BY day"

        params = {"days": days}
        if node_ids:
            params["node_ids"] = node_ids

        result = await session.execute(text(query), params)
    except Exception:
        # Fallback: plain SQL without TimescaleDB functions
        logger.info("TimescaleDB functions not available, using plain SQL fallback")
        query = """
            SELECT node_id,
                   DATE(ts) AS day,
                   value
            FROM node_values
            WHERE ts >= NOW() - make_interval(days => :days)
            ORDER BY ts
        """
        params = {"days": days}
        result = await session.execute(text(query), params)

    rows = [{"node_id": r.node_id, "day": r.day, "value": r.value} for r in result.fetchall()]
    df = build_daily_matrix_from_rows(rows)
    df = forward_fill_matrix(df)
    return df
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_causal_discovery/test_matrix.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/causal_discovery/engine/matrix.py backend/tests/test_causal_discovery/test_matrix.py
git commit -m "feat(causal-discovery): add daily matrix builder with forward-fill"
```

### Task 4.2: Create z-score engine

**Files:**
- Create: `backend/app/causal_discovery/engine/zscore.py`
- Test: `backend/tests/test_causal_discovery/test_zscore.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_causal_discovery/test_zscore.py
"""Tests for z-score computation."""

import pandas as pd
import numpy as np

from app.causal_discovery.engine.zscore import compute_rolling_zscore


def test_zscore_basic():
    """Z-score of a constant series is 0."""
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    df = pd.DataFrame({"A": [100.0] * 100}, index=dates)
    zscores = compute_rolling_zscore(df, window=20)
    # Constant series → std=0 → z-score should be 0 (or NaN, handled gracefully)
    assert zscores["A"].dropna().abs().max() < 0.01 or zscores["A"].isna().all()


def test_zscore_known_values():
    """Z-score with known mean and std."""
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    values = list(range(100))  # Linear increase
    df = pd.DataFrame({"A": values}, index=dates)
    zscores = compute_rolling_zscore(df, window=20)
    # Last value (99) should have positive z-score (above rolling mean)
    last_z = zscores["A"].iloc[-1]
    assert last_z > 0


def test_zscore_multiple_columns():
    """Z-score works on multiple columns independently."""
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    df = pd.DataFrame({
        "A": np.random.randn(100).cumsum(),
        "B": np.random.randn(100).cumsum(),
    }, index=dates)
    zscores = compute_rolling_zscore(df, window=20)
    assert "A" in zscores.columns
    assert "B" in zscores.columns
    assert len(zscores) == 100


def test_zscore_clamped():
    """Z-scores are clamped to [-3, 3] by default to prevent outliers."""
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    # Create a huge spike at the end
    values = [100.0] * 99 + [10000.0]
    df = pd.DataFrame({"A": values}, index=dates)
    zscores = compute_rolling_zscore(df, window=20, clamp=3.0)
    assert zscores["A"].iloc[-1] <= 3.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_causal_discovery/test_zscore.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: Write zscore.py**

```python
# backend/app/causal_discovery/engine/zscore.py
"""Rolling z-score computation for node values."""

from __future__ import annotations

import pandas as pd


def compute_rolling_zscore(
    df: pd.DataFrame,
    window: int = 90,
    clamp: float = 3.0,
) -> pd.DataFrame:
    """Compute rolling z-score for each column in the DataFrame.

    z = (value - rolling_mean) / rolling_std

    Args:
        df: DataFrame with columns=node_ids, index=dates, values=raw data
        window: Rolling window size in trading days
        clamp: Clamp z-scores to [-clamp, +clamp] to prevent outlier distortion

    Returns:
        DataFrame of same shape with z-scores instead of raw values.
    """
    rolling_mean = df.rolling(window=window, min_periods=max(1, window // 4)).mean()
    rolling_std = df.rolling(window=window, min_periods=max(1, window // 4)).std()

    # Avoid division by zero: where std is 0 or very small, z-score is 0
    rolling_std = rolling_std.replace(0, float("nan"))

    zscores = (df - rolling_mean) / rolling_std
    zscores = zscores.fillna(0.0)

    if clamp:
        zscores = zscores.clip(lower=-clamp, upper=clamp)

    return zscores
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_causal_discovery/test_zscore.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Verify all tests pass**

Run: `cd backend && pytest tests/ -q --tb=short`
Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/app/causal_discovery/engine/zscore.py backend/tests/test_causal_discovery/test_zscore.py
git commit -m "feat(causal-discovery): add rolling z-score engine with clamping"
```

---

## Chunk 5: Causal Discovery Engine

### Task 5.1: Create PCMCI wrapper

**Files:**
- Create: `backend/app/causal_discovery/engine/causal.py`
- Test: `backend/tests/test_causal_discovery/test_causal.py`

- [ ] **Step 1: Add tigramite and lingam to requirements.txt**

```bash
cd backend
echo "tigramite>=5.2" >> requirements.txt
echo "lingam>=1.12" >> requirements.txt
pip install tigramite lingam
```

- [ ] **Step 2: Write failing test**

```python
# backend/tests/test_causal_discovery/test_causal.py
"""Tests for causal discovery engine — uses synthetic data."""

import numpy as np
import pandas as pd
import pytest

# Skip entire module if tigramite not installed (e.g., CI without heavy deps)
tigramite = pytest.importorskip("tigramite", reason="tigramite not installed")

from app.causal_discovery.engine.causal import discover_edges_pcmci


def _make_causal_data(n=500):
    """Create synthetic time-series with known causal structure: A → B → C."""
    np.random.seed(42)
    a = np.random.randn(n).cumsum()
    b = np.zeros(n)
    c = np.zeros(n)
    for t in range(1, n):
        b[t] = 0.7 * a[t - 1] + 0.3 * np.random.randn()
        c[t] = 0.5 * b[t - 1] + 0.3 * np.random.randn()
    dates = pd.date_range("2020-01-01", periods=n, freq="B")
    return pd.DataFrame({"A": a, "B": b, "C": c}, index=dates)


def test_discover_edges_pcmci_finds_causal_link():
    """PCMCI should discover A → B edge from synthetic data."""
    df = _make_causal_data()
    edges = discover_edges_pcmci(df, max_lag=3, significance_level=0.05)
    # Should find at least A→B
    edge_pairs = [(e["source"], e["target"]) for e in edges]
    assert ("A", "B") in edge_pairs, f"Expected A→B in edges, got: {edge_pairs}"


def test_discover_edges_returns_weights():
    """Each discovered edge has a weight."""
    df = _make_causal_data()
    edges = discover_edges_pcmci(df, max_lag=3)
    for edge in edges:
        assert "weight" in edge
        assert "source" in edge
        assert "target" in edge
        assert "lag" in edge
        assert isinstance(edge["weight"], float)
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd backend && pytest tests/test_causal_discovery/test_causal.py -v`
Expected: FAIL — ImportError

- [ ] **Step 4: Write causal.py**

```python
# backend/app/causal_discovery/engine/causal.py
"""Causal discovery wrappers — PCMCI+ and VARLiNGAM."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def discover_edges_pcmci(
    df: pd.DataFrame,
    max_lag: int = 5,
    significance_level: float = 0.01,
) -> list[dict]:
    """Run PCMCI+ on a DataFrame and return discovered edges.

    Args:
        df: DataFrame with columns=node_ids, index=dates, values=z-scores or returns
        max_lag: Maximum time lag to test
        significance_level: p-value threshold for edge inclusion

    Returns:
        List of dicts: {source, target, weight, lag, direction}
    """
    import tigramite
    from tigramite import data_processing as pp
    from tigramite.pcmci import PCMCI
    from tigramite.independence_tests.parcorr import ParCorr

    var_names = list(df.columns)
    data = df.values  # numpy array (T x N)

    dataframe = pp.DataFrame(data, var_names=var_names)
    parcorr = ParCorr(significance="analytic")
    pcmci = PCMCI(dataframe=dataframe, cond_ind_test=parcorr, verbosity=0)

    results = pcmci.run_pcmciplus(tau_max=max_lag, pc_alpha=significance_level)

    edges = []
    graph = results["graph"]
    val_matrix = results["val_matrix"]

    n_vars = len(var_names)
    for i in range(n_vars):
        for j in range(n_vars):
            for tau in range(max_lag + 1):
                if graph[i, j, tau] == "-->":
                    weight = float(abs(val_matrix[i, j, tau]))
                    direction = "positive" if val_matrix[i, j, tau] > 0 else "negative"
                    edges.append({
                        "source": var_names[i],
                        "target": var_names[j],
                        "weight": weight,
                        "lag": tau,
                        "direction": direction,
                    })

    logger.info("PCMCI+ discovered %d edges from %d variables", len(edges), n_vars)
    return edges


def discover_edges_varlingam(
    df: pd.DataFrame,
    max_lag: int = 3,
    min_weight: float = 0.1,
) -> list[dict]:
    """Run VARLiNGAM on a DataFrame and return discovered edges.

    Args:
        df: DataFrame with columns=node_ids, index=dates
        max_lag: Number of lags in the VAR model
        min_weight: Minimum absolute weight to include an edge

    Returns:
        List of dicts: {source, target, weight, lag, direction}
    """
    import lingam

    var_names = list(df.columns)
    model = lingam.VARLiNGAM(lags=max_lag)
    model.fit(df.values)

    edges = []
    # adjacency_matrices_[k] is the (N x N) matrix for lag k
    for lag_idx, adj_matrix in enumerate(model.adjacency_matrices_):
        n = adj_matrix.shape[0]
        for i in range(n):
            for j in range(n):
                w = adj_matrix[i, j]
                if abs(w) >= min_weight:
                    edges.append({
                        "source": var_names[j],
                        "target": var_names[i],
                        "weight": float(abs(w)),
                        "lag": lag_idx,
                        "direction": "positive" if w > 0 else "negative",
                    })

    logger.info("VARLiNGAM discovered %d edges from %d variables", len(edges), len(var_names))
    return edges
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd backend && pytest tests/test_causal_discovery/test_causal.py -v --timeout=60`
Expected: All 2 tests PASS. PCMCI may take 10-30 seconds on synthetic data.

- [ ] **Step 6: Verify all tests pass**

Run: `cd backend && pytest tests/ -q --tb=short`
Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add backend/app/causal_discovery/engine/causal.py backend/tests/test_causal_discovery/test_causal.py backend/requirements.txt
git commit -m "feat(causal-discovery): add PCMCI+ and VARLiNGAM causal discovery engine"
```

---

## Chunk 6: Anchor Propagation + Node Importance

### Task 6.1: Create anchor propagation

**Files:**
- Create: `backend/app/causal_discovery/engine/anchors.py`
- Test: `backend/tests/test_causal_discovery/test_anchors.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_causal_discovery/test_anchors.py
"""Tests for anchor polarity propagation."""

import networkx as nx

from app.causal_discovery.engine.anchors import propagate_polarity


def test_positive_edge_preserves_polarity():
    """Positive edge: anchor +1 → neighbor +1."""
    g = nx.DiGraph()
    g.add_node("sp500")
    g.add_node("tech")
    g.add_edge("sp500", "tech", direction="positive", weight=0.8)
    anchors = {"sp500": 1}
    polarity = propagate_polarity(g, anchors)
    assert polarity["sp500"] == 1
    assert polarity["tech"] == 1


def test_negative_edge_flips_polarity():
    """Negative edge: anchor +1 → neighbor -1."""
    g = nx.DiGraph()
    g.add_node("sp500")
    g.add_node("vix")
    g.add_edge("sp500", "vix", direction="negative", weight=0.8)
    anchors = {"sp500": 1}
    polarity = propagate_polarity(g, anchors)
    assert polarity["vix"] == -1


def test_transitivity():
    """Polarity propagates through chains: sp500(+1) → vix(-1) → put_call(-1)."""
    g = nx.DiGraph()
    g.add_edge("sp500", "vix", direction="negative", weight=0.8)
    g.add_edge("vix", "put_call", direction="positive", weight=0.6)
    anchors = {"sp500": 1}
    polarity = propagate_polarity(g, anchors)
    assert polarity["vix"] == -1
    assert polarity["put_call"] == -1  # positive edge from negative node


def test_unconnected_node_gets_zero():
    """Nodes not reachable from any anchor get polarity 0."""
    g = nx.DiGraph()
    g.add_node("sp500")
    g.add_node("isolated")
    anchors = {"sp500": 1}
    polarity = propagate_polarity(g, anchors)
    assert polarity.get("isolated", 0) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_causal_discovery/test_anchors.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: Write anchors.py**

```python
# backend/app/causal_discovery/engine/anchors.py
"""Anchor polarity propagation — infer display polarity from a small set of anchor nodes."""

from __future__ import annotations

from collections import deque

import networkx as nx


def propagate_polarity(
    graph: nx.DiGraph,
    anchors: dict[str, int],
    max_depth: int = 10,
) -> dict[str, int]:
    """Propagate polarity (+1/-1) from anchor nodes through the causal graph.

    Uses BFS. Sign flips on negative edges, preserves on positive edges.
    Multiple paths sum — the dominant sign wins.

    Args:
        graph: Directed graph with edges having 'direction' and 'weight' attributes
        anchors: {node_id: +1 or -1} for anchor nodes
        max_depth: Maximum propagation depth

    Returns:
        {node_id: +1 or -1 or 0} for all nodes
    """
    # Accumulate weighted polarity signals
    signals: dict[str, float] = {}

    for anchor_id, anchor_polarity in anchors.items():
        if anchor_id not in graph:
            continue
        signals[anchor_id] = signals.get(anchor_id, 0) + float(anchor_polarity)

        # BFS from this anchor
        queue: deque[tuple[str, float, int]] = deque()
        queue.append((anchor_id, float(anchor_polarity), 0))
        visited: set[tuple[str, str]] = set()

        while queue:
            node_id, current_polarity, depth = queue.popleft()
            if depth >= max_depth:
                continue

            for _, target_id, edge_data in graph.out_edges(node_id, data=True):
                edge_key = (node_id, target_id)
                if edge_key in visited:
                    continue
                visited.add(edge_key)

                direction = edge_data.get("direction", "positive")
                weight = edge_data.get("weight", edge_data.get("effective_weight", 0.5))
                sign = -1.0 if direction == "negative" else 1.0

                propagated = current_polarity * sign * weight
                signals[target_id] = signals.get(target_id, 0) + propagated

                queue.append((target_id, propagated, depth + 1))

    # Convert accumulated signals to +1/-1/0
    polarity: dict[str, int] = {}
    for node_id in graph.nodes():
        s = signals.get(node_id, 0)
        if s > 0:
            polarity[node_id] = 1
        elif s < 0:
            polarity[node_id] = -1
        else:
            polarity[node_id] = 0

    return polarity
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_causal_discovery/test_anchors.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/causal_discovery/engine/anchors.py backend/tests/test_causal_discovery/test_anchors.py
git commit -m "feat(causal-discovery): add anchor polarity propagation via BFS"
```

### Task 6.2: Create node importance filter

**Files:**
- Create: `backend/app/causal_discovery/engine/importance.py`
- Test: `backend/tests/test_causal_discovery/test_importance.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_causal_discovery/test_importance.py
"""Tests for node importance ranking."""

import networkx as nx

from app.causal_discovery.engine.importance import rank_nodes_by_importance


def test_central_node_ranks_higher():
    """Hub node with many connections ranks higher than leaf."""
    g = nx.DiGraph()
    # Hub connects to 5 nodes
    for i in range(5):
        g.add_edge("hub", f"leaf_{i}", weight=0.5)
    # Leaf only has 1 connection
    g.add_edge("isolated", "leaf_0", weight=0.5)

    ranking = rank_nodes_by_importance(g)
    hub_rank = next(r for r in ranking if r["node_id"] == "hub")
    iso_rank = next(r for r in ranking if r["node_id"] == "isolated")
    assert hub_rank["score"] > iso_rank["score"]


def test_top_n_filter():
    """Can limit results to top N nodes."""
    g = nx.DiGraph()
    for i in range(20):
        g.add_edge(f"a_{i}", f"b_{i}", weight=0.5)
    ranking = rank_nodes_by_importance(g, top_n=5)
    assert len(ranking) == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_causal_discovery/test_importance.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: Write importance.py**

```python
# backend/app/causal_discovery/engine/importance.py
"""Node importance ranking for filtering the discovered graph."""

from __future__ import annotations

import networkx as nx


def rank_nodes_by_importance(
    graph: nx.DiGraph,
    top_n: int | None = None,
) -> list[dict]:
    """Rank nodes by combined importance score.

    Combines degree centrality, betweenness centrality, and eigenvector centrality.

    Returns:
        Sorted list of {node_id, score, degree, betweenness, eigenvector}
    """
    if graph.number_of_nodes() == 0:
        return []

    degree = nx.degree_centrality(graph)
    betweenness = nx.betweenness_centrality(graph, weight="weight")
    try:
        eigenvector = nx.eigenvector_centrality(graph, max_iter=1000, weight="weight")
    except nx.PowerIterationFailedConvergence:
        eigenvector = {n: 0.0 for n in graph.nodes()}

    ranking = []
    for node_id in graph.nodes():
        score = (
            0.4 * degree.get(node_id, 0)
            + 0.4 * betweenness.get(node_id, 0)
            + 0.2 * eigenvector.get(node_id, 0)
        )
        ranking.append({
            "node_id": node_id,
            "score": score,
            "degree": degree.get(node_id, 0),
            "betweenness": betweenness.get(node_id, 0),
            "eigenvector": eigenvector.get(node_id, 0),
        })

    ranking.sort(key=lambda x: x["score"], reverse=True)

    if top_n:
        ranking = ranking[:top_n]

    return ranking
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_causal_discovery/test_importance.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Verify all tests pass**

Run: `cd backend && pytest tests/ -q --tb=short`
Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/app/causal_discovery/engine/importance.py backend/tests/test_causal_discovery/test_importance.py
git commit -m "feat(causal-discovery): add node importance ranking (degree + betweenness + eigenvector)"
```

---

## Chunk 7: Full Pipeline API + Integration

### Task 7.1: Add discover endpoint that runs the full pipeline

**Files:**
- Modify: `backend/app/causal_discovery/api/routes.py`

- [ ] **Step 1: Add the `/api/causal/discover` and `/api/causal/graph` endpoints**

Add to `routes.py`:

```python
_discovery_status = {"running": False, "last_result": None}


async def _run_discovery_task():
    """Background task for causal discovery."""
    from app.causal_discovery.engine.causal import discover_edges_pcmci
    from app.causal_discovery.engine.matrix import get_daily_matrix
    from app.causal_discovery.engine.zscore import compute_rolling_zscore

    _discovery_status["running"] = True
    try:
        async with async_session() as session:
            matrix = await get_daily_matrix(session, days=252 * 2)
            if matrix.empty:
                _discovery_status["last_result"] = {"error": "No data. Run backfill first.", "edges": []}
                return

            zscores = compute_rolling_zscore(matrix, window=90)
            zscores = zscores.dropna(how="all")
            edges = discover_edges_pcmci(zscores, max_lag=5, significance_level=0.01)

            _discovery_status["last_result"] = {
                "edges_discovered": len(edges),
                "nodes_in_matrix": len(matrix.columns),
                "days_in_matrix": len(matrix),
                "edges": edges,
            }
    except Exception as e:
        _discovery_status["last_result"] = {"error": str(e)}
    finally:
        _discovery_status["running"] = False


@router.post("/discover")
async def run_discovery(background_tasks: BackgroundTasks):
    """Run full causal discovery pipeline in background (can take minutes)."""
    if _discovery_status["running"]:
        return {"status": "already_running"}
    background_tasks.add_task(_run_discovery_task)
    return {"status": "started"}


@router.get("/discover/status")
async def discovery_status():
    """Check causal discovery progress."""
    return _discovery_status


@router.get("/graph")
async def get_discovered_graph():
    """Get the full discovered graph with z-scores and polarity."""
    from app.causal_discovery.engine.anchors import propagate_polarity
    from app.causal_discovery.engine.importance import rank_nodes_by_importance
    from app.causal_discovery.engine.causal import discover_edges_pcmci
    from app.causal_discovery.engine.matrix import get_daily_matrix
    from app.causal_discovery.engine.zscore import compute_rolling_zscore

    import networkx as nx

    async with async_session() as session:
        matrix = await get_daily_matrix(session, days=252 * 2)
        if matrix.empty:
            return {"error": "No data available. Run backfill first."}

        zscores = compute_rolling_zscore(matrix, window=90).dropna(how="all")
        edges = discover_edges_pcmci(zscores, max_lag=5)

        # Build NetworkX graph from discovered edges
        g = nx.DiGraph()
        for col in zscores.columns:
            g.add_node(col)
        for e in edges:
            g.add_edge(e["source"], e["target"], weight=e["weight"], direction=e["direction"])

        # Polarity
        anchors = {"sp500": 1, "nasdaq": 1, "us_gdp_growth": 1, "unemployment_rate": -1}
        polarity = propagate_polarity(g, anchors)

        # Importance
        importance = rank_nodes_by_importance(g, top_n=100)
        important_ids = {r["node_id"] for r in importance}

        # Current z-scores (last row)
        latest_z = zscores.iloc[-1].to_dict() if len(zscores) > 0 else {}

        nodes = []
        for node_id in important_ids:
            z = latest_z.get(node_id, 0.0)
            p = polarity.get(node_id, 0)
            nodes.append({
                "id": node_id,
                "zscore": round(z, 4),
                "polarity": p,
                "display_sentiment": round(max(-1, min(1, z * p)), 4),
            })

        filtered_edges = [e for e in edges if e["source"] in important_ids and e["target"] in important_ids]

        return {
            "nodes": nodes,
            "edges": filtered_edges,
            "total_nodes": len(zscores.columns),
            "displayed_nodes": len(nodes),
            "total_edges": len(edges),
            "displayed_edges": len(filtered_edges),
        }
```

- [ ] **Step 2: Verify existing tests still pass**

Run: `cd backend && pytest tests/ -q --tb=short`
Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add backend/app/causal_discovery/api/routes.py
git commit -m "feat(causal-discovery): add discover + graph API endpoints for full pipeline"
```

### Task 7.2: Full integration test

- [ ] **Step 1: Rebuild Docker and test the full flow**

```bash
# Rebuild with new dependencies
sudo docker compose up --build backend -d

# Wait for startup
sleep 10

# Trigger backfill (takes 2-5 minutes depending on network)
curl -X POST http://localhost:8000/api/causal/backfill

# Monitor progress
curl http://localhost:8000/api/causal/backfill/status

# Check data stats
curl http://localhost:8000/api/causal/stats | python3 -m json.tool

# Run causal discovery (takes 30-120 seconds)
curl -X POST http://localhost:8000/api/causal/discover | python3 -m json.tool

# Get full graph
curl http://localhost:8000/api/causal/graph | python3 -m json.tool | head -50
```

Expected:
- `stats` shows 20+ nodes with 1000+ rows each
- `discover` returns edges with source, target, weight, lag, direction
- `graph` returns nodes with zscore, polarity, display_sentiment + filtered edges

- [ ] **Step 2: Verify all unit tests still pass**

Run: `cd backend && pytest tests/ -q --tb=short`
Expected: All tests pass.

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat(causal-discovery): complete Phase 1-6 integration — data pipeline to discovered graph"
```

---

## Summary of Phases

| Chunk | What it delivers | Exit criterion |
|-------|-----------------|----------------|
| 1 | Package structure + NodeValue model + config + hypertable | `pytest` passes, model importable, settings added |
| 2 | Data source registry + yfinance/FRED fetchers | Fetchers return DataFrames from real APIs |
| 3 | Backfill pipeline + API trigger | `curl /api/causal/backfill` fills DB with years of data |
| 4 | Matrix builder + z-score engine | `get_daily_matrix()` returns aligned DataFrame, z-scores computed |
| 5 | PCMCI/VARLiNGAM causal discovery | Synthetic test: A→B→C discovered from data |
| 6 | Anchor propagation + node importance | VIX gets negative polarity from sp500 anchor |
| 7 | Full pipeline API + integration | `curl /api/causal/graph` returns discovered graph with scores |

## Files Created (total)

```
backend/app/causal_discovery/
├── __init__.py
├── README.md                         (already exists)
├── models.py
├── pipeline/
│   ├── __init__.py
│   ├── sources.py
│   ├── fetchers.py
│   └── backfill.py
├── engine/
│   ├── __init__.py
│   ├── matrix.py
│   ├── zscore.py
│   ├── causal.py
│   ├── importance.py
│   └── anchors.py
└── api/
    ├── __init__.py
    └── routes.py

backend/tests/test_causal_discovery/
├── __init__.py
├── conftest.py                      ← shared fixtures (sample_daily_matrix)
├── test_models.py
├── test_sources.py
├── test_fetchers.py
├── test_backfill.py
├── test_matrix.py
├── test_zscore.py
├── test_causal.py
├── test_anchors.py
└── test_importance.py
```

## Files Created (config/tooling)

```
backend/pyproject.toml               ← pytest config (asyncio_mode, markers)
```

## Files Modified

```
backend/app/main.py                   (+5 lines: import + router + hypertable)
backend/app/config.py                 (+7 lines: causal discovery settings)
backend/requirements.txt              (+3 lines: pandas, tigramite, lingam)
```

## Dependencies Added

```
pandas>=2.2.0           # Matrix operations — new dependency
tigramite>=5.2          # PCMCI causal discovery — new dependency
lingam>=1.12            # VARLiNGAM causal discovery — new dependency
pytest-asyncio>=0.23.0  # Async test support — dev dependency
```

Note: `dowhy` and `graph-tool` are deferred to a future phase. They require additional setup (graph-tool needs conda) and are for validation/enhancement, not the core pipeline.
