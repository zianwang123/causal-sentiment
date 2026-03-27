"use client";

import { useMemo, useState } from "react";
import { useGraphStore } from "@/hooks/useGraphData";
import type { ForceGraphNode } from "@/types/graph";

const CATEGORY_ORDER = [
  "macro", "monetary_policy", "fiscal_policy", "rates_credit", "financial_system",
  "money_markets", "volatility", "commodities", "equities", "equity_fundamentals",
  "currencies", "flows_sentiment", "housing", "supply_chain", "global",
  "geopolitics", "private_credit",
];

const CATEGORY_SHORT: Record<string, string> = {
  macro: "Macro",
  monetary_policy: "MonPol",
  fiscal_policy: "Fiscal",
  rates_credit: "Rates",
  financial_system: "FinSys",
  money_markets: "MktMny",
  volatility: "Vol",
  commodities: "Commod",
  equities: "Equity",
  equity_fundamentals: "EqFund",
  currencies: "FX",
  flows_sentiment: "Flows",
  housing: "Housing",
  supply_chain: "Supply",
  global: "Global",
  geopolitics: "GeoPol",
  private_credit: "PvtCrd",
};

export default function CategoryMatrix({ onClose }: { onClose: () => void }) {
  const nodes = useGraphStore((s) => s.nodes);
  const links = useGraphStore((s) => s.links);
  const [hoveredCell, setHoveredCell] = useState<[string, string] | null>(null);

  // Build node-to-category mapping
  const nodeCat = useMemo(() => {
    const map = new Map<string, string>();
    nodes.forEach((n) => map.set(n.id, n.nodeType));
    return map;
  }, [nodes]);

  // Build matrix: category → category → { count, totalWeight }
  const matrix = useMemo(() => {
    const m: Record<string, Record<string, { count: number; weight: number }>> = {};
    for (const c of CATEGORY_ORDER) {
      m[c] = {};
      for (const c2 of CATEGORY_ORDER) {
        m[c][c2] = { count: 0, weight: 0 };
      }
    }
    for (const link of links) {
      const srcId = typeof link.source === "object" ? (link.source as ForceGraphNode).id : link.source;
      const tgtId = typeof link.target === "object" ? (link.target as ForceGraphNode).id : link.target;
      const srcCat = nodeCat.get(srcId);
      const tgtCat = nodeCat.get(tgtId);
      if (srcCat && tgtCat && m[srcCat]?.[tgtCat]) {
        m[srcCat][tgtCat].count += 1;
        m[srcCat][tgtCat].weight += link.weight ?? 0.5;
      }
    }
    return m;
  }, [links, nodeCat]);

  // Find max count for color scaling
  const maxCount = useMemo(() => {
    let max = 1;
    for (const src of CATEGORY_ORDER) {
      for (const tgt of CATEGORY_ORDER) {
        if (matrix[src]?.[tgt]?.count > max) max = matrix[src][tgt].count;
      }
    }
    return max;
  }, [matrix]);

  const handleCellClick = (src: string, tgt: string) => {
    const cell = matrix[src]?.[tgt];
    if (!cell || cell.count === 0) return;
    // Filter graph to show only edges between these two categories
    useGraphStore.setState({ edgeDisplayMode: "all", edgeWeightThreshold: 0 });
    // Focus camera on a node in the source category
    const srcNode = nodes.find((n) => n.nodeType === src);
    if (srcNode) {
      useGraphStore.getState().focusNode(srcNode.id);
    }
  };

  const cellSize = 36;

  return (
    <div className="absolute inset-0 z-30 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div
        className="bg-gray-900 border border-gray-600 rounded-lg p-4 shadow-2xl overflow-auto max-w-[95vw] max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-sm font-bold text-white">Category Edge Matrix (17 x 17)</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-lg">&times;</button>
        </div>
        <div className="text-xs text-gray-400 mb-3">
          Cell color = edge count between categories. Click a cell to highlight those edges on the graph.
        </div>

        <div className="relative" style={{ minWidth: (CATEGORY_ORDER.length + 1) * cellSize }}>
          {/* Column headers */}
          <div className="flex" style={{ marginLeft: cellSize * 2 }}>
            {CATEGORY_ORDER.map((cat) => (
              <div
                key={cat}
                className="text-[9px] text-gray-400 font-mono"
                style={{
                  width: cellSize,
                  height: cellSize * 2,
                  writingMode: "vertical-rl",
                  textAlign: "end",
                  paddingBottom: 4,
                }}
              >
                {CATEGORY_SHORT[cat] ?? cat}
              </div>
            ))}
          </div>

          {/* Rows */}
          {CATEGORY_ORDER.map((srcCat) => (
            <div key={srcCat} className="flex items-center">
              {/* Row label */}
              <div
                className="text-[9px] text-gray-400 font-mono text-right pr-2 shrink-0"
                style={{ width: cellSize * 2 }}
              >
                {CATEGORY_SHORT[srcCat] ?? srcCat}
              </div>
              {/* Cells */}
              {CATEGORY_ORDER.map((tgtCat) => {
                const cell = matrix[srcCat]?.[tgtCat] ?? { count: 0, weight: 0 };
                const intensity = cell.count / maxCount;
                const isHovered = hoveredCell?.[0] === srcCat && hoveredCell?.[1] === tgtCat;
                const bgColor = cell.count === 0
                  ? "transparent"
                  : `rgba(59, 130, 246, ${0.15 + intensity * 0.75})`;

                return (
                  <div
                    key={`${srcCat}-${tgtCat}`}
                    className={`border border-gray-800 flex items-center justify-center cursor-pointer transition-all ${
                      isHovered ? "ring-1 ring-blue-400 z-10" : ""
                    }`}
                    style={{ width: cellSize, height: cellSize, backgroundColor: bgColor }}
                    onMouseEnter={() => setHoveredCell([srcCat, tgtCat])}
                    onMouseLeave={() => setHoveredCell(null)}
                    onClick={() => handleCellClick(srcCat, tgtCat)}
                    title={`${CATEGORY_SHORT[srcCat]} → ${CATEGORY_SHORT[tgtCat]}: ${cell.count} edges`}
                  >
                    {cell.count > 0 && (
                      <span className="text-[9px] text-white/80 font-mono">
                        {cell.count}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>

        {/* Hover detail */}
        {hoveredCell && (
          <div className="mt-3 text-xs text-gray-300 bg-gray-800 rounded px-3 py-2">
            <span className="text-white font-medium">
              {CATEGORY_SHORT[hoveredCell[0]]} → {CATEGORY_SHORT[hoveredCell[1]]}
            </span>
            : {matrix[hoveredCell[0]]?.[hoveredCell[1]]?.count ?? 0} edges,
            total weight {(matrix[hoveredCell[0]]?.[hoveredCell[1]]?.weight ?? 0).toFixed(1)}
          </div>
        )}
      </div>
    </div>
  );
}
