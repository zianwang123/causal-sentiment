# Causal Discovery Phase D Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add DoWhy edge validation, RPCMCI per-regime discovery, shock propagation UI, anchor CRUD, historical score charts, expanded data sources, network stats, and utility API endpoints to the causal discovery module.

**Architecture:** Backend-first approach — new engine modules (validation.py), new data fetchers (CSV + API), expanded routes.py with CRUD + utility endpoints. Frontend follows with store updates, new components (CausalScoreChart, simulation slider), and CausalPanel extensions (anchors, stats, regime selector).

**Tech Stack:** Python (DoWhy, ruptures, httpx), FastAPI, SQLAlchemy, TimescaleDB, React/TypeScript, Zustand, Lightweight Charts

**Spec:** `docs/superpowers/specs/2026-03-15-causal-discovery-phase-d-design.md`

---

## Chunk 1: Backend — Algorithms, Validation, Endpoints

### Task 1: Dependencies

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Add new dependencies**

Add to `backend/requirements.txt`:
```
dowhy>=0.14
ruptures>=1.1
openpyxl>=3.1
```

- [ ] **Step 2: Install and verify**

Run: `cd backend && pip install dowhy ruptures openpyxl`
Verify: `python -c "import dowhy; import ruptures; print('OK')"`

- [ ] **Step 3: Commit**

```bash
git add backend/requirements.txt
git commit -m "deps: add dowhy, ruptures, openpyxl for Phase D"
```

---

### Task 2: DoWhy Edge Validation Engine

**Files:**
- Create: `backend/app/causal_discovery/engine/validation.py`
- Test: `backend/tests/test_causal_discovery/test_validation.py`

- [ ] **Step 1: Write the test**

```python
# backend/tests/test_causal_discovery/test_validation.py
import pandas as pd
import numpy as np
import networkx as nx
from app.causal_discovery.engine.validation import validate_edges

def test_validate_edges_basic():
    """validate_edges should return edges with validation field."""
    np.random.seed(42)
    n = 200
    x = np.random.randn(n)
    y = 0.5 * x + np.random.randn(n) * 0.3  # y causally depends on x
    z = np.random.randn(n)  # z is independent
    df = pd.DataFrame({"x": x, "y": y, "z": z})

    edges = [
        {"source": "x", "target": "y", "weight": 0.5, "lag": 0, "direction": "positive"},
        {"source": "z", "target": "y", "weight": 0.1, "lag": 0, "direction": "positive"},
    ]
    dag = nx.DiGraph()
    dag.add_edge("x", "y")
    dag.add_edge("z", "y")

    result = validate_edges(edges, df, dag)
    assert len(result) == 2
    # x->y should have validation data
    xy = next(e for e in result if e["source"] == "x")
    assert "validation" in xy
    assert xy["validation"] is not None
    assert "arrow_strength" in xy["validation"]
    assert "refutation_passed" in xy["validation"]

def test_validate_edges_graceful_failure():
    """validate_edges should return validation=null on failure, not crash."""
    df = pd.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0]})  # too few rows
    edges = [{"source": "a", "target": "b", "weight": 0.5, "lag": 0, "direction": "positive"}]
    dag = nx.DiGraph()
    dag.add_edge("a", "b")

    result = validate_edges(edges, df, dag)
    assert len(result) == 1
    assert result[0]["validation"] is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_causal_discovery/test_validation.py -v`
Expected: FAIL (module not found)

- [ ] **Step 3: Implement validation.py**

Create `backend/app/causal_discovery/engine/validation.py`:

```python
"""DoWhy edge validation — arrow strength + conditional independence refutation."""
from __future__ import annotations

import logging
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def validate_edges(
    edges: list[dict[str, Any]],
    data_matrix: pd.DataFrame,
    dag: nx.DiGraph,
) -> list[dict[str, Any]]:
    """Validate discovered edges using DoWhy's GCM module.

    For each edge, computes:
    - arrow_strength: causal contribution of source to target
    - refutation_passed: conditional independence test result

    Falls back gracefully — stores validation=null for edges that fail.

    Parameters
    ----------
    edges : list[dict]
        Discovered edges with source, target, weight, lag, direction.
    data_matrix : pd.DataFrame
        Aligned daily matrix used for discovery.
    dag : nx.DiGraph
        The full discovered DAG.

    Returns
    -------
    list[dict]
        Same edges, each enriched with a 'validation' field.
    """
    try:
        from dowhy import gcm
    except ImportError:
        logger.warning("DoWhy not installed — skipping validation")
        return [{**e, "validation": None} for e in edges]

    # Build SCM from DAG
    scm = gcm.StructuralCausalModel(dag)

    # Assign causal mechanisms (auto-assign AdditiveNoiseModel for continuous data)
    gcm.auto.assign_causal_mechanisms(scm, data_matrix)

    # Fit the SCM
    try:
        gcm.fit(scm, data_matrix)
    except Exception as exc:
        logger.warning("DoWhy SCM fitting failed: %s — skipping validation", exc)
        return [{**e, "validation": None} for e in edges]

    # Compute arrow strengths per target node
    # Cache: group edges by target, compute arrow_strength once per target
    targets = set(e["target"] for e in edges)
    strength_cache: dict[str, dict[str, float]] = {}

    for target in targets:
        try:
            strengths = gcm.arrow_strength(scm, target)
            strength_cache[target] = {
                str(k): float(v) for k, v in strengths.items()
            }
        except Exception as exc:
            logger.debug("Arrow strength failed for target=%s: %s", target, exc)
            strength_cache[target] = {}

    # Validate each edge
    validated = []
    for edge in edges:
        src, tgt = edge["source"], edge["target"]
        try:
            # Arrow strength
            arrow_str = strength_cache.get(tgt, {}).get(src, 0.0)

            # Conditional independence test: is src independent of tgt given other parents?
            parents = list(dag.predecessors(tgt))
            conditioning = [p for p in parents if p != src]

            if len(conditioning) > 0 and len(data_matrix) > 20:
                from scipy.stats import pearsonr
                # Partial correlation as CI proxy
                residual_src = _residualize(data_matrix[src].values,
                    data_matrix[conditioning].values)
                residual_tgt = _residualize(data_matrix[tgt].values,
                    data_matrix[conditioning].values)
                _, p_value = pearsonr(residual_src, residual_tgt)
            else:
                # No conditioning set — just test marginal correlation
                from scipy.stats import pearsonr
                _, p_value = pearsonr(
                    data_matrix[src].values, data_matrix[tgt].values
                )

            # p < 0.05 means we reject the null hypothesis of conditional independence,
            # i.e., the variables ARE dependent = edge is real.
            # NOTE: spec says p >= 0.05 but that's statistically backwards.
            # We use p < 0.05 (standard significance test for dependence).
            refutation_passed = (
                arrow_str > 0.01 and p_value < 0.05
            )

            validated.append({
                **edge,
                "validation": {
                    "arrow_strength": round(float(arrow_str), 4),
                    "refutation_passed": refutation_passed,
                    "ci_test_p_value": round(float(p_value), 4),
                },
            })
        except Exception as exc:
            logger.debug("Validation failed for %s->%s: %s", src, tgt, exc)
            validated.append({**edge, "validation": None})

    passed = sum(1 for e in validated if e.get("validation", {}) and e["validation"].get("refutation_passed"))
    logger.info("DoWhy validation: %d/%d edges passed", passed, len(validated))
    return validated


def _residualize(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Remove linear effect of X from y (OLS residuals)."""
    X = np.column_stack([X, np.ones(len(X))])
    try:
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        return y - X @ beta
    except np.linalg.LinAlgError:
        return y
```

