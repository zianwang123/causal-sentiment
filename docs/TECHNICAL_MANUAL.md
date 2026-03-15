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
17. [FAQ & Design Rationale](#17-faq--design-rationale)

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
  ├── AI Agent (Claude/GPT, 3-phase loop, 11 tools)
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

**Fed Funds Rate (6 outgoing edges):**

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

The agent runs a structured **Plan → Analyze → Validate** loop with a hard limit of 25 rounds total.

| Phase | Rounds | Purpose |
|-------|--------|---------|
| **Planning** | 0-2 (3 rounds) | Inspect graph state, decide priorities |
| **Analysis** | 3-19 (17 rounds) | Fetch data, write sentiment |
| **Validation** | 20-24 (5 rounds) | Self-critique, check contradictions, record predictions |

### Phase 1: Planning

The agent calls `get_analysis_context` to see:
- **Anomalies:** Which nodes have 2σ moves
- **Stale nodes:** Which nodes haven't been updated in 24+ hours
- **Regime:** Current risk-on/off state
- **Priority ranking:** `score = centrality × 0.4 + is_stale × 0.3 + is_anomalous × 0.3`

The agent also calls `get_agent_track_record` to review its past prediction accuracy and calibrate confidence.

### Phase 2: Analysis

The agent fetches data and writes sentiment. For each node it analyzes:
1. Fetch relevant data (FRED series, market prices, news, Reddit, SEC filings)
2. Call `get_graph_neighborhood` to understand the node's causal context
3. Call `update_sentiment_signal` with:
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

Between runs, the agent receives:
- **Previous 3 run summaries** (truncated to 300 chars each) with time-since labels
- **Prediction track record** (hit rate, recent outcomes, calibration warning if <50%)

### 11 Tools

| Tool | Purpose | Data Source |
|------|---------|-------------|
| `fetch_fred_data` | Macro data (rates, CPI, GDP, etc.) | FRED API |
| `fetch_market_prices` | ETF/futures prices and % changes | yfinance |
| `search_news` | Financial headlines | NewsAPI |
| `search_reddit` | Social sentiment | Reddit (asyncpraw) |
| `fetch_sec_filings` | Earnings, revenue, EPS | SEC EDGAR |
| `update_sentiment_signal` | Write sentiment to a node | Internal |
| `get_graph_neighborhood` | Inspect node + neighbors | Internal |
| `get_analysis_context` | Graph-wide state summary | Internal |
| `validate_consistency` | Check for contradictions | Internal |
| `record_prediction` | Store falsifiable prediction | Internal |
| `get_agent_track_record` | Review past accuracy | Internal |

---

## 9. Data Pipeline

### Scheduled Jobs (All Disabled by Default)

Set `SCHEDULER_ENABLED=true` in `.env` to enable.

| Job | Frequency | What It Does |
|-----|-----------|--------------|
| FRED fetch | Every 4 hours | Fetches 13 macro series, stores as raw observations |
| Market fetch | Every 1 hour | Fetches 13 tickers via yfinance |
| Reddit fetch | Every 2 hours | Fetches from r/wallstreetbets, r/economics, r/stocks |
| SEC EDGAR fetch | Daily at 6 AM UTC | Fetches financials for 10 tracked companies |
| Agent analysis | Every 6 hours | Runs agent on nodes with fresh data since last run |
| Weight recalculation | Daily at 3 AM UTC | Recomputes dynamic weights from Pearson correlations |
| Regime check | Every 2 hours | Detects regime, broadcasts via WebSocket |
| Sentiment decay | Daily at 2 AM UTC | Applies 24h half-life exponential decay |
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

### Reddit Keyword Matching

Posts are matched to nodes via naive substring matching (case-insensitive). Examples:
- "fed" or "federal reserve" → fed_funds_rate
- "inflation" or "cpi" → us_cpi_yoy
- "oil" or "crude" → wti_crude

**Known limitation:** "war" matches "software" and "warrant". NLP entity extraction would be better.

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

Centrality ranges [0, 1], so node size ranges [2, 100]. Higher centrality = bigger node = more connected/important.

### Cluster Layout

When enabled, nodes are pulled toward their category's centroid position using a custom D3 force:

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

Force strength: `alpha × 0.3` (where alpha is D3's cooling parameter).

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

| Event | Direction | Data |
|-------|-----------|------|
| `graph_update` | Server → Client | Full graph state |
| `agent_progress` | Server → Client | Round, phase, tool calls |
| `agent_complete` | Server → Client | Run ID, status, summary |
| `regime_update` | Server → Client | Regime state, confidence |
| `ping` | Client → Server | Heartbeat |
| `pong` | Server → Client | Heartbeat response |

---

## 16. Configuration Reference

All settings in `backend/app/config.py`, read from `.env`:

| Setting | Default | Description |
|---------|---------|-------------|
| `ANTHROPIC_API_KEY` | "" | Required for Claude agent |
| `OPENAI_API_KEY` | "" | Required for GPT agent |
| `LLM_PROVIDER` | "anthropic" | Which LLM to use |
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

## 17. FAQ & Design Rationale

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
Each agent run costs LLM tokens. With 7 background jobs running continuously, API costs add up fast. Disabled by default lets users explore the tool manually before opting into automated data fetching.

**Q: What's the known limitation of Reddit keyword matching?**
Naive substring matching. "war" matches "software" and "warrant". NLP entity extraction would fix this but adds complexity. It's on the roadmap.

**Q: How does the confidence breakdown work?**
Instead of a single confidence number, the agent provides three components:
- **Data freshness** (30% weight): How recent is the data?
- **Source agreement** (40% weight): Do multiple sources agree?
- **Signal strength** (30% weight): How clear is the signal?
The weighted sum produces the final confidence. This is more interpretable than a raw number and encourages the agent to think about *why* it's confident.
