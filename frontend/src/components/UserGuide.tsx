"use client";

import { useState } from "react";

const sections = [
  {
    id: "overview",
    title: "Overview",
    content:
      "This tool models the financial world as an interconnected causal graph. Nodes represent financial products and macro factors. Edges represent causal relationships. An AI agent autonomously analyzes data and propagates sentiment signals through the network.",
  },
  {
    id: "sentiment",
    title: "Sentiment & Confidence",
    content:
      "Sentiment ranges from -1 (bearish) to +1 (bullish). Confidence (0\u2013100%) indicates how certain the agent is. Colors: red = bearish, gray = neutral, green = bullish. Node size reflects systemic importance (centrality).",
  },
  {
    id: "deepdive",
    title: "Deep Dive",
    content:
      'Click any node to see its detail panel. Click "Deep Dive" to trigger a focused Claude analysis on that specific node. The agent will fetch fresh data (FRED, news, market prices, SEC filings) and update the sentiment.',
  },
  {
    id: "propagation",
    title: "Propagation",
    content:
      "When sentiment updates on a node, the signal propagates through causal edges. Positive edges amplify the signal in the same direction. Negative edges invert it. Signal decays with each hop (max 4 hops). Edge weight controls propagation strength.",
  },
  {
    id: "regime",
    title: "Market Regime",
    content:
      "The system classifies the market as Risk-On, Risk-Off, or Transitioning based on bellwether nodes (VIX, credit spreads, S&P 500, etc.). In Risk-Off, bearish signals propagate faster. In Risk-On, bullish signals propagate faster.",
  },
  {
    id: "features",
    title: "Features",
    items: [
      { label: "Time Travel", desc: "Replay graph state over the past 7 days" },
      {
        label: "Clustered Layout",
        desc: "Group nodes by type (macro, equities, commodities, etc.)",
      },
      {
        label: "Portfolio",
        desc: "Add your positions to highlight relevant nodes",
      },
      {
        label: "Evolve Graph",
        desc: "Claude suggests new causal edges based on empirical correlations",
      },
      {
        label: "Agent Log",
        desc: "View past analysis runs, tool calls, and summaries",
      },
      {
        label: "Backtest",
        desc: "See predictive power (hit rate, correlation) of sentiment vs returns",
      },
    ],
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