- [ ] **Step 4: Run tests**

Run: `cd backend && pytest tests/test_causal_discovery/test_validation.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/causal_discovery/engine/validation.py backend/tests/test_causal_discovery/test_validation.py
git commit -m "feat: add DoWhy edge validation engine"
```

---

### Task 3: RPCMCI Per-Regime Discovery

**Files:**
- Modify: `backend/app/causal_discovery/engine/causal.py`
- Test: `backend/tests/test_causal_discovery/test_rpcmci.py`

- [ ] **Step 1: Write the test**

```python
# backend/tests/test_causal_discovery/test_rpcmci.py
import pandas as pd
import numpy as np
from app.causal_discovery.engine.causal import discover_edges_rpcmci

def test_rpcmci_returns_regimes():
    """RPCMCI should return a list of (regime_index, edges, timerange) tuples."""
    np.random.seed(42)
    n = 300
    # Two regimes: first half has strong x->y, second half has weak
    x = np.random.randn(n)
    y = np.zeros(n)
    y[:150] = 0.8 * x[:150] + np.random.randn(150) * 0.2
    y[150:] = 0.1 * x[150:] + np.random.randn(150) * 0.8
    df = pd.DataFrame({"x": x, "y": y}, index=pd.date_range("2020-01-01", periods=n))

    result = discover_edges_rpcmci(df)
    assert isinstance(result, list)
    assert len(result) >= 1
    for regime_idx, edges, timerange in result:
        assert isinstance(regime_idx, int)
        assert isinstance(edges, list)
        assert isinstance(timerange, tuple)
        assert len(timerange) == 2  # (start_idx, end_idx)
```

- [ ] **Step 2: Implement discover_edges_rpcmci**

Add to `backend/app/causal_discovery/engine/causal.py`:

```python
def discover_edges_rpcmci(
    df: pd.DataFrame,
    max_lag: int = 5,
    significance_level: float = 0.01,
) -> list[tuple[int, list[dict[str, Any]], tuple[int, int]]]:
    """Per-regime causal discovery using change point detection + PCMCI+.

    Detects regime change points using the ruptures library (Pelt algorithm),
    then runs PCMCI+ independently on each regime's time window.

    Returns a list of (regime_index, edges, (start_idx, end_idx)) tuples.
    """
    import ruptures

    columns = list(df.columns)
    data = df.values.astype(np.float64)

    # Detect regime change points using variance-based Pelt
    model = "rbf"
    algo = ruptures.Pelt(model=model, min_size=max(30, len(data) // 10)).fit(data)
    breakpoints = algo.predict(pen=10)  # penalty controls sensitivity

    # Build regime windows from breakpoints
    boundaries = [0] + breakpoints  # breakpoints include len(data) as last element
    if boundaries[-1] != len(data):
        boundaries.append(len(data))

    # Ensure at least 2 regime windows; merge tiny segments
    MIN_SEGMENT = max(50, max_lag * 3)
    merged = [boundaries[0]]
    for b in boundaries[1:]:
        if b - merged[-1] >= MIN_SEGMENT:
            merged.append(b)
    if merged[-1] != len(data):
        merged.append(len(data))
    if len(merged) < 2:
        merged = [0, len(data)]

    results = []
    for i in range(len(merged) - 1):
        start, end = merged[i], merged[i + 1]
        if end - start < MIN_SEGMENT:
            continue
        segment_df = df.iloc[start:end]
        try:
            edges = discover_edges_pcmci(
                segment_df, max_lag=max_lag,
                significance_level=significance_level,
            )
            results.append((i, edges, (start, end)))
        except Exception as exc:
            logger.warning("RPCMCI regime %d failed: %s", i, exc)
            results.append((i, [], (start, end)))

    if not results:
        # Fallback: single regime = full data
        edges = discover_edges_pcmci(df, max_lag=max_lag, significance_level=significance_level)
        results.append((0, edges, (0, len(data))))

    logger.info("RPCMCI: %d regimes detected, breakpoints=%s", len(results),
                 [r[2] for r in results])
    return results
```

- [ ] **Step 3: Run tests**

