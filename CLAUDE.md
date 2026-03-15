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

## Tech Stack

- **Backend:** Python 3.12+, FastAPI, Uvicorn
- **Agent:** Anthropic SDK (Claude, raw tool-use loop — no framework)
- **Graph Engine:** NetworkX + numpy/scipy
- **Database:** PostgreSQL 16 + pgvector + TimescaleDB
- **Cache/PubSub:** Redis
- **Market Data:** yfinance (no API key needed)
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
      agent/
        orchestrator.py        # Three-phase reasoning loop: Plan → Analyze → Validate (max 25 rounds)
        tools.py               # 11 tools: fetch_fred, fetch_market, search_news, search_reddit, fetch_sec, update_sentiment, get_neighborhood, get_analysis_context, validate_consistency, record_prediction, get_agent_track_record
        prompts.py             # Phase-aware system prompts (planning, analysis, validation, self-calibration)
        schemas.py             # Anthropic tool definitions (11 tools)
      graph_engine/
        topology.py            # 52 nodes + 117 edges (hardcoded domain knowledge)
        propagation.py         # Weighted BFS with exponential decay
        weights.py             # Centrality, decay, clamping
        correlations.py        # Dynamic weight recalculation from empirical Pearson correlations
        anomalies.py           # Z-score anomaly detection on node observations (2σ threshold)
        predictions.py         # Prediction resolution — compare agent predictions against actual outcomes
      data_pipeline/
        fred.py                # FRED API client (14 macro series)
        market.py              # yfinance client (13 tickers mapped to nodes)
        retry.py               # Exponential backoff retry utility (3 attempts)
        reddit.py              # Reddit pipeline (asyncpraw, keyword→node mapping, 3 subreddits)
        scheduler.py           # APScheduler: 7 jobs (FRED 4h, market 1h, Reddit 2h, agent 6h, weights 3AM, decay 2AM, prediction resolution 1h) — disabled by default (SCHEDULER_ENABLED=false)
      api/
        routes_graph.py        # Graph CRUD + snapshot + anomalies + clusters + sentiment history + simulate + annotations + regime narrative
        routes_agent.py        # POST /api/agent/analyze, GET /api/agent/runs, GET /api/agent/predictions, GET /api/agent/predictions/summary
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

The agent runs a structured **Plan → Analyze → Validate** loop (max 25 rounds total):

1. **Planning Phase** — Agent inspects the graph state (anomalies, stale nodes, regime shifts, recent observations) via `get_analysis_context` and decides which nodes to prioritize and why. Outputs a structured analysis plan.
2. **Analysis Phase** — Standard tool-use loop: fetch data (FRED, market, news, Reddit), interpret, write sentiment via `update_sentiment_signal`. Same as before but guided by the plan.
3. **Validation Phase** — Agent calls `validate_consistency` to check for cross-node contradictions (e.g., bullish SPY + bullish VIX), then self-critiques and corrects if needed.

### Tools (11 total)
- `fetch_fred_data` — FRED macro series (14 series mapped to nodes)
- `fetch_market_prices` — yfinance ETF/futures prices (13 tickers)
- `search_news` — NewsAPI headlines
- `search_reddit` — Reddit social sentiment (r/wallstreetbets, r/economics, r/stocks)
- `fetch_sec_filings` — SEC EDGAR financial data
- `update_sentiment_signal` — write sentiment + trigger propagation (confidence decomposition: data_freshness, source_agreement, signal_strength)
- `get_graph_neighborhood` — inspect node + neighbors
- `get_analysis_context` — graph-wide state summary: anomalies, stale nodes, regime, recent changes, data freshness
- `validate_consistency` — check cross-node contradictions after updates (e.g., conflicting directional signals on causally linked nodes)
- `record_prediction` — store a falsifiable prediction for future backtesting
- `get_agent_track_record` — query prediction hit rate, accuracy stats, and recent outcomes for self-calibration

### Trigger Patterns
- **Scheduled** — every 6 hours on nodes with fresh data
- **Anomaly-driven** — auto-triggered when 2σ move detected after data fetch
- **User-initiated** — "Run Full Analysis" button or per-node "Deep Dive"

## Scheduler

APScheduler runs 7 background jobs (all disabled by default — set `SCHEDULER_ENABLED=true` in `.env`):
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
- **Agent run log** — expandable cards showing status, duration, tool calls, analyzed nodes
- **Predictions panel** — color-coded prediction tracker (green=hit, red=miss, yellow=pending) with hit rate summary and countdown timers
- **Real-time updates** — WebSocket pushes graph changes after analysis completes

## Environment

Users must provide their own API keys in `.env`:
- `ANTHROPIC_API_KEY` — required for agent analysis (or `OPENAI_API_KEY`)
- `SCHEDULER_ENABLED` — `false` by default; set `true` to enable background jobs (burns API credits)
- `FRED_API_KEY` — optional (mock data fallback)
- `NEWSAPI_KEY` — optional (mock data fallback)
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

### Next Up

1. **Morning brief** — scheduled daily summary: nodes that moved >1σ overnight, predictions resolved, regime changes, top risk propagation paths
2. **Edge discovery** — agent suggests new causal links from correlation anomalies (EdgeSuggestion model + TopologySuggestions.tsx already exist and are wired)
3. **Seasonal anomaly adjustment** — CPI, unemployment have seasonal patterns; current 2σ detector spams false positives
4. **Better Reddit keyword matching** — NLP entity extraction instead of naive substring ("war" currently matches "software", "warrant")
5. **Frontend polish** — node shapes actually rendered, per-panel error boundaries
6. **Integration tests** — API endpoints, agent reasoning, WebSocket

## Backlog (Deprioritized)

- **Multi-agent architecture:** Adds complexity without solving core value problem — nail single-agent first
- **Authentication/multi-tenant:** Premature — nail single-user experience first
- **More data sources:** Better analysis of existing data matters more than more data
- **More nodes:** 52 is already a lot to reason about; adding more increases noise
