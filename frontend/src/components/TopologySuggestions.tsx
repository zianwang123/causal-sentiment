"use client";

import { useCallback, useEffect, useState } from "react";
import { useGraphStore } from "@/hooks/useGraphData";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface EdgeSuggestion {
  id: number;
  source_id: string;
  target_id: string;
  suggested_direction: string;
  suggested_weight: number;
  correlation: number | null;
  llm_reasoning: string;
  status: string;
}

export default function TopologySuggestions() {
  const [open, setOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<EdgeSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const fetchGraph = useGraphStore((s) => s.fetchGraph);

  const fetchSuggestions = useCallback(() => {
    fetch(`${API}/api/graph/topology/suggestions?status=pending`)
      .then((r) => r.json())
      .then((data: EdgeSuggestion[]) => setSuggestions(data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (open) fetchSuggestions();
  }, [open, fetchSuggestions]);

  const generateSuggestions = async () => {
    setGenerating(true);
    try {
      const res = await fetch(`${API}/api/graph/topology/suggest`, {
        method: "POST",
      });
      if (res.ok) {
        fetchSuggestions();
      }
    } catch {
      // ignore
    } finally {
      setGenerating(false);
    }
  };

  const handleAction = async (id: number, action: "accept" | "reject") => {
    setLoading(true);
    try {
      await fetch(`${API}/api/graph/topology/suggestions/${id}/${action}`, {
        method: "POST",
      });
      setSuggestions((prev) => prev.filter((s) => s.id !== id));
      if (action === "accept") {
        fetchGraph(); // Refresh graph to show new edge
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const directionColor: Record<string, string> = {
    positive: "text-green-400",
    negative: "text-red-400",
    complex: "text-yellow-400",
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="bg-gray-800/90 backdrop-blur border border-gray-700 rounded-lg px-3 py-2 text-xs text-gray-300 hover:text-white transition-colors"
      >
        {open ? "Hide" : "Evolve Graph"}
        {suggestions.length > 0 && !open && (
          <span className="ml-1.5 bg-purple-600 rounded-full px-1.5 py-0.5 text-[10px]">
            {suggestions.length}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute bottom-10 left-0 w-96 max-h-[60vh] bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-xl z-10 overflow-hidden flex flex-col">
          <div className="p-3 border-b border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">
                Topology Learning
              </h3>
              <button
                onClick={generateSuggestions}
                disabled={generating}
                className="text-xs bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white px-2 py-1 rounded"
              >
                {generating ? "Analyzing..." : "Generate Suggestions"}
              </button>
            </div>
            <p className="text-[10px] text-gray-500 mt-1">
              Claude analyzes correlated but unconnected nodes and suggests new
              causal edges for your review.
            </p>
          </div>

          <div className="overflow-y-auto flex-1 p-2 space-y-2">
            {suggestions.length === 0 ? (
              <div className="text-xs text-gray-500 text-center py-6">
                {generating
                  ? "Claude is analyzing correlations..."
                  : "No pending suggestions. Click Generate to find new edges."}
              </div>
            ) : (
              suggestions.map((s) => (
                <div
                  key={s.id}
                  className="bg-gray-800 rounded-lg p-3 space-y-2"
                >
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-white font-semibold">
                      {s.source_id}
                    </span>
                    <span className="text-gray-500">&rarr;</span>
                    <span className="text-white font-semibold">
                      {s.target_id}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-[10px]">
                    <span
                      className={
                        directionColor[s.suggested_direction] || "text-gray-400"
                      }
                    >
                      {s.suggested_direction}
                    </span>
                    <span className="text-gray-400">
                      weight: {s.suggested_weight.toFixed(2)}
                    </span>
                    {s.correlation !== null && (
                      <span className="text-gray-400">
                        corr: {s.correlation > 0 ? "+" : ""}
                        {s.correlation.toFixed(3)}
                      </span>
                    )}
                  </div>

                  <p className="text-[11px] text-gray-300 leading-relaxed">
                    {s.llm_reasoning}
                  </p>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleAction(s.id, "accept")}
                      disabled={loading}
                      className="flex-1 bg-green-700 hover:bg-green-600 disabled:bg-gray-600 text-white text-xs py-1.5 rounded"
                    >
                      Accept
                    </button>
                    <button
                      onClick={() => handleAction(s.id, "reject")}
                      disabled={loading}
                      className="flex-1 bg-red-800 hover:bg-red-700 disabled:bg-gray-600 text-white text-xs py-1.5 rounded"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
