# Causal Sentiment Engine

**A second brain for macro analysts.** See the financial world as an interconnected causal graph. Ask "what if oil crashes?" and watch the shock cascade through energy, inflation, rates, and equities in real time. Pin your own reasoning to nodes. Let an AI agent do the data-gathering grunt work. The graph remembers what you think, not just what the data says.

> **Disclaimer:** This is a prototype built for fun to bring an idea to life. It was built with the help of AI. The sentiment analysis results are experimental, may contain errors and bugs, and should **NOT** be used for actual trading or investment decisions. Use at your own risk.

> **This project is a work in progress!** New ideas, feedback, and contributors are very welcome. If you have suggestions for new features, better data sources, improved propagation models, or anything else — feel free to open an issue or submit a PR. Let's build this together.

![3D Graph Visualization](https://img.shields.io/badge/3D-Interactive_Graph-blue) ![Claude + GPT](https://img.shields.io/badge/LLM-Claude_%7C_GPT-orange) ![Docker](https://img.shields.io/badge/deploy-Docker_Compose-2496ED) ![CI](https://github.com/yourusername/causal-sentiment/actions/workflows/ci.yml/badge.svg)

---

## Why This Exists

Traditional sentiment analysis tools treat assets in isolation — analyzing one stock, one headline, one data point at a time. But financial markets are deeply interconnected: a Fed rate decision affects Treasury yields, which affects credit spreads, which affects corporate bonds, which affects equity valuations, and so on. These cascading causal relationships are what macro investors like Bridgewater model systematically.

This project attempts to capture that interconnectedness in a causal graph and make it tangible through 3D visualization. Instead of reading a sentiment score for the S&P 500 in a vacuum, you can see how a change in CPI expectations propagates through monetary policy, into interest rates, through credit markets, and ultimately into equity indices — with the AI agent doing the heavy lifting of data gathering and analysis.

Most macro analysts hold this causal model in their heads, but it's implicit, fragile, and hard to stress-test. This project makes it **explicit, visual, and machine-augmented**.

### The core idea: shock propagation as a thinking tool

The graph isn't just a pretty visualization — it's a reasoning framework. When you shock a node (say, oil sentiment drops to -0.8), the impact doesn't just affect oil. It **propagates** through the causal network:

- **Some nodes get hit hard** — energy stocks take a direct hit (1 hop, high weight)
- **Some nodes feel it indirectly** — inflation expectations shift, which nudges rate expectations, which affects equities (3 hops, decayed)
- **Some nodes actually benefit** — airlines and consumers gain from lower energy costs (negative causal edge = inverse relationship)
- **Some nodes barely notice** — geopolitical risk index is causally distant, impact decays to near-zero

This is exactly how a macro strategist thinks about positioning: "if X happens, what gets hurt, what benefits, and what's uncorrelated?" The graph makes that reasoning visible and testable. You can brainstorm hedges, find second-order effects you hadn't considered, and spot which causal channels are currently hot vs. muted.

### What it does

- **52 nodes** (macro factors, rates, commodities, equities, currencies) connected by **117 directed causal edges** — the graph structure IS the domain knowledge
- **What-if simulator** — drag a node to a hypothetical sentiment and watch the shock cascade through the graph. See which nodes get crushed, which benefit, which are unaffected.
- **AI agent** — Claude or GPT fetches real data (FRED, yfinance, news, Reddit, SEC), analyzes it, and writes sentiment through a three-phase reasoning loop (Plan → Analyze → Validate)
- **Analyst annotations** — pin your own notes to nodes. "I think this CPI reading is transitory because of base effects." The tool remembers your reasoning across sessions.
- **Regime narrator** — not just "risk-off 0.7" but a story: "Shifted risk-off 3 days ago, driven by credit spread widening. Watch for 10Y breaking 4.5%."

Not a trading signal. A reasoning tool for anyone who thinks about macro causation.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Browser (localhost:3000)                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │         3D Force-Directed Graph (Three.js/WebGL)       │  │
│  │    52 nodes · 117 edges · real-time sentiment colors   │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────┐  │
│  │Node Panel│ │Time Slider│ │ Agent Log│ │Node Locator  │  │
│  │Detail +  │ │Historical │ │Tool call │ │Search + Focus│  │
│  │Charts    │ │Playback   │ │Audit     │ │by Category   │  │
│  └──────────┘ └───────────┘ └──────────┘ └──────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │ WebSocket (real-time push)
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (:8000)                     │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │  AI Agent    │  │ Graph Engine  │  │   Data Pipeline     │ │
│  │             │  │              │  │                     │ │
│  │ Claude/GPT  │  │ 52 nodes     │  │ APScheduler (6 jobs)│ │
│  │ 3-phase     │  │ 117 edges    │  │ FRED      (4h)     │ │
│  │ reasoning:  │  │ NetworkX     │  │ yfinance  (1h)     │ │
│  │ Plan →      │  │              │  │ Reddit    (2h)     │ │
│  │ Analyze →   │  │ Propagation  │  │ Agent     (6h)     │ │
│  │ Validate    │  │ (BFS + decay)│  │ Weights   (daily)  │ │
│  │ (25 rounds) │  │              │  │ Decay     (daily)  │ │
│  │             │  │ Anomaly      │  │                     │ │
│  │ 11 tools    │  │ detection    │  │ Anomaly check after │ │
│  │ incl.       │  │ (2σ z-score) │  │ each fetch: 2σ move │ │
│  │ self-       │  │              │  │ → auto-trigger agent│ │
│  │ critique +  │  │ Regime       │  │                     │ │
│  │ predictions │  │ detection    │  └─────────────────────┘ │
│  │             │  │ (risk-on/off)│                          │
│  └──────┬──────┘  │              │                          │
│         │         │ Dynamic      │                          │
│         │         │ weight       │                          │
│         │         │ learning     │                          │
│         ▼         │ (Pearson     │                          │
│  ┌─────────────┐  │ correlation) │                          │
│  │ LLM Client  │  └──────────────┘                          │
│  │ Claude API  │                                            │
│  │ OpenAI API  │  ┌──────────────────────────────────────┐  │
│  │(switchable) │  │         PostgreSQL + TimescaleDB      │  │
│  └─────────────┘  │  sentiment_observations (time-series) │  │
│                   │  agent_runs + tool_call_logs          │  │
│                   │  portfolio_positions                  │  │
│                   │  regime_history                       │  │
│                   └──────────────────────────────────────┘  │
│                   ┌──────────────┐                          │
│                   │    Redis     │                          │
│                   │ Cache/PubSub │                          │
│                   └──────────────┘                          │
└──────────────────────────────────────────────────────────────┘

External Data Sources:
  ┌──────┐  ┌─────────┐  ┌─────────┐  ┌────────┐  ┌──────────┐
  │ FRED │  │yfinance │  │ NewsAPI │  │ Reddit │  │SEC EDGAR│
  │(macro│  │(prices, │  │(headlines│  │(social │  │(earnings,│
  │rates,│  │ETFs,    │  │articles)│  │sentiment│ │filings) │
  │CPI)  │  │futures) │  │         │  │WSB etc)│  │          │
  └──────┘  └─────────┘  └─────────┘  └────────┘  └──────────┘
```

### How the Agent Works

The AI agent uses a **three-phase reasoning loop** — Plan, Analyze, Validate — not a simple prompt-response. Here's the flow:

1. **Trigger** — The agent is triggered by one of three mechanisms:
   - **Scheduled** (every 6 hours) — analyzes nodes that have received new data since the last run
   - **Anomaly-driven** — when a data fetch detects a 2-sigma move (z-score anomaly detection), the agent is auto-triggered to analyze that specific node and its neighborhood
   - **User-initiated** — "Run Full Analysis" button (all 52 nodes) or per-node "Deep Dive"

2. **Phase 1: Planning** (rounds 1-3) — The agent inspects the graph state before fetching any data:
   - Calls `get_analysis_context` to see anomalies, stale nodes, current regime, and priority-ranked nodes
   - Decides which nodes to prioritize and what hypotheses to test

3. **Phase 2: Analysis** (rounds 4-20) — The agent fetches data and updates sentiment using 7 data tools:
   - `fetch_fred_data` — pulls macro data (interest rates, CPI, GDP, unemployment, yield curves)
   - `fetch_market_prices` — pulls ETF/futures/forex prices via yfinance
   - `search_news` — searches recent headlines via NewsAPI
   - `search_reddit` — pulls social sentiment from r/wallstreetbets, r/economics, r/stocks
   - `fetch_sec_filings` — fetches SEC filings and earnings data
   - `get_graph_neighborhood` — inspects connected nodes to understand context
   - `update_sentiment_signal` — writes sentiment with decomposed confidence (data freshness, source agreement, signal strength)

4. **Phase 3: Validation** (rounds 21-25) — The agent self-critiques its own analysis:
   - `validate_consistency` — checks for contradictions (e.g., bullish SPY + bullish VIX)
   - Corrects any contradictions found or documents genuine market dislocations
   - `record_prediction` — stores 2-3 high-conviction falsifiable predictions for backtesting
   - `get_agent_track_record` — reviews past prediction accuracy for self-calibration

5. **Propagation** — After the agent writes a sentiment update, the signal propagates through the causal graph:
   - Weighted BFS outward from the updated node
   - Exponential decay (30% per hop), max 4 hops
   - Edge direction matters (positive/negative/complex causal relationships)
   - Regime-aware: in Risk-Off, bearish signals propagate stronger; in Risk-On, bullish signals propagate stronger
   - Multiple propagation paths are summed (constructive/destructive interference)

6. **WebSocket push** — The updated graph state is broadcast to all connected clients in real-time, with live progress showing the current phase

### Key Design Decisions

- **Dynamic weight adaptation** — Edge weights are dynamically adjusted based on 90-day rolling Pearson correlations between connected node pairs. The system learns from empirical data while maintaining the expert-defined causal structure.
- **Sentiment decay** — Sentiment observations have a 24-hour half-life. Old signals fade naturally, preventing stale data from dominating the graph.

---

## Features

### The Graph
- **52-node causal factor graph** covering 11 categories: macro, monetary policy, geopolitics, rates & credit, volatility, commodities, equities, equity fundamentals, currencies, flows & sentiment, and global
- **117 directed causal edges** with expert-defined base weights + dynamically-adapted weights from empirical correlations
- **3D interactive visualization** — WebGL-powered, sentiment-colored nodes (red = bearish, green = bullish), sized by centrality, with directional particles showing causal flow
- **Signal propagation** — sentiment changes cascade through the graph with exponential decay, regime awareness, and constructive/destructive interference

### What-If Simulator
- **Shock propagation** — drag a slider to set hypothetical sentiment on any node, click Simulate
- **Cascade visualization** — affected nodes glow green/red by impact direction, source node pulses orange, unaffected nodes dim out
- **Impact particles** — affected edges light up orange with 6x particles at 3x speed, showing the transmission path
- **Impact report** — bottom panel showing every affected node: magnitude, hop count, full causal path. Click any node to fly the camera there.

### Second Brain
- **Analyst annotations** — pin timestamped notes to any node ("I think this CPI print is transitory"). Persist in the database across sessions. Pin important notes, delete stale ones.
- **Regime narrator** — click the regime badge, generate an LLM-written macro narrative: "Shifted risk-off 2 days ago, driven by HY spread widening. Watch for 10Y breaking 4.5%." Top driver chips fly camera to the relevant node.

### AI Agent
- **Three-phase reasoning loop** — Plan → Analyze → Validate (25 rounds). Not a single prompt — a structured multi-step process with self-critique.
- **11 tools** — FRED, yfinance, NewsAPI, Reddit, SEC EDGAR, graph inspection, sentiment writing, consistency checks, prediction tracking
- **Self-calibration** — tracks prediction accuracy (direction + magnitude), adjusts confidence based on its own track record
- **Market regime detection** — automatic Risk-On / Risk-Off / Transitioning classification from 8 bellwether indicators

### Dashboard
- **Node detail panel** — sentiment, confidence, what-if slider, analyst notes, anomaly alert, causal edges with weight breakdown, sentiment chart, evidence, deep dive
- **Node locator** — searchable panel listing all 52 nodes grouped by category, click to fly the camera to any node
- **Sentiment history charts** — TradingView Lightweight Charts with 7d/30d/90d range buttons
- **Agent audit log** — expandable cards showing status, duration, tool calls, analyzed nodes
- **Predictions panel** — color-coded prediction tracker (green=hit, red=miss, yellow=pending) with hit rate and magnitude scoring
- **Time travel slider** — replay the graph state over the past 7 days with 1-hour resolution
- **Portfolio overlay** — add your positions, see them highlighted on the graph
- **Anomaly highlighting** — nodes with 2-sigma moves glow yellow and appear 1.5x larger
- **LLM topology suggestions** — AI suggests new causal edges from correlation anomalies

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend** | Python 3.12, FastAPI, Uvicorn | Async-native, fast, great for WebSocket support |
| **AI Agent** | Anthropic SDK + OpenAI SDK | Raw tool-use loop — no framework overhead |
| **Graph Engine** | NetworkX + NumPy/SciPy | Mature graph library, fast numerical compute |
| **Database** | PostgreSQL 16 + TimescaleDB | Time-series optimized storage for sentiment history |
| **Cache/PubSub** | Redis | Fast caching and pub/sub for real-time coordination |
| **Frontend** | Next.js 15, React 19 | Server components, fast dev experience |
| **3D Visualization** | react-force-graph-3d (Three.js/WebGL) | GPU-accelerated force-directed graph rendering |
| **State Management** | Zustand | Lightweight, no boilerplate, perfect for real-time updates |
| **Charts** | TradingView Lightweight Charts | Professional-grade financial time-series charts |
| **Styling** | Tailwind CSS | Rapid UI development |
| **Deployment** | Docker Compose | One-command local deployment (no server needed) |

### Data Sources

| Source | Data | Update Frequency |
|--------|------|-----------------|
| **FRED API** | Interest rates, CPI, GDP, unemployment, yield curves, credit spreads (14 series) | Every 4 hours |
| **yfinance** | Equities, ETFs, futures, forex prices (13 tickers) | Every 1 hour |
| **NewsAPI** | Headlines and articles matching node keywords | On agent trigger |
| **Reddit** (asyncpraw) | Social sentiment from r/wallstreetbets, r/economics, r/stocks | Every 2 hours |
| **SEC EDGAR** | Earnings data, financial filings for major companies | On agent trigger |

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- At least one LLM API key (Anthropic or OpenAI)

### Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/causal-sentiment.git
   cd causal-sentiment
   ```

2. Create your `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Add your API keys to `.env`:
   ```env
   # At least one LLM key is required
   ANTHROPIC_API_KEY=sk-ant-...
   OPENAI_API_KEY=sk-proj-...

   # Choose default provider: "anthropic" or "openai"
   LLM_PROVIDER=openai

   # Scheduler (disabled by default to save API credits)
   SCHEDULER_ENABLED=false

   # Optional data sources (mock data used if missing)
   FRED_API_KEY=
   NEWSAPI_KEY=

   # Optional Reddit integration (free at reddit.com/prefs/apps)
   REDDIT_CLIENT_ID=
   REDDIT_CLIENT_SECRET=
   ```

4. First-time install:
   ```bash
   ./setup.sh
   ```

5. Start everything:
   ```bash
   ./start.sh
   ```

6. Open **http://localhost:3000** — everything runs locally on your machine, no remote server required. Click **Run Full Analysis** to trigger the first agent run.

7. To shut down:
   ```bash
   ./stop.sh
   ```

   Alternatively, run the full stack via Docker:
   ```bash
   docker compose up --build
   ```

### Usage

| Action | How |
|--------|-----|
| **Simulate a shock** | Click a node → drag the "What-If Shock" slider → click "Simulate" → watch the cascade |
| **Add a note** | Click a node → scroll to "Analyst Notes" → type your reasoning → click "Add" |
| **Read regime narrative** | Click the regime badge (top-left, e.g. "TRANSITIONING") → it expands → click "Generate Narrative" (requires API key in `.env`) |
| **Run analysis** | Click "Run Full Analysis" in the top-left panel (all 52 nodes) |
| **Deep dive** | Click a node → click "Deep Dive" for focused single-node analysis |
| **Find a node** | Open "Nodes" in the bottom toolbar — search, sort, click to fly to it |
| **Switch LLM** | Toggle GPT/Claude in the top-left panel |
| **Time travel** | Open "Time Travel" in the bottom toolbar — drag slider to replay past 7 days |
| **Cluster layout** | Toggle "Clustered" in the top-left panel to group nodes by category |
| **Portfolio** | Open "Portfolio" in the bottom toolbar to add positions |
| **Topology suggestions** | Open "Evolve Graph" to see AI-suggested new causal edges |
| **Agent audit** | Open "Agent Log" to inspect past runs and tool calls |
| **Predictions** | Open "Predictions" to see pending/resolved predictions with hit rate |

---

## Graph Data Model

### Node Categories (52 nodes)

| Category | Count | Example Nodes |
|----------|-------|--------------|
| Macro | 8 | fed_funds_rate, us_cpi_yoy, us_gdp_growth, unemployment_rate, consumer_confidence, pce_deflator |
| Monetary Policy | 4 | fed_balance_sheet, rate_expectations, ecb_policy_rate, quantitative_tightening |
| Geopolitics | 4 | geopolitical_risk_index, trade_policy_tariffs, sanctions_risk, election_uncertainty |
| Rates & Credit | 6 | us_2y_yield, us_10y_yield, us_30y_yield, ig_credit_spread, hy_credit_spread, yield_curve_slope |
| Volatility | 5 | vix, move_index, put_call_ratio, skew_index, realized_vol |
| Commodities | 6 | wti_crude, brent_crude, gold, silver, copper, natural_gas |
| Equities | 6 | sp500, nasdaq, russell2000, tech_sector, energy_sector, financials_sector |
| Equity Fundamentals | 3 | earnings_growth, corporate_margins, buyback_activity |
| Currencies | 4 | dxy_index, eurusd, usdjpy, gbpusd |
| Flows & Sentiment | 3 | retail_sentiment, institutional_positioning, fund_flows |
| Global | 3 | china_pmi, eu_hicp, japan_boj_policy |

### Edge Properties

Each of the 117 directed edges has:
- **Direction** — positive (A↑ → B↑), negative (A↑ → B↓), or complex
- **Base weight** — expert-defined strength (0.0 to 1.0)
- **Dynamic weight** — empirically computed from 90-day Pearson correlations
- **Effective weight** — `0.6 × base_weight + 0.4 × dynamic_weight`
- **Transmission lag** — estimated delay for the causal effect

### Signal Propagation

Weighted BFS with exponential decay:
1. Agent updates sentiment on a source node
2. Signal propagates outward along causal edges
3. At each hop: `propagated = parent_signal × edge_weight × direction_sign × (1 - decay_rate)`
4. Decay rate: 30% per hop, max 4 hops
5. Regime-aware: Risk-Off amplifies bearish signals, Risk-On amplifies bullish signals
6. Multiple paths sum together (constructive/destructive interference)
7. All signals clamped to [-1.0, +1.0]

---

## Project Structure

```
causal-sentiment/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app + lifespan + graph seeding
│   │   ├── config.py                  # Settings (pydantic-settings, env vars)
│   │   ├── agent/
│   │   │   ├── orchestrator.py        # Three-phase reasoning loop (Plan → Analyze → Validate, 25 rounds)
│   │   │   ├── llm_client.py          # Unified Claude/GPT client
│   │   │   ├── tools.py               # 11 tool implementations (incl. track record, consistency check, predictions)
│   │   │   ├── schemas.py             # Tool definitions (Anthropic + OpenAI format)
│   │   │   └── prompts.py             # Phase-aware prompts (planning, analysis, validation)
│   │   ├── graph_engine/
│   │   │   ├── topology.py            # 52 nodes + 117 edges (domain knowledge)
│   │   │   ├── propagation.py         # Weighted BFS signal propagation
│   │   │   ├── weights.py             # Centrality + decay calculations
│   │   │   ├── correlations.py        # Dynamic weight learning (Pearson)
│   │   │   ├── anomalies.py           # Z-score anomaly detection
│   │   │   ├── regimes.py             # Market regime classification
│   │   │   ├── backtest.py            # Prediction accuracy metrics
│   │   │   ├── predictions.py        # Prediction resolution (compare predicted vs actual)
│   │   │   └── topology_learning.py   # LLM-suggested edges from correlations
│   │   ├── data_pipeline/
│   │   │   ├── fred.py                # FRED API client (14 macro series)
│   │   │   ├── market.py              # yfinance client (13 tickers)
│   │   │   ├── news.py                # NewsAPI client
│   │   │   ├── reddit.py              # Reddit via asyncpraw (3 subreddits)
│   │   │   ├── edgar.py               # SEC EDGAR client
│   │   │   ├── retry.py              # Exponential backoff retry (3 attempts)
│   │   │   └── scheduler.py           # APScheduler (7 jobs, disabled by default)
│   │   ├── api/
│   │   │   ├── routes_graph.py        # Graph CRUD + simulate + annotations + regime narrative
│   │   │   ├── routes_agent.py        # Agent trigger + LLM config
│   │   │   ├── routes_portfolio.py    # Portfolio CRUD
│   │   │   └── websocket.py           # Real-time push (WebSocket manager)
│   │   ├── db/
│   │   │   └── connection.py          # Async SQLAlchemy + asyncpg
│   │   └── models/
│   │       ├── graph.py               # Node + Edge SQLAlchemy models
│   │       └── observations.py        # Sentiment, regime, portfolio, prediction, annotation models
│   ├── tests/                         # 30 tests (propagation, correlations, anomalies)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── app/page.tsx               # Main dashboard layout
│       ├── components/
│       │   ├── Graph3D.tsx            # 3D force-directed graph (WebGL) + simulation overlay
│       │   ├── NodePanel.tsx          # Node detail + what-if slider + analyst notes
│       │   ├── SimulationPanel.tsx    # What-if impact report
│       │   ├── FilterBar.tsx          # Controls + regime narrator + LLM toggle
│       │   ├── SentimentChart.tsx     # TradingView time-series chart
│       │   ├── BacktestChart.tsx      # Sentiment vs return scatter plot
│       │   ├── SentimentTimeline.tsx  # Top movers bar
│       │   ├── TimeSlider.tsx         # Historical playback (7d, 1h steps)
│       │   ├── AgentRunLog.tsx        # Agent audit log
│       │   ├── PredictionsPanel.tsx   # Prediction tracker (hit/miss/pending)
│       │   ├── NodeLocator.tsx        # Searchable node directory + camera focus
│       │   ├── PortfolioPanel.tsx     # Portfolio overlay
│       │   ├── TopologySuggestions.tsx # LLM edge suggestions
│       │   └── UserGuide.tsx          # Onboarding help modal
│       ├── hooks/
│       │   ├── useGraphData.ts        # Zustand store + WebSocket sync
│       │   └── useNodeSelection.ts    # Node click + deep dive logic
│       ├── lib/
│       │   ├── graphTransforms.ts     # API → force-graph transforms + color mapping
│       │   ├── dateUtils.ts           # UTC timestamp parsing
│       │   ├── websocket.ts           # Auto-reconnecting WebSocket client
│       │   └── config.ts              # API/WS URL config
│       └── types/
│           └── graph.ts               # TypeScript interfaces
├── setup.sh                           # First-time setup (installs everything)
├── start.sh                           # Start all services (DB, backend, frontend)
├── stop.sh                            # Stop everything
├── .github/workflows/ci.yml           # CI: backend tests + frontend typecheck
├── docker-compose.yml                 # PostgreSQL + TimescaleDB + Redis + Backend
└── .env.example                       # Environment variable template
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check with node/edge counts |
| GET | `/api/graph/full` | Full graph state for 3D visualization |
| GET | `/api/graph/node/{id}` | Single node with edges and evidence |
| GET | `/api/graph/sentiment/history/{id}?days=30` | Sentiment time-series for a node |
| GET | `/api/graph/snapshot?timestamp=...` | Historical graph state at any point in time |
| GET | `/api/graph/anomalies?lookback_days=30&z_threshold=2` | Nodes with anomalous z-scores |
| GET | `/api/graph/clusters` | Node cluster assignments by category |
| GET | `/api/graph/regime` | Current market regime (risk-on/off) |
| GET | `/api/graph/backtest/{id}` | Backtest metrics for a node |
| POST | `/api/graph/topology/suggest` | LLM-suggested new causal edges |
| POST | `/api/agent/analyze` | Trigger agent analysis (`{"node_ids": [...]}` or all) |
| GET | `/api/agent/runs?limit=20` | Recent agent runs with tool call logs |
| GET | `/api/agent/predictions?limit=20&status=pending` | List predictions (pending/resolved) |
| GET | `/api/agent/predictions/summary` | Prediction stats: hit rate, by-direction breakdown |
| GET | `/api/agent/llm-config` | Current LLM provider and model |
| POST | `/api/agent/llm-config` | Switch LLM provider |
| POST | `/api/graph/simulate` | What-if shock propagation (read-only) |
| POST | `/api/graph/regime/narrative` | LLM-generated regime narrative |
| GET | `/api/annotations?node_id=...` | List analyst annotations |
| POST | `/api/annotations` | Create annotation |
| PUT | `/api/annotations/{id}` | Update annotation |
| DELETE | `/api/annotations/{id}` | Delete annotation |
| POST | `/api/portfolio/positions` | Add portfolio positions |
| GET | `/api/portfolio/positions` | Get portfolio positions |
| WS | `/ws` | Real-time graph updates (sentiment, progress, regime) |

---

## FAQ

**Q: How accurate is the sentiment analysis?**
A: This is experimental. The agent's analysis quality depends on the underlying LLM, the freshness of data sources, and the causal graph structure. The built-in backtesting feature lets you measure prediction accuracy (hit rate, correlation, information coefficient) for each node. Treat it as a research tool, not a trading signal.

**Q: Does this cost money to run?**
A: The LLM API calls cost money (Anthropic or OpenAI). A full analysis of all 52 nodes typically uses 30-60K tokens (the three-phase loop is more thorough than a single pass). Market data (yfinance) is free. FRED requires a free API key. NewsAPI has a free tier. Reddit API access is free. Background scheduled jobs are **disabled by default** (`SCHEDULER_ENABLED=false`) to prevent unexpected API costs.

**Q: Can I add my own nodes and edges?**
A: The graph topology is currently defined in `backend/app/graph_engine/topology.py`. You can add nodes and edges there. The LLM topology learning feature can also suggest new edges based on empirical correlation patterns.

**Q: Why not use LangChain / CrewAI / other framework?**
A: Simplicity and transparency. The agent is a structured three-phase reasoning loop (~200 lines in `orchestrator.py`). Every tool call is logged with its phase (planning/analysis/validation) and visible in the audit log. No hidden abstractions, no prompt magic.

**Q: Can I use only OpenAI / only Anthropic?**
A: Yes. You only need one API key. Set `LLM_PROVIDER` in `.env` to your preferred provider. You can switch at runtime via the UI.

**Q: How does the graph differ from a correlation matrix?**
A: Correlation is symmetric and undirected — it tells you two things move together but not why. This graph has **directed causal edges** — "rising CPI → higher rate expectations → lower equity valuations" is a chain of cause and effect with direction, sign, and magnitude. The dynamic weight learning uses correlations to *adapt* edge weights, but the causal structure is domain knowledge.

---

## Roadmap

- [x] Three-phase agent reasoning (Plan → Analyze → Validate)
- [x] Agent self-critique (cross-node consistency checking)
- [x] Confidence decomposition (data freshness, source agreement, signal strength)
- [x] Falsifiable prediction tracking (foundation for backtesting feedback loop)
- [x] Prediction resolution — automatic comparison of predicted vs actual outcomes
- [x] Agent track record — self-calibration from past prediction accuracy
- [x] Agent memory — cross-run context (previous analyses + track record injected into prompts)
- [x] Scheduler toggle — all background jobs disabled by default (`SCHEDULER_ENABLED=false`)
- [x] CI/CD pipeline — GitHub Actions (pytest + TypeScript typecheck)
- [x] Validation threshold fix — sign-flip detection with 0.15 magnitude filter
- [x] Edge muting — correlation disagreement mutes edges instead of permanently flipping direction
- [x] Data pipeline retry logic — exponential backoff for FRED and yfinance
- [x] Prediction magnitude scoring — track closeness, not just direction
- [x] Regime context refresh — fresh regime injected at each agent phase transition
- [x] What-if shock simulator — inject hypothetical sentiment, watch cascade propagation with impact report
- [x] Analyst annotations — persistent per-node notes with pin/unpin
- [x] Regime narrator — LLM-generated macro narrative with clickable driver chips
- [ ] Morning brief — daily summary of moves, predictions, regime changes
- [ ] Historical backtesting dashboard with equity curves
- [ ] User-defined custom graphs (bring your own nodes/edges)
- [ ] Alerting (email/Slack when anomalies detected)

---

## Contributing

This is a prototype and a learning project. Contributions of all kinds are welcome:

- **Ideas** — open an issue to discuss new features or improvements
- **Bug reports** — if something breaks, let me know
- **Pull requests** — code contributions are appreciated
- **Data sources** — suggestions for new data integrations
- **Domain expertise** — better causal relationships, node coverage, propagation models

---

## License

MIT

## Acknowledgments

- Built with the help of [Claude](https://claude.ai) (Anthropic)
- Drawing from ideas in Bridgewater Associates' systematic macro research
- 3D graph visualization powered by [react-force-graph-3d](https://github.com/vasturiano/react-force-graph)
- Financial charts by [TradingView Lightweight Charts](https://github.com/nicktom/lightweight-charts)
