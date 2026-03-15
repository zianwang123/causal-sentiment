# Causal Sentiment Engine

**A second brain for macro analysts.** See the financial world as an interconnected causal graph. Ask "what if oil crashes?" and watch the shock cascade through energy, inflation, rates, and equities in real time. Pin your own reasoning to nodes. Let an AI agent do the data-gathering grunt work. The graph remembers what you think, not just what the data says.

> **Disclaimer:** This is a prototype built for fun to bring an idea to life. It was built with the help of AI. The sentiment analysis results are experimental, may contain errors and bugs, and should **NOT** be used for actual trading or investment decisions. Use at your own risk.

> **This project is a work in progress!** New ideas, feedback, and contributors are very welcome. If you have suggestions for new features, better data sources, improved propagation models, or anything else — feel free to open an issue or submit a PR. Let's build this together.

**[Technical Manual](docs/TECHNICAL_MANUAL.md)** — deep dive into every algorithm, formula, and design decision (propagation, regime detection, agent architecture, edge weights, and more).

![3D Graph Visualization](https://img.shields.io/badge/3D-Interactive_Graph-blue) ![Claude + GPT](https://img.shields.io/badge/LLM-Claude_%7C_GPT-orange) ![Docker](https://img.shields.io/badge/deploy-Docker_Compose-2496ED) ![CI](https://github.com/yourusername/causal-sentiment/actions/workflows/ci.yml/badge.svg)

---

## Why This Exists

Traditional sentiment analysis tools treat assets in isolation. But financial markets are deeply interconnected: a Fed rate decision affects Treasury yields, which affects credit spreads, which affects corporate bonds, which affects equity valuations. These cascading causal relationships are what macro investors model systematically.

This project captures that interconnectedness in a **directed causal graph** — 52 nodes, 117 edges — and makes it tangible through 3D visualization. Instead of reading a sentiment score for the S&P 500 in a vacuum, you can see how a change in CPI expectations propagates through monetary policy, into interest rates, through credit markets, and ultimately into equity indices.

Most macro analysts hold this causal model in their heads, but it's implicit, fragile, and hard to stress-test. This project makes it **explicit, visual, and machine-augmented**.

### Shock propagation as a thinking tool

When you shock a node (say, oil sentiment drops to -0.8), the impact **propagates** through the causal network:

- **Direct hits** — energy stocks take an immediate hit (1 hop, high weight)
- **Indirect effects** — inflation expectations shift → rate expectations → equities (3 hops, decayed)
- **Inverse beneficiaries** — airlines and consumers gain from lower energy costs (negative causal edge)
- **Uncorrelated nodes** — geopolitical risk is causally distant, impact decays to near-zero

This is exactly how a macro strategist thinks about positioning. The graph makes that reasoning visible and testable.

---

## Features

- **52-node causal factor graph** — macro, rates, commodities, equities, currencies, and more, connected by 117 directed causal edges with expert-defined + dynamically-adapted weights
- **3D interactive visualization** — WebGL-powered, sentiment-colored, with directional particles showing causal flow
- **What-if simulator** — shock any node, watch the cascade, see the full impact report
- **AI agent** — Claude or GPT fetches real data (FRED, yfinance, news, Reddit, SEC) through a three-phase reasoning loop (Plan → Analyze → Validate) with self-calibration
- **Analyst annotations** — pin timestamped notes to any node, persisted across sessions
- **Regime narrator** — LLM-generated macro narrative from bellwether indicators
- **Prediction tracking** — agent records falsifiable predictions, system auto-resolves and tracks hit rate
- **Time travel** — replay graph state over the past 7 days
- **Portfolio overlay** — add your positions, see them highlighted on the graph
- **Edge discovery** — AI suggests new causal edges from correlation patterns

For details on algorithms, formulas, and design rationale, see the **[Technical Manual](docs/TECHNICAL_MANUAL.md)**.

---

## Architecture

```
Browser (localhost:3000)
  ├── 3D Force-Directed Graph (Three.js/WebGL)
  ├── Node Detail Panel + What-If Simulator
  ├── Agent Audit Log + Predictions Panel
  └── Analyst Annotations + Regime Narrator
       │
       │ WebSocket (real-time push)
       ▼
FastAPI Backend (localhost:8000)
  ├── AI Agent (Claude/GPT, 3-phase loop, 11 tools)
  ├── Graph Engine (NetworkX, propagation, anomalies, regimes)
  ├── Data Pipeline (APScheduler, 9 jobs, disabled by default)
  └── PostgreSQL + TimescaleDB + Redis

External Data Sources:
  FRED · yfinance · NewsAPI · Reddit · SEC EDGAR
```

For detailed architecture, agent design, and concurrency model, see **[Technical Manual §2, §8, §17](docs/TECHNICAL_MANUAL.md)**.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **AI Agent** | Anthropic SDK + OpenAI SDK (switchable) |
| **Graph Engine** | NetworkX + NumPy/SciPy |
| **Database** | PostgreSQL 16 + TimescaleDB |
| **Cache** | Redis |
| **Frontend** | Next.js 15, React 19 |
| **3D Visualization** | react-force-graph-3d (Three.js/WebGL) |
| **State** | Zustand |
| **Charts** | TradingView Lightweight Charts |
| **Deployment** | Docker Compose |

### Data Sources

| Source | Data | Frequency |
|--------|------|----------|
| **FRED API** | Rates, CPI, GDP, unemployment, credit spreads (14 series) | Every 4h |
| **yfinance** | Equities, ETFs, futures, forex (13 tickers) | Every 1h |
| **NewsAPI** | Headlines and articles | On agent trigger |
| **Reddit** | Social sentiment (r/wallstreetbets, r/economics, r/stocks) | Every 2h |
| **SEC EDGAR** | Earnings, financial filings | Daily |

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

6. Open **http://localhost:3000** — everything runs locally. Click **Run Full Analysis** to trigger the first agent run.

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
| **Simulate a shock** | Click a node → drag the "What-If Shock" slider → click "Simulate" |
| **Add a note** | Click a node → scroll to "Analyst Notes" → type your reasoning → click "Add" |
| **Regime narrative** | Click the regime badge (top-left) → click "Generate Narrative" |
| **Run analysis** | Click "Run Full Analysis" (all 52 nodes) |
| **Deep dive** | Click a node → click "Deep Dive" for focused single-node analysis |
| **Find a node** | Open "Nodes" in the bottom toolbar — search, sort, click to fly |
| **Switch LLM** | Toggle GPT/Claude in the top-left panel |
| **Time travel** | Open "Time Travel" in the bottom toolbar |
| **Portfolio** | Open "Portfolio" in the bottom toolbar to add positions |
| **Topology suggestions** | Open "Evolve Graph" to see AI-suggested new causal edges |

---

## Project Structure

```
causal-sentiment/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── agent/
│   │   │   ├── orchestrator.py
│   │   │   ├── llm_client.py
│   │   │   ├── tools.py
│   │   │   ├── schemas.py
│   │   │   └── prompts.py
│   │   ├── graph_engine/
│   │   │   ├── topology.py
│   │   │   ├── propagation.py
│   │   │   ├── weights.py
│   │   │   ├── correlations.py
│   │   │   ├── anomalies.py
│   │   │   ├── regimes.py
│   │   │   ├── backtest.py
│   │   │   ├── predictions.py
│   │   │   └── topology_learning.py
│   │   ├── data_pipeline/
│   │   │   ├── fred.py
│   │   │   ├── market.py
│   │   │   ├── reddit.py
│   │   │   ├── edgar.py
│   │   │   ├── retry.py
│   │   │   └── scheduler.py
│   │   ├── api/
│   │   │   ├── routes_graph.py
│   │   │   ├── routes_agent.py
│   │   │   ├── routes_portfolio.py
│   │   │   └── websocket.py
│   │   ├── db/
│   │   │   └── connection.py
│   │   └── models/
│   │       ├── graph.py
│   │       └── observations.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── app/page.tsx
│       ├── components/
│       ├── hooks/
│       ├── lib/
│       └── types/
├── docs/
│   └── TECHNICAL_MANUAL.md
├── setup.sh
├── start.sh
├── stop.sh
├── docker-compose.yml
└── .env.example
```

For detailed file descriptions, see **[Technical Manual](docs/TECHNICAL_MANUAL.md)**.

---

## FAQ

**Q: How accurate is the sentiment analysis?**
A: This is experimental. The agent's quality depends on the LLM, data freshness, and graph structure. The built-in prediction tracking measures accuracy over time. Treat it as a research tool, not a trading signal.

**Q: Does this cost money to run?**
A: LLM API calls cost money. A full 52-node analysis typically uses 30-60K tokens. Market data (yfinance) is free. FRED requires a free API key. Background jobs are **disabled by default** to prevent unexpected costs.

**Q: Can I add my own nodes and edges?**
A: Edit `backend/app/graph_engine/topology.py`. The topology learning feature can also suggest new edges from correlation patterns.

**Q: Why not use LangChain / CrewAI / other framework?**
A: Simplicity and transparency. The agent is ~200 lines in `orchestrator.py`. Every tool call is logged and visible in the audit log. No hidden abstractions.

**Q: Can I use only OpenAI / only Anthropic?**
A: Yes. You only need one API key. Set `LLM_PROVIDER` in `.env`. You can switch at runtime via the UI.

**Q: Where can I learn more about how the algorithms work?**
A: The **[Technical Manual](docs/TECHNICAL_MANUAL.md)** covers every algorithm, formula, constant, and design rationale in detail — propagation, regime detection, anomaly detection, dynamic weight learning, agent architecture, and more.

---

## Roadmap

- [x] Three-phase agent reasoning (Plan → Analyze → Validate)
- [x] Self-critique + confidence decomposition
- [x] Prediction tracking with auto-resolution and magnitude scoring
- [x] Agent memory (cross-run context injection)
- [x] What-if shock simulator with cascade visualization
- [x] Analyst annotations + regime narrator
- [x] Dynamic weight learning + edge muting
- [x] Portfolio overlay + backtesting
- [x] LLM topology suggestions
- [x] CI/CD pipeline
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
