# Causal Sentiment

A **second brain for macro analysts**. Models the financial world as an interconnected causal factor graph — 52 nodes (financial products + macro factors), 117 directed causal edges — and makes it tangible through a 3D interactive visualization. An AI agent fetches real data, analyzes sentiment, and propagates impact through the network. You simulate hypothetical shocks ("what if oil crashes?") and watch the cascade. You pin your own reasoning to nodes. The tool remembers what you think, not just what the data says.

Not a trading signal. A reasoning tool.

## Status

- **Phase 1 (Foundation):** Complete — graph model, agent, 3D viz, API, WebSocket
- **Phase 2 (Real-time + Autonomy):** Complete — 52 nodes, 117 edges, market data (yfinance), scheduler, sentiment history charts, agent audit log
- **Phase 3 (Intelligence + Polish):** Complete — dynamic weight recalculation, anomaly detection (2σ auto-trigger), time slider, node clustering, Reddit integration
- **Phase 4 (Agent Intelligence):** Complete — planning phase, self-critique, cross-node consistency, confidence decomposition
- **Phase 5 (Validation):** Complete — prediction resolution, agent memory, track record feedback loop, scheduler toggle, predictions panel
- **Phase 6 (Hardening):** Complete — validation threshold fix, edge muting (no more permanent flips), retry logic (FRED/yfinance), magnitude scoring for predictions, regime refresh per phase
- **Phase 7 (What-If Simulator):** Complete — shock propagation simulator, impact report panel, cascade visualization on graph
- **Phase 8 (Second Brain):** Complete — analyst annotations (persistent per-node notes), regime narrator (LLM-generated macro narrative)
- **Phase 9 (Hardening II):** Complete — graph mutation lock, session rollback, background task crash recovery, agent timeout, WebSocket heartbeat, error boundary, CRUD error handling, AbortController, graphData memoization, timestamp fix
- **Phase 13 (Hardening IV + Data Pipeline):** Complete — 16 bug fixes (LLM error handling + retry + timeout, graph state rollback on agent error, batch propagation cascade fix, concurrent scheduler agent guard, accept_suggestion lock, missing import NameError, broadcast task tracking, annotation error handling, WebSocket effect fix, SentimentChart catch, Graph3D linkColor O(n) → O(1)), expanded yfinance coverage (13→21 tickers: +3 forex, +3 volatility/credit indices, +2 bond ETFs), richer market data (5-day trend context per ticker), agent prompt optimization (~80→~25 tool calls: batch-first, no re-fetching pre-fetched data), FRED series sync fix
- **Phase 14 (Scenario Engine — "Macro Sim"):** Complete — scenario extrapolation agent (4-phase: research → history → generation → mapping, max 27 rounds), "generate first, map second" design (agent reasons freely about real-world impacts, then maps to graph nodes + suggests new nodes/edges), multi-shock simulate, branching scenarios with probability weights, editable shocks, quick triggers from RSS, scenario history, WebSocket progress, ScenarioPanel UI
- **Phase 15 (Scenario Intelligence):** Complete — 10 scenario engine improvements: economic calendar tool (FOMC/CPI/NFP/GDP + FRED API), options positioning tool (IV, put/call ratio, term structure), current date + market snapshot injected into all phases, expanded Mapper prompt (decision criteria, BAD/GOOD mapping examples, directionality notes), cross-branch coherence check, non-linear shock interaction model (stress multiplier + sigmoid compression), convergence detection in sub-agent loop, edge suggestion validation fix, scenario comparison view (frontend), conditional scenario chaining (chain follow-up scenarios from branch outcomes). Topic diversity fix: 12 domain-aligned news queries, LLM picks top 5 with diversity mandate, random auto-selection, recent trigger avoidance.

## Tech Stack

