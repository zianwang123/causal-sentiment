"use client";

import { useCallback, useEffect, useState } from "react";

import { API_URL as API } from "@/lib/config";

interface Position {
  id: number;
  ticker: string;
  node_id: string | null;
  shares: number;
  entry_price: number;
  notes: string;
}

interface PortfolioSummary {
  positions: Position[];
  total_value: number;
  total_cost: number;
  total_pnl: number;
  total_pnl_pct: number;
  mapped_node_ids: string[];
}

export default function PortfolioPanel({
  onPortfolioNodes,
}: {
  onPortfolioNodes?: (nodeIds: string[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [ticker, setTicker] = useState("");
  const [shares, setShares] = useState("");
  const [entryPrice, setEntryPrice] = useState("");

  const fetchSummary = useCallback(() => {
    fetch(`${API}/api/portfolio/summary`)
      .then((r) => r.json())
      .then((data: PortfolioSummary) => {
        setSummary(data);
        onPortfolioNodes?.(data.mapped_node_ids);
      })
      .catch(() => {});
  }, [onPortfolioNodes]);

  // Fetch on mount so portfolio nodes are highlighted immediately
  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  // Also refresh when panel is opened
  useEffect(() => {
    if (open) fetchSummary();
  }, [open, fetchSummary]);

  const addPosition = async () => {
    if (!ticker || !shares || !entryPrice) return;
    await fetch(`${API}/api/portfolio`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ticker,
        shares: parseFloat(shares),
        entry_price: parseFloat(entryPrice),
      }),
    });
    setTicker("");
    setShares("");
    setEntryPrice("");
    setShowForm(false);
    fetchSummary();
  };

  const deletePosition = async (id: number) => {
    await fetch(`${API}/api/portfolio/${id}`, { method: "DELETE" });
    fetchSummary();
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="bg-gray-800/90 backdrop-blur border border-gray-700 rounded-lg px-3 py-2 text-xs text-gray-300 hover:text-white transition-colors"
      >
        {open ? "Hide" : "Show"} Portfolio
        {summary && summary.positions.length > 0 && !open && (
          <span className="ml-1.5 bg-amber-600 rounded-full px-1.5 py-0.5 text-[10px]">
            {summary.positions.length}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute bottom-10 right-0 w-80 max-h-[60vh] bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-xl z-10 overflow-hidden flex flex-col">
          <div className="p-3 border-b border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Portfolio</h3>
              <button
                onClick={() => setShowForm(!showForm)}
                className="text-xs text-blue-400 hover:text-blue-300"
              >
                {showForm ? "Cancel" : "+ Add"}
              </button>
            </div>

            {summary && summary.positions.length > 0 && (
              <div className="mt-2 flex items-center gap-3 text-xs">
                <span className="text-gray-400">
                  Value: <span className="text-white">${summary.total_value.toLocaleString()}</span>
                </span>
                <span
                  className={
                    summary.total_pnl >= 0 ? "text-green-400" : "text-red-400"
                  }
                >
                  {summary.total_pnl >= 0 ? "+" : ""}
                  ${summary.total_pnl.toLocaleString()} (
                  {summary.total_pnl_pct >= 0 ? "+" : ""}
                  {summary.total_pnl_pct.toFixed(1)}%)
                </span>
              </div>
            )}
          </div>

          {showForm && (
            <div className="p-3 border-b border-gray-700 space-y-2">
              <input
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="Ticker (e.g., SPY)"
                className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500"
              />
              <div className="flex gap-2">
                <input
                  value={shares}
                  onChange={(e) => setShares(e.target.value)}
                  placeholder="Shares"
                  type="number"
                  className="flex-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500"
                />
                <input
                  value={entryPrice}
                  onChange={(e) => setEntryPrice(e.target.value)}
                  placeholder="Entry $"
                  type="number"
                  className="flex-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500"
                />
              </div>
              <button
                onClick={addPosition}
                className="w-full bg-amber-600 hover:bg-amber-700 text-white text-xs py-1.5 rounded"
              >
                Add Position
              </button>
            </div>
          )}

          <div className="overflow-y-auto flex-1 p-2 space-y-1.5">
            {!summary || summary.positions.length === 0 ? (
              <div className="text-xs text-gray-500 text-center py-4">
                No positions yet
              </div>
            ) : (
              summary.positions.map((pos) => (
                <div
                  key={pos.id}
                  className="bg-gray-800 rounded-lg px-2.5 py-2 flex items-center gap-2"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-semibold text-white">
                        {pos.ticker}
                      </span>
                      {pos.node_id && (
                        <span className="text-[9px] bg-amber-800/50 text-amber-300 rounded px-1">
                          mapped
                        </span>
                      )}
                    </div>
                    <div className="text-[10px] text-gray-400 mt-0.5">
                      {pos.shares} shares @ ${pos.entry_price.toFixed(2)}
                    </div>
                  </div>
                  <button
                    onClick={() => deletePosition(pos.id)}
                    className="text-gray-500 hover:text-red-400 text-xs"
                  >
                    &times;
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
