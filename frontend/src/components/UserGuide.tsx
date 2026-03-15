"use client";

import { useState } from "react";

const sections = [
  {
    id: "overview",
    title: "Overview",
    content:
      "This tool models the financial world as an interconnected causal graph. 52 nodes represent financial products and macro factors. 117 directed edges represent causal relationships. An AI agent autonomously analyzes data and propagates sentiment signals through the network.",
  },
  {
    id: "sentiment",
    title: "Sentiment & Colors",
    content:
      "Sentiment ranges from -1 (bearish) to +1 (bullish). Confidence (0\u2013100%) indicates how certain the agent is. Colors: red = bearish, gray = neutral, green = bullish. Node size reflects systemic importance (eigenvector centrality). Anomalous nodes (2\u03c3 moves) glow yellow and appear 1.5\u00d7 larger.",
  },
  {
    id: "whatif",
    title: "What-If Simulator",
    content:
      "Click any node, drag the \"What-If Shock\" slider to a hypothetical sentiment, and click Simulate. The shock propagates through causal edges with exponential decay (30% per hop, max 4 hops). Affected nodes glow green (positive impact) or red (negative impact). The source node pulses orange. Unaffected nodes dim out. An impact report panel shows every affected node with magnitude, hop count, and the full causal path. Click any node in the report to fly the camera there. The simulation is read-only \u2014 it does not change the actual graph.",
  },
  {
    id: "deepdive",
    title: "Agent & Deep Dive",
    content:
      "Click \"Run Full Analysis\" to analyze all 52 nodes, or click a node and hit \"Deep Dive\" for focused single-node analysis. The agent runs a three-phase loop: (1) Planning \u2014 inspects anomalies, stale nodes, and regime state to decide priorities. (2) Analysis \u2014 fetches data from FRED, yfinance, news, Reddit, and SEC, then writes sentiment with decomposed confidence. (3) Validation \u2014 checks for cross-node contradictions and records falsifiable predictions. Progress is shown in real-time via WebSocket.",
  },
  {
    id: "annotations",
    title: "Analyst Notes",
    content:
      "Click any node and scroll to \"Analyst Notes\" to add your own reasoning. Notes are timestamped and persist in the database across sessions and restarts. Pin important notes to keep them at the top. Delete stale notes when they no longer apply. This is the \"second brain\" feature \u2014 the tool remembers what you think, not just what the data says.",
  },
  {
    id: "regime",
    title: "Regime & Narrator",
    content:
      "The system classifies the market as Risk-On, Risk-Off, or Transitioning based on 8 bellwether nodes (VIX, credit spreads, S&P 500, yield curve, gold, dollar, put/call ratio). In Risk-Off, bearish signals propagate faster. In Risk-On, bullish signals flow further. Click the regime badge in the top-left to expand it, then click \"Generate Narrative\" for an LLM-written macro summary. Top driver chips let you fly the camera to the relevant node.",
  },
  {
    id: "predictions",
    title: "Predictions",
    content:
      "The agent records 2\u20133 high-conviction predictions during each validation phase. Each prediction has a direction (bullish/bearish/neutral), a target sentiment, a time horizon (default 7 days), and reasoning. Expired predictions are auto-resolved by comparing against actual sentiment. Open the \"Predictions\" panel in the bottom toolbar to see pending predictions (yellow), hits (green), and misses (red), along with the overall hit rate and magnitude score.",
  },
  {
    id: "features",
    title: "More Features",
    items: [
      { label: "Time Travel", desc: "Replay graph state over the past 7 days with 1-hour steps" },
      { label: "Clustered Layout", desc: "Toggle to group nodes spatially by category" },
      { label: "Portfolio", desc: "Add your positions to highlight relevant nodes on the graph" },
      { label: "Evolve Graph", desc: "AI suggests new causal edges based on empirical correlations" },
      { label: "Agent Log", desc: "Inspect past analysis runs with full tool call details" },
      { label: "Backtest", desc: "See predictive power (hit rate, correlation) of sentiment vs returns" },
      { label: "Node Locator", desc: "Search and sort all 52 nodes, click to fly the camera there" },
      { label: "LLM Switch", desc: "Toggle between Claude and GPT in the top-left panel" },
    ],
  },
  {
    id: "learnmore",
    title: "Learn More",
    content:
      "For a deep dive into every algorithm, formula, and design decision, read the Technical Manual: docs/TECHNICAL_MANUAL.md in the project repository. It covers signal propagation, dynamic weight learning, anomaly detection, regime detection, agent architecture, prediction tracking, and more.",
  },
] as const;

type Section = (typeof sections)[number];

export default function UserGuide() {
  const [open, setOpen] = useState(false);
  const [activeSection, setActiveSection] = useState<string>(sections[0].id);

  const active = sections.find((s) => s.id === activeSection) as Section;

  return (
    <>
      {/* Trigger button */}
      <button
        onClick={() => setOpen(true)}
        className="fixed top-4 right-[22rem] z-20 w-8 h-8 rounded-full bg-gray-900/90 border border-gray-700 text-gray-300 hover:text-white hover:border-gray-500 flex items-center justify-center text-sm font-semibold backdrop-blur transition-colors"
        aria-label="Open user guide"
      >
        ?
      </button>

      {/* Modal overlay */}
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setOpen(false)}
        >
          <div
            className="relative w-full max-w-lg max-h-[80vh] mx-4 bg-gray-900 border border-gray-700 rounded-lg shadow-2xl flex flex-col overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-700">
              <h2 className="text-lg font-semibold text-white">User Guide</h2>
              <button
                onClick={() => setOpen(false)}
                className="text-gray-400 hover:text-white text-xl leading-none transition-colors"
                aria-label="Close guide"
              >
                &times;
              </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 px-5 pt-3 pb-1 overflow-x-auto border-b border-gray-700 scrollbar-thin">
              {sections.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setActiveSection(s.id)}
                  className={`whitespace-nowrap px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                    activeSection === s.id
                      ? "bg-gray-700 text-white"
                      : "text-gray-400 hover:text-gray-200 hover:bg-gray-800"
                  }`}
                >
                  {s.title}
                </button>
              ))}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto px-5 py-4 text-sm leading-relaxed text-gray-300">
              <h3 className="text-white font-semibold mb-2">{active.title}</h3>

              {"content" in active && <p>{active.content}</p>}

              {"items" in active && (
                <ul className="space-y-3">
                  {active.items.map((item) => (
                    <li key={item.label}>
                      <span className="text-white font-medium">
                        {item.label}
                      </span>
                      <span className="text-gray-400"> &mdash; </span>
                      {item.desc}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