- **Backend:** Python 3.12+, FastAPI, Uvicorn
- **Agent:** Anthropic SDK (Claude, raw tool-use loop — no framework)
- **Graph Engine:** NetworkX + numpy/scipy
- **Database:** PostgreSQL 16 + pgvector + TimescaleDB
- **Cache/PubSub:** Redis
- **Market Data:** yfinance — 21 tickers (equities, commodities, forex, volatility indices, bond ETFs; no API key needed)
- **Macro Data:** FRED API — 16 series (optional, free key from fredaccount.stlouisfed.org; mock data fallback)
- **News Data:** 30 curated RSS feeds (no API key needed) + keyword→node matching engine
- **Social Data:** asyncpraw (Reddit, optional)
- **Frontend:** Next.js 15 + react-force-graph-3d (Three.js/WebGL)
- **State:** Zustand
- **Charts:** Lightweight Charts (TradingView)
- **Deployment:** Docker Compose (local-first, OSS)

## Project Structure

```
causal-sentiment/
  backend/
    app/
      main.py                  # FastAPI entry point + incremental graph seeding + CORS (ports 3000, 3001)
      config.py                # Settings (pydantic-settings, reads ../.env)
      models/
        graph.py               # Node, Edge, NodeType, EdgeDirection
        observations.py        # SentimentObservation, AgentRun, Prediction, Annotation
        scenarios.py           # Scenario, ScenarioShock, ScenarioPrediction, NodeSuggestion (+ parent_scenario_id for chaining)
      agent/
        orchestrator.py        # Three-phase reasoning loop: Plan → Analyze → Validate (max 35 rounds), pre-fetch data package, evidence provenance
        tools.py               # 12 tools: fetch_fred, fetch_market, search_news, search_reddit, fetch_sec, update_sentiment, batch_update_sentiment, get_neighborhood, get_analysis_context, validate_consistency, record_prediction, get_agent_track_record
        prompts.py             # Phase-aware system prompts (planning, analysis, validation, self-calibration)
        schemas.py             # Anthropic tool definitions (11 tools)
        scenario_agent.py      # Scenario extrapolation orchestrator (4-phase: research → history → generation → mapping, max 27 rounds), convergence detection, cross-branch coherence, topic diversity (12 domain queries)
        scenario_prompts.py    # Scenario system + phase prompts (intelligence analyst persona, calibration anchors, expanded mapper with BAD/GOOD examples)
        scenario_schemas.py    # Scenario tool schemas (get_graph_topology, get_economic_calendar, fetch_options_summary, preview_propagation, submit_scenarios + reused tools)
      graph_engine/
        topology.py            # 52 nodes + 117 edges (hardcoded domain knowledge)
        propagation.py         # Weighted BFS with exponential decay + merge_multi_shock_impacts (non-linear: stress multiplier + sigmoid compression)
        weights.py             # Centrality, decay, clamping
        correlations.py        # Dynamic weight recalculation from empirical Pearson correlations
        anomalies.py           # Z-score anomaly detection on node observations (2σ threshold)
        predictions.py         # Prediction resolution — compare agent predictions against actual outcomes
      data_pipeline/
        fred.py                # FRED API client (16 macro series, optional — mock data fallback)
        market.py              # yfinance client (21 tickers: equities, commodities, forex, vol indices, bond ETFs) + fetch_options_summary (IV, put/call ratio, term structure)
        calendar.py            # Economic calendar: FOMC dates, recurring releases (CPI/NFP/GDP/PCE/ISM), optional FRED releases API
        retry.py               # Exponential backoff retry utility (3 attempts)
        reddit.py              # Reddit pipeline (asyncpraw, keyword→node mapping, 3 subreddits)
        scheduler.py           # APScheduler: 9 jobs (FRED 4h, market 1h, Reddit 2h, EDGAR daily 6AM, agent 6h, weights 3AM, regime 2h, decay 2AM, prediction resolution 1h) — disabled by default (SCHEDULER_ENABLED=false)
      api/
        routes_graph.py        # Graph CRUD + snapshot + anomalies + clusters + sentiment history + simulate + annotations + regime narrative
        routes_agent.py        # POST /api/agent/analyze, GET /api/agent/runs, GET /api/agent/predictions, GET /api/agent/predictions/summary
        routes_scenario.py     # POST /api/scenarios, GET /api/scenarios, GET /api/scenarios/{id}, POST /api/scenarios/{id}/apply, POST /api/scenarios/{id}/chain, GET /api/scenarios/quick-triggers
        websocket.py           # WebSocket manager + broadcast
      db/
        connection.py          # async SQLAlchemy + asyncpg
    requirements.txt
    Dockerfile
  frontend/
    src/
      app/page.tsx             # Main dashboard layout
      components/
        Graph3D.tsx            # react-force-graph-3d wrapper + cluster forces + anomaly highlighting + simulation overlay
        NodePanel.tsx          # Node detail: sentiment, what-if simulator, analyst notes, chart, anomaly badge, causal edges, evidence, deep dive
        SimulationPanel.tsx    # What-if impact report: affected nodes, paths, hop count
        ScenarioPanel.tsx      # Scenario engine: trigger input, quick triggers, branching scenario cards, editable shocks, history, branch comparison view, scenario chaining UI
        SentimentChart.tsx     # Lightweight Charts time-series (7d/30d/90d)
        SentimentTimeline.tsx  # Bottom bar: top movers by sentiment
        FilterBar.tsx          # Run analysis button, clustered/free layout toggle, regime narrator, legend
        AgentRunLog.tsx        # Expandable agent run history with tool call details
        PredictionsPanel.tsx   # Prediction tracker: pending/resolved predictions, hit rate, color-coded cards
        TimeSlider.tsx         # Historical playback slider (7d range, 1h steps, play/pause)
      hooks/
        useGraphData.ts        # Zustand store: graph, anomalies, snapshots, clustering, WebSocket sync
        useNodeSelection.ts    # Node selection + deep dive logic
      lib/
        graphTransforms.ts     # API → force-graph transforms, color mapping, edge direction colors
        websocket.ts           # Auto-reconnecting WebSocket client
      types/graph.ts           # TypeScript interfaces: GraphNode, GraphEdge, ForceGraphNode, ForceGraphLink, AgentRun, AnomalyInfo
    package.json
  docker-compose.yml           # PostgreSQL + TimescaleDB + Redis
  .env.example
```

