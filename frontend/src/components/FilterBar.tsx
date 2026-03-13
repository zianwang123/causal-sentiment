"use client";

import { useCallback, useEffect, useState } from "react";
import { useGraphStore } from "@/hooks/useGraphData";

import { API_URL as API } from "@/lib/config";

interface LLMConfig {
  provider: string;
  anthropic_model: string;
  openai_model: string;
  has_anthropic_key: boolean;
  has_openai_key: boolean;
}

const REGIME_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  risk_on: { bg: "bg-green-900/60 border-green-600/50", text: "text-green-300", label: "RISK-ON" },
  risk_off: { bg: "bg-red-900/60 border-red-600/50", text: "text-red-300", label: "RISK-OFF" },
  transitioning: { bg: "bg-yellow-900/60 border-yellow-600/50", text: "text-yellow-300", label: "TRANSITIONING" },
};

export default function FilterBar() {
  const agentRunning = useGraphStore((s) => s.agentRunning);
  const agentProgress = useGraphStore((s) => s.agentProgress);
  const triggerAnalysis = useGraphStore((s) => s.triggerAnalysis);
  const lastRun = useGraphStore((s) => s.lastRun);
  const clustered = useGraphStore((s) => s.clustered);
  const toggleClustered = useGraphStore((s) => s.toggleClustered);
  const regime = useGraphStore((s) => s.regime);
  const fetchRegime = useGraphStore((s) => s.fetchRegime);
  const [llmConfig, setLlmConfig] = useState<LLMConfig | null>(null);

  const fetchLLMConfig = useCallback(() => {
    fetch(`${API}/api/agent/llm-config`)
      .then((r) => r.json())
      .then((data: LLMConfig) => setLlmConfig(data))
      .catch(() => {});
  }, []);

  const switchProvider = useCallback((provider: string) => {
    fetch(`${API}/api/agent/llm-config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider }),
    })
      .then((r) => r.json())
      .then((data: LLMConfig) => setLlmConfig(data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchRegime();
    fetchLLMConfig();
    const interval = setInterval(fetchRegime, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchRegime, fetchLLMConfig]);

  const regimeStyle = regime ? REGIME_STYLES[regime.state] || REGIME_STYLES.transitioning : null;

  return (
    <div className="absolute top-4 left-4 z-10 flex flex-col gap-3">
      <div className="bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg p-3">
        <h2 className="text-white text-sm font-semibold mb-2">
          Causal Sentiment Engine
        </h2>

        {regime && regimeStyle && (
          <div className={`mb-2 px-2.5 py-1.5 rounded border ${regimeStyle.bg}`}>
            <div className={`text-xs font-bold ${regimeStyle.text}`}>
              {regimeStyle.label}
            </div>
            <div className="text-[10px] text-gray-400 mt-0.5">
              Confidence: {(regime.confidence * 100).toFixed(0)}% · Score: {regime.composite_score > 0 ? "+" : ""}{regime.composite_score.toFixed(3)}
            </div>
          </div>
        )}

        <button
          onClick={() => triggerAnalysis()}
          disabled={agentRunning}
          className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-sm py-2 px-3 rounded transition-colors"
        >
          {agentRunning ? "Agent Running..." : "Run Full Analysis"}
        </button>
        {agentRunning && (
          <div className="w-full mt-2">
            <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
              {agentProgress ? (
                <div
                  className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(5, (agentProgress.round / agentProgress.maxRounds) * 100)}%` }}
                />
              ) : (
                <div className="h-full bg-emerald-500 rounded-full" style={{
                  animation: "progress-indeterminate 1.5s ease-in-out infinite",
                  width: "40%",
                }} />
              )}
            </div>
            <div className="text-[10px] text-gray-400 mt-0.5">
              {agentProgress
                ? `Round ${agentProgress.round}/${agentProgress.maxRounds} · ${agentProgress.totalToolCalls} tool calls`
                : "Starting analysis..."}
            </div>
            <style jsx>{`
              @keyframes progress-indeterminate {
                0% { margin-left: 0%; }
                50% { margin-left: 60%; }
                100% { margin-left: 0%; }
              }
            `}</style>
          </div>
        )}
        <button
          onClick={toggleClustered}
          className={`w-full mt-2 text-sm py-2 px-3 rounded transition-colors ${
            clustered
              ? "bg-blue-600 hover:bg-blue-700 text-white"
              : "bg-gray-700 hover:bg-gray-600 text-gray-300"
          }`}
        >
          {clustered ? "Clustered Layout" : "Free Layout"}
        </button>
        {llmConfig && (
          <div className="mt-2">
            <div className="text-[10px] text-gray-500 uppercase mb-1">LLM Provider</div>
            <div className="flex gap-1">
              <button
                onClick={() => switchProvider("openai")}
                disabled={!llmConfig.has_openai_key}
                className={`flex-1 text-[11px] py-1.5 rounded transition-colors ${
                  llmConfig.provider === "openai"
                    ? "bg-green-700 text-white"
                    : "bg-gray-700 text-gray-400 hover:text-gray-200"
                } ${!llmConfig.has_openai_key ? "opacity-40 cursor-not-allowed" : ""}`}
              >
                GPT
              </button>
              <button
                onClick={() => switchProvider("anthropic")}
                disabled={!llmConfig.has_anthropic_key}
                className={`flex-1 text-[11px] py-1.5 rounded transition-colors ${
                  llmConfig.provider === "anthropic"
                    ? "bg-orange-700 text-white"
                    : "bg-gray-700 text-gray-400 hover:text-gray-200"
                } ${!llmConfig.has_anthropic_key ? "opacity-40 cursor-not-allowed" : ""}`}
              >
                Claude
              </button>
            </div>
            <div className="text-[9px] text-gray-500 mt-0.5">
              {llmConfig.provider === "openai" ? llmConfig.openai_model : llmConfig.anthropic_model}
            </div>
          </div>
        )}
        {lastRun && (
          <div className="mt-2 text-xs text-gray-400">
            Last run: {lastRun.status}
            {lastRun.nodes_analyzed.length > 0 &&
              ` · ${lastRun.nodes_analyzed.length} nodes`}
          </div>
        )}
      </div>

      <div className="bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg p-3">
        <h3 className="text-white text-xs font-semibold uppercase mb-2">
          Legend
        </h3>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500 inline-block" />
            <span className="text-gray-300">Bullish</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-gray-400 inline-block" />
            <span className="text-gray-300">Neutral</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500 inline-block" />
            <span className="text-gray-300">Bearish</span>
          </div>
          <hr className="border-gray-700 my-1" />
          <div className="flex items-center gap-2">
            <span className="w-6 h-0.5 bg-green-500 inline-block" />
            <span className="text-gray-300">Positive causation</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-6 h-0.5 bg-red-500 inline-block" />
            <span className="text-gray-300">Negative causation</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-6 h-0.5 bg-yellow-500 inline-block" />
            <span className="text-gray-300">Complex</span>
          </div>
        </div>
      </div>
    </div>
  );
}
