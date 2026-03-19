# Causal Sentiment Engine — Technical Manual

> This document is the definitive technical reference for the Causal Sentiment Engine. It covers every design decision, algorithm, formula, constant, and rationale in the system. Written for anyone who wants to understand not just *what* the system does, but *why* it works the way it does.

---

## Table of Contents

1. [What This Is](#1-what-this-is)
2. [Architecture Overview](#2-architecture-overview)
3. [The Causal Graph: 52 Nodes and 117 Edges](#3-the-causal-graph)
4. [Signal Propagation Algorithm](#4-signal-propagation-algorithm)
5. [Dynamic Weight Learning](#5-dynamic-weight-learning)
6. [Anomaly Detection](#6-anomaly-detection)
7. [Market Regime Detection](#7-market-regime-detection)
8. [The AI Agent](#8-the-ai-agent)
9. [Data Pipeline](#9-data-pipeline)
10. [Prediction Tracking & Self-Calibration](#10-prediction-tracking)
11. [Sentiment Decay](#11-sentiment-decay)
12. [What-If Shock Simulator](#12-what-if-shock-simulator)
13. [Frontend Visualization](#13-frontend-visualization)
14. [Database Schema](#14-database-schema)
15. [API Reference](#15-api-reference)
16. [Configuration Reference](#16-configuration-reference)
17. [Concurrency Model](#17-concurrency-model)
18. [Edge Discovery & Topology Learning](#18-edge-discovery--topology-learning)
19. [Data Freshness & Latency](#19-data-freshness--latency)
20. [Portfolio Overlay](#20-portfolio-overlay)
21. [Backtesting](#21-backtesting)
22. [Scenario Extrapolation Engine](#22-scenario-extrapolation-engine-macro-sim)
23. [Limitations & Known Issues](#23-limitations--known-issues)
24. [FAQ & Design Rationale](#24-faq--design-rationale)

---

## 1. What This Is

The Causal Sentiment Engine models the financial world as a **directed causal graph** — 52 nodes representing macro factors, interest rates, commodities, equities, currencies, and more, connected by 117 directed edges representing causal relationships (e.g., "rising CPI → higher rate expectations → lower equity valuations").

An AI agent (Claude or GPT) autonomously fetches real data, analyzes sentiment, and writes scores to nodes. When a node's sentiment changes, the signal **propagates** through the causal network — just like how a macro analyst mentally traces second- and third-order effects.

It is **not** a trading signal. It is a reasoning tool — a second brain that makes implicit macro models explicit, visual, and testable.

---

## 2. Architecture Overview

```
Browser (localhost:3000)
  ├── 3D Force-Directed Graph (Three.js/WebGL)
  ├── Node Detail Panel (sentiment, charts, annotations)
  ├── What-If Simulator
  ├── Agent Audit Log
  └── Predictions Panel
       │
       │ WebSocket (real-time push)
       ▼
FastAPI Backend (localhost:8000)
  ├── AI Agent (Claude/GPT, 3-phase loop, 12 tools)
  ├── Graph Engine (NetworkX, propagation, anomalies, regimes)
  ├── Data Pipeline (APScheduler, FRED, yfinance, Reddit, SEC)
  └── PostgreSQL + TimescaleDB + Redis
```

**Data flow:** Data Pipeline fetches from external sources → anomaly check (2σ z-score) → if anomaly detected, auto-triggers Agent → Agent fetches more data, writes sentiment → propagation runs → WebSocket pushes to frontend → 3D graph updates in real-time.

**Concurrency:** All in-memory graph mutations are protected by `asyncio.Lock` (`app_state.graph_lock`) to prevent race conditions between concurrent agent runs, scheduler jobs, and API requests.

---

## 3. The Causal Graph

### Why 52 Nodes?

The graph covers the major factors that macro analysts track across 11 categories. The goal is **coverage without noise** — enough nodes to capture the key causal chains in global macro, but not so many that the graph becomes unmanageable.

### Node Categories

| Category | Count | Nodes |
|----------|-------|-------|
| **Macro** | 8 | fed_funds_rate, us_cpi_yoy, us_gdp_growth, unemployment_rate, us_pmi, pce_deflator, consumer_confidence, wage_growth |
| **Monetary Policy** | 4 | fed_balance_sheet, rate_expectations, qe_pace, global_central_bank_liquidity |
| **Geopolitics** | 4 | geopolitical_risk_index, trade_policy_tariffs, us_political_risk, sanctions_pressure |
| **Rates & Credit** | 6 | us_2y_yield, us_10y_yield, us_30y_yield, yield_curve_spread, ig_credit_spread, hy_credit_spread |
| **Volatility** | 5 | vix, move_index, put_call_ratio, skew_index, credit_default_swaps |
| **Commodities** | 6 | wti_crude, gold, copper, natural_gas, silver, wheat |
| **Equities** | 6 | sp500, nasdaq, tech_sector, energy_sector, financials_sector, russell2000 |
| **Equity Fundamentals** | 3 | earnings_momentum, pe_valuations, revenue_growth |
| **Currencies** | 4 | dxy_index, eurusd, usdjpy, usdcny |
| **Flows & Sentiment** | 3 | retail_sentiment, fund_flows, institutional_positioning |
| **Global** | 3 | china_pmi, eu_hicp, japan_boj_policy |

### Why These Specific Nodes?

Each node was chosen because it represents a factor that:
1. Has a clear causal relationship to other factors in the graph
2. Is tracked by real macro analysts (Bridgewater-style research)
3. Has accessible data (FRED, yfinance, or news)
4. Moves on timescales relevant to macro analysis (days to months, not milliseconds)

### Edge Design: 117 Directed Causal Edges

Every edge has:
- **Direction:** POSITIVE (A↑ → B↑), NEGATIVE (A↑ → B↓), or COMPLEX (regime-dependent)
- **Base weight:** Expert-defined strength [0.0, 1.0] — encodes domain knowledge
- **Dynamic weight:** Computed from 90-day Pearson correlations — adapts to empirical data
- **Effective weight:** `0.6 × base_weight + 0.4 × dynamic_weight`
- **Description:** Explains the causal mechanism

### Complete Edge List

**Fed Funds Rate (8 outgoing edges):**

| Target | Dir | Weight | Why |
|--------|-----|--------|-----|
| us_2y_yield | + | 0.9 | Short-term rates track fed funds closely |
| us_10y_yield | + | 0.6 | Long rates respond but also reflect term premium |
| dxy_index | + | 0.5 | Higher rates attract capital → stronger dollar |
| sp500 | - | 0.5 | Higher rates → higher discount rate → lower valuations |
| gold | - | 0.4 | Higher real yields → gold less attractive |
| ig_credit_spread | + | 0.3 | Tighter policy → wider spreads |
| hy_credit_spread | + | 0.5 | HY more sensitive to rate hikes (leverage) |
| russell2000 | - | 0.5 | Small caps more leveraged → more rate sensitive |

**CPI (4 outgoing edges):**

| Target | Dir | Weight | Why |
|--------|-----|--------|-----|
| fed_funds_rate | + | 0.7 | Inflation drives Fed tightening |
| rate_expectations | + | 0.8 | Inflation shifts rate path expectations |
| gold | + | 0.4 | Inflation → gold as inflation hedge |
| us_10y_yield | + | 0.5 | Inflation → higher nominal yields |

**GDP Growth (8 outgoing edges):**

| Target | Dir | Weight | Why |
|--------|-----|--------|-----|
| sp500 | + | 0.6 | Growth → higher earnings → equities up |
| earnings_momentum | + | 0.7 | Growth drives corporate earnings |
| copper | + | 0.5 | Growth → industrial demand for copper |
| ig_credit_spread | - | 0.4 | Growth → lower default risk → tighter spreads |
| hy_credit_spread | - | 0.6 | Growth → lower HY default risk |
| unemployment_rate | - | 0.7 | Okun's law: GDP growth reduces unemployment |
| russell2000 | + | 0.6 | Small caps more sensitive to domestic growth |
| revenue_growth | + | 0.6 | Economic growth drives corporate revenue |

**Unemployment Rate (3 outgoing edges):**

| Target | Dir | Weight | Why |
|--------|-----|--------|-----|
| retail_sentiment | - | 0.5 | Jobs situation drives consumer confidence |
| us_cpi_yoy | - | 0.3 | Phillips curve — weak but present |
| wage_growth | - | 0.5 | Tight labor market → wage pressure |

**PMI (3 outgoing edges):**

| Target | Dir | Weight | Why |
|--------|-----|--------|-----|
| sp500 | + | 0.4 | PMI is a leading indicator for equities |
| copper | + | 0.5 | PMI → industrial activity → copper demand |
| wti_crude | + | 0.3 | Manufacturing activity drives energy demand |

**Monetary Policy (12 outgoing edges):**

| Source | Target | Dir | Weight | Why |
|--------|--------|-----|--------|-----|
| fed_balance_sheet | sp500 | + | 0.5 | QE → asset price inflation |
| fed_balance_sheet | gold | + | 0.4 | Balance sheet expansion → gold hedge |
| fed_balance_sheet | us_10y_yield | - | 0.4 | QE suppresses long-term yields |
| rate_expectations | us_2y_yield | + | 0.85 | 2Y yield = pure market rate expectations |
| rate_expectations | nasdaq | - | 0.6 | Rate expectations hit growth stocks hardest |
| rate_expectations | tech_sector | - | 0.6 | Tech valuations very sensitive to rate path |
| qe_pace | fed_balance_sheet | + | 0.9 | QE pace directly drives balance sheet size |
| qe_pace | us_10y_yield | - | 0.5 | Active QE suppresses long-term yields |
| qe_pace | sp500 | + | 0.4 | QE → liquidity → risk assets |
| global_central_bank_liquidity | sp500 | + | 0.4 | Global liquidity lifts all risk assets |
| global_central_bank_liquidity | gold | + | 0.5 | Liquidity expansion → debasement fear → gold |
| global_central_bank_liquidity | dxy_index | COMPLEX | 0.3 | Depends on relative easing rates |

**Geopolitics (16 outgoing edges):**

| Source | Target | Dir | Weight | Why |
|--------|--------|-----|--------|-----|
| geopolitical_risk | gold | + | 0.6 | Flight to safety |
| geopolitical_risk | vix | + | 0.5 | Uncertainty → volatility |
| geopolitical_risk | wti_crude | + | 0.5 | Supply disruption fear |
| geopolitical_risk | dxy_index | + | 0.3 | Dollar safe haven bid |
| geopolitical_risk | wheat | + | 0.4 | Grain supply disruption |
| trade_policy_tariffs | china_pmi | - | 0.5 | Tariffs → trade disruption |
| trade_policy_tariffs | wti_crude | - | 0.3 | Trade war → less activity → less oil demand |
| trade_policy_tariffs | sp500 | - | 0.4 | Tariffs → margin pressure |
| trade_policy_tariffs | usdcny | + | 0.4 | Tariffs → capital outflow from China |
| us_political_risk | vix | + | 0.4 | Domestic uncertainty → volatility |
| us_political_risk | dxy_index | - | 0.3 | Political instability weakens dollar |
| us_political_risk | sp500 | - | 0.3 | Policy uncertainty → equity risk premium |
| sanctions_pressure | wti_crude | + | 0.4 | Sanctions on producers → supply disruption |
| sanctions_pressure | natural_gas | + | 0.4 | Energy sanctions → gas supply risk |
| sanctions_pressure | gold | + | 0.3 | Geopolitical hedge |
| sanctions_pressure | dxy_index | + | 0.2 | Sanctions strengthen dollar hegemony |

**Yield Curve & Credit (8 outgoing edges):**

| Source | Target | Dir | Weight | Why |
|--------|--------|-----|--------|-----|
| us_2y_yield | yield_curve_spread | - | 0.9 | Higher 2Y → flatter/inverted curve |
| us_10y_yield | yield_curve_spread | + | 0.9 | Higher 10Y → steeper curve |
| yield_curve_spread | financials_sector | + | 0.6 | Steeper curve → bank NIM expansion |
| yield_curve_spread | sp500 | + | 0.3 | Inversion signals recession risk |
| yield_curve_spread | russell2000 | + | 0.4 | Steeper curve → small cap banks benefit |
| ig_credit_spread | sp500 | - | 0.3 | Wider spreads → risk-off |
| hy_credit_spread | sp500 | - | 0.5 | HY spreads are a leading indicator for equities |
| hy_credit_spread | vix | + | 0.4 | Credit stress → equity volatility |

**Volatility (9 outgoing edges):**

| Source | Target | Dir | Weight | Why |
|--------|--------|-----|--------|-----|
| vix | sp500 | - | 0.6 | Vol spikes → equity selloff (leverage effect) |
| vix | put_call_ratio | + | 0.5 | Fear → more put buying |
| put_call_ratio | retail_sentiment | - | 0.3 | High put/call → bearish sentiment |
| move_index | us_10y_yield | COMPLEX | 0.3 | Bond vol → yield uncertainty |
| skew_index | vix | + | 0.4 | Tail risk pricing → broad vol pickup |
| skew_index | put_call_ratio | + | 0.3 | Tail risk fear → OTM put demand |
| credit_default_swaps | hy_credit_spread | + | 0.7 | CDS leads cash credit spreads |
| credit_default_swaps | ig_credit_spread | + | 0.6 | CDS prices credit risk ahead of cash |
| credit_default_swaps | vix | + | 0.3 | Credit stress → equity vol contagion |

**Commodities (10 outgoing edges):**

| Source | Target | Dir | Weight | Why |
|--------|--------|-----|--------|-----|
| wti_crude | us_cpi_yoy | + | 0.4 | Oil → energy component of CPI |
| wti_crude | energy_sector | + | 0.8 | Oil price drives energy stocks directly |
| copper | china_pmi | + | 0.4 | Copper demand reflects China manufacturing |
| gold | dxy_index | - | 0.5 | Gold and dollar inversely correlated |
| natural_gas | us_cpi_yoy | + | 0.3 | Gas → utilities/heating component of CPI |
| natural_gas | energy_sector | + | 0.4 | Gas prices drive gas-weighted energy stocks |
| silver | gold | + | 0.6 | Silver tracks gold as precious metal |
| silver | copper | + | 0.3 | Silver has industrial demand overlap |
| wheat | us_cpi_yoy | + | 0.2 | Wheat → food component of CPI |
| dxy_index | wti_crude | - | 0.3 | Strong dollar → commodities cheaper |

**Equities (7 outgoing edges):**

| Source | Target | Dir | Weight | Why |
|--------|--------|-----|--------|-----|
| sp500 | vix | - | 0.7 | Equity drops → vol spike (leverage effect) |
| sp500 | retail_sentiment | + | 0.5 | Market performance drives sentiment |
| nasdaq | tech_sector | + | 0.9 | NASDAQ heavily weighted to tech |
| earnings_momentum | sp500 | + | 0.6 | Earnings drive equity returns |
| earnings_momentum | nasdaq | + | 0.5 | Tech earnings drive NASDAQ |
| earnings_momentum | tech_sector | + | 0.6 | Tech earnings drive sector |
| russell2000 | sp500 | + | 0.4 | Small-cap breadth confirms broad market |

**Currencies (5 outgoing edges):**

| Source | Target | Dir | Weight | Why |
|--------|--------|-----|--------|-----|
| dxy_index | eurusd | - | 0.9 | Dollar strength → EUR/USD down |
| dxy_index | usdjpy | + | 0.7 | Dollar strength → USD/JPY up |
| dxy_index | gold | - | 0.5 | Strong dollar → gold weaker |
| dxy_index | usdcny | + | 0.6 | Broad dollar strength lifts USD/CNY |
| usdcny | china_pmi | - | 0.3 | Yuan depreciation hurts Chinese purchasing power |

**Equity Fundamentals (4 outgoing edges):**

| Source | Target | Dir | Weight | Why |
|--------|--------|-----|--------|-----|
| pe_valuations | sp500 | - | 0.3 | Stretched valuations → mean-reversion risk |
| pe_valuations | nasdaq | - | 0.4 | Growth/tech more vulnerable to PE compression |
| revenue_growth | earnings_momentum | + | 0.7 | Revenue is the top-line driver of earnings |
| revenue_growth | sp500 | + | 0.4 | Revenue growth signals fundamental health |

**Flows & Positioning (5 outgoing edges):**

| Source | Target | Dir | Weight | Why |
|--------|--------|-----|--------|-----|
| fund_flows | sp500 | + | 0.5 | Net inflows → buying pressure |
| fund_flows | us_10y_yield | - | 0.3 | Flows into bonds → yield compression |
| institutional_positioning | sp500 | + | 0.4 | Net long positioning supports equities |
| institutional_positioning | vix | - | 0.3 | Heavy positioning → vol suppression |
| retail_sentiment | fund_flows | + | 0.3 | Retail sentiment drives retail allocation |

**Global (5 outgoing edges):**

| Source | Target | Dir | Weight | Why |
|--------|--------|-----|--------|-----|
| china_pmi | copper | + | 0.6 | China growth → industrial metal demand |
| china_pmi | wti_crude | + | 0.3 | China growth → energy demand |
| china_pmi | sp500 | + | 0.2 | China growth → global risk-on |
| eu_hicp | eurusd | COMPLEX | 0.3 | EU inflation → ECB hawkishness (complex) |
| eu_hicp | us_cpi_yoy | + | 0.2 | Global inflation co-moves |
| japan_boj_policy | usdjpy | - | 0.5 | BOJ hawkish → yen strengthens |
| japan_boj_policy | us_10y_yield | + | 0.2 | BOJ selling JGBs → global yield spillover |
| japan_boj_policy | gold | + | 0.2 | BOJ shifts → currency vol → gold demand |

**PCE / Wage / Consumer (7 outgoing edges):**

| Source | Target | Dir | Weight | Why |
|--------|--------|-----|--------|-----|
| pce_deflator | fed_funds_rate | + | 0.6 | PCE is Fed's preferred inflation gauge |
| pce_deflator | rate_expectations | + | 0.7 | Core PCE shifts rate path expectations |
| wage_growth | us_cpi_yoy | + | 0.5 | Wage-price spiral: labor costs → CPI |
| wage_growth | pce_deflator | + | 0.5 | Wage growth drives services inflation in PCE |
| wage_growth | consumer_confidence | + | 0.4 | Rising wages boost consumer sentiment |
| consumer_confidence | retail_sentiment | + | 0.7 | Consumer confidence drives retail investor mood |
| consumer_confidence | sp500 | + | 0.3 | Confidence → spending → earnings → equities |

---

## 4. Signal Propagation Algorithm

### The Core Idea

When a node's sentiment changes, the impact should flow through the causal network — just like how a real macro shock cascades through markets. The algorithm uses **weighted Breadth-First Search (BFS) with exponential decay**.

### Why BFS (not DFS)?

BFS ensures signals reach all immediate neighbors before going deeper. This matches how markets work — the closest causal connections react first, then second-order effects follow. DFS would trace one deep path before exploring breadth, which doesn't match how shocks propagate.

### Algorithm Step-by-Step

```
Input:
  source_node: the node being shocked
  signal: sentiment value [-1.0, +1.0]
  max_depth: 4 (how many hops to propagate)
  decay_per_hop: 0.3 (30% signal loss per hop)
  min_threshold: 0.01 (stop propagating below this)
  regime: "risk_on" | "risk_off" | null

1. Initialize queue with (source_node, signal, depth=0, path=[source_node])
2. Track visited_edges to prevent re-traversing the same edge

3. While queue is not empty:
   a. Pop (node_id, current_signal, depth, path) from queue
   b. If depth >= max_depth: skip (too deep)

   c. For each outgoing edge from node_id:
      - Skip if this edge was already visited
      - Mark edge as visited

      - Get effective_weight (0.6 × base + 0.4 × dynamic)

      - Determine direction_sign:
          POSITIVE → +1.0  (same direction)
          NEGATIVE → -1.0  (inverted)
          COMPLEX  → +0.5  (attenuated, ambiguous)

      - Apply regime-aware decay:
          In RISK_OFF:
            Negative edges: decay × 0.7 = 0.21 (fear propagates FASTER)
            Other edges:    decay × 1.3 = 0.39 (positive signals DAMPENED)
          In RISK_ON:
            Negative edges: decay × 1.3 = 0.39 (fear DAMPENED)
            Other edges:    decay × 0.7 = 0.21 (positive signals flow FASTER)
          Neutral: decay = 0.3 (no adjustment)
          Clamp decay to [0.1, 0.9]

      - Apply transmission lag factor:
          lag_factor = 1.0 / (1.0 + 0.1 × lag_hours)
          Example: 10h lag → factor = 1/2 = 0.5 (halved signal)

      - Compute propagated signal:
          propagated = current_signal × weight × direction_sign × (1 - decay) × lag_factor

      - If |propagated| < 0.01: stop (below threshold)

      - Accumulate at target (interference):
          If target already received signal from another path:
            impacts[target] += propagated  (constructive/destructive interference)
          Else:
            impacts[target] = propagated
          Clamp to [-1.0, +1.0]

      - Add target to queue for next hop
```

### Why 30% Decay Per Hop?

With 30% decay and max 4 hops, the signal attenuation is:
- Hop 1: 70% of original (direct neighbor)
- Hop 2: 49% of original (second-order)
- Hop 3: 34% of original (third-order)
- Hop 4: 24% of original (fourth-order, max)

This means direct neighbors feel most of the impact, but distant nodes still feel something. Below 4 hops, the signal decays below the 0.01 threshold for most paths.

### Why Regime-Aware Decay?

In a risk-off environment, fear is contagious — bad news spreads faster and further than good news. The multipliers (0.7 for fear in risk-off, 1.3 for dampening) capture this asymmetry. In risk-on, the opposite: positive momentum carries further.

### Constructive/Destructive Interference

If a node is reachable by multiple paths, signals **add** together. This means:
- If two positive paths converge on a node, it gets a **stronger** signal (constructive)
- If a positive and negative path converge, they **cancel** out (destructive)
- This matches reality: a node affected by both bullish and bearish forces nets out

### Cycle Prevention

The graph has cycles (e.g., SPY → VIX → SPY). The `visited_edges` set ensures each edge is traversed at most once per propagation, preventing infinite loops. This is edge-based (not node-based), so a node CAN be reached multiple times via different edges — which is correct for interference.

---

## 5. Dynamic Weight Learning

### The Problem

Expert-defined base weights are a good starting point, but markets evolve. A causal relationship that was strong last year might be weak now. Dynamic weights adapt edge strengths from empirical data.

### How It Works

1. **Fetch time series** for each connected node pair (90-day lookback)
2. **Align** irregular observations into 3-hour buckets (take mean within bucket)
3. **Compute Pearson correlation** between aligned series
4. **Update dynamic_weight** = |correlation| (absolute value, clamped to [0, 1])
5. **Effective weight** = 0.6 × base + 0.4 × dynamic

### Edge Muting (Not Flipping)

If the empirical correlation **strongly disagrees** with the expert-defined direction:
- POSITIVE edge but correlation < -0.3: **mute** the edge (set dynamic_weight = 0.05)
- NEGATIVE edge but correlation > +0.3: **mute** the edge

**Why mute instead of flip?** Early versions flipped edge directions, but this caused cascading errors. The domain knowledge in topology.py represents known causal mechanisms (e.g., "higher rates → lower equity valuations"). A temporary negative correlation doesn't mean the causal mechanism reversed — it might just mean other forces dominate right now. Muting preserves the structural knowledge while reducing the edge's influence.

COMPLEX edges are **never** muted — they're already acknowledged as ambiguous.

### Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `correlation_lookback_days` | 90 | Time window for correlation |
| `correlation_bucket_hours` | 3 | Time bucket size for alignment |
| `correlation_min_data_points` | 3 | Minimum aligned buckets required |
| `correlation_direction_flip_threshold` | 0.3 | Correlation strength to trigger muting |
| `edge_weight_base_ratio` | 0.6 | How much to trust base vs. dynamic weight |

---

## 6. Anomaly Detection

### Method

Z-score anomaly detection on each node's observation history.

```
z_score = (latest_value - historical_mean) / historical_std
```

- **Threshold:** |z_score| ≥ 2.0 (2 standard deviations)
- **Lookback:** 30 days of observations
- **Minimum observations:** 5 per node
- **Mean/std** computed from all observations EXCEPT the latest one

### Data Extraction Priority

For each observation, the system tries to extract a numeric value in this order:
1. `raw_data["close"]` — market price
2. `raw_data["change_pct"]` — percentage change
3. `raw_data["observations"][0]["value"]` — FRED series value
4. `obs.sentiment` — sentiment score
5. If all fail: skip

### What Triggers an Anomaly Response?

When a data fetch (FRED, market, EDGAR) completes, `_check_anomalies_and_trigger()` runs anomaly detection. If any node has |z_score| ≥ 2.0, the AI agent is **automatically triggered** to analyze those specific nodes.

This means the system is reactive: unusual market moves get immediate agent attention without waiting for the next scheduled run.

---

## 7. Market Regime Detection

### The Idea

The market is always in one of three states: Risk-On, Risk-Off, or Transitioning. This affects how signals propagate (see Section 4).

### Bellwether Nodes

8 nodes are used as regime indicators, each with a weight reflecting its importance:

| Node | Weight | Logic |
|------|--------|-------|
| VIX | -0.25 | High VIX = fear = risk-off |
| HY Credit Spread | -0.15 | Widening spreads = credit stress = risk-off |
| S&P 500 | +0.20 | Rising equities = risk-on |
| Yield Curve Spread | +0.10 | Steepening curve = growth expectations = risk-on |
| Gold | -0.10 | Rising gold = flight to safety = risk-off |
| IG Credit Spread | -0.10 | Widening IG spreads = risk-off |
| DXY (Dollar) | -0.05 | Strong dollar = safe haven flows = risk-off |
| Put/Call Ratio | -0.05 | High put/call = fear = risk-off |

### Composite Score

```
composite = Σ(sentiment[node] × weight) / Σ|weight|
```

The weights sum to 1.0 in absolute value, so the composite is naturally normalized.

### Classification

| Composite Score | Regime |
|----------------|--------|
| > +0.2 | RISK_ON |
| < -0.2 | RISK_OFF |
| -0.2 to +0.2 | TRANSITIONING |

### Confidence

```
confidence = min(1.0, |composite| / 0.5)
```

At ±0.2 (boundary): confidence = 40%. At ±0.5: confidence = 100%.

---

## 8. The AI Agent

### Three-Phase Reasoning Loop

The agent runs a structured **Plan → Analyze → Validate** loop with a hard limit of 35 rounds total.

| Phase | Rounds | Purpose |
|-------|--------|---------|
| **Planning** | 0-2 (3 rounds) | Inspect graph state, decide priorities |
| **Analysis** | 3-27 (25 rounds) | Reason about pre-fetched data, write sentiment |
| **Validation** | 28-34 (7 rounds) | Self-critique, check contradictions, record predictions |

### Pre-Fetch Data Package

Before the agent starts, the system programmatically fetches all available data and injects it into the agent's context:
- **All 16 FRED series** — latest values with real/mock status labels
- **All 13 market tickers** — close prices and daily % changes from yfinance
- **Top 20 RSS headlines** — from 30 curated feeds with source tier labels (T1/T2/T3)
- **Coverage gaps** — nodes with no direct data source are flagged so the agent knows to search news or infer

This eliminates ~20 redundant data-fetching rounds. The agent still has access to all fetch tools for deeper investigation.

### Batch Sentiment Update

The `batch_update_sentiment` tool lets the agent update 10-15 nodes in a single call instead of one-by-one. Typical run: 4 batch calls updating all 52 nodes (vs 55 individual calls without batching). Each update carries `data_sources` provenance from the pre-fetch, stored in `Node.evidence[].data_sources`.

### Evidence Provenance

Each node's evidence now includes a `data_sources` dict showing what fed the analysis:
```json
{
  "fred": {"status": "real", "series": "FEDFUNDS", "latest_value": "4.33"},
  "yfinance": {"status": "real", "ticker": "SPY", "close": 542.3},
  "rss": {"status": "real", "count": 3, "best_tier": 1},
  "_none": {"status": "inferred"}
}
```
Status values: `real` (live data), `mock` (API key missing), `inferred` (no direct source). Displayed in the frontend NodePanel as color-coded badges.

### Phase 1: Planning

The agent calls `get_analysis_context` to see:
- **Anomalies:** Which nodes have 2σ moves
- **Stale nodes:** Which nodes haven't been updated in 24+ hours
- **Regime:** Current risk-on/off state
- **Priority ranking:** `score = centrality × 0.4 + is_stale × 0.3 + is_anomalous × 0.3`

The agent also calls `get_agent_track_record` to review its past prediction accuracy and calibrate confidence.

### Phase 2: Analysis

The agent reasons about the pre-fetched data and writes sentiment. For each node:
1. Review pre-fetched data (FRED, yfinance, RSS) already in context
2. Optionally fetch more detail (news, Reddit, SEC) for specific topics
3. Call `batch_update_sentiment` (or individual `update_sentiment_signal`) with:
   - **sentiment:** [-1.0, +1.0]
   - **confidence breakdown:**
     - `data_freshness`: 1.0 = very fresh (<1h), 0.5 = moderate (<24h), 0.0 = stale (>7d)
     - `source_agreement`: 1.0 = strong consensus, 0.5 = mixed, 0.0 = contradictory
     - `signal_strength`: 1.0 = very clear signal, 0.5 = moderate, 0.0 = ambiguous
   - **Final confidence** = `0.3 × freshness + 0.4 × agreement + 0.3 × strength`

### Phase 3: Validation

1. Calls `validate_consistency` with all updated node IDs
2. **Contradiction detection:** For each pair of connected nodes, checks if their sentiments conflict with the edge direction:
   - POSITIVE edge: source and target should have same sign
   - NEGATIVE edge: source and target should have opposite signs
   - Both must have |sentiment| > 0.15 to be considered (weak signals ignored)
3. Records 2-3 high-conviction predictions via `record_prediction`

### Agent Memory

Between runs, the agent receives context injected directly into the **system prompt** (built by `_build_memory_context()` in `orchestrator.py`):

- **Previous 3 run summaries** (truncated to 300 chars each) with time-since labels (e.g., "2h ago", "1d ago") — appended as a `## Previous Analyses` section in the system prompt
- **Prediction track record** (hit rate, recent outcomes, calibration warning if <50%) — appended as a `## Your Track Record` section

This is not stored in a separate memory system — it's queried from the database at the start of each agent run and concatenated to the system prompt. The agent sees its own history as part of its instructions, enabling self-calibration without external memory infrastructure.

### 12 Tools

| Tool | Purpose | Data Source |
|------|---------|-------------|
| `fetch_fred_data` | Macro data (rates, CPI, GDP, etc.) | FRED API |
| `fetch_market_prices` | ETF/futures prices and % changes | yfinance |
| `search_news` | Financial headlines | RSS (30 curated feeds) |
| `search_reddit` | Social sentiment | Reddit (asyncpraw) |
| `fetch_sec_filings` | Earnings, revenue, EPS | SEC EDGAR |
| `update_sentiment_signal` | Write sentiment to a single node | Internal |
| `batch_update_sentiment` | Write sentiment to multiple nodes (single lock + commit) | Internal |
| `get_graph_neighborhood` | Inspect node + neighbors | Internal |
| `get_analysis_context` | Graph-wide state summary | Internal |
| `validate_consistency` | Check for contradictions | Internal |
| `record_prediction` | Store falsifiable prediction | Internal |
| `get_agent_track_record` | Review past accuracy | Internal |

---

## 9. Data Pipeline

### End-to-End Data Flow (Including Agent Decision Loop)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  EXTERNAL DATA SOURCES                                                          │
│                                                                                 │
│  FRED API ──────┐    yfinance ──────┐    RSS Feeds (30) ──┐    Reddit ────┐    │
│  (16 series)    │    (21 tickers)   │    T1/T2/T3 tiers   │    (3 subs)  │    │
│  4h interval    │    1h interval    │    2h interval       │    2h interval│    │
└────────┬────────┘────────┬──────────┘────────┬─────────────┘────────┬─────┘────┘
         │                 │                   │                      │
         ▼                 ▼                   ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  SCHEDULER PIPELINE (APScheduler, disabled by default)                          │
│                                                                                 │
│  Each fetch job:                                                                │
│  1. Fetch raw data from external source                                         │
│  2. Store as SentimentObservation (raw_data JSONB)                              │
│  3. Run anomaly detection (z-score, 2σ threshold)                               │
│  4. If anomaly detected → auto-trigger agent on affected nodes                  │
│                                                                                 │
│  Additional jobs:                                                               │
│  · Weight recalculation (3 AM) — 90-day Pearson correlations → dynamic_weight   │
│  · Sentiment decay (2 AM) — 24h half-life exponential decay on all nodes        │
│  · Prediction resolution (1h) — compare predictions vs actuals, score hit/miss  │
│  · Trending detection — 3+ sources on same node → auto-trigger agent            │
│  · Morning brief (7 AM) — overnight movers + prediction scorecard + narrative   │
└────────────────────────────────┬────────────────────────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │  TRIGGER         │                   │
              │  · Scheduled (6h)│                   │
              │  · Anomaly (2σ)  │                   │
              │  · User button   │                   │
              ▼                  ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  PRE-FETCH DATA PACKAGE  (orchestrator.py → _build_data_package)                │
│                                                                                 │
│  Before the agent starts, the system fetches ALL available data:                │
│                                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐                  │
│  │ FRED (16)    │  │ yfinance (13)│  │ RSS (30 feeds)       │                  │
│  │ Latest value │  │ Close price  │  │ Top 20 headlines     │                  │
│  │ real/mock    │  │ % change     │  │ T1/T2/T3 tier labels │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘                  │
│         │                 │                      │                              │
│         └─────────────────┼──────────────────────┘                              │
│                           ▼                                                     │
│                   source_map: dict[node_id → {fred?, yfinance?, rss?}]          │
│                   + prompt text injected into agent system prompt                │
│                   + nodes without data flagged as "inferred"                     │
└────────────────────────────────┬────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  AGENT REASONING LOOP  (Claude / GPT, 35 round budget)                          │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │  PHASE 1: PLANNING  (rounds 0-2, max 3)                        │            │
│  │                                                                 │            │
│  │  Tools called:                                                  │            │
│  │  · get_analysis_context → anomalies, stale nodes, regime,       │            │
│  │                           priority ranking                      │            │
│  │  · get_agent_track_record → past prediction accuracy            │            │
│  │                                                                 │            │
│  │  Agent decides:                                                 │            │
│  │  · Which nodes to prioritize (anomalies + stale + high-cent.)   │            │
│  │  · What additional data to fetch                                │            │
│  │  · Hypotheses to test (cross-asset relationships)               │            │
│  └─────────────────────────┬───────────────────────────────────────┘            │
│                            ▼                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │  PHASE 2: ANALYSIS  (rounds 3-27, max 25)                      │            │
│  │                                                                 │            │
│  │  Step 1: Use pre-fetched data already in context                │            │
│  │  Step 2: Optionally fetch more (search_news, search_reddit,     │            │
│  │          fetch_sec_filings) for specific topics                 │            │
│  │  Step 3: For each node, write sentiment:                        │            │
│  │                                                                 │            │
│  │  ┌─ batch_update_sentiment (preferred: ~5 calls for 52 nodes)   │            │
│  │  │  OR                                                          │            │
│  │  └─ update_sentiment_signal (individual: 52 calls)              │            │
│  │                                                                 │            │
│  │  Each update includes:                                          │            │
│  │  · sentiment [-1.0, +1.0]                                       │            │
│  │  · confidence breakdown (freshness, agreement, strength)        │            │
│  │  · evidence text citing FRED values + RSS headlines + tiers     │            │
│  │  · sources list (["FRED", "Bloomberg", "Reuters", ...])         │            │
│  │                                                                 │            │
│  │  Under the hood, each update:                                   │            │
│  │  1. Writes to Node table (DB) + in-memory graph                 │            │
│  │  2. Runs signal propagation (BFS, 4 hops, regime-aware decay)   │            │
│  │  3. Updates propagated neighbors' sentiment (blended)            │            │
│  │  4. Appends evidence entry with data_sources provenance         │            │
│  │  5. Records SentimentObservation (audit trail)                  │            │
│  └─────────────────────────┬───────────────────────────────────────┘            │
│                            ▼                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │  PHASE 3: VALIDATION  (rounds 28-34, max 7)                    │            │
│  │                                                                 │            │
│  │  1. validate_consistency(all updated node_ids)                  │            │
│  │     · Checks POSITIVE edges: source & target same sign?         │            │
│  │     · Checks NEGATIVE edges: source & target opposite signs?    │            │
│  │     · Also checks unchanged neighbors with |sentiment| > 0.15  │            │
│  │     · Only flags when both |sentiment| > 0.15                   │            │
│  │                                                                 │            │
│  │  2. If contradictions found → agent corrects or documents       │            │
│  │                                                                 │            │
│  │  3. record_prediction (2-3 high-conviction, falsifiable)        │            │
│  │     · node_id, direction, predicted_sentiment, horizon (7d)     │            │
│  │     · Resolved hourly by comparing against actual observations  │            │
│  └─────────────────────────────────────────────────────────────────┘            │
│                                                                                 │
│  All tool calls + outputs stored in AgentRun.tool_calls (JSONB)                 │
│  Outputs truncated to 2000 chars for DB efficiency                              │
└────────────────────────────────┬────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  EVIDENCE & PROVENANCE STORAGE                                                  │
│                                                                                 │
│  Node.evidence (JSONB array, latest 20 entries):                                │
│  ┌──────────────────────────────────────────────────────────────┐               │
│  │ {                                                            │               │
│  │   "text": "FEDFUNDS at 4.33, Reuters reports rate cut...",   │               │
│  │   "timestamp": "2026-03-17T19:10:30Z",                      │               │
│  │   "sources": ["FRED", "Reuters", "Bloomberg"],               │               │
│  │   "confidence_breakdown": {                                  │               │
│  │     "data_freshness": 0.5,                                   │               │
│  │     "source_agreement": 0.8,                                 │               │
│  │     "signal_strength": 0.7                                   │               │
│  │   },                                                         │               │
│  │   "data_sources": {            ← provenance from pre-fetch   │               │
│  │     "fred":    {"status":"real","series":"FEDFUNDS"},         │               │
│  │     "yfinance":{"status":"real","ticker":"SPY","close":542}, │               │
│  │     "rss":     {"status":"real","count":5,"best_tier":1}     │               │
│  │   }                                                          │               │
│  │ }                                                            │               │
│  └──────────────────────────────────────────────────────────────┘               │
│                                                                                 │
│  SentimentObservation table (full audit trail, one row per update):              │
│  · sentiment, confidence, source, evidence text, raw_data (JSONB)               │
│  · raw_data includes confidence_breakdown + data_sources provenance             │
│                                                                                 │
│  AgentRun.tool_calls (JSONB array, one entry per tool call):                    │
│  · tool name, input args, output (truncated), round number, phase               │
│  · Viewable in Agent Run Log panel (expandable per tool call)                   │
│  · Included in /api/graph/export for offline audit                              │
└────────────────────────────────┬────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  FRONTEND DELIVERY                                                              │
│                                                                                 │
│  WebSocket broadcast → 3D graph updates (node colors, edge particles)           │
│  Node Panel shows: evidence history (20 entries), data sources provenance,      │
│                     confidence breakdown, causal edges, sentiment chart          │
│  Agent Run Log shows: tool calls with expandable outputs per phase              │
│  Export All button: full JSON dump of runs, observations, predictions, nodes    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Scheduled Jobs (All Disabled by Default)

Set `SCHEDULER_ENABLED=true` in `.env` to enable.

| Job | Frequency | What It Does |
|-----|-----------|--------------|
| FRED fetch | Every 4 hours | Fetches 16 FRED series, stores as raw observations |
| Market fetch | Every 1 hour | Fetches 21 tickers via yfinance (equities, commodities, forex, vol indices, bond ETFs) |
| Reddit fetch | Every 2 hours | Fetches from r/wallstreetbets, r/economics, r/stocks |
| SEC EDGAR fetch | Daily at 6 AM UTC | Fetches financials for 10 tracked companies |
| Agent analysis | Every 6 hours | Runs agent on nodes with fresh data since last run |
| Weight recalculation | Daily at 3 AM UTC | Recomputes dynamic weights from Pearson correlations |
| Regime check | Every 2 hours | Detects regime, broadcasts via WebSocket |
| Sentiment decay | Daily at 2 AM UTC | Applies 24h half-life exponential decay |
| News fetch | Every 2 hours | Fetches 30 RSS feeds, stores articles as observations, detects trending topics |
| Morning brief | Daily at 7 AM UTC | Generates overnight movers, prediction scorecard, regime status, LLM narrative |
| Prediction resolution | Every 1 hour | Resolves expired predictions (no LLM cost) |

### FRED Series Mapping

| FRED Series | Node | What It Measures |
|------------|------|------------------|
| FEDFUNDS | fed_funds_rate | Federal Funds Rate (%) |
| CPIAUCSL | us_cpi_yoy | CPI All Urban Consumers |
| GDP | us_gdp_growth | Real GDP (% change) |
| UNRATE | unemployment_rate | Unemployment Rate (%) |
| MANEMP | us_pmi | Manufacturing Employment |
| T10Y2Y | yield_curve_spread | 10Y-2Y Spread |
| DGS2 | us_2y_yield | 2-Year Treasury Yield |
| DGS10 | us_10y_yield | 10-Year Treasury Yield |
| DGS30 | us_30y_yield | 30-Year Treasury Yield |
| VIXCLS | vix | VIX |
| DTWEXBGS | dxy_index | Trade-Weighted Dollar Index |
| BAMLH0A0HYM2 | hy_credit_spread | HY Credit Spread |
| BAMLC0A0CM | ig_credit_spread | IG Credit Spread |
| DCOILWTICO | wti_crude | WTI Crude Oil |
| UMCSENT | consumer_confidence | U. of Michigan Consumer Sentiment |
| CES0500000003 | wage_growth | Average Hourly Earnings |

### Market Ticker Mapping

| Ticker | Node | What It Tracks |
|--------|------|---------------|
| SPY | sp500 | S&P 500 |
| QQQ | nasdaq | NASDAQ-100 |
| IWM | russell2000 | Russell 2000 |
| XLK | tech_sector | Technology Sector |
| XLE | energy_sector | Energy Sector |
| XLF | financials_sector | Financials Sector |
| GLD | gold | Gold |
| SLV | silver | Silver |
| USO | wti_crude | Oil |
| UNG | natural_gas | Natural Gas |
| HG=F | copper | Copper Futures |
| ZW=F | wheat | Wheat Futures |
| DX-Y.NYB | dxy_index | Dollar Index |

### RSS News Pipeline

The system fetches news from **30 curated RSS feeds** — no API key required. Feeds are organized into two groups:

**Dedicated financial feeds (10):** Federal Reserve, Bloomberg Markets, CNBC (Top News + Economy), Yahoo Finance, OilPrice.com, Mining.com, Seeking Alpha, ZeroHedge, Investing.com.

**Google News topic feeds (17):** Custom search queries for: Federal Reserve, oil prices, stock market, inflation/CPI, central banks, commodities, geopolitics, interest rates, jobs, forex, earnings, FOMC, credit spreads, volatility/VIX, tariffs/trade, housing, China economy.

**Source reliability tiers** are passed to the agent so it weighs evidence appropriately:
- **T1 (wire/official):** Federal Reserve, Bloomberg — highest credibility
- **T2 (major outlet):** CNBC, Yahoo Finance, Google News aggregated — high credibility
- **T3 (specialist):** ZeroHedge, Seeking Alpha, OilPrice — require corroboration

**Deduplication:** Jaccard similarity on titles (>60% overlap = duplicate). When duplicates are found, the article from the higher-tier source is kept.

**Trending detection:** After each fetch, articles are grouped by node_id. If 3+ unique sources cover the same node, it's flagged as trending and the agent is auto-triggered on those nodes.

### Keyword → Node Matching

A shared `keyword_matcher.py` module is used by both the news and Reddit pipelines. Improvements over naive substring matching:

1. **Word boundary regex:** `\bwar\b` won't match "software" or "warrant"
2. **Multi-word phrase priority:** "federal reserve" (weight 2.0) scores higher than "fed" (weight 0.8)
3. **Negative keyword exclusions:** e.g., "gold" excludes "golden", "goldfish"; "war" excludes "software", "warrant", "star wars"
4. **Confidence scoring:** headline match = 1.0× weight, body match = 0.5× weight. Multiple keywords for the same node accumulate (capped at 1.0). Only mapped if confidence ≥ 0.3.

80+ keyword rules covering all 52 nodes.

### Morning Brief

A daily intelligence summary generated on-demand or scheduled (7 AM UTC). Contains:
1. **Overnight movers** — nodes with >1σ moves in the last 24 hours (from `detect_anomalies`)
2. **Prediction scorecard** — predictions resolved in the last 24 hours with hit/miss counts
3. **Regime status** — current state (risk-on/risk-off/transitioning), confidence, and whether a transition occurred
4. **Propagation paths** — top 3 movers' cascade impact through the causal graph
5. **LLM narrative** — 4-6 sentence macro summary tying all sections together

### Automation Toggles

Two automations can be toggled on/off at runtime via `POST /api/agent/automations/toggle`:
- **Background Scheduler** — all data-fetching jobs (FRED, market, news, Reddit, agent, weights, decay, regime, predictions)
- **Morning Brief** — daily 7 AM UTC intelligence summary

Toggles are independent — enabling the scheduler does not enable the morning brief, and vice versa. These are runtime-only changes; on restart, the system reverts to `.env` defaults (`SCHEDULER_ENABLED`).

### Retry Logic

All external API calls use exponential backoff:
- **Max attempts:** 3
- **Delays:** 1s, 2s, 4s
- On final failure: raises exception (logged, does not crash scheduler)

---

## 10. Prediction Tracking & Self-Calibration

### How Predictions Work

1. Agent records predictions during validation phase: node_id, direction (bullish/bearish/neutral), predicted_sentiment, horizon (default 7 days), reasoning
2. Every hour, `scheduled_prediction_resolution` checks for expired predictions
3. For each expired prediction, fetches the latest agent-sourced sentiment observation after the prediction was created

### Hit/Miss Criteria

| Direction | Hit Condition |
|-----------|--------------|
| Bullish | actual_sentiment > 0 |
| Bearish | actual_sentiment < 0 |
| Neutral | |actual_sentiment| < 0.2 |

### Magnitude Score

```
error = |predicted_sentiment - actual_sentiment|
magnitude_score = max(0.0, 1.0 - error)
```

- Perfect match (error=0): score = 1.0
- Off by 0.5: score = 0.5
- Off by 1.0 (max): score = 0.0

### Self-Calibration

The agent's track record is injected into its system prompt. If hit_rate < 50% with ≥5 predictions, a calibration warning is included: "your hit rate is below 50% — consider being more conservative."

---

## 11. Sentiment Decay

### Why Decay?

Old sentiment observations become stale. Without decay, a signal from a week ago would have the same weight as today's data. Exponential decay naturally fades old signals.

### Formula

```
decay_factor = exp(-0.693 × age_hours / half_life_hours)
decayed_value = original × decay_factor
```

- **Half-life:** 24 hours (configurable)
- `-0.693 = -ln(2)`, which ensures the value halves every `half_life_hours`
- **Skip threshold:** Decay is not applied to observations younger than 6 hours
- **Zero threshold:** Values decayed below |0.01| are set to 0.0

### Decay Examples

| Age | Remaining Signal |
|-----|-----------------|
| 6h | 84% |
| 12h | 71% |
| 24h | 50% |
| 48h | 25% |
| 72h | 12.5% |
| 96h | 6.25% |

---

## 12. What-If Shock Simulator

### How It Works

The simulator is **read-only** — it does not modify the database or in-memory graph.

1. User drags slider to set hypothetical sentiment for a node
2. System computes `shock_delta = hypothetical - current_sentiment`
3. Calls `propagate_signal(graph, node_id, shock_delta, regime=current_regime)`
4. Returns impact on every affected node with:
   - **magnitude:** how much the node's sentiment would change
   - **path:** the causal chain from source to affected node
   - **hops:** path length

### Visual Overlay

When simulation is active:
- **Source node:** orange, 2× size
- **Positively affected nodes:** green, scaled by impact
- **Negatively affected nodes:** red, scaled by impact
- **Unaffected nodes:** dark gray, 0.5× size
- **Affected edges:** orange, 2.5px wide, 6 particles at 3× speed
- **Unaffected edges:** very dim, 0.3px wide, no particles

---

## 13. Frontend Visualization

### Sentiment Color Mapping

```
Bearish (sentiment < -0.01):
  intensity = sqrt(|sentiment|)
  Color: rgb(100 + 155×i, 100×(1-i), 60×(1-i))
  Range: muted red → pure red

Bullish (sentiment > +0.01):
  intensity = sqrt(sentiment)
  Color: rgb(60×(1-i), 100 + 155×i, 60×(1-i))
  Range: muted green → pure green

Neutral (|sentiment| < 0.01):
  Color: rgb(120, 120, 120)  [gray]
```

The `sqrt()` makes low sentiments more visible — without it, a sentiment of 0.1 would barely change the color.

### Edge Colors

| Direction | Color |
|-----------|-------|
| Positive | #22c55e (green) |
| Negative | #ef4444 (red) |
| Complex | #eab308 (yellow) |

### Node Sizing

```
base = max(2, centrality × 100)
```

Centrality is computed using **eigenvector centrality** (`nx.eigenvector_centrality_numpy` with `weight="effective_weight"`), which measures a node's influence — a node is important if it connects to other important nodes. Falls back to degree centrality for disconnected graphs. Cached with a 300-second TTL to avoid recomputation on every request.

Centrality ranges [0, 1], so node size ranges [2, 100]. Higher centrality = bigger node = more connected/important.

### Node Positioning & Forces

The 3D graph uses [d3-force-3d](https://github.com/vasturiano/d3-force-3d) (built into `react-force-graph-3d`) to determine node positions. Three forces act simultaneously:

1. **Link force** — connected nodes attract each other like springs. Nodes sharing a causal edge end up closer together.
2. **Charge force** — every node repels every other node, preventing overlap and spreading the graph out.
3. **Center force** — gently pulls all nodes toward the origin so the graph doesn't drift off screen.

Node positions are **not** manually set — they emerge from the force simulation reaching equilibrium. Nodes with more shared connections naturally cluster together. The edge weight does not currently affect link distance or spring stiffness (D3 defaults are used).

### Cluster Layout

When the user toggles clustered mode, a **fourth custom force** is added that pulls each node toward a hardcoded centroid position based on its category:

```
macro:              [  0,  150,   0]
monetary_policy:    [150,  100,   0]
geopolitics:        [-150, 100,   0]
rates_credit:       [100,    0, 100]
volatility:         [-100,   0, 100]
commodities:        [100,    0, -100]
equities:           [-100,   0, -100]
equity_fundamentals:[  0,  -50, -150]
currencies:         [  0,  -50,  150]
flows_sentiment:    [150, -100,   0]
global:             [-150,-100,   0]
```

**Centroid positions are manually chosen** to spread 11 categories roughly evenly across a 3D sphere of radius ~200 units. They do not reflect the number of cross-category edges or causal proximity — they are purely for visual separation.

**Future improvement:** Centroid positions could be computed algorithmically from the graph topology — e.g., by counting cross-category edges and placing categories with more interconnections closer together, or by running a force simulation on the 11 category meta-nodes where link strength equals the number of edges between categories. This would make the spatial layout encode real causal structure rather than arbitrary coordinates.

**Force strength:** `alpha × 0.3` (where alpha is D3's cooling parameter). This is soft enough that D3's link and charge forces still determine fine positioning within each cluster. Densely connected nodes within a category clump tighter; cross-cluster edges pull connected nodes slightly across cluster boundaries.

**Final node position** is where all four forces reach equilibrium: cluster pull groups nodes by category, link force pulls connected neighbors closer, and charge repulsion spreads nodes within each group.

### WebSocket Heartbeat

- Client pings every 30 seconds
- Server responds with `{"type": "pong"}`
- If no response within 10 seconds, connection is considered dead and reconnect is triggered
- Reconnection uses exponential backoff: 2s, 3s, 4.5s, ... capped at 30s

### Error Boundary

The app is wrapped in an `ErrorBoundary` component. If any React component throws an exception, instead of a white screen, users see a "Something went wrong" message with a "Try Again" button that resets the error state.

### Agent Timeout

If `agentRunning` stays true for 15 minutes without receiving an `agent_complete` WebSocket event, the frontend automatically resets the state and shows an error message. This prevents the UI from being stuck in "Analyzing..." forever if the backend crashes.

---

## 14. Database Schema

### Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `nodes` | Graph vertices | id, label, node_type, composite_sentiment, confidence, evidence (JSONB), last_updated |
| `edges` | Causal connections | source_id, target_id, direction, base_weight, dynamic_weight, transmission_lag_hours |
| `sentiment_observations` | Time-series of all observations | node_id, sentiment, confidence, source, evidence, raw_data (JSONB), created_at |
| `agent_runs` | Agent execution log | trigger, status, nodes_analyzed (JSONB), tool_calls (JSONB), summary, started_at, finished_at |
| `predictions` | Falsifiable predictions | node_id, predicted_direction, predicted_sentiment, horizon_hours, hit, magnitude_score |
| `annotations` | Analyst notes | node_id, text, pinned, created_at |
| `edge_suggestions` | LLM-suggested edges | source_id, target_id, suggested_direction, correlation, llm_reasoning, status |
| `regime_snapshots` | Regime history | state, confidence, composite_score, contributing_signals (JSONB) |
| `portfolio_positions` | User portfolio | ticker, shares, entry_price |

### Timestamps

All timestamps are stored as `TIMESTAMP WITHOUT TIME ZONE` in UTC. Code uses `datetime.utcnow()` (naive) — never `datetime.now(timezone.utc)` (aware) to avoid comparison errors.

---

## 15. API Reference

### Graph Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/graph/full` | Full graph for 3D visualization |
| GET | `/api/graph/node/{id}` | Single node details |
| GET | `/api/graph/sentiment/history/{id}?days=30` | Sentiment time series |
| GET | `/api/graph/snapshot?timestamp=...` | Historical graph state |
| GET | `/api/graph/anomalies` | Anomalous nodes |
| GET | `/api/graph/regime` | Current regime |
| GET | `/api/graph/clusters` | Node cluster assignments |
| GET | `/api/graph/raw-data/{id}?limit=5` | Raw observations |
| GET | `/api/graph/backtest/{id}` | Backtest metrics |
| POST | `/api/graph/simulate` | What-if shock (read-only) |
| POST | `/api/graph/regime/narrative` | LLM regime narrative |
| POST | `/api/graph/topology/suggest` | Trigger edge discovery |

### Agent Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/agent/analyze` | Trigger analysis |
| GET | `/api/agent/runs?limit=20` | Agent run history |
| GET | `/api/agent/predictions` | List predictions |
| GET | `/api/agent/predictions/summary` | Hit rate summary |
| GET/POST | `/api/agent/llm-config` | Get/switch LLM provider |

### Annotation Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/annotations?node_id=...` | List annotations |
| POST | `/api/annotations` | Create annotation |
| PUT | `/api/annotations/{id}` | Update annotation |
| DELETE | `/api/annotations/{id}` | Delete annotation |

### WebSocket

Connect to `ws://localhost:8000/ws`. Events are JSON objects with `type` and `data` fields.

| Event | Direction | Data |
|-------|-----------|------|
| `graph_update` | Server → Client | Full graph state |
| `agent_progress` | Server → Client | Round, phase, tool calls |
| `agent_complete` | Server → Client | Run ID, status, summary |
| `regime_update` | Server → Client | Regime state, confidence |
| `ping` | Client → Server | Heartbeat |
| `pong` | Server → Client | Heartbeat response |

**Example payloads:**

```json
// agent_progress
{"type": "agent_progress", "data": {
  "round": 5, "max_rounds": 25, "phase": "analysis",
  "tool_calls": ["fetch_fred_data", "fetch_market_prices"],
  "total_tool_calls": 12
}}

// agent_complete
{"type": "agent_complete", "data": {
  "run_id": 42, "status": "completed",
  "nodes_analyzed": ["sp500", "vix", "fed_funds_rate"],
  "summary": "Analyzed 3 nodes. SPY showing bullish momentum..."
}}

// regime_update
{"type": "regime_update", "data": {
  "state": "risk_off", "confidence": 0.72,
  "composite_score": -0.36,
  "contributing_signals": {"vix": 0.45, "hy_credit_spread": 0.3, "sp500": -0.2}
}}

// graph_update (sent after agent completes)
{"type": "graph_update", "data": {
  "nodes": [{"id": "sp500", "composite_sentiment": 0.35, "confidence": 0.8, ...}],
  "edges": [...]
}}
```

---

## 16. Configuration Reference

All settings in `backend/app/config.py`, read from `.env`:

| Setting | Default | Description |
|---------|---------|-------------|
| `ANTHROPIC_API_KEY` | "" | Required for Claude agent |
| `OPENAI_API_KEY` | "" | Required for GPT agent |
| `LLM_PROVIDER` | "openai" | Which LLM to use ("anthropic" or "openai") |
| `ANTHROPIC_MODEL` | "claude-sonnet-4-20250514" | Claude model |
| `OPENAI_MODEL` | "gpt-4o" | GPT model |
| `SCHEDULER_ENABLED` | false | Enable background jobs |
| `FRED_API_KEY` | "" | Optional (mock fallback) |
| `NEWSAPI_KEY` | "" | Optional (mock fallback) |
| `REDDIT_CLIENT_ID` | "" | Optional |
| `REDDIT_CLIENT_SECRET` | "" | Optional |
| `propagation_max_depth` | 4 | Max BFS hops |
| `propagation_decay_per_hop` | 0.3 | Signal loss per hop |
| `propagation_min_threshold` | 0.01 | Stop propagating below |
| `propagation_blend_ratio` | 0.3 | Blend propagated with existing |
| `anomaly_z_threshold` | 2.0 | Z-score for anomaly detection |
| `anomaly_min_observations` | 5 | Min observations per node |
| `correlation_lookback_days` | 90 | Window for dynamic weights |
| `correlation_bucket_hours` | 3 | Time bucket for alignment |
| `correlation_direction_flip_threshold` | 0.3 | Muting threshold |
| `sentiment_half_life_hours` | 24.0 | Decay half-life |
| `sentiment_decay_skip_hours` | 6.0 | Don't decay if younger |
| `edge_weight_base_ratio` | 0.6 | Base vs dynamic weight ratio |
| `centrality_cache_ttl` | 300 | Centrality cache (seconds) |

---

## 17. Concurrency Model

### Graph Lock

All mutations to the in-memory NetworkX graph (`app_state.graph`) are protected by an `asyncio.Lock` (`app_state.graph_lock`). This prevents race conditions between:
- Concurrent agent runs writing sentiment and running propagation
- Scheduler jobs updating edge weights or applying sentiment decay
- API requests reading graph state

The lock is acquired in:
- `update_sentiment_signal()` — wraps both propagation and in-memory graph writes
- `scheduled_sentiment_decay()` — wraps bulk node sentiment updates
- Any topology mutation (adding edges from suggestions)

### Contention Pattern

Contention is low in practice: agent runs take seconds per tool call (LLM latency dominates), scheduler jobs run every 1-6 hours, and API reads are non-locking. The main risk is a long propagation blocking a concurrent agent tool call, but propagation over 52 nodes with max 4 hops is sub-millisecond.

### Session Lifecycle

- **API requests:** Sessions are created per-request via FastAPI's `Depends(get_session)` and automatically closed
- **Scheduler jobs:** Each job creates its own session via `async with async_session() as session:` — these run outside the FastAPI request lifecycle
- **Agent runs:** A single session spans the entire run (up to 25 rounds). On error, the session is rolled back and the error state is persisted in a clean commit

---

## 18. Edge Discovery & Topology Learning

### How It Works

The system can suggest new causal edges by combining statistical analysis with LLM reasoning:

1. **Correlation scanning** (`find_correlated_unconnected_pairs` in `topology_learning.py`): Computes Pearson correlations between all node pairs that are NOT currently connected. Pairs with |correlation| > threshold are candidates.

2. **LLM evaluation** (`suggest_edges_with_llm`): The LLM evaluates each candidate pair and decides whether the correlation reflects a plausible causal mechanism or is spurious. It provides:
   - Suggested direction (POSITIVE / NEGATIVE / COMPLEX)
   - Suggested weight
   - Reasoning explaining the causal mechanism

3. **Human review**: Suggestions are stored as `EdgeSuggestion` records with status "pending". The UI ("Evolve Graph" panel, `TopologySuggestions.tsx`) shows suggestions for the user to accept or reject.

4. **Acceptance**: Accepting a suggestion creates a real `Edge` in the database and adds it to the in-memory graph.

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/graph/topology/suggest` | Trigger edge discovery scan |
| GET | `/api/graph/topology/suggestions?status=pending` | List pending suggestions |
| POST | `/api/graph/topology/suggestions/{id}/accept` | Accept a suggestion |
| POST | `/api/graph/topology/suggestions/{id}/reject` | Reject a suggestion |

### Requirements

Nodes need at least 3 sentiment observations each for correlation analysis. Running more agent analyses across different time windows builds the observation history needed for edge discovery.

---

## 19. Data Freshness & Latency

### Source Latency

| Source | Typical Latency | Notes |
|--------|----------------|-------|
| FRED | Days to weeks | Most series update monthly (CPI, GDP, unemployment) or weekly (rates). Data represents the *reporting date*, not real-time |
| yfinance | 15-minute delay (free tier) | End-of-day prices are reliable; intraday is delayed. Markets closed on weekends/holidays |
| NewsAPI | Minutes | Headlines are near real-time but limited to 100 requests/day on free tier |
| Reddit | Minutes to hours | Post scores and comments lag the actual post time |
| SEC EDGAR | Days | Filings appear 1-2 days after submission |

### System Latency

- **Data fetch → anomaly check → agent trigger:** Seconds (limited by API response times)
- **Agent analysis → WebSocket push:** 1-5 minutes (dominated by LLM response time across 10-25 tool-use rounds)
- **Propagation:** Sub-millisecond for 52 nodes, max 4 hops

### Implications for Users

This system is designed for **macro analysis on daily-to-weekly timescales**. It is NOT a real-time trading signal. FRED data may be weeks old when the agent analyzes it. The value is in the causal reasoning and cross-node consistency, not in speed.

---

## 20. Portfolio Overlay

### What It Does

Users can register portfolio positions (ticker, shares, entry price) via the API. When positions are registered:
- The agent receives portfolio context in its system prompt: "User Portfolio: AAPL (100 shares @ $150.00), ..." — and is instructed to flag signals particularly relevant to these holdings
- Portfolio-linked nodes are highlighted amber in the 3D graph

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/portfolio` | List portfolio positions |
| POST | `/api/portfolio` | Add a position |
| PUT | `/api/portfolio/{id}` | Update a position |
| DELETE | `/api/portfolio/{id}` | Remove a position |
| GET | `/api/portfolio/summary` | Portfolio summary with sentiment exposure |

### Limitations

Portfolio overlay is informational only — it does not compute P&L, risk metrics, or hedging suggestions. It simply focuses the agent's attention on nodes relevant to your holdings.

---

## 21. Backtesting

### How It Works

The backtesting system measures the predictive power of sentiment signals by comparing historical sentiment observations against subsequent market returns.

For a given node:
1. Fetch all agent sentiment observations from the lookback window (default: 90 days)
2. For each observation, fetch the market price change over the forward window (default: 5 days)
3. Compute metrics:
   - **Hit rate:** % of times sentiment direction (positive/negative) predicted return direction correctly
   - **Correlation:** Pearson correlation between sentiment scores and forward returns
   - **Information Coefficient (IC):** Rank correlation between sentiment and returns
   - **Average return by direction:** Mean forward return when sentiment was bullish vs bearish
   - **Scatter plot data:** (sentiment, forward_return) pairs for visualization

### Frontend

`BacktestChart.tsx` renders a scatter plot of sentiment vs. forward returns with:
- Green dots: correct direction (bullish sentiment + positive return, or bearish + negative)
- Red dots: wrong direction
- Dashed blue trend line (linear regression)

### API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/graph/backtest/{node_id}?lookback_days=90&forward_days=5` | Backtest a single node |
| GET | `/api/graph/backtest/summary?lookback_days=90&forward_days=5` | Backtest all nodes |

---

## 22. Scenario Extrapolation Engine ("Macro Sim")

The scenario engine is a strategic foresight tool that generates branching probability-weighted scenarios from any trigger — a news event, a hypothetical, or an auto-picked headline. It is the most complex subsystem in the project: a 4-agent pipeline with ~1,600 lines of orchestration code and ~1,050 lines of prompts.

### 22.1 Design Philosophy: "Generate First, Map Second"

The agent reasons freely about real-world consequences first (unconstrained by the graph's 52 nodes), THEN is shown the graph topology and asked to map its impacts. This is the single most important design decision in the scenario engine.

**Why this matters:** If the Strategist were shown the graph topology during scenario generation, it would anchor to existing nodes and produce scenarios limited to "oil goes up, VIX goes up, equities go down" — the obvious first-order effects. By withholding the graph until Phase 4, the Strategist reasons about constitutional court rulings, deposit flight mechanics, TARGET2 imbalances, carry trade unwinds — concepts that don't have graph nodes but represent real transmission mechanisms. The Mapper then identifies these as graph gaps and suggests new nodes.

**Isolation principle:** The scenario agent reuses existing **code** (search_news, fetch_market_prices, validate_consistency, LLM client, WebSocket) but NEVER reads previous agent **outputs** (stored sentiments, past agent runs, prediction history). It reads only graph topology (nodes + edges = domain knowledge). Shocks are generated relative to neutral (0), not relative to current graph sentiment. This prevents anchoring to stale state and keeps scenarios fresh.

### 22.2 Architecture: 4-Phase Multi-Agent Pipeline

```
Trigger (user text or auto-picked from news)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Pre-flight: validate API key, auto-pick trigger    │
│  if empty, fetch market snapshot (SPY/VIX/Oil/DXY/  │
│  10Y), detect trigger domain, build vulnerability   │
│  context from graph state                           │
└────────────────────┬────────────────────────────────┘
                     │
    ┌────────────────▼─────────────────┐
    │  Phase 1: RESEARCHER (4 rounds)  │
    │  Tools: search_news,             │
    │         fetch_market_prices,     │
    │         get_economic_calendar    │
    │  Output: submit_research →       │
    │    {trigger, facts, key_actors,  │
    │     market_reaction,             │
    │     structural_context,          │
    │     domain_classification}       │
    └────────────────┬─────────────────┘
                     │ research brief (formatted text)
    ┌────────────────▼─────────────────┐
    │  Phase 2: HISTORIAN (5 rounds)   │
    │  Tools: search_news,             │
    │         fetch_market_prices,     │
    │         fetch_historical_prices  │
    │  Output: submit_history →        │
    │    {parallels: [{event,          │
    │     structural_match,            │
    │     transmission_mechanism,      │
    │     duration, consensus_error,   │
    │     specific_data}]}             │
    └────────────────┬─────────────────┘
                     │ historical brief (formatted text)
    ┌────────────────▼─────────────────┐
    │  Phase 3: STRATEGIST (12 rounds) │
    │  Tools: search_news,             │
    │         fetch_market_prices,     │
    │         get_economic_calendar,   │
    │         fetch_options_summary    │
    │  Input: research + history +     │
    │    track record + date/snapshot  │
    │  Output: submit_free_scenarios → │
    │    {branches: [{title,           │
    │     probability, narrative,      │
    │     causal_chain,                │
    │     free_form_impacts,           │  ← NOT node IDs
    │     specific_predictions,        │
    │     structural_outcome}]}        │
    └────────────────┬─────────────────┘
                     │ coherence check (Jaccard)
    ┌────────────────▼─────────────────┐
    │  Phase 4: MAPPER (6 rounds)      │
    │  Tools: get_graph_topology,      │
    │         preview_propagation,     │
    │         validate_consistency     │
    │  Input: strategist branches +    │
    │    full graph topology (52 nodes,│
    │    117 edges, NO sentiments)     │
    │  Output: submit_scenarios →      │
    │    {branches: [{shocks,          │  ← NOW node IDs
    │     node_suggestions,            │
    │     edge_suggestions, ...}]}     │
    └────────────────┬─────────────────┘
                     │
    ┌────────────────▼─────────────────┐
    │  Post-processing:                │
    │  - Persist shocks, suggestions   │
    │  - Extract market predictions    │
    │  - Broadcast completion via WS   │
    └──────────────────────────────────┘
```

Each sub-agent gets a **fresh conversation** — no cross-contamination between phases. Only the formatted brief is passed forward. Max tokens per LLM call: 24,576 (higher than the main agent's 8,192 to accommodate large structured JSON outputs).

### 22.3 Sub-Agent Runner

`_run_sub_agent()` is the core loop shared by all 4 phases:

1. Initialize messages with user prompt
2. For each round (up to phase budget):
   a. Call `chat_with_tools(system, messages, tools, max_tokens=24576)`
   b. If `llm_response.done` or no tool calls → break
   c. For each tool call:
      - If submission tool (`submit_research`, `submit_history`, `submit_free_scenarios`, `submit_scenarios`) → intercept input as result, return `{"status": "accepted"}`
      - If convergence-checked tool (`search_news`, `fetch_market_prices`) → check Jaccard similarity against recent calls; if >0.7, return nudge instead of executing
      - Otherwise → dispatch to `_execute_scenario_tool()`
   d. Append tool results to messages
   e. Broadcast progress via WebSocket
   f. If submission intercepted → break
3. If no submission tool called → extract last assistant text as `{"_text_brief": text}` fallback

**Fallback chain:** If the Strategist doesn't call `submit_free_scenarios`, the scenario is marked completed with an error note. If the Mapper doesn't call `submit_scenarios`, `_fallback_from_strategist()` converts free-form impacts to empty shocks (preserving narratives and causal chains but without graph mapping).

### 22.4 Context Injection

Before Phase 1, the orchestrator pre-fetches and injects several context layers:

**Current date + market snapshot:**
```
## Current Date: 2026-03-19
## Current Market Context
- SPY: 567.23 (+0.45% 1d, -1.23% 5d)
- ^VIX: 18.32 (-2.10% 1d, +5.67% 5d)
- CL=F: 68.91 (+1.05% 1d, -3.45% 5d)
- DX-Y.NYB: 104.12 (+0.15% 1d, +0.89% 5d)
- ^TNX: 4.28 (-0.50% 1d, +2.10% 5d)
```
Injected into Phases 1, 2, and 3 so the agent knows the current date (preventing temporal grounding errors from training cutoff) and current market levels.

**Domain-specific supplements:** The trigger text is classified against 7 domain keyword sets:

| Domain | Example Keywords | Supplement Focus |
|--------|-----------------|------------------|
| `geopolitical` | war, invasion, strait, hormuz, nato | Actor-incentive-capability analysis, chokepoints, proxy networks, alliance fracture |
| `policy_monetary` | fed, fomc, ecb, rate cut, taper | Transmission lag structure, carry trade exposure, collateral chains, forward guidance credibility |
| `trade_tariff` | tariff, reshoring, decoupling, wto | Retaliation sequences, substitution timelines, consumer price pass-through, FX weaponization |
| `technology_systemic` | cyberattack, ai disruption, outage | Concentration risk, platform dependency, labor dislocation, regulatory lag |
| `climate_energy` | hurricane, renewable, carbon tax | Stranded assets, transition bottlenecks, insurance withdrawal, green premium inflation |
| `pandemic_health` | pandemic, virus, lockdown, vaccine | Behavioral cascade, JIT fragility, fiscal capacity, vaccine timeline |
| `corporate_financial` | default, bankruptcy, bank run | Counterparty network, collateral chain, deposit flight speed, regulatory intervention threshold |

Multi-word phrases score 2 points; single words score 1. Top 2 domains are injected. Each supplement includes cross-domain cascade prompts.

**Vulnerability context:** Graph state is scanned for:
- Nodes with extreme sentiment (|composite_sentiment| > 0.7) → listed as "fragility points"
- Highest-weight transmission channels (effective_weight > 0.5) → listed as "strongest causal links"
- Current regime (risk_on / risk_off / transitioning)

**Track record:** Resolved `ScenarioPrediction` records are queried and formatted as calibration feedback for the Strategist:
- Overall hit rate by confidence bucket (low 0-0.3, medium 0.3-0.6, high 0.6-1.0)
- Systematic bias flags: "OVERCONFIDENT" if high-confidence bucket <50% hit rate (≥3 predictions)
- Last 5 resolved predictions with outcomes

### 22.5 Prompt Engineering

The prompts (~1,050 lines in `scenario_prompts.py`) are the core intellectual property of the scenario engine. Key design techniques:

**BAD/GOOD contrast pairs** — Used in Strategist and Mapper prompts to prevent lazy outputs:
```
BAD: "Markets would sell off and volatility would increase."
GOOD: "Forced selling from CTAs hitting stop-loss levels around S&P 4,200,
triggering ~$50B of systematic selling over 2-3 days. This would push
realized vol above 25, forcing risk-parity funds to de-lever both equity
AND bond allocations simultaneously."
```

**"And Then What?" doctrine** — The Strategist is instructed to recursively ask "and then what?" at least 3 times for every consequence, with worked examples:
```
Khamenei killed → IRGC factional vacuum → Houthi/Hezbollah proxy commanders
act independently → Strait of Hormuz harassment → tanker insurance +500% →
shipping reroutes add 10-14 days → global supply chain cost spike
```

**Temporal layering** — Every causal chain must have at least 3 temporal layers:
- IMMEDIATE (0-24h): Reflexive, automated responses
- SHORT-TERM (1-7d): Deliberate responses, initial repricing
- MEDIUM-TERM (1-4w): Second-order effects materialize
- STRUCTURAL (1-6m): Regime shifts, new equilibria (required for at least one path per branch)

**Calibration anchors** — ~120 lines of specific historical precedents with shock magnitudes:

| Event | Shock Reference |
|-------|----------------|
| 2008 GFC | S&P from +0.3 to -0.9 over 6 months |
| 2023 SVB | Regional banks -0.6, broader financials -0.3, VIX +0.4 |
| Russia-Ukraine 2022 | Oil +0.5, gas +0.7, gold +0.3, European equities -0.4 |
| Soleimani 2020 | Oil +4% intraday then faded in 3 days |
| COVID 2020 | VIX from -0.3 to +0.95 in 2 weeks |
| 2022 Rate Shock | Fed funds from -0.2 to +0.9 over 12 months |
| UK LDI 2022 | Gilt yields +0.6 in days, pension forced selling spiral |
| US-China tariffs 2018 | Market impact from UNCERTAINTY (capex froze), not tariff cost |
| Texas freeze 2021 | Natural gas +0.8, power prices 100x ($9,000/MWh) |

**Probability anchoring** — Base rates provided as starting points:
- Geopolitical escalation beyond initial event: ~25-35%
- Monetary policy surprises that break consensus: ~15-20%
- Trade wars escalating beyond initial tariffs: ~40-50%

**Domain-specific escalation frameworks** — 7 cascade logic templates:
- Geopolitical: trace POLITICAL cascade first (power structures → escalation ladder → proxy activation → chokepoints)
- Monetary: trace TRANSMISSION MECHANISM first (lag structure → carry trade exposure → collateral chains)
- Trade: trace SUPPLY CHAIN cascade first (retaliation sequence → substitution timelines → consumer pass-through)
- etc.

**Mapper decision criteria** — Explicit guidance on when to use existing nodes vs. suggest new ones:
- Directionality notes: spread nodes (positive = wider = more stress), yield nodes (positive = higher yields), currency nodes (DXY vs. individual pairs)
- Mapping examples with calibration reasoning
- Instruction to call `preview_propagation` to verify cascades match narrative before submitting

### 22.6 Tool Details

**`get_economic_calendar(days_ahead=30)`** — Returns upcoming macro events:
- Hardcoded FOMC dates for 2025-2027
- Rule-based recurring releases: CPI (~12th monthly), NFP (first Friday), GDP (quarterly), PCE (~28th monthly), ISM (1st business day)
- Optional FRED releases API (`https://api.stlouisfed.org/fred/releases/dates`) for precise dates when `FRED_API_KEY` is configured
- Returns `[{name, date, type, description}]` sorted by date

**`fetch_options_summary(ticker)`** — Returns options positioning via yfinance:
- Put/call ratio (volume-weighted)
- OI-weighted average implied volatility (calls and puts separately)
- Highest open-interest strike levels (call and put)
- IV term structure: near-month vs. next-month IV, contango flag, slope
- Graceful degradation if ticker has no options data

**`fetch_historical_prices(ticker, start_date, end_date)`** — Returns summary stats (not raw bars):
- Open, close, high, low, total return, max drawdown, peak/trough dates, annualized volatility
- Max 1 year per request. Async via `asyncio.to_thread()`

**`preview_propagation(shocks)`** — Runs `merge_multi_shock_impacts()` and returns top 15 affected nodes:
- Node ID, label, impact magnitude, contributing shocks, hop count
- Non-linear note included when stress multiplier > 1.0

**`get_graph_topology()`** — Returns full graph structure without sentiment values:
- 52 nodes: id, label, node_type, description
- 117 edges: source, target, direction, base_weight, description
- No composite_sentiment, no confidence, no evidence — prevents contamination

### 22.7 Three Branch Types

- **Base case (~50-60%)**: Well-reasoned mainstream scenario with clear transmission mechanics. "An expert reads this and nods."
- **Alternative (~25-35%)**: Non-obvious scenario connecting domains most analysts treat separately. "An expert reads this and pauses to think."
- **Tail risk (~5-15%)**: The scenario where a consensus assumption breaks — not random doom, but a specific mechanism being systematically underpriced. "An expert reads this and says 'I need to check our exposure to that.'"

Each branch must include: title, probability (with explicit reasoning), narrative, causal chain (temporal layers), structural outcome (1-6 month new equilibrium), free-form impacts, specific predictions (≥2 market-checkable with ticker/direction/threshold), time horizon, invalidation condition, key assumption.

### 22.8 Non-Linear Multi-Shock Simulation

`merge_multi_shock_impacts()` in `propagation.py` is used by both `_preview_propagation` (during agent reasoning) and `apply_scenario_branch` (when user applies a branch):

```python
# For each shock:
delta = shock_value - current_sentiment
propagation_result = propagate_signal(graph, node_id, delta, regime=regime_val)

# Merge all propagation results additively
merged[affected_node]["total_impact"] += impact

# Non-linear adjustments:
# 1. Stress multiplier for simultaneous shocks
if n_shocks > 3:
    stress_multiplier = 1.0 + 0.15 * (n_shocks - 3)

# 2. Sigmoid compression near extremes
if abs(adjusted) > 0.8:
    compressed = sign * (0.8 + 0.2 * (1 - exp(-excess * 2.5)))

# 3. Clamp to [-1.0, 1.0]
```

| Shocks | Stress Multiplier | Effect |
|--------|-------------------|--------|
| 1-3 | 1.0 | Pure additive (no amplification) |
| 4 | 1.15 | 15% amplification |
| 5 | 1.30 | 30% amplification |
| 8 | 1.75 | 75% amplification |

The sigmoid compression prevents runaway values: an impact of 1.5 after stress multiplication compresses to ~0.95 instead of clamping to 1.0.

### 22.9 Prediction Extraction & Auto-Resolution

After scenario completion, `_extract_and_store_predictions()` processes each branch's `specific_predictions`:

**Ticker normalization** — LLMs invent ticker symbols. Two mapping layers:
1. Market term → yfinance: `"brent" → "BZ=F"`, `"gold" → "GC=F"`, `"10-year" → "^TNX"`, `"high yield" → "HYG"` (19 mappings)
2. LLM-invented → yfinance: `"US10Y" → "^TNX"`, `"XAUUSD" → "GC=F"`, `"USOIL" → "CL=F"`, `"DXY" → "DX-Y.NYB"` (18 mappings)

**Time window parsing** — Converts free-text to absolute expiry:
- `"1-2 weeks"` → upper bound (2 weeks from now)
- `"5 business days"` → `days * 7/5` conversion
- `"1-3 months"` → `upper_bound * 30` days
- Returns `None` for unparseable strings

**Direction extraction** — Regex parses `above/below/over/under/exceeds/drops below` from prediction text when structured fields are missing.

Stored as `ScenarioPrediction` with: `scenario_id, branch_idx, branch_title, prediction_text, confidence, time_window, expires_at, ticker, threshold_value, threshold_direction, resolution_type (pending|market_resolved|unresolvable), resolved_at, actual_value, hit`.

### 22.10 Data Persistence

**Scenario** (PostgreSQL):
```
id, trigger, trigger_type, status (running|completed|error),
scenarios_json (JSONB — full output), research_summary, historical_parallels,
selected_branch_idx, simulation_result, error,
parent_scenario_id (FK → scenarios.id), parent_branch_idx,
created_at, finished_at
```

**ScenarioShock**: `id, scenario_id, branch_idx, node_id, shock_value [-1,1], reasoning, original_impact, created_at`

**ScenarioPrediction**: `id, scenario_id, branch_idx, branch_title, prediction_text, confidence, time_window, expires_at, ticker, threshold_value, threshold_direction, resolution_type, resolved_at, actual_value, hit, created_at`
- Indexed on `scenario_id` and pending predictions (`resolved_at IS NULL`)

**NodeSuggestion**: `id, scenario_id, branch_idx, suggested_id, suggested_label, suggested_type, description, reasoning, status (pending|accepted|rejected), created_at`

**EdgeSuggestion**: Stored only when both endpoints are existing graph nodes (FK constraint). Edges referencing suggested-only nodes are preserved in `scenarios_json` for frontend display.

### 22.11 WebSocket Broadcasting

**Progress** — Broadcast after every tool call:
```json
{"type": "scenario_progress", "data": {
  "scenario_id": 29, "round": 5, "max_rounds": 27,
  "phase": "generation", "total_tool_calls": 12
}}
```

**Completion** — Broadcast when scenario finishes:
```json
{"type": "scenario_complete", "data": {
  "scenario_id": 29, "status": "completed",
  "trigger": "...", "branch_count": 3,
  "branches": [{"title": "...", "probability": 0.55, "shock_count": 5}]
}}
```

Broadcasts are fire-and-forget via `asyncio.create_task()` with done-callbacks tracked in `_broadcast_tasks` set. Non-blocking — broadcast failures are logged at debug level.

### 22.12 Error Handling

- **API key validation** — Returns `Scenario(status="error")` immediately if no key configured
- **No news found** — Returns error scenario when auto-pick finds nothing
- **Sub-agent failure** — Logs exception, creates fresh session for error persistence (original session may be stale after long run), sets `status="error"` with truncated error text
- **Session staleness** — Fresh `async_session()` created for prediction extraction to avoid greenlet issues from the long-running agent session
- **Non-fatal failures** — Track record query failure, prediction extraction failure, broadcast failure — all logged as warnings, scenario still completes
- **Graph lock** — Not held during scenario generation (scenarios are read-only analysis). Lock only acquired when user applies shocks to graph.

### 22.13 Graph Evolution

When the Mapper identifies impacts that don't map to existing nodes:
- **NodeSuggestion** — `{suggested_id (snake_case), suggested_label, suggested_type, description, reasoning}`
- **EdgeSuggestion** — `{source_id, target_id, direction, reasoning}`
- Edge validation: edges can reference suggested nodes (for frontend display) but only edges between existing graph nodes are persisted to DB (FK constraint)

When user clicks "Apply + Evolve":
1. Hypothetical nodes added to in-memory graph with `hypothetical=True` flag
2. Tracked in `app_state.hypothetical_node_ids` and `app_state.hypothetical_edge_keys`
3. Rendered in purple on the 3D graph
4. Removed via `/reset-evolve` endpoint or "Clear" button

### 22.14 Cross-Branch Coherence Check

After Phase 3, `_check_branch_coherence()` computes word-set Jaccard similarity across branch `free_form_impacts`:

```python
for each pair (branch_i, branch_j):
    words_i = set(words from all free_form_impacts in branch_i)
    words_j = set(words from all free_form_impacts in branch_j)
    jaccard = |words_i ∩ words_j| / |words_i ∪ words_j|
    if jaccard > 0.8:
        log warning "branches are too similar"
```

Purely informational — logs warnings but does not block. Prevents the LLM from producing three variations of the same scenario.

### 22.15 Convergence Detection

The sub-agent runner tracks recent tool calls to prevent redundant searches:

```python
recent_calls: list[(tool_name, word_set)]  # last 8 calls
for each new tool call:
    if tool_name in {search_news, fetch_market_prices}:
        input_words = set(words from JSON input)
        for (prev_name, prev_words) in recent_calls:
            if prev_name == tool_name:
                jaccard = |input_words ∩ prev_words| / |input_words ∪ prev_words|
                if jaccard > 0.7:
                    return nudge: "Synthesize what you have and proceed to submission"
```

Only applied to `search_news` and `fetch_market_prices` — not to submission tools or validation tools.

### 22.16 Scenario Chaining

`POST /api/scenarios/{id}/chain` with `{branch_idx, follow_up_trigger}`:

1. Fetch parent scenario from DB
2. Extract parent branch: narrative, shocks (first 10), structural outcome
3. Build parent context string:
   ```
   The following scenario has ALREADY PLAYED OUT (treat as given):
   Parent trigger: ...
   Branch that materialized: ... (55% probability)
   Narrative: ...
   Shocks applied: [...]
   Structural outcome: ...
   Now analyze the FOLLOW-UP trigger: "..."
   ```
4. Create child `Scenario` with `parent_scenario_id` and `parent_branch_idx`
5. Launch `run_scenario_extrapolation()` in background with parent context prepended to Phase 1

Enables multi-step strategic planning: "If the ECB intervenes (Branch A), what happens when Italy holds elections 3 months later?"

### 22.17 Scenario Comparison (Frontend)

Compare mode in `ScenarioPanel.tsx`:

1. User clicks "Compare" toggle in header
2. Checkbox appears on each branch card (max 2 selections)
3. When 2 branches selected, `ComparisonView` renders:
   - Side-by-side titles + probabilities
   - Node impact table: `node_id | Branch A shock | Branch B shock | color`
   - Color coding: green (both positive), red (both negative), blue (opposite directions), gray (unique to one branch)
   - "Common Risk Nodes" section — nodes affected in both branches regardless of direction

State managed in Zustand store: `scenarioCompareMode`, `scenarioCompareBranches[]`.

### 22.18 Topic Diversity (Quick Triggers)

**Problem solved:** A single news query (`"markets economy geopolitics"`) caused the engine to always pick the dominant story (e.g., tariffs in 2026).

**Solution:** 12 domain-aligned queries run concurrently:

| # | Query | Domain |
|---|-------|--------|
| 1 | `geopolitics conflict war sanctions military escalation` | Geopolitical/military |
| 2 | `central banks monetary policy rate decision FOMC ECB BOJ` | Monetary policy |
| 3 | `tariffs trade war supply chain reshoring sanctions` | Trade/tariff |
| 4 | `AI disruption technology cyber attack outage systemic` | Technology |
| 5 | `energy crisis oil gas climate transition renewable` | Energy/climate |
| 6 | `bank failure credit crisis contagion default bankruptcy` | Financial stability |
| 7 | `pandemic outbreak virus health emergency supply chain` | Health |
| 8 | `labor shortage strike immigration wage automation` | Labor/demographics |
| 9 | `government debt fiscal deficit downgrade sovereign crisis` | Sovereign debt |
| 10 | `housing market mortgage commercial real estate crisis` | Real estate |
| 11 | `China economy emerging markets currency crisis capital flight` | EM/China |
| 12 | `food prices agriculture drought famine water crisis` | Food/agriculture |

3 articles per query → ~36 headlines, deduplicated by title prefix (first 50 chars). LLM picks top 5 with explicit diversity mandate: "Do NOT pick multiple events from the same domain." Recent scenario triggers (last 5) injected as avoidance list.

`_auto_pick_trigger()` uses `random.choice(triggers[:5])` instead of always picking #1, ensuring different topics across multiple auto-generated scenarios.

### 22.19 Output Schema

Complete `scenarios_json` structure stored in the `Scenario` JSONB column:

```json
{
  "research_summary": "...",
  "historical_parallels": "...",
  "branches": [
    {
      "title": "Orderly Repricing with ECB Backstop",
      "probability": 0.55,
      "probability_reasoning": "Most likely as ECB has proven intervention capability...",
      "narrative": "A sovereign downgrade cascade begins...",
      "causal_chain": [
        "TRIGGER: Italy faces credit rating downgrade...",
        "PATH A (Financial Markets, Mark-to-Market Cascade):",
        "IMMEDIATE (0-24h): European bank stocks gap down 8-12%...",
        "-> SHORT-TERM (1-7d): Banks report mark-to-market losses...",
        "-> MEDIUM-TERM (1-4w): ECB announces conditional program...",
        "-> STRUCTURAL (1-6m): Banking sector consolidation...",
        "CROSS-DOMAIN SPILLOVER: Financial stress triggers..."
      ],
      "structural_outcome": "Permanent repricing of eurozone sovereign risk...",
      "time_horizon": "weeks",
      "invalidation": "ECB legally constrained from intervention...",
      "key_assumption": "ECB maintains credibility despite inflation...",
      "free_form_impacts": [
        "European bank equity valuations drop 15-25%",
        "Credit spreads widen 75-100bps across eurozone periphery"
      ],
      "specific_predictions": [
        {
          "prediction": "European financials falls 15-25%",
          "confidence": 0.8,
          "time_window": "2-4 weeks",
          "ticker": "SX7E",
          "direction": "below",
          "threshold": 85
        }
      ],
      "shocks": [
        {
          "node_id": "financials_sector",
          "shock_value": -0.5,
          "reasoning": "European bank equity valuations drop 15-25%...",
          "original_impact": "European bank equity valuations drop 15-25%"
        }
      ],
      "node_suggestions": [
        {
          "suggested_id": "european_bank_equity",
          "suggested_label": "European Bank Equity",
          "suggested_type": "equities",
          "description": "European banking sector equity index (STOXX Banks)",
          "reasoning": "Graph only has US Financials Sector (XLF)"
        }
      ],
      "edge_suggestions": [
        {
          "source_id": "eurusd",
          "target_id": "financials_sector",
          "direction": "positive",
          "reasoning": "EUR weakness coincides with banking stress"
        }
      ]
    }
  ]
}
```

### 22.20 Constants & Thresholds

| Constant | Value | Purpose |
|----------|-------|---------|
| `PHASE1_ROUNDS` | 4 | Researcher round budget |
| `PHASE2_ROUNDS` | 5 | Historian round budget |
| `PHASE3_ROUNDS` | 12 | Strategist round budget (core value) |
| `PHASE4_ROUNDS` | 6 | Mapper round budget |
| `MAX_ROUNDS` | 27 | Total budget across all phases |
| `SCENARIO_MAX_TOKENS` | 24,576 | LLM output token limit (3x main agent) |
| Extreme sentiment threshold | ±0.7 | Flags as fragility point in vulnerability context |
| High-weight edge threshold | >0.5 | Effective weight for "strongest causal links" |
| Shock value clamping | [-1.0, 1.0] | Min/max during persistence |
| Preview propagation top-N | 15 | Affected nodes returned in preview |
| Stress multiplier onset | >3 shocks | Non-linear amplification begins |
| Stress multiplier rate | +0.15 per shock | Linear scaling above threshold |
| Sigmoid compression onset | |impact| > 0.8 | Diminishing returns begin |
| Convergence Jaccard threshold | >0.7 | Triggers redundant search nudge |
| Coherence Jaccard threshold | >0.8 | Flags branch pair as too similar |
| Prediction calibration buckets | 0.3, 0.6 | Low/medium/high confidence boundaries |
| Quick trigger queries | 12 | Domain-aligned news scan breadth |
| Quick trigger results | 5 | LLM picks per scan (was 3) |
| Recent trigger avoidance | 5 | Past scenarios to inject as "avoid" |

### 22.21 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/scenarios` | Trigger scenario generation (background task) |
| GET | `/api/scenarios?limit=20` | List recent scenarios with branch counts |
| GET | `/api/scenarios/{id}` | Get full scenario with branches, shocks, suggestions |
| POST | `/api/scenarios/{id}/apply` | Apply branch shocks to graph (non-linear multi-shock, read-only) |
| POST | `/api/scenarios/{id}/chain` | Chain follow-up scenario from parent branch outcome |
| POST | `/api/scenarios/{id}/evolve` | Add hypothetical nodes/edges from branch suggestions |
| POST | `/api/scenarios/reset-evolve` | Remove all hypothetical nodes/edges |
| GET | `/api/scenarios/quick-triggers` | Get 5 diverse scenario-worthy events from 12-domain news scan |
| GET | `/api/scenarios/hypothetical` | Get current hypothetical node/edge state |

### 22.22 Key Files

| File | Lines | Role |
|------|-------|------|
| `backend/app/agent/scenario_agent.py` | ~1,600 | 4-phase orchestrator, sub-agent runner, tool dispatch, prediction extraction, track record, topic diversity, convergence detection, coherence check |
| `backend/app/agent/scenario_prompts.py` | ~1,050 | System prompts (Researcher, Historian, Strategist, Mapper), phase user prompts, calibration anchors, domain escalation frameworks, quick triggers prompt |
| `backend/app/agent/scenario_schemas.py` | ~460 | Tool schemas: `get_graph_topology`, `get_economic_calendar`, `fetch_options_summary`, `fetch_historical_prices`, `preview_propagation`, 4 submission tools, per-phase tool lists |
| `backend/app/data_pipeline/calendar.py` | ~190 | Economic calendar: FOMC dates 2025-2027, recurring release rules, FRED releases API integration |
| `backend/app/data_pipeline/market.py` | ~260 | `fetch_options_summary()`: IV, put/call ratio, key strikes, term structure via yfinance |
| `backend/app/graph_engine/propagation.py` | ~200 | `merge_multi_shock_impacts()`: stress multiplier + sigmoid compression + per-shock propagation |
| `backend/app/models/scenarios.py` | ~82 | `Scenario` (+ parent chaining), `ScenarioShock`, `ScenarioPrediction`, `NodeSuggestion` |
| `backend/app/api/routes_scenario.py` | ~590 | API endpoints, `_extract_branches()`, chain endpoint, evolve/reset endpoints |
| `frontend/src/components/ScenarioPanel.tsx` | ~700 | Scenario UI: trigger input, quick triggers, branch cards, shock editor, comparison view, chain UI, export |

---

## 23. Limitations & Known Issues

This section documents the system's known limitations honestly — both theoretical and practical.

### "Causal" Is Used Loosely

The edges represent **directed correlational assumptions** grounded in macro finance domain knowledge, not rigorously identified causal relationships. There is no Granger causality testing, no instrumental variables, and no DAG validation. The edges encode "when A moves, B tends to move in this direction because of this mechanism" — which is how macro analysts actually think, but is not causal in the econometric sense.

**Why this is acceptable:** The system is a reasoning tool, not a statistical proof. The edges represent well-known macro transmission channels (e.g., "higher rates → lower equity valuations") that have theoretical backing. The dynamic weight learning adapts these assumptions to empirical data, and edge muting handles cases where the empirical relationship temporarily breaks down.

### One-Size-Fits-All Sentiment Decay

All nodes use the same 24-hour half-life for sentiment decay. This is clearly wrong for nodes with different data frequencies:

- **FRED macro data** (GDP, CPI, unemployment) updates monthly or quarterly — a 24h decay means the signal is nearly gone before the next data point arrives
- **Market prices** (yfinance) update hourly — 24h decay is appropriate
- **News sentiment** can be ephemeral — 24h may even be too long

A better approach would be per-node-type decay rates, but this adds complexity. For now, the 24h half-life is a reasonable middle ground that prevents stale signals from dominating.

### Pearson Correlation Assumptions

Dynamic weight learning uses Pearson correlation, which assumes linear relationships. Financial relationships are often nonlinear (e.g., VIX has a convex relationship with SPY). Spearman rank correlation would be more robust to nonlinearity but would lose magnitude information.

Additionally, `correlation_min_data_points = 3` is very low. With only 3 data points, a Pearson correlation is statistically unreliable. In practice, most node pairs accumulate more observations over time, but newly-deployed instances may produce noisy dynamic weights.

### Signal Amplification Through Interference

When a node is reachable by multiple paths, signals are summed (constructive interference). Two paths each contributing +0.6 produce a total impact of +1.0 (clamped). This means the graph can produce impact signals **stronger than the original shock** at convergence points. This is a deliberate design choice — it models how multiple causal channels can compound — but users should be aware that high-centrality nodes may show amplified signals.

### Cold Start Problem

On first deployment with no historical observations:
- **Anomaly detection** requires minimum 5 observations per node — no anomalies will be detected until sufficient data is collected
- **Dynamic weights** default to base weights (static expert opinion) until enough observations exist for correlation analysis
- **Backtesting** requires historical sentiment-vs-return data that doesn't exist yet
- **Agent memory** has no previous runs to reference for self-calibration

The system bootstraps over time as the agent runs analyses and accumulates observations. Running a few manual "Full Analysis" cycles builds the initial observation history.

### LLM Cost

A full analysis of all 52 nodes typically uses **30-60K tokens** depending on the LLM and how many tools the agent calls. With Claude Sonnet, this is roughly $0.10-0.20 per run. With scheduled jobs enabled (agent every 6h + regime narratives), expect ~$1-2/day in API costs. Deep dives on single nodes are much cheaper (~5-10K tokens).

### Reddit Keyword Matching

Posts are matched to nodes via naive substring matching. "war" matches "software" and "warrant". NLP entity extraction would fix this but adds complexity.

### Not a Trading Signal

The system is designed for **macro analysis on daily-to-weekly timescales**. FRED data may be weeks old when analyzed. yfinance has a 15-minute delay on the free tier. The value is in causal reasoning and cross-node consistency, not in speed or precision.

### Why Not a GNN / VAR / Diffusion Model?

- **GNNs** could learn edge weights from data, but require large training datasets of labeled macro regimes — which don't exist in sufficient quantity. The handcrafted BFS approach is interpretable and works with expert knowledge from day one.
- **VAR/VECM models** handle feedback loops and contemporaneous effects better, but are harder to explain to users. BFS with depth limits gives predictable, interpretable results where each hop has a clear meaning.
- **Diffusion models** converge to steady states, which obscures the "trace the causal chain" intuition that makes the tool useful for macro analysts.

---

## 24. FAQ & Design Rationale

**Q: Why not just use a correlation matrix?**
Correlation is symmetric and undirected. This graph has directed causal edges — "rising CPI → higher rate expectations → lower equities" is a chain with direction, sign, and magnitude. Correlation can't capture that.

**Q: Is the agent accurate?**
It depends on the LLM, data freshness, and graph structure. The built-in prediction tracking measures accuracy over time. Treat it as a research tool, not a signal. The self-calibration mechanism adjusts confidence when hit rate is low.

**Q: Why 0.6/0.4 base/dynamic weight split?**
Domain knowledge (base weights) should dominate because causal mechanisms don't change quickly. Dynamic weights provide adaptation but shouldn't override expert knowledge — a temporary correlation anomaly shouldn't rewire the graph.

**Q: Why mute edges instead of flipping direction?**
Edge flipping caused cascading errors in early versions. If "fed_funds_rate → sp500 (NEGATIVE)" temporarily showed positive correlation (e.g., both rising in a bull market), flipping it to POSITIVE would break the fundamental causal logic. Muting reduces influence without destroying structure.

**Q: Why 2σ for anomaly detection?**
Standard choice for outlier detection. 1σ would trigger too often (32% of observations). 3σ would miss important moves. 2σ captures ~5% of observations — enough to be unusual without being rare.

**Q: Why exponential decay with 24h half-life?**
Markets move fast. A sentiment observation from a week ago is nearly irrelevant. 24h half-life means yesterday's signal is at 50%, last week's is at ~1.5%. This naturally fades stale data without requiring manual cleanup.

**Q: Why BFS instead of PageRank or diffusion?**
BFS with depth limits gives predictable, interpretable results. Each hop has a clear physical meaning (1st-order effect, 2nd-order effect, etc.). Diffusion models are harder to explain to users and don't have the same "trace the causal chain" intuition.

**Q: Can I add my own nodes and edges?**
Yes — edit `backend/app/graph_engine/topology.py`. The topology learning feature can also suggest new edges from correlation patterns. The UI has an "Evolve Graph" panel for accepting/rejecting LLM-suggested edges.

**Q: Why is the scheduler disabled by default?**
Each agent run costs LLM tokens. With 9 background jobs running continuously, API costs add up fast. Disabled by default lets users explore the tool manually before opting into automated data fetching.

**Q: What's the known limitation of Reddit keyword matching?**
Naive substring matching. "war" matches "software" and "warrant". NLP entity extraction would fix this but adds complexity. It's on the roadmap.

**Q: How does the confidence breakdown work?**
Instead of a single confidence number, the agent provides three components:
- **Data freshness** (30% weight): How recent is the data?
- **Source agreement** (40% weight): Do multiple sources agree?
- **Signal strength** (30% weight): How clear is the signal?
The weighted sum produces the final confidence. This is more interpretable than a raw number and encourages the agent to think about *why* it's confident.