## Key Commands

```bash
# First-time setup (installs everything)
./setup.sh

# Start all services (DB, backend, frontend)
./start.sh

# Stop everything
./stop.sh

# Tests
cd backend && source .venv/bin/activate && pytest

# Full stack via Docker
docker-compose up --build
```

## Architecture

```
3D Visualization (Next.js + react-force-graph-3d)
          ↕ WebSocket
API Layer (FastAPI)
          ↕
┌─────────┼──────────┬────────────────┐
Agent     Graph      Data Pipeline    Historical
(Claude   Engine     (APScheduler)    Store
tool-use) (NetworkX)                  (TimescaleDB)
```

**Flow:** Data Pipeline fetches from FRED/yfinance/news/Reddit → anomaly check → triggers Agent if 2σ move detected → Agent calls Claude with tools → sentiment written to Graph Engine → propagation runs → WebSocket pushes to 3D visualization.

## Graph Model

- **52 nodes** across 11 categories: macro (8), monetary policy (4), geopolitics (4), rates/credit (6), volatility (5), commodities (6), equities (6), equity fundamentals (3), currencies (4), flows/sentiment (3), global (3)
- **117 directed edges** with causal direction (positive/negative/complex), base weight, dynamic weight, transmission lag
- **Impact propagation:** Weighted BFS with exponential decay (30% per hop), max 4 hops, signals clamped to [-1, 1]
- **Edge effective weight:** `0.6 * base_weight + 0.4 * dynamic_weight`
- **Dynamic weights:** Updated daily from 90-day Pearson correlations between connected node pairs

## Agent Design

### Architecture: Three-Phase Reasoning Loop

The agent runs a structured **Plan → Analyze → Validate** loop (max 35 rounds total):

