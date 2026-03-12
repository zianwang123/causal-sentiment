# Causal Sentiment

Agentic sentiment analysis tool for quant finance investment. Models the financial world as an interconnected **causal factor graph** — nodes are financial products and macro/micro factors, edges are causal relationships. A Claude-powered agent fetches data, analyzes sentiment, and propagates impact through the network, visualized as an interactive 3D graph.

Inspired by Bridgewater's systematic macro approach.

## Status

- **Phase 1 (Foundation):** Complete — graph model, agent, 3D viz, API, WebSocket
- **Phase 2 (Real-time + Autonomy):** Complete — 52 nodes, 117 edges, market data (yfinance), scheduler, sentiment history charts, agent audit log
- **Phase 3 (Intelligence + Polish):** Complete — dynamic weight recalculation, anomaly detection (2σ auto-trigger), time slider, node clustering, Reddit integration
- **Phase 4 (Advanced):** Not started — multi-regime awareness, SEC EDGAR, portfolio overlay, backtesting

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
        observations.py        # SentimentObservation, AgentRun
      agent/
        orchestrator.py        # Claude tool-use loop (max 20 rounds)
        tools.py               # 6 tools: fetch_fred, fetch_market, search_news, search_reddit, update_sentiment, get_neighborhood
        prompts.py             # System prompt + analysis template
        schemas.py             # Anthropic tool definitions
      graph_engine/
        topology.py            # 52 nodes + 117 edges (hardcoded domain knowledge)
        propagation.py         # Weighted BFS with exponential decay
        weights.py             # Centrality, decay, clamping
        correlations.py        # Dynamic weight recalculation from empirical Pearson correlations
        anomalies.py           # Z-score anomaly detection on node observations (2σ threshold)
      data_pipeline/
        fred.py                # FRED API client (13 macro series)
        market.py              # yfinance client (13 tickers mapped to nodes)
        reddit.py              # Reddit pipeline (asyncpraw, keyword→node mapping, 3 subreddits)
        scheduler.py           # APScheduler: 6 jobs (FRED 4h, market 1h, Reddit 2h, agent 6h, weights 3AM, decay 2AM)
      api/
        routes_graph.py        # Graph CRUD + snapshot + anomalies + clusters + sentiment history
        routes_agent.py        # POST /api/agent/analyze, GET /api/agent/runs
        websocket.py           # WebSocket manager + broadcast
      db/
        connection.py          # async SQLAlchemy + asyncpg
    requirements.txt
    Dockerfile
  frontend/
    src/
      app/page.tsx             # Main dashboard layout
      components/
        Graph3D.tsx            # react-force-graph-3d wrapper + cluster forces + anomaly highlighting
        NodePanel.tsx          # Node detail: sentiment, chart, anomaly badge, causal edges (base/dynamic/effective weights), evidence, deep dive
        SentimentChart.tsx     # Lightweight Charts time-series (7d/30d/90d)
        SentimentTimeline.tsx  # Bottom bar: top movers by sentiment
        FilterBar.tsx          # Run analysis button, clustered/free layout toggle, legend
        AgentRunLog.tsx        # Expandable agent run history with tool call details
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
# Start DB + Redis
docker-compose up db redis -d

# Backend (dev)
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Frontend (dev)
cd frontend && npm run dev

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

Single Claude agent with tool-use loop (max 20 rounds). 6 tools:
- `fetch_fred_data` — FRED macro series (14 series mapped to nodes)
- `fetch_market_prices` — yfinance ETF/futures prices (13 tickers)
- `search_news` — NewsAPI headlines
- `search_reddit` — Reddit social sentiment (r/wallstreetbets, r/economics, r/stocks)
- `update_sentiment_signal` — write sentiment + trigger propagation
- `get_graph_neighborhood` — inspect node + neighbors

### Trigger Patterns
- **Scheduled** — every 6 hours on nodes with fresh data
- **Anomaly-driven** — auto-triggered when 2σ move detected after data fetch
- **User-initiated** — "Run Full Analysis" button or per-node "Deep Dive"

## Scheduler

APScheduler runs 6 background jobs:
- **FRED fetch** — every 4 hours (+ anomaly check → auto-trigger agent if 2σ)
- **Market fetch** (yfinance) — every 1 hour (+ anomaly check → auto-trigger agent if 2σ)
- **Reddit fetch** — every 2 hours (stores posts matched to nodes by keyword)
- **Agent analysis** — every 6 hours (only nodes with fresh data since last run)
- **Weight recalculation** — daily at 3AM UTC (Pearson correlation → dynamic_weight on edges)
- **Sentiment decay** — daily at 2AM UTC (24h half-life exponential decay)

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
| WS | `/ws` | Real-time graph updates |

## Frontend Features

- **3D Force Graph** — WebGL visualization with sentiment-colored nodes, directional edge particles
- **Node shapes** — sphere (factors), cube (products), octahedron (policy)
- **Anomaly highlighting** — anomalous nodes glow yellow and appear 1.5x larger
- **Clustered layout** — toggle to group nodes spatially by type (macro, equities, etc.)
- **Node detail panel** — sentiment score, confidence, anomaly alert, causal edges with weight breakdown, sentiment chart, evidence, deep dive button
- **Sentiment chart** — Lightweight Charts line chart with 7d/30d/90d range buttons
- **Time slider** — historical playback over 7 days with 1-hour steps and auto-play
- **Agent run log** — expandable cards showing status, duration, tool calls, analyzed nodes
- **Real-time updates** — WebSocket pushes graph changes after analysis completes

## Environment

Users must provide their own API keys in `.env`:
- `ANTHROPIC_API_KEY` — required for agent analysis
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

## Backlog

- **User guide:** Onboarding overlay explaining sentiment/confidence, colors/shapes, propagation, how to use Deep Dive
- **Raw data in NodePanel:** Surface `SentimentObservation.raw_data` (FRED values, market prices) alongside sentiment scores
