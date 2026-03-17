"use client";

import { useState } from "react";
import { API_URL as API } from "@/lib/config";

interface MoverItem {
  node_id: string;
  label: string;
  direction: string;
  z_score: number;
  latest_value: number | null;
}

interface PredictionItem {
  node_id: string;
  predicted_direction: string;
  predicted_sentiment: number;
  actual_sentiment: number | null;
  hit: number | null;
  reasoning: string;
}

interface BriefData {
  generated_at: string;
  overnight_movers: MoverItem[];
  resolved_predictions: PredictionItem[];
  prediction_summary: {
    total: number;
    hits: number;
    misses: number;
    hit_rate: number | null;
  };
  regime: {
    state: string;
    confidence: number;
    composite_score: number;
    changed: boolean;
    from_state: string | null;
    top_drivers: string[];
  };
  top_propagation_paths: {
    source: string;
    source_label: string;
    impacts: { node_id: string; label: string; impact: number; hops: number }[];
  }[];
  narrative: string;
}

const REGIME_COLORS: Record<string, string> = {
  risk_on: "text-green-400",
  risk_off: "text-red-400",
  transitioning: "text-yellow-400",
};

export default function MorningBrief() {
  const [open, setOpen] = useState(false);
  const [brief, setBrief] = useState<BriefData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/api/agent/morning-brief`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: BriefData = await res.json();
      setBrief(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate brief");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="bg-gray-800/90 backdrop-blur border border-gray-700 rounded-lg px-3 py-2 text-xs text-gray-300 hover:text-white transition-colors"
      >
        {open ? "Hide" : "Morning"} Brief
      </button>

      {open && (
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-[28rem] max-h-[70vh] bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-xl z-10 overflow-hidden flex flex-col">
          <div className="p-3 border-b border-gray-700 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">
              Morning Brief
            </h3>
            <button
              onClick={generate}
              disabled={loading}
              className="text-xs bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 text-white rounded px-2.5 py-1 transition-colors"
            >
              {loading ? "Generating..." : "Generate"}
            </button>
          </div>

          <div className="overflow-y-auto flex-1 p-3 space-y-3">
            {error && (
              <div className="text-xs text-red-400 bg-red-900/20 border border-red-800/30 rounded px-3 py-2">
                {error}
              </div>
            )}

            {!brief && !loading && !error && (
              <div className="text-xs text-gray-500 text-center py-6">
                Click Generate to create your morning intelligence brief.
              </div>
            )}

            {loading && !brief && (
              <div className="text-xs text-gray-400 text-center py-6">
                Analyzing overnight data and generating narrative...
              </div>
            )}

            {brief && (
              <>
                {/* Narrative */}
                <div>
                  <div className="text-[10px] text-gray-500 uppercase mb-1">
                    Summary
                  </div>
                  <p className="text-xs text-gray-200 leading-relaxed">
                    {brief.narrative}
                  </p>
                </div>

                {/* Regime */}
                <div>
                  <div className="text-[10px] text-gray-500 uppercase mb-1">
                    Regime
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs font-semibold ${
                        REGIME_COLORS[brief.regime.state] ?? "text-gray-300"
                      }`}
                    >
                      {brief.regime.state.replace("_", " ").toUpperCase()}
                    </span>
                    <span className="text-[10px] text-gray-500">
                      {(brief.regime.confidence * 100).toFixed(0)}% confidence
                    </span>
                    {brief.regime.changed && (
                      <span className="text-[10px] text-yellow-400">
                        shifted from {brief.regime.from_state}
                      </span>
                    )}
                  </div>
                  <div className="flex gap-1 mt-1 flex-wrap">
                    {brief.regime.top_drivers.map((d) => (
                      <span
                        key={d}
                        className="text-[10px] bg-gray-800 rounded px-1.5 py-0.5 text-gray-400"
                      >
                        {d}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Overnight Movers */}
                {brief.overnight_movers.length > 0 && (
                  <div>
                    <div className="text-[10px] text-gray-500 uppercase mb-1">
                      Overnight Movers
                    </div>
                    <div className="space-y-1">
                      {brief.overnight_movers.map((m) => (
                        <div
                          key={m.node_id}
                          className="flex items-center justify-between text-xs bg-gray-800 rounded px-2 py-1"
                        >
                          <span className="text-gray-300">{m.label}</span>
                          <span
                            className={
                              m.direction === "up"
                                ? "text-green-400"
                                : "text-red-400"
                            }
                          >
                            {m.direction === "up" ? "+" : ""}
                            {m.z_score.toFixed(1)}&sigma;
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Prediction Scorecard */}
                {brief.prediction_summary.total > 0 && (
                  <div>
                    <div className="text-[10px] text-gray-500 uppercase mb-1">
                      Predictions Resolved (24h)
                    </div>
                    <div className="flex gap-3 text-xs">
                      <span className="text-green-400">
                        {brief.prediction_summary.hits} hits
                      </span>
                      <span className="text-red-400">
                        {brief.prediction_summary.misses} misses
                      </span>
                      {brief.prediction_summary.hit_rate !== null && (
                        <span className="text-gray-400">
                          ({(brief.prediction_summary.hit_rate * 100).toFixed(0)}
                          % rate)
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Propagation Paths */}
                {brief.top_propagation_paths.length > 0 && (
                  <div>
                    <div className="text-[10px] text-gray-500 uppercase mb-1">
                      Risk Propagation
                    </div>
                    <div className="space-y-1.5">
                      {brief.top_propagation_paths.map((p) => (
                        <div key={p.source} className="text-[10px]">
                          <span className="text-gray-300 font-medium">
                            {p.source_label}
                          </span>
                          <span className="text-gray-600 mx-1">&rarr;</span>
                          {p.impacts.slice(0, 3).map((imp, i) => (
                            <span key={imp.node_id}>
                              {i > 0 && (
                                <span className="text-gray-600">, </span>
                              )}
                              <span className="text-gray-400">
                                {imp.label}
                              </span>
                              <span
                                className={
                                  imp.impact > 0
                                    ? "text-green-500"
                                    : "text-red-500"
                                }
                              >
                                {" "}
                                ({imp.impact > 0 ? "+" : ""}
                                {imp.impact.toFixed(3)})
                              </span>
                            </span>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Timestamp */}
                <div className="text-[9px] text-gray-600 text-right pt-1">
                  Generated{" "}
                  {new Date(brief.generated_at).toLocaleString(undefined, {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
