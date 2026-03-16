# Causal Discovery Phase D — Design Spec

**Goal:** Extend the causal discovery module with edge validation, per-regime discovery, shock simulation UI, anchor management, historical charts, expanded data sources, network stats, and two utility API endpoints.

**Context:** Phase A-C delivered: data pipeline (35 nodes, yfinance + FRED), 3 scoring methods, PCMCI+/Granger discovery, graph persistence, frontend toggle/panel/animation. Phase D adds production depth.

---

## 1. DoWhy Edge Validation (auto, post-discovery)

### Behavior

After any causal discovery run completes (PCMCI+, Granger, RPCMCI), automatically run DoWhy validation on every discovered edge before storing the snapshot. Each edge is enriched with validation metadata.

### DoWhy integration approach

The discovered edges form a DAG (directed acyclic graph after time-lag unrolling). To validate with DoWhy:

1. Build a `dowhy.gcm.StructuralCausalModel` from the full discovered DAG
2. Fit the SCM to the time-series data matrix (each column = node, each row = time step)
3. For each edge `(source → target)`:
   - **Arrow strength**: call `dowhy.gcm.arrow_strength(scm, target)` which returns the causal contribution of each parent to the target. Extract the value for `source`.
   - **Refutation**: use `dowhy.gcm.falsify_graph()` or per-edge conditional independence tests. For each edge, test if `source ⊥ target | parents(target) \ {source}` — if independent, the edge is spurious.
4. Time-lagged edges: flatten to contemporaneous by treating `node_t` and `node_t-1` as separate variables in the SCM. The data matrix is augmented with lagged columns before fitting.

### Validation steps per edge

1. **Arrow strength** — `dowhy.gcm.arrow_strength()` on the fitted SCM: quantifies the causal contribution of the source node to the target. Returns a float (higher = stronger causal claim).
2. **Refutation** — conditional independence test: for each edge `source → target`, test whether source and target are conditionally independent given the other parents of target. If independent (p-value < 0.05), the edge is likely spurious.
3. An edge "passes" if arrow_strength > 0.01 AND the conditional independence test confirms dependence (p-value >= 0.05).

### Data storage

Each edge in the `DiscoveredGraph.edges` JSONB array gains a `validation` field:

```json
{
  "source": "sp500",
  "target": "vix",
  "weight": 0.45,
  "direction": "negative",
  "lag": 1,
  "validation": {
    "arrow_strength": 0.32,
    "refutation_passed": true,
    "ci_test_p_value": 0.72
  }
}
```

### Backend

- New file: `engine/validation.py`
  - `validate_edges(edges, data_matrix, dag: nx.DiGraph) -> list[dict]` — takes discovered edges, the time-series matrix, AND the full DAG structure. Builds a DoWhy SCM, fits it, computes arrow strength per edge and runs conditional independence refutation. Returns edges enriched with validation data.
  - Falls back gracefully if DoWhy fails on specific edges (stores `validation: null` for those edges)
- Modify `api/routes.py` discovery flow: after `discover_edges_*()` returns, build the DAG, call `validate_edges()` before persisting
- Add `dowhy>=0.14` to `requirements.txt`

### Frontend

- `CausalNodePanel.tsx`: each edge in the incoming/outgoing lists shows a validation badge — green checkmark if refutation passed, red X if failed, strength score as a number
- `CausalPanel.tsx`: in the network stats section, show "X/Y edges validated" summary

---

## 2. Per-Regime Discovery (RPCMCI)

### Behavior

New algorithm option "RPCMCI" in the frontend dropdown. Tigramite's `RPCMCI` auto-detects regime change points in the time-series data and discovers separate causal structures per regime.

### Flow

1. User selects algorithm="RPCMCI" and a scoring method
2. `POST /api/causal/discover?algorithm=rpcmci&scoring=zscore`
3. Backend runs `RPCMCI` which returns multiple causal graphs (one per detected regime)
4. Each regime stored as a separate `DiscoveredGraph` snapshot:
   - `run_name`: `rpcmci_zscore_regime0`, `rpcmci_zscore_regime1`, etc.
   - `parameters` JSONB includes: `{ regime_index: 0, regime_count: 2, regime_timepoints: [...] }`