1. **Planning Phase** — Agent inspects the graph state (anomalies, stale nodes, regime shifts, recent observations) via `get_analysis_context` and decides which nodes to prioritize and why. Outputs a structured analysis plan.
2. **Analysis Phase** — Pre-fetched data (FRED, yfinance, RSS headlines) is already in context. Agent reasons about it, writes sentiment via `batch_update_sentiment` (batch-first, ~25 tool call budget). Must cite RSS headlines from T1/T2/T3 sources in evidence. Agent should NOT re-fetch pre-fetched data.
3. **Validation Phase** — Agent calls `validate_consistency` to check for cross-node contradictions (including unchanged neighbors with non-zero sentiment), then self-critiques and corrects if needed.

### Tools (12 total)
- `fetch_fred_data` — FRED macro series (16 series mapped to nodes, optional)
- `fetch_market_prices` — yfinance prices (21 tickers: equities, forex, vol indices, bond ETFs)
- `search_news` — RSS headlines (30 curated feeds, no API key needed)
- `search_reddit` — Reddit social sentiment (r/wallstreetbets, r/economics, r/stocks)
- `fetch_sec_filings` — SEC EDGAR financial data
- `update_sentiment_signal` — write sentiment to single node + trigger propagation (confidence decomposition: data_freshness, source_agreement, signal_strength)
- `batch_update_sentiment` — write sentiment to multiple nodes in one call (single graph lock + atomic commit)
- `get_graph_neighborhood` — inspect node + neighbors
- `get_analysis_context` — graph-wide state summary: anomalies, stale nodes, regime, recent changes, data freshness
- `validate_consistency` — check cross-node contradictions after updates (e.g., conflicting directional signals on causally linked nodes)
- `record_prediction` — store a falsifiable prediction for future backtesting
- `get_agent_track_record` — query prediction hit rate, accuracy stats, and recent outcomes for self-calibration

### Trigger Patterns
- **Scheduled** — every 6 hours on nodes with fresh data
- **Anomaly-driven** — auto-triggered when 2σ move detected after data fetch
- **User-initiated** — "Run Full Analysis" button or per-node "Deep Dive"

## Scenario Engine ("Macro Sim")

A scenario extrapolation agent that takes a real-world event or hypothetical trigger and generates branching probability-weighted scenarios with multi-node shocks.

### "Generate First, Map Second" Design
The agent reasons freely about real-world consequences first (unconstrained by graph structure), THEN is shown the graph topology and asked to map impacts to nodes. If no node fits, it suggests new nodes/edges. This avoids anchoring bias and enables graph evolution.

### 4-Phase Multi-Agent Loop (max 27 rounds)
Each phase is a separate sub-agent with fresh context and focused tools:

| Phase | Agent | Rounds | Tools | Purpose |
|-------|-------|--------|-------|---------|
| 1 | Researcher | 4 | search_news, fetch_market_prices, get_economic_calendar | Structural situational awareness: facts, actors, market reaction, upcoming catalysts |
| 2 | Historian | 5 | search_news, fetch_market_prices, fetch_historical_prices | Calibration: 2-3 structural parallels grounded in real price data |
| 3 | Strategist | 12 | search_news, fetch_market_prices, get_economic_calendar, fetch_options_summary | Scenario generation: 2-3 branches with free-form impacts, causal chains, probability weights |
| 4 | Mapper | 6 | validate_consistency, get_graph_topology, preview_propagation | Map free-form impacts to nodes, calibrate shock values, verify cascades |

### Context Injection
- **Current date + market snapshot** (SPY, VIX, Oil, DXY, 10Y) injected into Phases 1-3 so the agent knows what year it is and current market levels
- **Domain-specific supplements** auto-detected from trigger keywords (7 domains: geopolitical, monetary, trade, technology, climate, pandemic, corporate)
- **Vulnerability context** — extreme-sentiment nodes and high-weight edges injected as "fragility points"
- **Track record** — resolved scenario predictions injected into Phase 3 for self-calibration

### Isolation Principle
Reuses existing **code** (search_news, fetch_market_prices, validate_consistency, LLM client, WebSocket) but NEVER reads previous agent **outputs** (stored sentiments, past runs, predictions). Reads only graph topology (nodes + edges = domain knowledge).

