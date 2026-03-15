"use client";

import { useEffect, useState } from "react";
import { useGraphStore } from "@/hooks/useGraphData";
import { API_URL as API } from "@/lib/config";
import { parseUTCTimestamp } from "@/lib/dateUtils";

interface PredictionItem {
  id: number;
  node_id: string;
  predicted_direction: string;
  predicted_sentiment: number;
  horizon_hours: number;
  reasoning: string;
  created_at: string;
  resolved_at: string | null;
  actual_sentiment: number | null;
  hit: number | null;
}

interface PredictionSummaryData {
  total: number;
  resolved: number;
  pending: number;
  hit_rate: number | null;
  by_direction: Record<string, { total: number; hits: number; misses: number }>;
}

const DIRECTION_COLORS: Record<string, string> = {
  bullish: "text-green-400",
  bearish: "text-red-400",
  neutral: "text-gray-400",
};

export default function PredictionsPanel() {
  const [open, setOpen] = useState(false);
  const [predictions, setPredictions] = useState<PredictionItem[]>([]);
  const [summary, setSummary] = useState<PredictionSummaryData | null>(null);
  const agentRunning = useGraphStore((s) => s.agentRunning);

  const fetchData = () => {
    fetch(`${API}/api/agent/predictions?limit=20`)
      .then((r) => r.json())
      .then(setPredictions)
      .catch(() => {});
    fetch(`${API}/api/agent/predictions/summary`)
      .then((r) => r.json())
      .then(setSummary)
      .catch(() => {});
  };

  useEffect(() => {
    if (open) fetchData();
  }, [open]);

  // Refresh when agent finishes
  useEffect(() => {
    if (!agentRunning && open) {
      const t = setTimeout(fetchData, 1500);
      return () => clearTimeout(t);
    }
  }, [agentRunning, open]);

  // Tick every 60s to keep countdown labels fresh
  const [, setTick] = useState(0);
  useEffect(() => {
    if (!open) return;
    const interval = setInterval(() => setTick((t) => t + 1), 60_000);
    return () => clearInterval(interval);
  }, [open]);

  const timeRemaining = (createdAt: string, horizonHours: number) => {
    const created = parseUTCTimestamp(createdAt).getTime();
    const expiry = created + horizonHours * 3600 * 1000;
    const remaining = expiry - Date.now();
    if (remaining <= 0) return "expired";
    const hours = Math.floor(remaining / 3600000);
    if (hours < 1) return "< 1h";
    if (hours < 24) return `${hours}h`;
    return `${Math.floor(hours / 24)}d ${hours % 24}h`;
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="bg-gray-800/90 backdrop-blur border border-gray-700 rounded-lg px-3 py-2 text-xs text-gray-300 hover:text-white transition-colors"
      >
        {open ? "Hide" : "Show"} Predictions
        {summary && summary.total > 0 && !open && (
          <span className="ml-1.5 bg-gray-600 rounded-full px-1.5 py-0.5 text-[10px]">
            {summary.total}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-96 max-h-[60vh] bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-xl z-10 overflow-hidden flex flex-col">
          <div className="p-3 border-b border-gray-700 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Predictions</h3>
            <button
              onClick={fetchData}
              className="text-xs text-gray-400 hover:text-white"
            >
              Refresh
            </button>
          </div>

          {/* Summary bar */}
          {summary && summary.total > 0 && (
            <div className="px-3 py-2 border-b border-gray-700 flex items-center gap-3 text-[10px]">
              <span className="text-gray-400">
                {summary.total} total
              </span>
              <span className="text-yellow-400">
                {summary.pending} pending
              </span>
              <span className="text-green-400">
                {summary.resolved} resolved
              </span>
              {summary.hit_rate !== null && (
                <span className={`font-semibold ${summary.hit_rate >= 0.5 ? "text-green-400" : "text-red-400"}`}>
                  {(summary.hit_rate * 100).toFixed(0)}% hit rate
                </span>
              )}
            </div>
          )}

          <div className="overflow-y-auto flex-1 p-2 space-y-2">
            {predictions.length === 0 ? (
              <div className="text-xs text-gray-500 text-center py-4">
                No predictions yet — run an analysis to generate predictions
              </div>
            ) : (
              predictions.map((pred) => {
                const isPending = pred.resolved_at === null;
                const isHit = pred.hit === 1;
                const isMiss = pred.hit === 0;

                let borderColor = "border-gray-700";
                let bgColor = "bg-gray-800";
                if (isHit) {
                  borderColor = "border-green-700/50";
                  bgColor = "bg-green-900/20";
                } else if (isMiss) {
                  borderColor = "border-red-700/50";
                  bgColor = "bg-red-900/20";
                }

                return (
                  <div
                    key={pred.id}
                    className={`${bgColor} border ${borderColor} rounded-lg p-2.5`}
                  >
                    <div className="flex items-center gap-2">
                      {/* Status indicator */}
                      <span
                        className={`w-2 h-2 rounded-full flex-shrink-0 ${
                          isPending ? "bg-yellow-500" : isHit ? "bg-green-500" : "bg-red-500"
                        }`}
                      />
                      <span className="text-xs text-gray-200 font-medium flex-1">
                        {pred.node_id}
                      </span>
                      <span className={`text-[10px] font-semibold ${DIRECTION_COLORS[pred.predicted_direction] ?? "text-gray-400"}`}>
                        {pred.predicted_direction.toUpperCase()}
                      </span>
                    </div>

                    <div className="mt-1 flex items-center gap-2 text-[10px]">
                      <span className="text-gray-500">
                        Predicted: {pred.predicted_sentiment > 0 ? "+" : ""}{pred.predicted_sentiment.toFixed(2)}
                      </span>
                      {pred.actual_sentiment !== null && (
                        <span className="text-gray-400">
                          Actual: {pred.actual_sentiment > 0 ? "+" : ""}{pred.actual_sentiment.toFixed(2)}
                        </span>
                      )}
                      {isPending && (
                        <span className="text-yellow-500 ml-auto">
                          {timeRemaining(pred.created_at, pred.horizon_hours)} left
                        </span>
                      )}
                      {!isPending && (
                        <span className={`ml-auto font-semibold ${isHit ? "text-green-400" : "text-red-400"}`}>
                          {isHit ? "Correct" : pred.hit === 0 ? "Wrong" : "Inconclusive"}
                        </span>
                      )}
                    </div>

                    {pred.reasoning && (
                      <div className="mt-1 text-[10px] text-gray-500 leading-snug">
                        {pred.reasoning.slice(0, 150)}{pred.reasoning.length > 150 ? "..." : ""}
                      </div>
                    )}

                    <div className="mt-1 text-[9px] text-gray-600">
                      {parseUTCTimestamp(pred.created_at).toLocaleString(undefined, {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                      {" · "}{pred.horizon_hours}h horizon
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
