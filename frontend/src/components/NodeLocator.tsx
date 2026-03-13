"use client";

import { useMemo, useState } from "react";
import { useGraphStore } from "@/hooks/useGraphData";
import { sentimentToColor } from "@/lib/graphTransforms";

type SortMode = "category" | "confidence" | "sentiment";

const CATEGORY_LABELS: Record<string, string> = {
  macro: "Macro",
  monetary_policy: "Monetary Policy",
  geopolitics: "Geopolitics",
  rates_credit: "Rates & Credit",
  volatility: "Volatility",
  commodities: "Commodities",
  equities: "Equities",
  equity_fundamentals: "Equity Fundamentals",
  currencies: "Currencies",
  flows_sentiment: "Flows & Sentiment",
  global: "Global",
};

const CATEGORY_ORDER = Object.keys(CATEGORY_LABELS);

export default function NodeLocator() {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [sortMode, setSortMode] = useState<SortMode>("category");
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());
  const nodes = useGraphStore((s) => s.nodes);
  const focusNode = useGraphStore((s) => s.focusNode);

  const filtered = useMemo(() => {
    if (!search) return nodes;
    const q = search.toLowerCase();
    return nodes.filter(
      (n) => n.label.toLowerCase().includes(q) || n.id.toLowerCase().includes(q)
    );
  }, [nodes, search]);

  const grouped = useMemo(() => {
    const groups: Record<string, typeof nodes> = {};
    for (const node of filtered) {
      const cat = node.nodeType || "other";
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(node);
    }
    // Sort within each group by label
    for (const key of Object.keys(groups)) {
      groups[key].sort((a, b) => a.label.localeCompare(b.label));
    }
    return groups;
  }, [filtered]);

  const sortedFlat = useMemo(() => {
    if (sortMode === "confidence") {
      return [...filtered].sort((a, b) => b.confidence - a.confidence);
    }
    if (sortMode === "sentiment") {
      return [...filtered].sort(
        (a, b) => Math.abs(b.sentiment) - Math.abs(a.sentiment)
      );
    }
    return [];
  }, [filtered, sortMode]);

  const toggleCategory = (cat: string) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  };

  const renderNode = (node: typeof nodes[0]) => (
    <button
      key={node.id}
      onClick={() => focusNode(node.id)}
      className="w-full flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-700/50 transition-colors text-left"
    >
      <span
        className="w-1.5 h-1.5 rounded-full flex-shrink-0"
        style={{ backgroundColor: sentimentToColor(node.sentiment) }}
      />
      <span className="text-xs text-gray-300 truncate flex-1">
        {node.label}
      </span>
      <span
        className="text-[10px] font-mono flex-shrink-0"
        style={{ color: sentimentToColor(node.sentiment) }}
      >
        {node.sentiment > 0 ? "+" : ""}
        {node.sentiment.toFixed(2)}
      </span>
      <span className="text-[10px] text-gray-500 flex-shrink-0">
        {(node.confidence * 100).toFixed(0)}%
      </span>
    </button>
  );

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="bg-gray-800/90 backdrop-blur border border-gray-700 rounded-lg px-3 py-2 text-xs text-gray-300 hover:text-white transition-colors"
      >
        {open ? "Hide" : "Nodes"}
        {!open && (
          <span className="ml-1.5 bg-gray-600 rounded-full px-1.5 py-0.5 text-[10px]">
            {nodes.length}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-72 max-h-[60vh] bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-xl z-10 overflow-hidden flex flex-col">
          <div className="p-3 border-b border-gray-700 space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Node Locator</h3>
              <span className="text-[10px] text-gray-500">{filtered.length} nodes</span>
            </div>

            {/* Search */}
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search nodes..."
              className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500"
            />

            {/* Sort mode */}
            <div className="flex gap-1">
              {(["category", "confidence", "sentiment"] as SortMode[]).map(
                (mode) => (
                  <button
                    key={mode}
                    onClick={() => setSortMode(mode)}
                    className={`flex-1 text-[10px] py-1 rounded transition-colors ${
                      sortMode === mode
                        ? "bg-blue-600 text-white"
                        : "bg-gray-700 text-gray-400 hover:text-gray-200"
                    }`}
                  >
                    {mode === "category"
                      ? "Category"
                      : mode === "confidence"
                        ? "Confidence"
                        : "Sentiment"}
                  </button>
                )
              )}
            </div>
          </div>

          <div className="overflow-y-auto flex-1 p-1.5">
            {sortMode === "category" ? (
              // Grouped by category
              CATEGORY_ORDER.filter((cat) => grouped[cat]?.length).map(
                (cat) => (
                  <div key={cat} className="mb-1">
                    <button
                      onClick={() => toggleCategory(cat)}
                      className="w-full flex items-center gap-1.5 px-2 py-1 text-xs font-semibold text-gray-400 hover:text-white rounded hover:bg-gray-800 transition-colors"
                    >
                      <span className="text-[10px]">
                        {collapsed.has(cat) ? "▶" : "▼"}
                      </span>
                      {CATEGORY_LABELS[cat] || cat}
                      <span className="text-[10px] text-gray-600 ml-auto">
                        {grouped[cat].length}
                      </span>
                    </button>
                    {!collapsed.has(cat) && (
                      <div className="ml-2">
                        {grouped[cat].map(renderNode)}
                      </div>
                    )}
                  </div>
                )
              )
            ) : (
              // Flat sorted list
              <div>
                {sortedFlat.map((node, i) => (
                  <div key={node.id} className="flex items-center">
                    <span className="text-[10px] text-gray-600 w-5 text-right mr-1 flex-shrink-0">
                      {i + 1}
                    </span>
                    {renderNode(node)}
                  </div>
                ))}
              </div>
            )}

            {filtered.length === 0 && (
              <div className="text-xs text-gray-500 text-center py-4">
                No nodes match &quot;{search}&quot;
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