Run: `cd backend && pytest tests/test_causal_discovery/test_rpcmci.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add backend/app/causal_discovery/engine/causal.py backend/tests/test_causal_discovery/test_rpcmci.py
git commit -m "feat: add RPCMCI per-regime causal discovery"
```

---

### Task 4: CausalAnchor Model + CRUD Endpoints

**Files:**
- Modify: `backend/app/causal_discovery/models.py`
- Modify: `backend/app/causal_discovery/api/routes.py`

- [ ] **Step 1: Add CausalAnchor model**

Add to `models.py` after `DiscoveredGraph`:

Add `UniqueConstraint` to the imports at the top of `models.py`:
```python
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, text, func, UniqueConstraint
```

Then add the model:
```python
class CausalAnchor(Base):
    """Anchor nodes for polarity propagation, configurable per scoring method."""
    __tablename__ = "causal_anchors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String(64), nullable=False)
    scoring = Column(String(32), nullable=False)  # 'zscore', 'returns', 'volatility'
    polarity = Column(Integer, nullable=False)  # +1 or -1
    created_at = Column(DateTime(timezone=True), default=func.now())

    __table_args__ = (UniqueConstraint("node_id", "scoring", name="uq_anchor_node_scoring"),)
```

- [ ] **Step 2: Add seed function**

Add to `models.py`:

```python
async def seed_default_anchors(conn: AsyncConnection) -> None:
    """Seed default anchors if the table is empty."""
    from sqlalchemy import select, func as sqlfunc
    result = await conn.execute(select(sqlfunc.count()).select_from(CausalAnchor))
    count = result.scalar()
    if count and count > 0:
        return

    defaults = {
        "zscore": {"sp500": 1, "nasdaq": 1, "russell2000": 1, "us_gdp_growth": 1,
                   "unemployment_rate": -1, "dxy_index": -1, "us_10y_yield": -1,
                   "vix": -1, "wti_crude": -1},
        "returns": {"sp500": 1, "nasdaq": 1, "russell2000": 1, "us_gdp_growth": 1,
                    "unemployment_rate": -1, "dxy_index": -1, "us_10y_yield": -1,
                    "vix": -1, "wti_crude": -1},
        "volatility": {"sp500": -1, "nasdaq": -1, "russell2000": -1, "vix": -1,
                       "us_10y_yield": -1, "gold": 1, "dxy_index": -1,
                       "hy_credit_spread": -1, "wti_crude": -1},
    }

    for scoring, anchors in defaults.items():
        for node_id, polarity in anchors.items():
            await conn.execute(
                CausalAnchor.__table__.insert().values(
                    node_id=node_id, scoring=scoring, polarity=polarity
                )
            )
    # No explicit commit needed — engine.begin() auto-commits on context exit
    logger.info("Seeded %d default anchors", sum(len(a) for a in defaults.values()))
```

- [ ] **Step 3: Add CRUD endpoints to routes.py**

Add to `routes.py`:

```python
@router.get("/anchors")
async def list_anchors(
    scoring: str = "zscore",
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """List anchor nodes for a scoring method."""
    from app.causal_discovery.models import CausalAnchor
    from sqlalchemy import select
    query = select(CausalAnchor).where(CausalAnchor.scoring == scoring)
    result = await session.execute(query)
    return [{"id": r.id, "node_id": r.node_id, "scoring": r.scoring,
             "polarity": r.polarity} for r in result.scalars().all()]

from pydantic import BaseModel

class AnchorCreate(BaseModel):
    node_id: str
    scoring: str
    polarity: int  # +1 or -1

@router.post("/anchors")
async def create_anchor(
    body: AnchorCreate,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Create a new anchor node."""
    from app.causal_discovery.models import CausalAnchor
    if body.polarity not in (1, -1):
        raise HTTPException(400, "Polarity must be +1 or -1")
    anchor = CausalAnchor(node_id=body.node_id, scoring=body.scoring, polarity=body.polarity)
    session.add(anchor)
    await session.commit()
    return {"id": anchor.id, "node_id": anchor.node_id,
            "scoring": anchor.scoring, "polarity": anchor.polarity}

@router.put("/anchors/{anchor_id}")
async def update_anchor(
    anchor_id: int, polarity: int,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Update an anchor's polarity."""
    from app.causal_discovery.models import CausalAnchor
    from sqlalchemy import select
    if polarity not in (1, -1):
        raise HTTPException(400, "Polarity must be +1 or -1")
    result = await session.execute(
        select(CausalAnchor).where(CausalAnchor.id == anchor_id))
    anchor = result.scalar_one_or_none()
    if not anchor:
        raise HTTPException(404, "Anchor not found")
    anchor.polarity = polarity
    await session.commit()
    return {"id": anchor.id, "node_id": anchor.node_id,
            "scoring": anchor.scoring, "polarity": anchor.polarity}

@router.delete("/anchors/{anchor_id}")
async def delete_anchor(
    anchor_id: int,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Delete an anchor."""
    from app.causal_discovery.models import CausalAnchor
    from sqlalchemy import select
    result = await session.execute(
        select(CausalAnchor).where(CausalAnchor.id == anchor_id))
    anchor = result.scalar_one_or_none()
    if not anchor:
        raise HTTPException(404, "Anchor not found")
    await session.delete(anchor)
    await session.commit()
    return {"deleted": True}
```

- [ ] **Step 4: Add repropagate endpoint**