### Non-Linear Multi-Shock Simulate
When user applies a branch, `merge_multi_shock_impacts()` runs propagate_signal for each shock independently, then applies:
- **Stress multiplier** — when 4+ shocks fire simultaneously: `1.0 + 0.15 * (n_shocks - 3)`
- **Sigmoid compression** — diminishing returns near ±1.0 extremes
- Read-only (no DB writes to graph state)

### Cross-Branch Coherence Check
After Phase 3, Jaccard similarity is computed across branch impact sets. Branches with >0.8 overlap are flagged as too similar (logged as warnings).

### Convergence Detection
Sub-agent loop tracks recent tool calls. If the same tool is called with >70% similar inputs (Jaccard on word sets), a nudge is injected: "Synthesize what you have and proceed to submission."

### Scenario Chaining
`POST /api/scenarios/{id}/chain` creates a follow-up scenario from a parent branch outcome. The parent's narrative, shocks, and structural outcome are injected as "assumed context" into the child's Phase 1. Enables multi-step strategic planning: "If Branch A materializes, what happens next?"

### Scenario Comparison
Frontend Compare mode lets users select 2 branches side-by-side. Shows node-by-node shock comparison with color coding (green=both positive, red=both negative, blue=opposite, gray=unique) and "Common Risk Nodes" summary.

### Topic Diversity (Quick Triggers)
12 domain-aligned news queries (geopolitics, monetary, trade, tech, energy, financial stability, health, labor, sovereign, housing, EM, food) replace the old single query. LLM picks top 5 with explicit diversity mandate. Recent scenario triggers injected as avoidance list. Auto-pick uses `random.choice(triggers[:5])`.

## Scheduler

APScheduler runs 9 background jobs (all disabled by default — set `SCHEDULER_ENABLED=true` in `.env`):
- **FRED fetch** — every 4 hours (+ anomaly check → auto-trigger agent if 2σ)
- **Market fetch** (yfinance) — every 1 hour (+ anomaly check → auto-trigger agent if 2σ)
- **Reddit fetch** — every 2 hours (stores posts matched to nodes by keyword)
- **Agent analysis** — every 6 hours (only nodes with fresh data since last run)
- **Weight recalculation** — daily at 3AM UTC (Pearson correlation → dynamic_weight on edges)
- **Sentiment decay** — daily at 2AM UTC (24h half-life exponential decay)
- **Prediction resolution** — every 1 hour (resolves expired predictions, no LLM cost)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check with node/edge counts |
| GET | `/api/graph/full` | Full graph for 3D visualization |
| GET | `/api/graph/node/{id}` | Single node details |
| GET | `/api/graph/sentiment/history/{id}?days=30` | Sentiment time-series |
| GET | `/api/graph/snapshot?timestamp=...` | Historical graph state at a point in time |
| GET | `/api/graph/anomalies?lookback_days=30&z_threshold=2` | Anomalous nodes (z-score) |
| GET | `/api/graph/clusters` | Node cluster assignments by type |
| POST | `/api/agent/analyze` | Trigger agent analysis (`{"node_ids": [...]}` or all) |
| GET | `/api/agent/runs?limit=20` | Recent agent runs with tool call logs |
| GET | `/api/agent/predictions?limit=20&status=pending` | List predictions (pending/resolved) |
| GET | `/api/agent/predictions/summary` | Prediction stats: hit rate, by-direction breakdown |
| POST | `/api/graph/simulate` | What-if shock propagation (read-only, no DB write) |
| GET | `/api/annotations?node_id=...` | List analyst annotations for a node |
| POST | `/api/annotations` | Create analyst annotation |
| PUT | `/api/annotations/{id}` | Update annotation text/pin |
| DELETE | `/api/annotations/{id}` | Delete annotation |
| POST | `/api/graph/regime/narrative` | LLM-generated regime narrative |
| POST | `/api/scenarios` | Trigger scenario extrapolation (runs in background) |
| GET | `/api/scenarios?limit=20` | List recent scenarios |
| GET | `/api/scenarios/{id}` | Get full scenario with branches, shocks, suggestions |
| POST | `/api/scenarios/{id}/apply` | Apply a branch (multi-shock simulate, read-only) |
| POST | `/api/scenarios/{id}/chain` | Chain a follow-up scenario from a parent branch outcome |
| GET | `/api/scenarios/quick-triggers` | Get 5 scenario-worthy events from current news (12 domain queries) |
| WS | `/ws` | Real-time graph updates |