5. DoWhy validation runs independently on each regime's graph

### Backend

- New function in `engine/causal.py`: `discover_edges_rpcmci(matrix, node_ids, **kwargs)`
  - **Primary approach**: use `tigramite.rpcmci.RPCMCI` if available in tigramite >= 5.2. This class extends PCMCI with regime detection via hidden Markov models.
  - **Fallback approach**: if `RPCMCI` class is not available in the installed tigramite version, implement manual regime segmentation: (1) detect regime change points using `ruptures` library (Pelt algorithm on variance), (2) run standard PCMCI+ separately on each regime's time window, (3) return per-regime edge lists.
  - Add `ruptures>=1.1` to `requirements.txt` as fallback dependency.
  - Passes raw daily matrix (not z-scored — regime detection needs raw dynamics)
  - Returns a list of `(regime_index, edges, timepoint_range)` tuples
- Modify discovery route to handle multi-snapshot return: loop over regimes, validate each, store each as separate snapshot

### Feasibility note

At implementation time, verify tigramite's RPCMCI API with `python -c "from tigramite.rpcmci import RPCMCI"`. If the import fails, use the fallback approach. Both approaches produce the same output shape (per-regime edge lists) so the rest of the pipeline is unaffected.

### Frontend

- Add "RPCMCI" to algorithm dropdown options in `CausalPanel.tsx`
- When RPCMCI snapshots exist for current scoring: show a regime selector sub-dropdown (e.g., "Regime 0 (2023-01 to 2024-06)" / "Regime 1 (2024-06 to 2025-03)")
- Each regime graph is a standard snapshot — animation, simulation, node panel all work unchanged

---

## 3. Shock Propagation UI on Discovered Graph

### Behavior

When a node is selected in discovered mode, CausalNodePanel shows a what-if slider. User drags to a hypothetical value, clicks Simulate, sees cascade visualized on the 3D graph.

### Backend

None — `POST /api/causal/graph/simulate` already exists and works with discovered graphs. Note: this endpoint accepts **query parameters** (not JSON body): `?node_id=sp500&signal=-0.5&snapshot_id=3`.

### Frontend

- Add `CausalSimulationSlider` to `CausalNodePanel.tsx`:
  - Slider range: -1.0 to +1.0, step 0.05 — represents the **shock signal magnitude** sent directly to the API's `signal` parameter (not an absolute sentiment level)
  - Label shows "Shock: +0.35" or "Shock: -0.50"
  - "Simulate" button, disabled if |value| < 0.01
  - "Clear" button when simulation active
  - Shows total affected nodes after simulation
- Add `runCausalSimulation(nodeId: string, signal: number)` to `useCausalStore`:
  - Calls `POST /api/causal/graph/simulate?node_id=${nodeId}&signal=${signal}&snapshot_id=${currentGraph.id}` (query params, matching the existing endpoint signature)
  - Writes result to `useGraphStore.simulation` so Graph3D's existing overlay renders
- Add `clearCausalSimulation()` to `useCausalStore` — clears `useGraphStore.simulation`

### Type note

The causal simulate endpoint returns `snapshot_id` in its response which is not in the existing `SimulationResult` TypeScript interface. Either extend the type or strip the field before writing to the store.

---

## 4. Anchor CRUD UI/API

### Data model

```sql
CREATE TABLE causal_anchors (
    id          SERIAL PRIMARY KEY,
    node_id     TEXT NOT NULL,
    scoring     TEXT NOT NULL,  -- 'zscore', 'returns', 'volatility'
    polarity    INTEGER NOT NULL,  -- +1 or -1
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(node_id, scoring)
);
```

Seeded on startup with current hardcoded anchors if table is empty.

### Backend

- New model in `models.py`: `CausalAnchor`
- New endpoints in `routes.py`:
  - `GET /api/causal/anchors?scoring=zscore` — list anchors
  - `POST /api/causal/anchors` — create `{ node_id, scoring, polarity }`
  - `PUT /api/causal/anchors/{id}` — update polarity
  - `DELETE /api/causal/anchors/{id}` — remove
