"use client";

import { useCallback, useEffect, useState } from "react";
import { useGraphStore } from "@/hooks/useGraphData";
import { API_URL } from "@/lib/config";

interface Chain {
  id: string;
  name: string;
  tier: number;
  nodes: string[];
  lag_profile: string;
  end_to_end_lag: string;
  description: string;
}

const TIER_COLORS: Record<number, string> = {
  1: "border-red-500/50 bg-red-950/30",
  2: "border-orange-500/50 bg-orange-950/30",
  3: "border-yellow-500/50 bg-yellow-950/30",
  4: "border-blue-500/50 bg-blue-950/30",
};

const TIER_LABELS: Record<number, string> = {
  1: "Primary (every cycle)",
  2: "High-frequency (most cycles)",
  3: "Crisis-specific",
  4: "Structural / Secular",
};

export default function ChainExplorer({ onClose }: { onClose: () => void }) {
  const [chains, setChains] = useState<Chain[]>([]);
  const [expandedTier, setExpandedTier] = useState<number | null>(1);
  const [activeChain, setActiveChain] = useState<string | null>(null);
  const nodes = useGraphStore((s) => s.nodes);
  const setSelectedNode = useGraphStore((s) => s.setSelectedNode);
  const focusNode = useGraphStore((s) => s.focusNode);

  useEffect(() => {
    fetch(`${API_URL}/api/graph/chains`)
      .then((r) => r.json())
      .then((data: Chain[]) => setChains(data))
      .catch(() => {});
  }, []);

  const nodeMap = new Map(nodes.map((n) => [n.id, n]));

  const highlightChain = useCallback(
    (chain: Chain) => {
      if (activeChain === chain.id) {
        setActiveChain(null);
        // Reset edge display
        useGraphStore.setState({ edgeDisplayMode: "selected" });
        return;
      }
      setActiveChain(chain.id);
      // Switch to "all" mode so chain edges are visible
      useGraphStore.setState({ edgeDisplayMode: "all" });
      // Focus on first node in chain
      if (chain.nodes.length > 0) {
        focusNode(chain.nodes[0]);
      }
    },
    [activeChain, focusNode]
  );

  const tiers = [1, 2, 3, 4];

  return (
    <div className="absolute right-0 top-0 w-96 h-full bg-gray-900/95 border-l border-gray-700 overflow-y-auto z-20">
      <div className="sticky top-0 bg-gray-900 border-b border-gray-700 px-4 py-3 flex justify-between items-center">
        <h2 className="text-sm font-bold text-white">Chain Explorer</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white text-lg leading-none"
        >
          &times;
        </button>
      </div>
      <div className="p-3 text-xs text-gray-400 border-b border-gray-800">
        25 dominant transmission chains ranked by historical explanatory power.
        Click a chain to highlight its path on the graph.
      </div>

      {tiers.map((tier) => {
        const tierChains = chains.filter((c) => c.tier === tier);
        if (tierChains.length === 0) return null;
        const isExpanded = expandedTier === tier;

        return (
          <div key={tier}>
            <button
              onClick={() => setExpandedTier(isExpanded ? null : tier)}
              className="w-full px-4 py-2.5 flex items-center justify-between text-sm font-medium text-gray-200 hover:bg-gray-800/50 border-b border-gray-800"
            >
              <span>
                Tier {tier}: {TIER_LABELS[tier]}
              </span>
              <span className="text-xs text-gray-500">
                {tierChains.length} chains {isExpanded ? "▾" : "▸"}
              </span>
            </button>

            {isExpanded && (
              <div className="space-y-2 p-2">
                {tierChains.map((chain) => {
                  const isActive = activeChain === chain.id;
                  return (
                    <button
                      key={chain.id}
                      onClick={() => highlightChain(chain)}
                      className={`w-full text-left p-3 rounded border transition-all ${
                        isActive
                          ? "border-blue-400 bg-blue-950/40 ring-1 ring-blue-400/30"
                          : TIER_COLORS[tier] + " hover:brightness-125"
                      }`}
                    >
                      <div className="text-xs font-semibold text-white mb-1">
                        {chain.name}
                      </div>
                      <div className="text-xs text-gray-400 mb-2">
                        {chain.description}
                      </div>
                      {/* Node path */}
                      <div className="flex flex-wrap items-center gap-1 mb-1.5">
                        {chain.nodes.map((nid, i) => {
                          const node = nodeMap.get(nid);
                          const label = node?.label ?? nid;
                          return (
                            <span key={`${nid}-${i}`} className="flex items-center">
                              {i > 0 && (
                                <span className="text-gray-600 mx-0.5">→</span>
                              )}
                              <span
                                className="bg-gray-700/80 text-gray-200 px-1.5 py-0.5 rounded text-[10px] cursor-pointer hover:bg-gray-600"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (node) {
                                    setSelectedNode(node);
                                    focusNode(nid);
                                  }
                                }}
                              >
                                {label}
                              </span>
                            </span>
                          );
                        })}
                      </div>
                      <div className="text-[10px] text-gray-500">
                        End-to-end: {chain.end_to_end_lag} &middot; {chain.lag_profile}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