## Frontend Features

- **3D Force Graph** — WebGL visualization with sentiment-colored nodes, directional edge particles
- **What-if shock simulator** — drag slider to hypothetical sentiment, click Simulate: affected nodes glow, unaffected dim, impact particles flow along causal paths. Impact report shows all affected nodes with magnitude and path.
- **Analyst annotations** — persistent per-node notes. Pin important notes, delete stale ones. Survives page refreshes and restarts.
- **Regime narrator** — click the regime badge to expand, click "Generate Narrative" for LLM-generated macro prose. Top driver chips fly camera to that node.
- **Node detail panel** — sentiment score, confidence, what-if slider, analyst notes, anomaly alert, causal edges with weight breakdown, sentiment chart, evidence, deep dive button
- **Anomaly highlighting** — anomalous nodes glow yellow and appear 1.5x larger
- **Clustered layout** — toggle to group nodes spatially by type (macro, equities, etc.)
- **Sentiment chart** — Lightweight Charts line chart with 7d/30d/90d range buttons
- **Time slider** — historical playback over 7 days with 1-hour steps and auto-play
- **Agent run log** — expandable cards showing status, duration, tool calls with outputs, analyzed nodes
- **Predictions panel** — color-coded prediction tracker (green=hit, red=miss, yellow=pending) with hit rate summary and countdown timers
- **Scenario engine** — type a trigger event or click a quick trigger from current news (12 domain queries for diversity), see 2-3 branching scenarios with probability weights, causal chains, and mapped shocks. Edit shock values before applying. Compare mode: select 2 branches side-by-side with color-coded node impacts and common risk nodes. Chain mode: generate follow-up scenarios from branch outcomes. Suggested new nodes/edges shown when graph has gaps. Export as JSON.
- **Real-time updates** — WebSocket pushes graph changes after analysis completes

## Environment

Users must provide their own API keys in `.env`:
- `ANTHROPIC_API_KEY` — required for agent analysis (or `OPENAI_API_KEY`)
- `SCHEDULER_ENABLED` — `false` by default; set `true` to enable background jobs (burns API credits)
- `FRED_API_KEY` — optional (free key from fredaccount.stlouisfed.org; mock data fallback without it)
- `NEWSAPI_KEY` — optional (RSS feeds are primary news source, no key needed)
- `REDDIT_CLIENT_ID` — optional (Reddit social sentiment, free at reddit.com/prefs/apps)
- `REDDIT_CLIENT_SECRET` — optional (Reddit social sentiment)

## Conventions

- Backend uses async Python throughout (asyncpg, httpx, yfinance via to_thread)
- All data models: Pydantic v2 in `backend/app/models/`
- Config reads `.env` from both `backend/` and project root (`../.env`)
- All timestamps in UTC; DB columns are `TIMESTAMP WITHOUT TIME ZONE` — always use `datetime.utcnow()` not `datetime.now(timezone.utc)` to avoid offset-naive/aware mismatch
- Sentiment scores always in [-1.0, +1.0] range
- Confidence scores in [0.0, 1.0]
- `SentimentObservation.raw_data` (JSONB) stores original FRED/market/Reddit data
- CORS allows both `localhost:3000` and `localhost:3001` (Next.js may pick either port)
- Scheduler jobs create their own `async_session()` — they run outside FastAPI request lifecycle
- **Graph lock:** All in-memory graph mutations must use `async with app_state.graph_lock:` to prevent race conditions between concurrent agent runs, scheduler jobs, and API requests
- **Error boundary:** Frontend is wrapped in `ErrorBoundary` component — component crashes show recovery UI instead of white screen
- **WebSocket heartbeat:** Client pings every 30s, server responds with pong. Connection considered dead after 10s without response.

## Roadmap

### Completed