```python
@router.post("/graph/repropagate")
async def repropagate_polarity(
    id: int,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Re-run polarity propagation on an existing snapshot using current DB anchors."""
    from app.causal_discovery.models import DiscoveredGraph, CausalAnchor
    from sqlalchemy import select

    result = await session.execute(
        select(DiscoveredGraph).where(DiscoveredGraph.id == id))
    graph = result.scalar_one_or_none()
    if not graph:
        raise HTTPException(404, "Graph not found")

    scoring = graph.parameters.get("scoring", "zscore") if graph.parameters else "zscore"
    anchor_result = await session.execute(
        select(CausalAnchor).where(CausalAnchor.scoring == scoring))
    anchors = {r.node_id: r.polarity for r in anchor_result.scalars().all()}

    if not anchors:
        anchors = _ANCHORS_BY_SCORING.get(scoring, _DEFAULT_ANCHORS)

    g = _build_graph_from_edges(graph.edges)
    polarity = propagate_polarity(g, anchors)

    updated_nodes = []
    for node in graph.nodes:
        p = polarity.get(node["id"], 0)
        z = node.get("zscore", 0.0)
        display = p * min(abs(z) / 3.0, 1.0)
        updated_nodes.append({**node, "polarity": p,
                             "display_sentiment": round(max(-1, min(1, display)), 4)})

    graph.nodes = updated_nodes
    await session.commit()
    return {"id": graph.id, "node_count": len(updated_nodes),
            "anchors_used": len(anchors)}
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/causal_discovery/models.py backend/app/causal_discovery/api/routes.py
git commit -m "feat: add CausalAnchor model + CRUD + repropagate endpoints"
```

---

### Task 5: Wire Validation + RPCMCI + Stats into Discovery Flow

**Files:**
- Modify: `backend/app/causal_discovery/api/routes.py`

- [ ] **Step 1: Modify _run_discovery_task to load anchors from DB**

In `_run_discovery_task`, replace:
```python
anchors = _ANCHORS_BY_SCORING.get(scoring, _DEFAULT_ANCHORS)
```
with:
```python
# Load anchors from DB, fall back to hardcoded
from app.causal_discovery.models import CausalAnchor
from sqlalchemy import select as sa_select
anchor_result = await session.execute(
    sa_select(CausalAnchor).where(CausalAnchor.scoring == scoring))
db_anchors = {r.node_id: r.polarity for r in anchor_result.scalars().all()}
anchors = db_anchors if db_anchors else _ANCHORS_BY_SCORING.get(scoring, _DEFAULT_ANCHORS)
```

(This requires moving the anchor query inside the `async with async_session()` block.)

- [ ] **Step 2: Add RPCMCI to the algorithm dispatcher**

First, extract the node-building + persisting logic from the existing single-regime flow into a reusable helper function `_persist_snapshot()`. This function takes edges, the scored dataframe, scoring method, anchors, and metadata, and handles: building the graph, propagating polarity, computing importance, computing display z-scores, validating edges via DoWhy, computing graph stats, and persisting to DB.

Then add the RPCMCI branch after the `granger` elif:
```python
elif algorithm == "rpcmci":
    from app.causal_discovery.engine.causal import discover_edges_rpcmci
    # RPCMCI uses raw data for regime detection (not z-scored)
    regime_results = await asyncio.to_thread(
        discover_edges_rpcmci, df, max_lag, significance_level,
    )
    # Store each regime as a separate snapshot
    snapshot_ids = []
    async with async_session() as session:
        for regime_idx, regime_edges, timerange in regime_results:
            regime_run_name = f"{run_name}_regime{regime_idx}"
            snapshot_id = await _persist_snapshot(
                session=session,
                edges=regime_edges,
                scored_df=zscores,
                raw_df=df,
                run_name=regime_run_name,
                algorithm=algorithm,
                scoring=scoring,
                anchors=anchors,
                zscore_window=zscore_window,
                extra_params={
                    "regime_index": regime_idx,
                    "regime_count": len(regime_results),
                    "regime_timepoints": list(timerange),
                },
            )
            snapshot_ids.append(snapshot_id)
    _discovery_status["state"] = "completed"
    _discovery_status["last_result"] = {
        "snapshot_ids": snapshot_ids,
        "run_name": run_name,
        "algorithm": algorithm,
        "regime_count": len(regime_results),
    }
    return  # Early return — multi-snapshot handled
```

The `_persist_snapshot` helper should be extracted from lines 199-271 of the existing `_run_discovery_task` function. It encapsulates: `_build_graph_from_edges`, `propagate_polarity`, `rank_nodes_by_importance`, display z-score computation, DoWhy `validate_edges`, graph stats computation, and `DiscoveredGraph` creation + commit.

- [ ] **Step 3: Add DoWhy validation before persisting**

After building `edges_json` and before persisting, add:
```python
# DoWhy validation
from app.causal_discovery.engine.validation import validate_edges
edges_json = await asyncio.to_thread(validate_edges, edges_json, zscores, g)
```

- [ ] **Step 4: Compute and store graph stats**

After building the graph `g`, add:
```python
# Compute graph stats for network panel
stats = {
    "density": round(nx.density(g), 4),
    "avg_degree": round(sum(d for _, d in g.degree()) / max(g.number_of_nodes(), 1), 2),
    "clustering": round(nx.average_clustering(g), 4),
}
```

Then in the `parameters` dict when creating the snapshot, add `"stats": stats`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/causal_discovery/api/routes.py
git commit -m "feat: wire DoWhy validation + RPCMCI + stats into discovery flow"
```

---

### Task 6: Node History + Matrix API Endpoints

**Files:**
- Modify: `backend/app/causal_discovery/api/routes.py`

- [ ] **Step 1: Add GET /node/{node_id} endpoint**

```python
@router.get("/node/{node_id}")
async def get_node_history(
    node_id: str,
    scoring: str = "zscore",
    days: int = 90,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get a node's scored time-series history."""
    df = await get_daily_matrix(session, days=days)
    if node_id not in df.columns:
        raise HTTPException(404, f"Node '{node_id}' not found in data")

    from app.causal_discovery.engine.scoring import compute_scores
    scored = compute_scores(df[[node_id]], method=scoring,
                           window=90 if scoring == "zscore" else 20)

    history = []
    for date, row in scored.iterrows():
        raw_val = df.loc[date, node_id] if date in df.index else None
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "raw_value": round(float(raw_val), 4) if raw_val is not None else None,
            "scored_value": round(float(row[node_id]), 4),
        })

    return {"node_id": node_id, "scoring": scoring, "days": days, "history": history}