- Modify discovery flow: query `causal_anchors` table instead of hardcoded `_ANCHORS_BY_SCORING`
- New endpoint: `POST /api/causal/graph/repropagate?id=N` — re-runs anchor polarity propagation on an existing snapshot using current anchors, updates the snapshot's node polarity in-place. This lets users see the effect of anchor changes without re-running full discovery.
- Seed defaults in lifespan startup if table empty
- `CausalAnchor` model extends `Base` (same as `DiscoveredGraph`, `NodeValue`) — auto-created by `Base.metadata.create_all()` during startup

### Anchor change semantics

- Anchor changes only affect **future discovery runs** and explicit **re-propagation** calls
- Existing snapshots retain their original polarity until re-propagated
- Changing anchors while a discovery run is in progress has no effect on that run (it reads anchors at start)

### Frontend

- New collapsible section in `CausalPanel.tsx`: "Anchor Nodes"
- Lists anchors for current scoring: node label, polarity badge (+1 green / -1 red), delete button
- "Add Anchor" row: node dropdown + polarity toggle + add button
- Click polarity badge to flip +1 ↔ -1
- After CRUD, call re-propagate endpoint on current snapshot and reload graph

---

## 5. Historical Score Chart on Discovered Nodes

### Backend endpoint

`GET /api/causal/node/{node_id}?scoring=zscore&days=90`

Returns:
```json
{
  "node_id": "sp500",
  "scoring": "zscore",
  "days": 90,
  "history": [
    { "date": "2025-03-15", "raw_value": 5620.1, "scored_value": 0.42 },
    ...
  ]
}
```

Queries `node_values`, applies scoring function over the window, returns scored time-series only. Node metadata (polarity, importance, edges) is already available from the graph snapshot — no duplication needed.

### Frontend

- New component: `CausalScoreChart.tsx` — Lightweight Charts line chart
  - Green line above 0, red below 0
  - Zero-line reference
  - Range buttons: 30d / 90d / 1y
  - Current value dot highlighted
- Embedded in `CausalNodePanel.tsx` between stats and edges sections
- Same UX pattern as expert mode's `SentimentChart.tsx`

---

## 6. More Data Sources

### Tier 1 — Extend existing pipelines

Add to `sources.py`:

| Node | Source | Ticker/Series |
|------|--------|--------------|
| eurusd | yfinance | `EURUSD=X` |
| usdjpy | yfinance | `USDJPY=X` |
| gbpusd | yfinance | `GBPUSD=X` |
| usdcny | yfinance | `USDCNY=X` |
| brent_crude | yfinance | `BZ=F` |
| move_index | yfinance | `^MOVE` |
| skew_index | yfinance | `^SKEW` |
| us_political_risk | FRED | `USEPUINDXD` |
| ecb_policy_rate | FRED | `ECBDFR` |
| japan_boj_policy | FRED | `INTDSRJPM193N` |
| consumer_confidence | FRED | `UMCSENT` |
| pce_deflator | FRED | `PCEPILFE` |
| wage_growth | FRED | `CES0500000003` |

### Tier 2 — CSV download fetchers

New file: `pipeline/fetchers_csv.py`

| Source | URL pattern | Frequency | Node |
|--------|------------|-----------|------|
| CBOE put/call ratio | `cboe.com/market_statistics/` | Daily | put_call_ratio |
| AAII investor sentiment | `aaii.com/sentimentsurvey` | Weekly | retail_sentiment |
| Shiller CAPE | `shiller.xls` from Yale | Monthly | pe_valuations |
| GPR Index | `matteoiacoviello.com/gpr_files/` | Monthly | geopolitical_risk_index |

### Tier 3 — REST API fetchers

New file: `pipeline/fetchers_api.py`

| Source | API | Frequency | Nodes |
|--------|-----|-----------|-------|
| CFTC CoT | CFTC.gov JSON API | Weekly | institutional_positioning |
| GDELT | api.gdeltproject.org | Daily | geopolitical_risk, sanctions_risk |
| ECB rates (fallback) | ECB Statistical Data Warehouse | Daily | ecb_policy_rate |
| BOJ rates (fallback) | BOJ time-series | Daily | japan_boj_policy |