- **Phase 6 (Hardening):** Validation threshold fix, edge muting, retry logic, magnitude scoring, regime refresh
- **Phase 7 (What-If Simulator):** Shock propagation simulator with cascade visualization + impact report panel
- **Phase 8 (Second Brain):** Analyst annotations (persistent per-node notes with pin), regime narrator (LLM-generated macro narrative)
- **Phase 9 (Hardening II):** Graph mutation lock (asyncio.Lock), session rollback on agent error, background task crash recovery, agent timeout fallback (15min), WebSocket heartbeat, error boundary, annotation CRUD error handling, AbortController on fetches, graphData useMemo, timestamp standardization
- **Phase 10 (Intelligence Pipeline):** RSS news pipeline (27→30 curated feeds, no API key needed), enhanced keyword→node matching with word boundaries/exclusions/confidence scoring, source reliability tiers in agent prompts, morning brief (daily intelligence summary with LLM narrative), news trending detection (auto-trigger agent on 3+ source convergence), automation toggles UI (runtime scheduler control)
- **Phase 11 (Agent Intelligence):** Pre-fetch data package (FRED + yfinance + RSS injected into agent prompt before it starts), batch sentiment update tool (84→33 tool calls), filled all 10 empty nodes with data sources (FRED: UMCSENT, CES0500000003 + 40 keyword rules + 3 RSS feeds), evidence panel provenance (real/mock/inferred per source per node), increased round budget (25→35), camera reset on background click
- **Phase 12 (Hardening III):** 10 bug fixes (missing Prediction import, FRED series mismatch, batch lock race condition, WebSocket broadcast concurrency, agent timeout, prediction source filter, validate_consistency neighbor coverage), RSS evidence pipeline (agent now cites Bloomberg/Reuters/CNBC in evidence text), evidence accumulation (20 entries per node instead of overwrite), tool call outputs stored in agent runs for audit/export, data_sources provenance fixed (FRED_SERIES_MAP import was missing — pre-fetch silently failed every run), LLM token limit increased (4096→8192)
- **Phase 13 (Hardening IV + Data Pipeline):** 16 bug fixes (LLM API error handling with retry/timeout, graph state rollback on agent error, batch propagation cascade fix, concurrent scheduler agent semaphore, accept_suggestion graph lock, missing run_analysis import, broadcast task tracking, annotation error handling, WebSocket effect stabilization, SentimentChart dynamic import catch, Graph3D linkColor performance O(n)→O(1) via nodeMap), yfinance expansion (13→21 tickers: EURUSD=X, USDJPY=X, USDCNY=X, ^MOVE, ^SKEW, ^VIX, HYG, LQD), richer market data (5-day trend/range per ticker), agent prompt optimization (~80→~25 tool calls: batch-first mandate, removed redundant fetch instructions), FRED series sync (MANEMP added to scheduler)
- **Phase 14 (Scenario Engine — "Macro Sim"):** Scenario extrapolation agent (4-phase multi-agent: research → history → generation → mapping), "generate first, map second" design, multi-shock simulate, branching scenarios, editable shocks, quick triggers from RSS, scenario history, WebSocket progress, ScenarioPanel UI
- **Phase 15 (Scenario Intelligence):** 10 improvements (economic calendar tool, options positioning tool, date/market injection, expanded Mapper prompt, cross-branch coherence, non-linear shock model, convergence detection, edge suggestion fix, comparison view, scenario chaining) + topic diversity fix (12 domain queries, diversity mandate, recent trigger avoidance)

### Next Up

1. **Edge discovery** — agent suggests new causal links from correlation anomalies (EdgeSuggestion model + TopologySuggestions.tsx already exist and are wired)
2. **Seasonal anomaly adjustment** — CPI, unemployment have seasonal patterns; current 2σ detector spams false positives
3. **Frontend polish** — node shapes actually rendered, per-panel error boundaries
4. **Integration tests** — API endpoints, agent reasoning, WebSocket

## Backlog (Deprioritized)

- **Multi-agent architecture:** Adds complexity without solving core value problem — nail single-agent first
- **Authentication/multi-tenant:** Premature — nail single-user experience first
- **More nodes:** 52 is already a lot to reason about; adding more increases noise