```

- [ ] **Step 2: Add GET /matrix endpoint**

```python
@router.get("/matrix")
async def get_matrix(
    days: int = 252,
    scoring: str = "raw",
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get the aligned daily data matrix, optionally scored."""
    df = await get_daily_matrix(session, days=days)
    if df.empty:
        raise HTTPException(400, "No data available")

    if scoring != "raw":
        from app.causal_discovery.engine.scoring import compute_scores
        window = 90 if scoring == "zscore" else 20
        df = compute_scores(df, method=scoring, window=window)

    return {
        "days": days,
        "scoring": scoring,
        "node_ids": list(df.columns),
        "dates": [d.strftime("%Y-%m-%d") for d in df.index],
        "matrix": df.round(4).values.tolist(),
    }
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/causal_discovery/api/routes.py
git commit -m "feat: add /node/{id} history + /matrix API endpoints"
```

---

### Task 7: Seed Anchors on Startup

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Add anchor seeding to lifespan**

In the `lifespan` handler in `main.py`, after `create_hypertable_if_needed`, add:
```python
from app.causal_discovery.models import seed_default_anchors
await seed_default_anchors(conn)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/main.py
git commit -m "feat: seed default anchors on startup"
```

---

## Chunk 2: Data Sources Expansion

### Task 8: Tier 1 — Add Missing yfinance + FRED Sources

**Files:**
- Modify: `backend/app/causal_discovery/pipeline/sources.py`

- [ ] **Step 1: Add missing sources**

The following are NOT yet in sources.py and need adding:

To `YFINANCE_SOURCES`:
```python
{"node_id": "gbpusd", "ticker": "GBPUSD=X", "source_type": "yfinance",
 "description": "GBP/USD exchange rate"},
```

To `FRED_SOURCES`:
```python
{"node_id": "ecb_policy_rate", "series_id": "ECBDFR",
 "source_type": "fred", "description": "ECB deposit facility rate"},
{"node_id": "japan_boj_policy", "series_id": "INTDSRJPM193N",
 "source_type": "fred", "description": "Bank of Japan policy rate"},
```

Note: eurusd, usdjpy, usdcny, brent_crude, move_index, skew_index, consumer_confidence, pce_deflator, wage_growth, us_political_risk are ALREADY in sources.py.

- [ ] **Step 2: Commit**

```bash
git add backend/app/causal_discovery/pipeline/sources.py
git commit -m "feat: add gbpusd, ECB rate, BOJ rate data sources"
```

---

### Task 9: Tier 2 — CSV Download Fetchers

**Files:**
- Create: `backend/app/causal_discovery/pipeline/fetchers_csv.py`

- [ ] **Step 1: Implement CSV fetchers**

```python
"""CSV/Excel download fetchers for CBOE, AAII, Shiller, GPR data sources."""
from __future__ import annotations

import io
import logging
from datetime import datetime

import httpx
import pandas as pd

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*",
}


async def fetch_shiller_cape(start_date: str = "2000-01-01") -> list[dict]:
    """Fetch Shiller CAPE ratio from Yale's Excel file."""
    url = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
    async with httpx.AsyncClient(timeout=30, headers=HEADERS) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    df = pd.read_excel(io.BytesIO(resp.content), sheet_name="Data",
                       skiprows=7, usecols="A,B,K", names=["date_raw", "price", "cape"])
    df = df.dropna(subset=["cape"])
    # date_raw is like 2020.01 (year.month)
    df["date"] = pd.to_datetime(df["date_raw"].apply(
        lambda x: f"{int(x)}-{int((x % 1) * 100 + 0.5):02d}-01" if pd.notna(x) else None
    ))
    df = df[df["date"] >= start_date]

    return [{"node_id": "pe_valuations", "ts": row["date"], "value": float(row["cape"]),
             "source": "shiller"} for _, row in df.iterrows()]


async def fetch_gpr_index(start_date: str = "2000-01-01") -> list[dict]:
    """Fetch Geopolitical Risk Index from Caldara-Iacoviello."""
    url = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
    async with httpx.AsyncClient(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    df = pd.read_excel(io.BytesIO(resp.content))
    # Columns vary; look for date + GPR
    date_col = [c for c in df.columns if "date" in str(c).lower()][0]
    gpr_col = [c for c in df.columns if "gpr" in str(c).lower() and "hist" not in str(c).lower()][0]
    df["date"] = pd.to_datetime(df[date_col])
    df = df[df["date"] >= start_date].dropna(subset=[gpr_col])

    return [{"node_id": "geopolitical_risk_index", "ts": row["date"],
             "value": float(row[gpr_col]), "source": "gpr_index"}
            for _, row in df.iterrows()]


async def fetch_cboe_put_call() -> list[dict]:
    """Fetch CBOE equity put/call ratio. URL may change — fail gracefully."""
    url = "https://www.cboe.com/us/options/market_statistics/daily/"
    try:
        async with httpx.AsyncClient(timeout=30, headers=HEADERS, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
        # Parse HTML table or CSV — CBOE format varies
        # Fallback: use the totalpc.csv endpoint
        csv_url = "https://www.cboe.com/us/options/market_statistics/daily/totalpc.csv"
        async with httpx.AsyncClient(timeout=30, headers=HEADERS) as client:
            resp = await client.get(csv_url)
        df = pd.read_csv(io.StringIO(resp.text))
        df.columns = [c.strip().lower() for c in df.columns]
        return [{"node_id": "put_call_ratio", "ts": pd.to_datetime(row.get("trade_date", row.get("date"))),
                 "value": float(row.get("p/c_ratio", row.get("total_ratio", 0))),
                 "source": "cboe"} for _, row in df.iterrows() if row.get("p/c_ratio") or row.get("total_ratio")]
    except Exception as exc:
        logger.warning("CBOE put/call fetch failed: %s", exc)
        return []


async def fetch_aaii_sentiment() -> list[dict]:
    """Fetch AAII investor sentiment survey. May require membership — fail gracefully."""
    try:
        url = "https://www.aaii.com/files/surveys/sentiment.xls"
        async with httpx.AsyncClient(timeout=30, headers=HEADERS, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
        df = pd.read_excel(io.BytesIO(resp.content), skiprows=3)
        date_col = df.columns[0]
        bull_col = [c for c in df.columns if "bull" in str(c).lower()][0]
        df["date"] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=["date", bull_col])
        # Use bull-bear spread as sentiment score
        bear_col = [c for c in df.columns if "bear" in str(c).lower()]
        if bear_col:
            df["spread"] = df[bull_col] - df[bear_col[0]]
        else:
            df["spread"] = df[bull_col]
        return [{"node_id": "retail_sentiment", "ts": row["date"],
                 "value": float(row["spread"]), "source": "aaii"}
                for _, row in df.iterrows()]
    except Exception as exc:
        logger.warning("AAII sentiment fetch failed (may need membership): %s", exc)
        return []
```

- [ ] **Step 2: Add source entries to sources.py**

```python
# Tier 2 CSV sources
CSV_SOURCES: list[dict] = [
    {"node_id": "pe_valuations", "source_type": "csv_shiller",
     "description": "Shiller CAPE ratio (monthly)"},
    {"node_id": "geopolitical_risk_index", "source_type": "csv_gpr",
     "description": "Geopolitical Risk Index (daily)"},
    {"node_id": "put_call_ratio", "source_type": "csv_cboe",
     "description": "CBOE equity put/call ratio (daily)"},
    {"node_id": "retail_sentiment", "source_type": "csv_aaii",
     "description": "AAII investor sentiment survey (weekly)"},
]
```

Update `get_all_sources()` to include `CSV_SOURCES`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/causal_discovery/pipeline/fetchers_csv.py backend/app/causal_discovery/pipeline/sources.py
git commit -m "feat: add CSV fetchers for Shiller, GPR, CBOE, AAII"
```

---

### Task 10: Tier 3 — REST API Fetchers

**Files:**
- Create: `backend/app/causal_discovery/pipeline/fetchers_api.py`

- [ ] **Step 1: Implement API fetchers**

```python
"""REST API fetchers for CFTC CoT and GDELT data sources."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

import httpx
import pandas as pd

logger = logging.getLogger(__name__)


async def fetch_cftc_cot(start_date: str = "2020-01-01") -> list[dict]:
    """Fetch CFTC Commitments of Traders data (weekly, 3-day delay)."""
    # CFTC EDGAR-like API
    url = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
    params = {
        "$where": f"report_date_as_yyyy_mm_dd >= '{start_date}'",
        "$limit": 5000,
        "$order": "report_date_as_yyyy_mm_dd DESC",
        "market_and_exchange_names": "S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE",
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
        data = resp.json()
        results = []
        for row in data:
            date = pd.to_datetime(row.get("report_date_as_yyyy_mm_dd"))
            # Net speculative position = long - short
            net = (int(row.get("noncomm_positions_long_all", 0)) -
                   int(row.get("noncomm_positions_short_all", 0)))
            results.append({"node_id": "institutional_positioning", "ts": date,
                           "value": float(net), "source": "cftc"})
        return results
    except Exception as exc:
        logger.warning("CFTC CoT fetch failed: %s", exc)
        return []


async def fetch_gdelt_tone(days: int = 365) -> list[dict]:
    """Fetch GDELT daily average tone for geopolitical risk and sanctions."""
    results = []
    # GDELT GKG API — daily summary
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    queries = {
        "geopolitical_risk": "geopolitical risk conflict military",
        "sanctions_risk": "sanctions embargo trade restrictions",
    }

    for node_id, query in queries.items():
        try:
            url = "https://api.gdeltproject.org/api/v2/doc/doc"
            params = {
                "query": query,
                "mode": "timelinetone",
                "format": "json",
                "timespan": f"{days}days",
            }
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
            data = resp.json()
            for entry in data.get("timeline", [{}])[0].get("data", []):
                date = pd.to_datetime(entry["date"], format="%Y%m%dT%H%M%S")
                results.append({"node_id": node_id, "ts": date,
                               "value": float(entry["value"]), "source": "gdelt"})
        except Exception as exc:
            logger.warning("GDELT fetch failed for %s: %s", node_id, exc)

    return results
```

- [ ] **Step 2: Add source entries**

Add to `sources.py`:
```python
API_SOURCES: list[dict] = [
    {"node_id": "institutional_positioning", "source_type": "api_cftc",
     "description": "CFTC Commitments of Traders (weekly)"},
    {"node_id": "geopolitical_risk", "source_type": "api_gdelt",
     "description": "GDELT geopolitical risk tone (daily)"},
    {"node_id": "sanctions_risk", "source_type": "api_gdelt",
     "description": "GDELT sanctions risk tone (daily)"},
]
```

Update `get_all_sources()` to include `API_SOURCES`.

- [ ] **Step 3: Update backfill.py to include new sources**

Add calls to the new fetchers in `run_backfill()`:
```python
# Tier 2: CSV sources
from app.causal_discovery.pipeline.fetchers_csv import (
    fetch_shiller_cape, fetch_gpr_index, fetch_cboe_put_call, fetch_aaii_sentiment
)
for fetcher in [fetch_shiller_cape, fetch_gpr_index, fetch_cboe_put_call, fetch_aaii_sentiment]:
    try:
        rows = await fetcher()
        # Insert rows into node_values...
    except Exception as exc:
        logger.warning("CSV fetch failed: %s", exc)

# Tier 3: API sources
from app.causal_discovery.pipeline.fetchers_api import fetch_cftc_cot, fetch_gdelt_tone
for fetcher in [fetch_cftc_cot, fetch_gdelt_tone]:
    try:
        rows = await fetcher()
        # Insert rows into node_values...
    except Exception as exc:
        logger.warning("API fetch failed: %s", exc)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/causal_discovery/pipeline/fetchers_api.py backend/app/causal_discovery/pipeline/sources.py backend/app/causal_discovery/pipeline/backfill.py
git commit -m "feat: add CFTC + GDELT API fetchers, wire all new sources into backfill"
```

---

## Chunk 3: Frontend

### Task 11: TypeScript Types + Store Updates

**Files:**
- Modify: `frontend/src/types/graph.ts`
- Modify: `frontend/src/hooks/useCausalStore.ts`

- [ ] **Step 1: Extend CausalEdge type**

In `types/graph.ts`, update `CausalEdge`:
```typescript
export interface EdgeValidation {
  arrow_strength: number;
  refutation_passed: boolean;
  ci_test_p_value: number;
}

export interface CausalEdge {
  source: string;
  target: string;
  weight: number;
  lag: number;
  direction: "positive" | "negative";
  validation?: EdgeValidation | null;
}
```

- [ ] **Step 2: Add causal simulation methods to useCausalStore**

```typescript
runCausalSimulation: async (nodeId: string, signal: number) => {
  const { currentGraph } = get();
  if (!currentGraph) return;
  try {
    const params = new URLSearchParams({
      node_id: nodeId,
      signal: String(signal),
      snapshot_id: String(currentGraph.id),
    });
    const res = await fetch(`${API_URL}/api/causal/graph/simulate?${params}`, {
      method: "POST",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    // Write to graphStore so Graph3D renders the overlay
    const { useGraphStore } = await import("@/hooks/useGraphData");
    useGraphStore.setState({ simulation: data });
  } catch (e) {
    set({ error: (e as Error).message });
  }
},
clearCausalSimulation: () => {
  // useGraphStore is imported at the top of the file (already used elsewhere in this store)
  useGraphStore.setState({ simulation: null });
},
```

Also add anchor fetch methods:
```typescript
fetchAnchors: async (scoring: string) => {
  try {
    const res = await fetch(`${API_URL}/api/causal/anchors?scoring=${scoring}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    set({ error: (e as Error).message });
    return [];
  }
},
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types/graph.ts frontend/src/hooks/useCausalStore.ts
git commit -m "feat: extend types + add simulation/anchor store methods"
```

---

### Task 12: Shock Propagation Slider in CausalNodePanel

**Files:**
- Modify: `frontend/src/components/CausalNodePanel.tsx`

- [ ] **Step 1: Add CausalSimulationSlider component**

Add before `EdgeRow` function:
```typescript
function CausalSimulationSlider({ nodeId }: { nodeId: string }) {
  const [value, setValue] = useState(0);
  const [running, setRunning] = useState(false);
  const runSim = useCausalStore((s) => s.runCausalSimulation);
  const clearSim = useCausalStore((s) => s.clearCausalSimulation);
  const simulation = useGraphStore((s) => s.simulation);
  const isActive = simulation?.source_node === nodeId;

  return (
    <div className="mb-4">
      <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">What-If Shock</h4>
      <div className="flex items-center gap-2 mb-2">
        <input type="range" min={-100} max={100} value={value * 100}
          onChange={(e) => setValue(Number(e.target.value) / 100)}
          className="flex-1 h-1 accent-purple-500" />
        <span className="text-xs font-mono text-gray-300 w-14 text-right">
          {value >= 0 ? "+" : ""}{value.toFixed(2)}
        </span>
      </div>
      <div className="flex gap-2">
        <button onClick={async () => { setRunning(true); await runSim(nodeId, value); setRunning(false); }}
          disabled={running || Math.abs(value) < 0.01}
          className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white text-xs py-1.5 rounded">
          {running ? "..." : "Simulate"}
        </button>
        {isActive && (
          <button onClick={clearSim}
            className="bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs py-1.5 px-3 rounded">
            Clear
          </button>
        )}
      </div>
      {isActive && simulation && (
        <div className="mt-1 text-[10px] text-gray-400">
          {simulation.total_nodes_affected} nodes affected
        </div>
      )}
    </div>
  );
}
```

Add `<CausalSimulationSlider nodeId={selectedNode.id} />` to the panel after the stats grid.

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/CausalNodePanel.tsx
git commit -m "feat: add shock propagation slider to CausalNodePanel"
```

---

### Task 13: Historical Score Chart

**Files:**
- Create: `frontend/src/components/CausalScoreChart.tsx`
- Modify: `frontend/src/components/CausalNodePanel.tsx`

- [ ] **Step 1: Create CausalScoreChart.tsx**

Follow the exact same pattern as `SentimentChart.tsx` but:
- Fetch from `${API_URL}/api/causal/node/${nodeId}?scoring=${scoring}&days=${range}`
- Range buttons: 30d / 90d / 365d
- Use `scored_value` from the response for the chart data
- Green line color above 0, red below 0

- [ ] **Step 2: Embed in CausalNodePanel**

Add `<CausalScoreChart nodeId={selectedNode.id} scoring={currentGraph.parameters.scoring} />` between stats grid and edges section.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/CausalScoreChart.tsx frontend/src/components/CausalNodePanel.tsx
git commit -m "feat: add historical score chart for discovered nodes"
```

---

### Task 14: Validation Badges on Edges

**Files:**
- Modify: `frontend/src/components/CausalNodePanel.tsx`

- [ ] **Step 1: Update EdgeRow to show validation**

In the `EdgeRow` component, after the weight/lag line, add:
```typescript
{edge.validation && (
  <div className="flex items-center gap-2 mt-0.5 text-[10px]">
    <span className={edge.validation.refutation_passed ? "text-green-400" : "text-red-400"}>
      {edge.validation.refutation_passed ? "✓" : "✗"} validated
    </span>
    <span className="text-gray-500">
      str: {edge.validation.arrow_strength.toFixed(2)}
    </span>
  </div>
)}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/CausalNodePanel.tsx
git commit -m "feat: add validation badges to edge rows"
```

---

### Task 15: Network Stats Panel + RPCMCI Dropdown + Anchor CRUD in CausalPanel

**Files:**
- Modify: `frontend/src/components/CausalPanel.tsx`

- [ ] **Step 1: Add RPCMCI to algorithm dropdown**

Change the algorithm `<select>` options:
```typescript
<option value="pcmci">PCMCI+</option>
<option value="granger">Granger</option>
<option value="rpcmci">RPCMCI (per-regime)</option>
```

Add explanation:
```typescript
rpcmci: "RPCMCI detects market regime changes and discovers separate causal structures per regime. Different relationships emerge in normal markets vs. crises.",
```

- [ ] **Step 2: Add regime selector**

When RPCMCI snapshots exist, show a sub-dropdown filtering by `regime` in run_name:
```typescript
{algorithm === "rpcmci" && snapshots.filter(s => s.run_name.startsWith(`rpcmci_${scoring}_regime`)).length > 0 && (
  <div className="mb-2">
    <label className="text-[10px] text-gray-500 uppercase block mb-1">Regime</label>
    <select ...>
      {snapshots.filter(s => s.run_name.startsWith(`rpcmci_${scoring}_regime`))
        .map(s => <option key={s.id} value={s.id}>{s.run_name}</option>)}
    </select>
  </div>
)}
```

- [ ] **Step 3: Add network stats section**

Below the "Current Graph" info box, add a stats section:
```typescript
{currentGraph && (
  <div className="mb-3 bg-gray-800/80 rounded p-2">
    <div className="text-[10px] text-gray-500 uppercase mb-1">Network Stats</div>
    <div className="text-[11px] text-gray-300 grid grid-cols-2 gap-1">
      <div>Density: <span className="text-gray-200">{currentGraph.parameters?.stats?.density ?? "—"}</span></div>
      <div>Avg degree: <span className="text-gray-200">{currentGraph.parameters?.stats?.avg_degree ?? "—"}</span></div>
      <div>Clustering: <span className="text-gray-200">{currentGraph.parameters?.stats?.clustering ?? "—"}</span></div>
      <div>Validated: <span className="text-gray-200">
        {currentGraph.edges.filter(e => e.validation?.refutation_passed).length}/{currentGraph.edges.length}
      </span></div>
    </div>
    {/* Top 3 hubs by degree centrality (clickable) */}
    <div className="mt-1 text-[10px] text-gray-500">
      Hubs: {(() => {
        const degree = new Map<string, number>();
        currentGraph.edges.forEach(e => {
          degree.set(e.source, (degree.get(e.source) ?? 0) + 1);
          degree.set(e.target, (degree.get(e.target) ?? 0) + 1);
        });
        return [...degree.entries()]
          .sort((a, b) => b[1] - a[1])
          .slice(0, 3)
          .map(([id]) => (
            <button key={id} onClick={() => loadGraph(currentGraph.id)}
              className="text-purple-400 hover:text-purple-300 mr-1">
              {getNodeLabel(id)}
            </button>
          ));
      })()}
    </div>
  </div>
)}
```

- [ ] **Step 4: Add anchor CRUD section**

Add a collapsible "Anchor Nodes" section with:
- Fetch anchors on scoring change: `useEffect` calls `GET /api/causal/anchors?scoring=${scoring}`
- List: node label, polarity badge (green +1 / red -1), delete button
- Add row: node dropdown, polarity toggle, add button
- CRUD calls the anchor endpoints, then calls repropagate

This is the most complex UI section. Implement as a sub-component `AnchorSection` within CausalPanel.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/CausalPanel.tsx
git commit -m "feat: add RPCMCI dropdown, regime selector, network stats, anchor CRUD to CausalPanel"
```

---

### Task 16: Update nodeLabels for new data sources

**Files:**
- Modify: `frontend/src/lib/nodeLabels.ts`

- [ ] **Step 1: Add labels for new nodes**

```typescript
gbpusd: "GBP/USD",
ecb_policy_rate: "ECB Policy Rate",
japan_boj_policy: "BOJ Policy Rate",
pe_valuations: "Shiller CAPE",
geopolitical_risk_index: "Geopolitical Risk (GPR)",
put_call_ratio: "Put/Call Ratio",
retail_sentiment: "Retail Sentiment (AAII)",
institutional_positioning: "Institutional Positioning",
geopolitical_risk: "Geopolitical Risk (GDELT)",
sanctions_risk: "Sanctions Risk",
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/lib/nodeLabels.ts
git commit -m "feat: add node labels for Phase D data sources"
```

---

### Task 17: Final Integration Test

- [ ] **Step 1: Restart backend**

```bash
cd /home/max/Documents/causal-sentiment/.worktrees/causal-discovery
docker compose restart backend
```

- [ ] **Step 2: Verify new endpoints**

```bash
# Anchors
curl http://localhost:8000/api/causal/anchors?scoring=zscore
# Node history
curl http://localhost:8000/api/causal/node/sp500?scoring=zscore&days=30
# Matrix
curl http://localhost:8000/api/causal/matrix?days=30&scoring=raw | head -100
```

- [ ] **Step 3: Trigger discovery with validation**

```bash
curl -X POST "http://localhost:8000/api/causal/discover?algorithm=pcmci&scoring=zscore&run_name=pcmci_zscore"
# Poll status
curl http://localhost:8000/api/causal/discover/status
# After completion, check validation data on edges
curl http://localhost:8000/api/causal/graph | python -m json.tool | grep -A5 validation
```

- [ ] **Step 4: Test frontend**

Open http://localhost:3001, switch to Discovered mode:
- Verify network stats show in CausalPanel
- Verify RPCMCI option in algorithm dropdown
- Verify anchor section appears
- Click a node → verify score chart loads
- Click a node → verify shock slider works
- Click a node → verify validation badges on edges

- [ ] **Step 5: Commit all remaining changes**

```bash
git add -A
git commit -m "feat: complete Phase D causal discovery integration"
```
