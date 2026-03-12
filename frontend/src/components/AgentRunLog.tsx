"use client";

import { useEffect, useState } from "react";
import { useGraphStore } from "@/hooks/useGraphData";
import type { AgentRun } from "@/types/graph";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const STATUS_COLORS: Record<string, string> = {
  completed: "bg-green-600",
  running: "bg-yellow-500",
  error: "bg-red-600",
};

export default function AgentRunLog() {
  const [open, setOpen] = useState(false);
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const agentRunning = useGraphStore((s) => s.agentRunning);

  const fetchRuns = () => {
    fetch(`${API}/api/agent/runs?limit=20`)
      .then((r) => r.json())
      .then(setRuns)
      .catch(() => {});
  };

  useEffect(() => {
    if (open) fetchRuns();
  }, [open]);

  // Refresh when agent finishes
  useEffect(() => {
    if (!agentRunning && open) {
      const t = setTimeout(fetchRuns, 1000);
      return () => clearTimeout(t);
    }
  }, [agentRunning, open]);

  const formatDuration = (run: AgentRun) => {
    if (!run.finished_at) return "running...";
    const start = new Date(run.started_at).getTime();
    const end = new Date(run.finished_at).getTime();
    const secs = Math.round((end - start) / 1000);
    return secs < 60 ? `${secs}s` : `${Math.floor(secs / 60)}m ${secs % 60}s`;
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="bg-gray-800/90 backdrop-blur border border-gray-700 rounded-lg px-3 py-2 text-xs text-gray-300 hover:text-white transition-colors"
      >
        {open ? "Hide" : "Show"} Agent Log
        {runs.length > 0 && !open && (
          <span className="ml-1.5 bg-gray-600 rounded-full px-1.5 py-0.5 text-[10px]">
            {runs.length}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute bottom-10 left-0 w-96 max-h-[60vh] bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-xl z-10 overflow-hidden flex flex-col">
          <div className="p-3 border-b border-gray-700 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Agent Runs</h3>
            <button
              onClick={fetchRuns}
              className="text-xs text-gray-400 hover:text-white"
            >
              Refresh
            </button>
          </div>

          <div className="overflow-y-auto flex-1 p-2 space-y-2">
            {runs.length === 0 ? (
              <div className="text-xs text-gray-500 text-center py-4">
                No runs yet
              </div>
            ) : (
              runs.map((run) => (
                <div
                  key={run.id}
                  className="bg-gray-800 rounded-lg p-2.5 cursor-pointer hover:bg-gray-750"
                  onClick={() =>
                    setExpandedId(expandedId === run.id ? null : run.id)
                  }
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={`w-2 h-2 rounded-full ${STATUS_COLORS[run.status] ?? "bg-gray-500"}`}
                    />
                    <span className="text-xs text-gray-300 flex-1">
                      {run.trigger === "scheduled" ? "Scheduled" : "Manual"} ·{" "}
                      {new Date(run.started_at).toLocaleString(undefined, {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                    <span className="text-[10px] text-gray-500">
                      {formatDuration(run)}
                    </span>
                  </div>

                  {/* Node count chips */}
                  <div className="mt-1 flex items-center gap-1 flex-wrap">
                    <span className="text-[10px] text-gray-500">
                      {run.nodes_analyzed.length} nodes
                    </span>
                    {run.tool_calls && (
                      <span className="text-[10px] text-gray-500">
                        · {run.tool_calls.length} tool calls
                      </span>
                    )}
                  </div>

                  {/* Expanded details */}
                  {expandedId === run.id && (
                    <div className="mt-2 pt-2 border-t border-gray-700 space-y-2">
                      {run.summary && (
                        <div>
                          <div className="text-[10px] text-gray-500 uppercase mb-0.5">
                            Summary
                          </div>
                          <p className="text-xs text-gray-300 leading-relaxed">
                            {run.summary.slice(0, 500)}
                            {run.summary.length > 500 && "..."}
                          </p>
                        </div>
                      )}

                      {run.error && (
                        <div>
                          <div className="text-[10px] text-red-400 uppercase mb-0.5">
                            Error
                          </div>
                          <p className="text-xs text-red-300">{run.error}</p>
                        </div>
                      )}

                      {run.tool_calls && run.tool_calls.length > 0 && (
                        <div>
                          <div className="text-[10px] text-gray-500 uppercase mb-0.5">
                            Tool Calls
                          </div>
                          <div className="space-y-1 max-h-32 overflow-y-auto">
                            {run.tool_calls.map((tc, i) => (
                              <div
                                key={i}
                                className="text-[10px] bg-gray-900 rounded px-2 py-1 font-mono"
                              >
                                <span className="text-blue-400">
                                  {tc.tool}
                                </span>
                                <span className="text-gray-500">
                                  ({JSON.stringify(tc.input).slice(0, 80)})
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div>
                        <div className="text-[10px] text-gray-500 uppercase mb-0.5">
                          Nodes
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {run.nodes_analyzed.map((n) => (
                            <span
                              key={n}
                              className="text-[10px] bg-gray-700 rounded px-1.5 py-0.5 text-gray-300"
                            >
                              {n}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
