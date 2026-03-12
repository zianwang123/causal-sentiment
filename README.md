# Causal Sentiment Engine

A causal factor graph + agentic sentiment engine for quant finance, inspired by Bridgewater's systematic macro approach. The system models the financial world as an interconnected graph where nodes are financial products and macro factors, and edges represent causal relationships. An AI agent autonomously fetches data, performs sentiment analysis, and propagates impact signals through this network — visualized as an interactive 3D graph.

> **Disclaimer:** This project was built for fun to realize an idea in my head. It was built with the help of AI (Claude). The sentiment analysis results are experimental, may contain errors, and should NOT be used for actual trading or investment decisions. Use at your own risk.

![3D Graph Visualization](https://img.shields.io/badge/3D-Interactive_Graph-blue) ![Claude + GPT](https://img.shields.io/badge/LLM-Claude_%7C_GPT-orange) ![Docker](https://img.shields.io/badge/deploy-Docker_Compose-2496ED)

## How It Works

```
  3D Visualization (Next.js + react-force-graph-3d)
            ↕ WebSocket (real-time updates)
  API Layer (FastAPI)
            ↕
  ┌─────────┼──────────┬────────────────┐
  Agent     Graph      Data Pipeline    Historical
  (Claude   Engine     (APScheduler)    Store
  or GPT    (NetworkX)                  (TimescaleDB)
  tool-use)
```

**Flow:** Data pipeline fetches from FRED/news/market/Reddit/SEC EDGAR → triggers agent → agent calls LLM with 7 tools → sentiment written to graph → propagation runs through causal edges → WebSocket pushes to 3D visualization.

## Features

- **52-node causal factor graph** covering macro, rates, equities, commodities, currencies, volatility, and geopolitics
- **117 causal edges** with expert-defined + dynamically-adjusted weights
- **Agentic analysis** — Claude or GPT autonomously fetches data and updates sentiment using a tool-use loop
- **3D interactive visualization** — nodes colored by sentiment (red/green), sized by centrality, with directional particles showing causal flow
- **Market regime detection** — Risk-On / Risk-Off / Transitioning classification that modifies signal propagation
- **Signal propagation** — sentiment changes cascade through the causal graph with regime-aware decay
- **Dynamic weight learning** — edge weights adapt from empirical correlations
- **Anomaly detection** — 2-sigma moves auto-trigger targeted analysis
- **Time travel** — replay graph state over the past 7 days
- **Portfolio overlay** — add your positions, see them highlighted on the graph
- **Backtesting** — measure sentiment prediction accuracy vs actual returns (hit rate, correlation, IC)
- **LLM topology learning** — Claude/GPT suggests new causal edges from empirical data
- **Dual LLM support** — switch between Claude and GPT at runtime via the UI
- **Sentiment history charts** — TradingView Lightweight Charts for each node
- **Agent audit log** — full visibility into tool calls, reasoning, and summaries

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, Uvicorn |
| Agent | Anthropic SDK + OpenAI SDK (raw tool-use loop) |
| Graph compute | NetworkX + NumPy/SciPy |
| Database | PostgreSQL 16 + TimescaleDB |
| Cache/PubSub | Redis |
| Frontend | Next.js 15, react-force-graph-3d (Three.js/WebGL) |
| State management | Zustand |
| Charts | TradingView Lightweight Charts |
| Styling | Tailwind CSS |

### Data Sources

- **FRED API** — interest rates, CPI, GDP, yield curves, credit spreads
- **yfinance** — equities, ETFs, futures, forex
- **NewsAPI** — headlines and articles
- **Reddit** (asyncpraw) — r/wallstreetbets, r/economics, r/stocks
- **SEC EDGAR** — earnings and financial data for major companies

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

2. Create your `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Add your API keys to `.env`:
   ```env
   # At least one LLM key is required
   ANTHROPIC_API_KEY=sk-ant-...
   OPENAI_API_KEY=sk-proj-...

   # Choose default provider: "anthropic" or "openai"
   LLM_PROVIDER=anthropic

   # Optional — data sources (mock data used if missing)
   FRED_API_KEY=
   NEWSAPI_KEY=
   ```

4. Start everything:
   ```bash
   docker compose up --build
   ```

5. Open **http://localhost:3000**

### Usage

- **Run Full Analysis** — triggers the agent to analyze all 52 nodes
- **Click a node** — opens the detail panel with sentiment, confidence, evidence, charts, and backtest stats
- **Deep Dive** — focused analysis on a single node
- **Toggle Claude/GPT** — switch LLM provider in the top-left panel
- **Time Travel** — drag the slider to replay historical graph state
- **Clustered Layout** — group nodes by type
- **Portfolio** — add positions (bottom-right) to highlight relevant nodes
- **Evolve Graph** — let the LLM suggest new causal edges (bottom-left)
- **Agent Log** — inspect past analysis runs and tool calls (bottom-left)
- **?** button — opens the user guide

## Graph Data Model

### Node Types

| Category | Example Nodes |
|----------|--------------|
| Macro | fed_funds_rate, us_cpi_yoy, us_gdp_growth, unemployment_rate |
| Monetary Policy | fed_balance_sheet, rate_expectations |
| Geopolitics | geopolitical_risk_index, trade_policy_tariffs |
| Rates & Credit | us_2y_yield, us_10y_yield, ig_credit_spread, hy_credit_spread |
| Volatility | vix, move_index, put_call_ratio |
| Commodities | wti_crude, gold, copper |
| Equities | sp500, nasdaq, tech_sector, energy_sector |
| Currencies | dxy_index, eurusd, usdjpy |
| Flows & Sentiment | retail_sentiment, institutional_positioning |
| Global | china_pmi, eu_hicp, japan_boj_policy |

### Propagation Algorithm

Weighted BFS with exponential decay:
- Signal propagates outward from the source node
- At each hop: `propagated = parent_signal × edge_weight × direction_sign × (1 - decay)`
- Regime-aware: in Risk-Off, bearish signals propagate faster; in Risk-On, bullish signals propagate faster
- Max depth: 4 hops, multiple paths are summed (interference)

## Project Structure

```
causal-sentiment/
├── backend/
│   └── app/
│       ├── main.py                    # FastAPI app + lifespan
│       ├── config.py                  # Settings (env vars)
│       ├── agent/
│       │   ├── orchestrator.py        # LLM tool-use loop
│       │   ├── llm_client.py          # Unified Claude/GPT client
│       │   ├── tools.py               # Tool implementations
│       │   ├── schemas.py             # Tool definitions
│       │   └── prompts.py             # System + analysis prompts
│       ├── graph_engine/
│       │   ├── topology.py            # 52 nodes + 117 edges
│       │   ├── propagation.py         # Signal propagation (BFS)
│       │   ├── weights.py             # Centrality + decay
│       │   ├── correlations.py        # Dynamic weight learning
│       │   ├── anomalies.py           # Z-score anomaly detection
│       │   ├── regimes.py             # Risk-on/off classification
│       │   ├── backtest.py            # Predictive accuracy metrics
│       │   └── topology_learning.py   # LLM-suggested edges
│       ├── data_pipeline/
│       │   ├── fred.py                # FRED API client
│       │   ├── market.py              # yfinance market data
│       │   ├── news.py                # NewsAPI client
│       │   ├── reddit.py              # Reddit (asyncpraw)
│       │   ├── edgar.py               # SEC EDGAR client
│       │   └── scheduler.py           # APScheduler jobs
│       ├── api/
│       │   ├── routes_graph.py        # Graph + backtest + topology endpoints
│       │   ├── routes_agent.py        # Agent trigger + LLM config
│       │   ├── routes_portfolio.py    # Portfolio CRUD
│       │   └── websocket.py           # Real-time push
│       ├── db/
│       │   └── connection.py          # AsyncSession factory
│       └── models/
│           ├── graph.py               # Node + Edge tables
│           └── observations.py        # Sentiment, regime, portfolio, etc.
├── frontend/
│   └── src/
│       ├── app/page.tsx               # Main layout
│       ├── components/
│       │   ├── Graph3D.tsx            # 3D force-directed graph
│       │   ├── NodePanel.tsx          # Node detail sidebar
│       │   ├── FilterBar.tsx          # Controls + regime badge + LLM toggle
│       │   ├── SentimentChart.tsx     # TradingView line chart
│       │   ├── BacktestChart.tsx      # Scatter plot (sentiment vs return)
│       │   ├── SentimentTimeline.tsx  # Top signals bar
│       │   ├── TimeSlider.tsx         # Historical playback
│       │   ├── AgentRunLog.tsx        # Agent audit log
│       │   ├── PortfolioPanel.tsx     # Portfolio overlay
│       │   ├── TopologySuggestions.tsx # LLM edge suggestions
│       │   └── UserGuide.tsx          # Help modal
│       ├── hooks/
│       │   ├── useGraphData.ts        # Zustand store + WebSocket
│       │   └── useNodeSelection.ts    # Node click handling
│       ├── lib/
│       │   └── graphTransforms.ts     # Color mapping + data transforms
│       └── types/
│           └── graph.ts               # TypeScript interfaces
└── docker-compose.yml
```

## License

MIT

## Acknowledgments

- Built with the help of [Claude](https://claude.ai) (Anthropic)
- Inspired by Bridgewater Associates' systematic macro research approach
- 3D graph visualization powered by [react-force-graph-3d](https://github.com/vasturiano/react-force-graph)