FRED proxies preferred for ECB/BOJ. Direct APIs are fallback only.

### Feasibility notes

- **CBOE put/call**: URL may change; implement with fallback error handling
- **AAII sentiment**: free data may be limited; check if CSV export requires membership. If blocked, skip this source.
- **GDELT**: aggressive rate limits, noisy data. Use daily summary endpoint, not real-time.
- **CFTC CoT**: released Fridays with 3-day delay. Store as weekly frequency.
- **GPR/Shiller**: monthly frequency, use `last()` forward-fill for daily alignment (already handled by TimescaleDB query)

### Integration

- Extend `backfill.py` to include all new sources
- Each writes to `node_values` table (same schema)
- Expected node count: ~35 → ~55-60

---

## 7. Network Stats Panel

### Metrics displayed

- Node count / Edge count
- Graph density (edges / max possible)
- Average degree
- Top 3 hub nodes (by degree centrality) — clickable
- Clustering coefficient
- Validation summary (if available): "X/Y edges passed refutation"

### Backend

- Compute density, average degree, and clustering coefficient server-side during graph storage. Store in the snapshot's `parameters` JSONB: `{ ..., stats: { density: 0.12, avg_degree: 3.5, clustering: 0.31 } }`
- Clustering coefficient uses NetworkX `nx.average_clustering(G)` on the directed graph — correct semantics for directed networks

### Frontend

- New collapsible section in `CausalPanel.tsx` below algorithm/scoring selectors
- Node count, edge count, top 3 hubs: computed client-side from snapshot
- Density, average degree, clustering coefficient: read from `currentGraph.parameters.stats`
- Validation summary: computed client-side by counting edges with `validation.refutation_passed === true`

---

## 8. GET /api/causal/matrix

### Endpoint

`GET /api/causal/matrix?days=252&scoring=raw`

Parameters:
- `days` — lookback window (default 252)
- `scoring` — `raw` (unscored matrix, bypasses `compute_scores`), `zscore`, `returns`, `volatility`

Response:
```json
{
  "days": 252,
  "scoring": "zscore",
  "node_ids": ["sp500", "vix", ...],
  "dates": ["2025-03-15", "2025-03-14", ...],
  "matrix": [[0.42, -1.3, ...], ...]
}
```

~60 nodes × 252 days = ~15K cells. No pagination needed.

### Backend

- New endpoint in `routes.py`
- Calls existing `get_daily_matrix()` + optionally applies scoring from `scoring.py`

---

## File Impact Summary

### New files
- `backend/app/causal_discovery/engine/validation.py`
- `backend/app/causal_discovery/pipeline/fetchers_csv.py`
- `backend/app/causal_discovery/pipeline/fetchers_api.py`
- `frontend/src/components/CausalScoreChart.tsx`

### Type changes
- `frontend/src/types/graph.ts` — extend `CausalEdge` with optional `validation` field; extend `SimulationResult` or strip `snapshot_id` from causal simulate response

### Modified files
- `backend/app/causal_discovery/engine/causal.py` — add `discover_edges_rpcmci()`
- `backend/app/causal_discovery/models.py` — add `CausalAnchor` model
- `backend/app/causal_discovery/api/routes.py` — anchor CRUD, `/node/{id}`, `/matrix`, validation in discovery flow, RPCMCI multi-snapshot
- `backend/app/causal_discovery/pipeline/sources.py` — expand node registry
- `backend/app/causal_discovery/pipeline/backfill.py` — include new sources
- `backend/requirements.txt` — add `dowhy>=0.14`
- `frontend/src/components/CausalPanel.tsx` — RPCMCI dropdown, regime selector, anchor CRUD section, network stats
- `frontend/src/components/CausalNodePanel.tsx` — simulation slider, score chart, validation badges
- `frontend/src/hooks/useCausalStore.ts` — causal simulation methods, anchor fetch
