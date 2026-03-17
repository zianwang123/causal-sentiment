# Causal Sentiment Engine

**A second brain for macro analysis — built with AI doing most of the heavy lifting.**

Financial markets are deeply interconnected. A Fed rate decision ripples through Treasury yields, credit spreads, corporate bonds, and equity valuations. Most analysts hold this causal map in their heads — implicit, fragile, and impossible to stress-test. What if we made it **explicit, visual, and interactive**?

Causal Sentiment Engine is a **3D interactive causal graph** with 52 macro nodes and 117 directed edges, powered by an AI agent that fetches real-time data, analyzes sentiment, and propagates impact through the network. Simulate "what if" shocks — drag oil sentiment to -0.8 and watch the cascade through energy, inflation, rates, and equities. Pin your own reasoning to nodes. The tool remembers what you think, not just what the data says.

This entire full-stack application — Python backend, Next.js frontend, 3D WebGL visualization, PostgreSQL with TimescaleDB, WebSocket real-time sync, a multi-phase AI agent with 12 tools — was built with the help of [Claude Code](https://claude.ai/claude-code). The velocity of what's possible with AI-assisted development is staggering.

Is it perfect? Not even close. The agent's reasoning could be sharper. The clustering and sentiment propagation models are simplistic. There's a whole world of scenario analysis and market stress testing that could be layered on. This is a prototype — a proof of concept showing how AI + good visualization can expand how we think about macro causation.

> **Disclaimer:** This is a prototype built for fun to bring an idea to life. The sentiment analysis results are experimental, may contain errors and bugs, and should **NOT** be used for actual trading or investment decisions. Use at your own risk.

> **This project is a work in progress!** If you have ideas for new features, better propagation models, or want to contribute — let's push the boundaries of what AI-augmented analysis tools can look like. Open an issue or submit a PR.

**[Technical Manual](docs/TECHNICAL_MANUAL.md)** — deep dive into every algorithm, formula, and design decision.

![3D Graph Visualization](https://img.shields.io/badge/3D-Interactive_Graph-blue) ![Claude + GPT](https://img.shields.io/badge/LLM-Claude_%7C_GPT-orange) ![Docker](https://img.shields.io/badge/deploy-Docker_Compose-2496ED) ![CI](https://github.com/zianwang123/causal-sentiment/actions/workflows/ci.yml/badge.svg)

---

## Why This Exists

Traditional sentiment analysis tools treat assets in isolation — one stock, one headline, one data point at a time. But a change in CPI expectations propagates through monetary policy, into interest rates, through credit markets, and ultimately into equity indices. These cascading causal relationships are what macro investors like Bridgewater model systematically.

This project captures that interconnectedness in a **directed causal graph** and makes it tangible through 3D visualization. Most macro analysts hold this causal model in their heads. This project makes it **explicit, visual, and machine-augmented**.


<details>
<summary><strong>Shock propagation as a thinking tool</strong></summary>

The graph isn't just a pretty visualization — it's a reasoning framework. When you shock a node (say, oil sentiment drops to -0.8), the impact **propagates** through the causal network:

- **Direct hits** — energy stocks take an immediate hit (1 hop, high weight)
- **Indirect effects** — inflation expectations shift → rate expectations → equities (3 hops, decayed)
- **Inverse beneficiaries** — airlines and consumers gain from lower energy costs (negative causal edge)
- **Uncorrelated nodes** — geopolitical risk is causally distant, impact decays to near-zero

This is exactly how a macro strategist thinks about positioning: "if X happens, what gets hurt, what benefits, and what's uncorrelated?" The graph makes that reasoning visible and testable.
</details>

---

## Features

- **52-node causal factor graph** — macro, rates, commodities, equities, currencies, and more, connected by 117 directed causal edges with expert-defined + dynamically-adapted weights
- **3D interactive visualization** — WebGL-powered, sentiment-colored, with directional particles showing causal flow
- **What-if simulator** — shock any node, watch the cascade, see the full impact report
- **AI agent** — Claude or GPT with pre-fetched data package (FRED + yfinance + RSS injected before analysis), three-phase reasoning loop (Plan → Analyze → Validate), batch sentiment updates, and self-calibration. All 52 nodes have mapped data sources — no blind spots
- **RSS news pipeline** — 27 curated financial RSS feeds (no API key needed): Fed, Bloomberg, CNBC, Google News topics. Enhanced keyword matching with word boundaries, exclusions, and confidence scoring. Source reliability tiers (T1 wire → T3 blog) inform agent reasoning
- **Morning brief** — daily intelligence summary: overnight movers (>1σ), prediction scorecard, regime shifts, risk propagation paths, LLM-generated narrative
- **Automation toggles** — runtime control of background scheduler and morning brief from the UI (no restart needed)
- **News trending detection** — auto-triggers agent analysis when 3+ sources converge on the same topic
- **Analyst annotations** — pin timestamped notes to any node, persisted across sessions
- **Regime narrator** — LLM-generated macro narrative from bellwether indicators
- **Prediction tracking** — agent records falsifiable predictions, system auto-resolves and tracks hit rate
- **Time travel** — replay graph state over the past 7 days
- **Portfolio overlay** — add your positions, see them highlighted on the graph
- **Edge discovery** — AI suggests new causal edges from correlation patterns
- **Causal discovery module** — computationally discovers causal networks from data using PCMCI+, Granger, and RPCMCI algorithms, with DoWhy statistical validation (see [Causal Discovery](#causal-discovery-module) below)

For details on algorithms, formulas, and design rationale, see the **[Technical Manual](docs/TECHNICAL_MANUAL.md)**.

---

<details>
<summary><h2>Architecture</h2></summary>

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
  ├── AI Agent (Claude/GPT, 3-phase loop, 12 tools)
  ├── Graph Engine (NetworkX, propagation, anomalies, regimes)
  ├── Data Pipeline (APScheduler, 10 jobs, disabled by default)
  └── PostgreSQL + TimescaleDB + Redis

External Data Sources:
  FRED · yfinance · 30 RSS feeds · NewsAPI · Reddit · SEC EDGAR
```

For detailed architecture, agent design, and concurrency model, see **[Technical Manual §2, §8, §17](docs/TECHNICAL_MANUAL.md)**.
</details>

<details>
<summary><h2>Tech Stack</h2></summary>

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
| **FRED API** | Rates, CPI, GDP, unemployment, credit spreads, consumer confidence, wages (16 series) | Every 4h |
| **yfinance** | Equities, ETFs, futures, forex (13 tickers) | Every 1h |
| **RSS Feeds** | 30 curated financial feeds (Fed, Bloomberg, CNBC, Google News topics) — free, no API key | Every 2h |
| **NewsAPI** | Headlines and articles (optional fallback) | On agent trigger |
| **Reddit** | Social sentiment (r/wallstreetbets, r/economics, r/stocks) | Every 2h |
| **SEC EDGAR** | Earnings, financial filings | Daily |
</details>

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- At least one LLM API key (Anthropic or OpenAI)

### Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/zianwang123/causal-sentiment.git
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

   > **Note:** News works out of the box via **30 curated RSS feeds** (no API key needed). Without `FRED_API_KEY`, the agent uses **mock data** for FRED macro series — add your own for real data (free: [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)). `NEWSAPI_KEY` is optional — RSS feeds are the primary news source, NewsAPI is a fallback.

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
| **Morning brief** | Click "Morning Brief" in the bottom toolbar → click "Generate" |
| **Toggle automations** | In the top-left panel under "Automations" — flip scheduler and morning brief on/off |
| **Switch LLM** | Toggle GPT/Claude in the top-left panel |
| **Time travel** | Open "Time Travel" in the bottom toolbar |
| **Portfolio** | Open "Portfolio" in the bottom toolbar to add positions |
| **Topology suggestions** | Open "Evolve Graph" to see AI-suggested new causal edges |

---

<details>
<summary><h2>Project Structure</h2></summary>

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
</details>

<details>
<summary><h2>FAQ</h2></summary>

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
</details>

---

<details>
<summary><h2>Roadmap</h2></summary>

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
- [x] Morning brief — daily summary of moves, predictions, regime changes
- [x] RSS news pipeline — 30 curated feeds (no API key), source reliability tiers (T1/T2/T3)
- [x] Pre-fetch data package — FRED + yfinance + RSS injected before agent starts
- [x] Evidence provenance — real/mock/inferred per data source per node, evidence history (20 entries)
- [x] Tool audit trail — full tool call inputs + outputs stored per agent run
- [x] Batch sentiment updates — atomic multi-node writes with single graph lock
- [ ] Historical backtesting dashboard with equity curves
- [ ] User-defined custom graphs (bring your own nodes/edges)
- [ ] Alerting (email/Slack when anomalies detected)
</details>

---

<details>
<summary><h2>Causal Discovery Module</h2></summary>

In addition to the hand-crafted expert graph (52 nodes, 117 edges), the project includes a **computational causal discovery module** that discovers the network structure directly from historical data — no manual edge definitions needed.

### How it works

1. **Data pipeline** fetches daily prices and macro indicators from 45 sources (yfinance, FRED, CFTC, GDELT, GPR Index) into a TimescaleDB hypertable
2. **Scoring** transforms raw data into comparable signals: z-score (deviation from 90-day average), log returns (daily changes), or rolling volatility (20-day choppiness)
3. **Causal algorithms** discover which factors statistically predict which others:
   - **PCMCI+** — controls for confounders, best for time-series (primary)
   - **Granger** — pairwise tests, fast but more spurious edges
   - **RPCMCI** — detects market regime shifts and discovers different causal structures per regime
4. **DoWhy validation** automatically tests every discovered edge with conditional independence tests — typically 74-84% of PCMCI+ edges pass
5. **Anchor propagation** infers display polarity (green/red) from a small set of anchor nodes (e.g., S&P 500 = positive, VIX = negative) via BFS through causal edges

### Expert vs. Discovered

| | Expert Graph | Discovered Graph |
|---|---|---|
| Nodes | 52 hand-picked | 34-42 from data, filtered by statistical significance |
| Edges | 117 hand-drawn | 39-287 learned from algorithms |
| Weights | Expert-defined | Data-driven |
| Scores | LLM sentiment (~$0.04/node, ~30s) | Z-score (free, instant) |
| Validation | None | DoWhy statistical tests |

The frontend lets you toggle between expert and discovered modes. Both support shock simulation, animation, and node inspection.

For the full technical specification, see **[backend/app/causal_discovery/README.md](backend/app/causal_discovery/README.md)**.
</details>

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
