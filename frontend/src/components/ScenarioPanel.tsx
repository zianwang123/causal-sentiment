"use client";

import { useCallback, useEffect, useState } from "react";
import { useGraphStore } from "@/hooks/useGraphData";
import type { ScenarioBranch, ScenarioShock } from "@/types/graph";

const PHASE_LABELS: Record<string, string> = {
  news: "Researching news...",
  history: "Finding historical parallels...",
  generation: "Generating scenarios...",
  mapping: "Mapping to graph...",
};

export default function ScenarioPanel() {
  const [open, setOpen] = useState(false);
  const [triggerText, setTriggerText] = useState("");
  const [expandedBranch, setExpandedBranch] = useState<number | null>(null);
  const [editedShocks, setEditedShocks] = useState<Record<string, Record<string, number>>>({});

  const scenarioResult = useGraphStore((s) => s.scenarioResult);
  const scenarioLoading = useGraphStore((s) => s.scenarioLoading);
  const scenarioProgress = useGraphStore((s) => s.scenarioProgress);
  const scenarioHistory = useGraphStore((s) => s.scenarioHistory);
  const quickTriggers = useGraphStore((s) => s.quickTriggers);
  const triggerScenario = useGraphStore((s) => s.triggerScenario);
  const applyScenarioBranch = useGraphStore((s) => s.applyScenarioBranch);
  const fetchScenarioHistory = useGraphStore((s) => s.fetchScenarioHistory);
  const fetchQuickTriggers = useGraphStore((s) => s.fetchQuickTriggers);
  const fetchScenario = useGraphStore((s) => s.fetchScenario);
  const evolveGraph = useGraphStore((s) => s.evolveGraph);
  const hypotheticalNodeIds = useGraphStore((s) => s.hypotheticalNodeIds);
  const resetEvolve = useGraphStore((s) => s.resetEvolve);
  const clearScenario = useGraphStore((s) => s.clearScenario);
  const focusNode = useGraphStore((s) => s.focusNode);

  useEffect(() => {
    if (open) {
      fetchScenarioHistory();
      fetchQuickTriggers();
    }
  }, [open, fetchScenarioHistory, fetchQuickTriggers]);

  const handleGenerate = useCallback((customTrigger?: string) => {
    const text = customTrigger || triggerText.trim();
    // If no text, trigger with empty string — backend will auto-pick from news
    triggerScenario(text || "", text ? "user_prompt" : "news_auto");
    setEditedShocks({});
    setExpandedBranch(null);
  }, [triggerText, triggerScenario]);

  const handleQuickTrigger = useCallback((prompt: string) => {
    setTriggerText(prompt);
    handleGenerate(prompt);
  }, [handleGenerate]);

  const handleApply = useCallback((branchIdx: number) => {
    if (!scenarioResult) return;
    const branch = scenarioResult.branches[branchIdx];
    if (!branch) return;

    const overrides = branch.shocks
      .map((s) => {
        const edited = editedShocks[branchIdx]?.[s.node_id];
        if (edited !== undefined && edited !== s.shock_value) {
          return { node_id: s.node_id, shock_value: edited };
        }
        return null;
      })
      .filter(Boolean) as Array<{node_id: string; shock_value: number}>;

    // Apply shocks to graph
    applyScenarioBranch(scenarioResult.id, branchIdx, overrides.length > 0 ? overrides : undefined);

    // Also evolve graph with node/edge suggestions if any
    const hasSuggestions = !!branch.node_suggestions?.length || !!branch.edge_suggestions?.length;
    if (hasSuggestions) {
      evolveGraph(scenarioResult.id, branchIdx);
    }
  }, [scenarioResult, editedShocks, applyScenarioBranch, evolveGraph]);

  const handleEvolve = useCallback((branchIdx: number) => {
    if (!scenarioResult) return;
    evolveGraph(scenarioResult.id, branchIdx);
  }, [scenarioResult, evolveGraph]);

  const handleExport = useCallback(() => {
    if (!scenarioResult) return;
    const data = JSON.stringify(scenarioResult, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const slug = scenarioResult.trigger.slice(0, 30).replace(/[^a-zA-Z0-9]+/g, "-").toLowerCase();
    a.href = url;
    a.download = `scenario-${slug}-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [scenarioResult]);

  const handleShockEdit = useCallback((branchIdx: number, nodeId: string, value: number) => {
    setEditedShocks((prev) => ({
      ...prev,
      [branchIdx]: {
        ...(prev[branchIdx] || {}),
        [nodeId]: Math.max(-1, Math.min(1, value)),
      },
    }));
  }, []);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="absolute top-4 right-[340px] z-10 bg-purple-700 hover:bg-purple-600 text-white text-xs font-semibold py-2 px-3 rounded-lg shadow-lg transition-colors"
      >
        Scenario Engine
      </button>
    );
  }

  return (
    <div className="absolute top-4 right-[340px] w-[420px] max-h-[90vh] overflow-y-auto bg-gray-900/95 backdrop-blur border border-purple-700/50 rounded-lg shadow-xl p-4 text-white z-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-purple-400">Scenario Engine</h3>
        <div className="flex items-center gap-1">
          {scenarioResult && (
            <>
              <button
                onClick={handleExport}
                className="text-gray-400 hover:text-white text-[10px] px-2 py-0.5 border border-gray-700 rounded hover:border-gray-500 transition-colors"
                title="Export scenario as JSON"
              >
                Export
              </button>
              <button
                onClick={() => { clearScenario(); resetEvolve(); }}
                className="text-gray-400 hover:text-white text-[10px] px-2 py-0.5 border border-gray-700 rounded hover:border-gray-500 transition-colors"
                title="Clear results"
              >
                Clear
              </button>
            </>
          )}
          <button
            onClick={() => setOpen(false)}
            className="text-gray-400 hover:text-white text-sm px-2 py-0.5 border border-gray-700 rounded hover:border-gray-500 transition-colors"
            title="Minimize panel"
          >
            _
          </button>
        </div>
      </div>

      {/* Hypothetical nodes indicator (info only, Clear button in header handles removal) */}
      {hypotheticalNodeIds.length > 0 && (
        <div className="mb-2 bg-purple-900/20 border border-purple-700/30 rounded px-2.5 py-1.5">
          <span className="text-[11px] text-purple-300">
            {hypotheticalNodeIds.length} hypothetical node{hypotheticalNodeIds.length > 1 ? "s" : ""} on graph (purple)
          </span>
        </div>
      )}

      {/* Primary action — one click, no typing */}
      {!scenarioResult && (
        <div className="mb-3">
          <button
            onClick={() => handleGenerate()}
            disabled={scenarioLoading}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-sm py-2.5 rounded font-medium transition-colors"
          >
            {scenarioLoading ? "Generating..." : "Generate Scenario"}
          </button>

          {/* Optional custom trigger */}
          {!scenarioLoading && (
            <>
              <div className="flex items-center gap-2 my-2">
                <div className="h-px flex-1 bg-gray-700" />
                <span className="text-[10px] text-gray-500">or type your own</span>
                <div className="h-px flex-1 bg-gray-700" />
              </div>
              <textarea
                value={triggerText}
                onChange={(e) => setTriggerText(e.target.value)}
                placeholder="What if UBS collapses? Big earthquake in California?"
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-xs text-white placeholder-gray-500 resize-none focus:outline-none focus:border-purple-500"
                rows={2}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleGenerate();
                  }
                }}
              />
              {triggerText.trim() && (
                <button
                  onClick={() => handleGenerate()}
                  className="w-full mt-1 bg-purple-700/60 hover:bg-purple-700 text-white text-xs py-1.5 rounded transition-colors"
                >
                  Generate Scenario
                </button>
              )}
            </>
          )}
        </div>
      )}

      {/* Quick triggers */}
      {quickTriggers.length > 0 && !scenarioLoading && !scenarioResult && (
        <div className="mb-3">
          <div className="text-[10px] text-gray-500 uppercase mb-1">Quick Triggers</div>
          <div className="flex flex-wrap gap-1">
            {quickTriggers.map((t, i) => (
              <button
                key={i}
                onClick={() => handleQuickTrigger(t.suggested_prompt)}
                className="text-[11px] bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white rounded px-2 py-1 transition-colors border border-gray-700/50"
                title={`Source: ${t.source}`}
              >
                {t.headline}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading / progress */}
      {scenarioLoading && (
        <div className="mb-3">
          <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
            {scenarioProgress ? (
              <div
                className="h-full bg-purple-500 rounded-full transition-all duration-500"
                style={{ width: `${Math.max(5, (scenarioProgress.round / scenarioProgress.max_rounds) * 100)}%` }}
              />
            ) : (
              <div className="h-full bg-purple-500 rounded-full animate-pulse" style={{ width: "30%" }} />
            )}
          </div>
          <div className="text-[10px] text-gray-400 mt-1">
            {scenarioProgress
              ? `${PHASE_LABELS[scenarioProgress.phase] || scenarioProgress.phase} (round ${scenarioProgress.round}/${scenarioProgress.max_rounds})`
              : "Starting scenario analysis..."}
          </div>
        </div>
      )}

      {/* Results */}
      {scenarioResult && scenarioResult.branches.length > 0 && (
        <div className="space-y-2">
          {/* Research summary */}
          {scenarioResult.research_summary && (
            <div className="bg-gray-800/50 rounded p-2 mb-2">
              <div className="text-[10px] text-gray-500 uppercase mb-0.5">Research</div>
              <p className="text-[11px] text-gray-300 leading-relaxed">{scenarioResult.research_summary}</p>
            </div>
          )}
          {scenarioResult.historical_parallels && (
            <div className="bg-gray-800/50 rounded p-2 mb-2">
              <div className="text-[10px] text-gray-500 uppercase mb-0.5">Historical Parallels</div>
              <p className="text-[11px] text-gray-300 leading-relaxed">{scenarioResult.historical_parallels}</p>
            </div>
          )}

          {/* Branch cards */}
          {scenarioResult.branches.map((branch, idx) => (
            <BranchCard
              key={idx}
              branch={branch}
              branchIdx={idx}
              expanded={expandedBranch === idx}
              onToggle={() => setExpandedBranch(expandedBranch === idx ? null : idx)}
              onApply={() => handleApply(idx)}
              onEvolve={() => handleEvolve(idx)}
              onShockEdit={(nodeId, value) => handleShockEdit(idx, nodeId, value)}
              editedShocks={editedShocks[idx] || {}}
              onFocusNode={focusNode}
              hasSuggestions={!!branch.node_suggestions?.length || !!branch.edge_suggestions?.length}
            />
          ))}
        </div>
      )}

      {/* Error */}
      {scenarioResult?.error && (
        <div className="bg-red-900/30 border border-red-700/50 rounded p-2 text-xs text-red-300">
          {scenarioResult.error}
        </div>
      )}

      {/* History */}
      {scenarioHistory.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-700">
          <div className="text-[10px] text-gray-500 uppercase mb-1">History</div>
          <div className="flex flex-wrap gap-1">
            {scenarioHistory.slice(0, 6).map((s) => (
              <button
                key={s.id}
                onClick={() => fetchScenario(s.id)}
                className={`text-[10px] rounded px-2 py-0.5 transition-colors border ${
                  scenarioResult?.id === s.id
                    ? "bg-purple-900/30 border-purple-700/50 text-purple-300"
                    : "bg-gray-800 border-gray-700/50 text-gray-400 hover:text-white hover:bg-gray-700"
                }`}
              >
                {s.trigger.slice(0, 30)}{s.trigger.length > 30 ? "..." : ""}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}


function BranchCard({
  branch,
  branchIdx,
  expanded,
  onToggle,
  onApply,
  onEvolve,
  onShockEdit,
  editedShocks,
  onFocusNode,
  hasSuggestions,
}: {
  branch: ScenarioBranch;
  branchIdx: number;
  expanded: boolean;
  onToggle: () => void;
  onApply: () => void;
  onEvolve: () => void;
  onShockEdit: (nodeId: string, value: number) => void;
  editedShocks: Record<string, number>;
  onFocusNode: (nodeId: string) => void;
  hasSuggestions: boolean;
}) {
  const branchLabel = String.fromCharCode(65 + branchIdx); // A, B, C
  const probPct = Math.round(branch.probability * 100);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700/50 overflow-hidden">
      {/* Header — always visible */}
      <button
        onClick={onToggle}
        className="w-full text-left px-3 py-2 hover:bg-gray-750 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold bg-purple-700/50 text-purple-300 rounded px-1.5 py-0.5">
              {branchLabel}
            </span>
            <span className="text-xs font-medium text-white">{branch.title}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-[10px] font-bold rounded px-1.5 py-0.5 ${
              probPct >= 50 ? "bg-green-900/50 text-green-300" :
              probPct >= 25 ? "bg-yellow-900/50 text-yellow-300" :
              "bg-red-900/50 text-red-300"
            }`}>
              {probPct}%
            </span>
            <span className="text-[10px] text-gray-500">{expanded ? "\u25B2" : "\u25BC"}</span>
          </div>
        </div>
        {!expanded && (
          <p className="text-[11px] text-gray-400 mt-1 line-clamp-2">{branch.narrative}</p>
        )}
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="px-3 pb-3 border-t border-gray-700/50">
          {/* Full narrative */}
          <p className="text-[11px] text-gray-300 mt-2 leading-relaxed">{branch.narrative}</p>

          {/* Causal chain */}
          {branch.causal_chain.length > 0 && (
            <div className="mt-2">
              <div className="text-[10px] text-gray-500 uppercase mb-1">Causal Chain</div>
              <div className="space-y-0.5">
                {branch.causal_chain.map((step, i) => (
                  <div key={i} className="text-[11px] text-gray-300 flex items-start gap-1">
                    <span className="text-purple-400 flex-shrink-0">{i === 0 ? "\u25CF" : "\u2192"}</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Shocks */}
          <div className="mt-2">
            <div className="text-[10px] text-gray-500 uppercase mb-1">
              Shocks ({branch.shocks.length})
            </div>
            <div className="space-y-1">
              {branch.shocks.map((shock) => (
                <ShockRow
                  key={shock.node_id}
                  shock={shock}
                  editedValue={editedShocks[shock.node_id]}
                  onEdit={(v) => onShockEdit(shock.node_id, v)}
                  onFocus={() => onFocusNode(shock.node_id)}
                />
              ))}
            </div>
          </div>

          {/* Node suggestions */}
          {branch.node_suggestions && branch.node_suggestions.length > 0 && (
            <div className="mt-2">
              <div className="text-[10px] text-gray-500 uppercase mb-1">Suggested New Nodes</div>
              {branch.node_suggestions.map((ns, i) => (
                <div key={i} className="text-[11px] bg-gray-900/50 rounded px-2 py-1 mb-1">
                  <span className="text-purple-300 font-medium">{ns.suggested_label}</span>
                  <span className="text-gray-500 ml-1">({ns.suggested_type})</span>
                  {ns.reasoning && <p className="text-gray-500 text-[10px] mt-0.5">{ns.reasoning}</p>}
                </div>
              ))}
            </div>
          )}

          {/* Edge suggestions */}
          {branch.edge_suggestions && branch.edge_suggestions.length > 0 && (
            <div className="mt-2">
              <div className="text-[10px] text-gray-500 uppercase mb-1">Suggested New Edges</div>
              {branch.edge_suggestions.map((es, i) => (
                <div key={i} className="text-[10px] text-gray-400">
                  {es.source_id} {"\u2192"} {es.target_id} ({es.direction})
                </div>
              ))}
            </div>
          )}

          {/* Time horizon + invalidation */}
          <div className="mt-2 flex items-center gap-3 text-[10px] text-gray-500">
            <span>Horizon: {branch.time_horizon}</span>
            {branch.invalidation && (
              <span title={branch.invalidation} className="truncate cursor-help">
                Invalidation: {branch.invalidation}
              </span>
            )}
          </div>

          {/* Apply button — applies shocks + evolves graph with suggestions */}
          <button
            onClick={onApply}
            className="w-full mt-2 bg-purple-600 hover:bg-purple-700 text-white text-xs py-1.5 rounded transition-colors"
          >
            {hasSuggestions ? "Apply to Graph + Evolve" : "Apply to Graph"}
          </button>
        </div>
      )}
    </div>
  );
}


function ShockRow({
  shock,
  editedValue,
  onEdit,
  onFocus,
}: {
  shock: ScenarioShock;
  editedValue: number | undefined;
  onEdit: (value: number) => void;
  onFocus: () => void;
}) {
  const displayValue = editedValue !== undefined ? editedValue : shock.shock_value;
  const isEdited = editedValue !== undefined && editedValue !== shock.shock_value;

  return (
    <div className="flex items-center gap-2 bg-gray-900/50 rounded px-2 py-1">
      <button
        onClick={onFocus}
        className="text-[11px] text-gray-300 hover:text-white truncate flex-1 text-left"
        title={shock.reasoning}
      >
        {shock.node_id}
      </button>
      <input
        type="number"
        value={displayValue}
        onChange={(e) => onEdit(parseFloat(e.target.value) || 0)}
        min={-1}
        max={1}
        step={0.1}
        className={`w-16 text-right text-[11px] font-mono bg-gray-800 border rounded px-1 py-0.5 focus:outline-none ${
          isEdited ? "border-purple-500 text-purple-300" :
          displayValue > 0 ? "border-green-700/50 text-green-400" :
          displayValue < 0 ? "border-red-700/50 text-red-400" :
          "border-gray-700 text-gray-400"
        }`}
      />
    </div>
  );
}
