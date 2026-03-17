"use client";

import { useCallback, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { useNodeSelection } from "@/hooks/useNodeSelection";
import { sentimentToColor, edgeDirectionColor, isRiskNode } from "@/lib/graphTransforms";
import { useGraphStore } from "@/hooks/useGraphData";

const SentimentChart = dynamic(() => import("./SentimentChart"), { ssr: false });
const BacktestChart = dynamic(() => import("./BacktestChart"), { ssr: false });

import { API_URL as API } from "@/lib/config";
import { parseUTCTimestamp } from "@/lib/dateUtils";


function SimulationSlider({ nodeId, currentSentiment }: { nodeId: string; currentSentiment: number }) {
  const runSimulation = useGraphStore((s) => s.runSimulation);
  const clearSimulation = useGraphStore((s) => s.clearSimulation);
  const simulation = useGraphStore((s) => s.simulation);
  const [value, setValue] = useState(currentSentiment);
  const [running, setRunning] = useState(false);

  // Reset slider when node changes
  useEffect(() => {
    setValue(currentSentiment);
  }, [nodeId, currentSentiment]);

  const handleSimulate = useCallback(async () => {
    setRunning(true);
    await runSimulation(nodeId, value);
    setRunning(false);
  }, [nodeId, value, runSimulation]);

  const isActive = simulation?.source_node === nodeId;

  return (
    <div className="mb-4 bg-gray-800 rounded p-3">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-xs font-semibold text-gray-400 uppercase">What-If Shock</h4>
        {isActive && (
          <button
            onClick={clearSimulation}
            className="text-[10px] text-gray-500 hover:text-gray-300"
          >
            Clear
          </button>
        )}
      </div>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[10px] text-red-400 w-6">-1.0</span>
        <input
          type="range"
          min={-1}
          max={1}
          step={0.05}
          value={value}
          onChange={(e) => setValue(parseFloat(e.target.value))}
          className="flex-1 h-1.5 accent-orange-500"
        />
        <span className="text-[10px] text-green-400 w-6">+1.0</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono" style={{ color: sentimentToColor(value) }}>
          {value >= 0 ? "+" : ""}{value.toFixed(2)}
          <span className="text-gray-500 ml-1">
            (delta: {(value - currentSentiment) >= 0 ? "+" : ""}{(value - currentSentiment).toFixed(2)})
          </span>
        </span>
        <button
          onClick={handleSimulate}
          disabled={running || Math.abs(value - currentSentiment) < 0.01}
          className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-[11px] py-1 px-3 rounded transition-colors"
        >
          {running ? "..." : "Simulate"}
        </button>
      </div>
      {isActive && (
        <div className="mt-2 text-[10px] text-orange-300">
          {simulation.total_nodes_affected} nodes affected · regime: {simulation.regime}
        </div>
      )}
    </div>
  );
}

import type { Annotation } from "@/types/graph";

function AnnotationsSection({ nodeId }: { nodeId: string }) {
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [newText, setNewText] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API}/api/annotations?node_id=${nodeId}`, { signal: controller.signal })
      .then((r) => r.json())
      .then((data) => setAnnotations(data))
      .catch((e) => {
        if (e.name !== "AbortError") setAnnotations([]);
      });
    return () => controller.abort();
  }, [nodeId]);

  const handleAdd = async () => {
    if (!newText.trim()) return;
    setSaving(true);
    try {
      const res = await fetch(`${API}/api/annotations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_id: nodeId, text: newText.trim() }),
      });
      if (res.ok) {
        const created: Annotation = await res.json();
        setAnnotations((prev) => [created, ...prev]);
        setNewText("");
      } else {
        console.error("Failed to save annotation:", res.status);
      }
    } catch (e) {
      console.error("Failed to save annotation:", e);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      const res = await fetch(`${API}/api/annotations/${id}`, { method: "DELETE" });
      if (!res.ok) {
        console.error("Failed to delete annotation:", res.status);
        return;
      }
      setAnnotations((prev) => prev.filter((a) => a.id !== id));
    } catch (e) {
      console.error("Failed to delete annotation:", e);
    }
  };

  const handleTogglePin = async (a: Annotation) => {
    try {
      const res = await fetch(`${API}/api/annotations/${a.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pinned: !a.pinned }),
      });
      if (!res.ok) {
        console.error("Failed to update annotation:", res.status);
        return;
      }
      const updated: Annotation = await res.json();
      setAnnotations((prev) =>
        prev.map((x) => (x.id === updated.id ? updated : x))
          .sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0))
      );
    } catch (e) {
      console.error("Failed to update annotation:", e);
    }
  };

  return (
    <div className="mb-4">
      <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">
        Analyst Notes ({annotations.length})
      </h4>
      {annotations.length > 0 && (
        <div className="space-y-1 max-h-28 overflow-y-auto mb-2">
          {annotations.map((a) => (
            <div
              key={a.id}
              className={`text-xs rounded px-2 py-1.5 ${a.pinned ? "bg-yellow-900/20 border border-yellow-800/30" : "bg-gray-800"}`}
            >
              <div className="flex items-start justify-between gap-1">
                <span className="text-gray-300 flex-1">{a.text}</span>
                <div className="flex gap-1 flex-shrink-0 mt-0.5">
                  <button
                    onClick={() => handleTogglePin(a)}
                    className={`text-[10px] ${a.pinned ? "text-yellow-400" : "text-gray-600 hover:text-gray-400"}`}
                    title={a.pinned ? "Unpin" : "Pin"}
                  >
                    {a.pinned ? "\u2605" : "\u2606"}
                  </button>
                  <button
                    onClick={() => handleDelete(a.id)}
                    className="text-[10px] text-gray-600 hover:text-red-400"
                    title="Delete"
                  >
                    &times;
                  </button>
                </div>
              </div>
              <div className="text-[10px] text-gray-500 mt-0.5">
                {new Date(a.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}
      <div className="flex gap-1">
        <input
          type="text"
          value={newText}
          onChange={(e) => setNewText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAdd()}
          placeholder="Add a note..."
          className="flex-1 bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-gray-500"
        />
        <button
          onClick={handleAdd}
          disabled={saving || !newText.trim()}
          className="bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white text-xs px-2 py-1 rounded transition-colors"
        >
          Add
        </button>
      </div>
    </div>
  );
}


interface RawDataPoint {
  source: string;
  timestamp: string;
  data: Record<string, unknown>;
}

const SOURCE_LABELS: Record<string, string> = {
  fred_scheduled: "FRED",
  market_scheduled: "Market",
  edgar_scheduled: "EDGAR",
};

function formatRawData(source: string, data: Record<string, unknown>) {
  if (source === "market_scheduled") {
    const parts: string[] = [];
    if (data.close != null) parts.push(`Close: $${Number(data.close).toFixed(2)}`);
    if (data.open != null) parts.push(`Open: $${Number(data.open).toFixed(2)}`);
    if (data.high != null) parts.push(`High: $${Number(data.high).toFixed(2)}`);
    if (data.low != null) parts.push(`Low: $${Number(data.low).toFixed(2)}`);
    if (data.volume != null) parts.push(`Vol: ${Number(data.volume).toLocaleString()}`);
    if (data.change_pct != null) parts.push(`Chg: ${Number(data.change_pct).toFixed(2)}%`);
    if (parts.length > 0) return parts;
  }
  if (source === "fred_scheduled") {
    const parts: string[] = [];
    if (data.value != null) parts.push(`Value: ${Number(data.value).toFixed(4)}`);
    if (data.series_id) parts.push(`Series: ${String(data.series_id)}`);
    if (data.date) parts.push(`Date: ${String(data.date)}`);
    if (parts.length > 0) return parts;
  }
  // Fallback: show all keys
  return Object.entries(data).map(([k, v]) => `${k}: ${typeof v === "number" ? Number(v).toFixed(4) : String(v)}`);
}

export default function NodePanel() {
  const { selectedNode: rawSelectedNode, handleDeepDive, clearSelection } = useNodeSelection();
  const agentRunning = useGraphStore((s) => s.agentRunning);
  const nodes = useGraphStore((s) => s.nodes);
  const links = useGraphStore((s) => s.links);
  const anomalies = useGraphStore((s) => s.anomalies);

  // Always use the freshest node data from the store
  const selectedNode = rawSelectedNode
    ? nodes.find((n) => n.id === rawSelectedNode.id) ?? rawSelectedNode
    : null;

  const [rawData, setRawData] = useState<RawDataPoint[]>([]);
  const [rawLoading, setRawLoading] = useState(false);

  useEffect(() => {
    if (!selectedNode) {
      setRawData([]);
      return;
    }
    const controller = new AbortController();
    setRawLoading(true);
    fetch(`${API}/api/graph/raw-data/${selectedNode.id}?limit=5`, { signal: controller.signal })
      .then((r) => r.json())
      .then((data: RawDataPoint[]) => {
        setRawData(data);
      })
      .catch((e) => {
        if (e.name !== "AbortError") setRawData([]);
      })
      .finally(() => {
        if (!controller.signal.aborted) setRawLoading(false);
      });
    return () => {
      controller.abort();
    };
  }, [selectedNode?.id]);

  if (!selectedNode) return null;

  const sentimentColor = sentimentToColor(selectedNode.sentiment, selectedNode.id);
  const risk = isRiskNode(selectedNode.id);
  const sentimentLabel = risk
    ? selectedNode.sentiment > 0.2
      ? "Elevated"
      : selectedNode.sentiment < -0.2
        ? "Subdued"
        : "Neutral"
    : selectedNode.sentiment > 0.2
      ? "Bullish"
      : selectedNode.sentiment < -0.2
        ? "Bearish"
        : "Neutral";

  return (
    <div className="absolute top-4 right-4 w-80 bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg shadow-xl p-4 text-white z-10">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">{selectedNode.label}</h3>
        <button
          onClick={clearSelection}
          className="text-gray-400 hover:text-white text-xl leading-none"
        >
          &times;
        </button>
      </div>

      <p className="text-sm text-gray-400 mb-2">{selectedNode.description}</p>
      <div className={`text-[10px] px-2 py-1 rounded mb-3 ${
        risk
          ? "bg-red-900/20 text-red-400 border border-red-800/30"
          : "bg-green-900/20 text-green-400 border border-green-800/30"
      }`}>
        {risk
          ? "Risk indicator — positive = elevated risk (bad for markets), negative = low risk (good)"
          : "Asset indicator — positive = bullish (good for markets), negative = bearish (bad)"}
      </div>

      {(() => {
        const anomaly = anomalies.find((a) => a.node_id === selectedNode.id);
        if (!anomaly) return null;
        return (
          <div className={`mb-3 px-3 py-2 rounded text-xs border ${
            anomaly.direction === "up"
              ? "bg-yellow-900/30 border-yellow-700/50 text-yellow-300"
              : "bg-red-900/30 border-red-700/50 text-red-300"
          }`}>
            <div className="font-semibold">
              Anomaly Detected ({anomaly.z_score > 0 ? "+" : ""}{anomaly.z_score.toFixed(1)}σ {anomaly.direction})
            </div>
            <div className="text-[10px] mt-0.5 opacity-80">
              Latest: {anomaly.latest_value.toFixed(4)} · Mean: {anomaly.mean.toFixed(4)} · Std: {anomaly.std.toFixed(4)}
            </div>
          </div>
        );
      })()}

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-gray-800 rounded p-2">
          <div className="text-xs text-gray-400">Sentiment</div>
          <div className="text-xl font-mono" style={{ color: sentimentColor }}>
            {selectedNode.sentiment.toFixed(3)}
          </div>
          <div className="text-xs" style={{ color: sentimentColor }}>
            {sentimentLabel}
          </div>
        </div>
        <div className="bg-gray-800 rounded p-2">
          <div className="text-xs text-gray-400">Confidence</div>
          <div className="text-xl font-mono">
            {(selectedNode.confidence * 100).toFixed(0)}%
          </div>
          {(() => {
            const breakdown = selectedNode.evidence?.[0]?.confidence_breakdown;
            if (!breakdown) return null;
            return (
              <div className="mt-1 space-y-0.5">
                <div className="flex justify-between text-[9px]">
                  <span className="text-gray-500">Freshness</span>
                  <span className="text-gray-400">{(breakdown.data_freshness * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between text-[9px]">
                  <span className="text-gray-500">Agreement</span>
                  <span className="text-gray-400">{(breakdown.source_agreement * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between text-[9px]">
                  <span className="text-gray-500">Strength</span>
                  <span className="text-gray-400">{(breakdown.signal_strength * 100).toFixed(0)}%</span>
                </div>
              </div>
            );
          })()}
        </div>
      </div>

      {/* What-If Simulator */}
      <SimulationSlider nodeId={selectedNode.id} currentSentiment={selectedNode.sentiment} />

      <SentimentChart nodeId={selectedNode.id} />

      <BacktestChart nodeId={selectedNode.id} />

      {/* Raw Data */}
      {rawLoading ? (
        <div className="mb-4 text-xs text-gray-500">Loading raw data...</div>
      ) : rawData.length > 0 ? (
        <div className="mb-4">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">
            Raw Data
          </h4>
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {rawData.map((rd, i) => (
              <div key={i} className="text-xs bg-gray-800 rounded px-2 py-1.5">
                <div className="flex items-center justify-between mb-0.5">
                  <span className="font-medium text-gray-300">
                    {SOURCE_LABELS[rd.source] ?? rd.source}
                  </span>
                  <span className="text-[10px] text-gray-500">
                    {parseUTCTimestamp(rd.timestamp).toLocaleDateString()}
                  </span>
                </div>
                <div className="text-gray-400 space-y-px">
                  {formatRawData(rd.source, rd.data).map((line, j) => (
                    <div key={j}>{line}</div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {/* Data Sources Provenance */}
      {selectedNode.evidence?.[0]?.data_sources && (
        <div className="mb-4">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">
            Data Sources
          </h4>
          <div className="space-y-1">
            {Object.entries(selectedNode.evidence[0].data_sources as Record<string, { status: string; series?: string; latest_value?: string; ticker?: string; close?: number; change_pct?: number; count?: number; best_tier?: number }>).map(([source, info]) => {
              if (source === "_none") return (
                <div key={source} className="text-[10px] text-yellow-400 bg-yellow-900/20 rounded px-2 py-1">
                  No direct data source — sentiment inferred from causal neighbors
                </div>
              );
              const statusColor = info.status === "real" ? "text-green-400" : info.status === "mock" ? "text-yellow-400" : "text-gray-500";
              const statusIcon = info.status === "real" ? "\u2713" : info.status === "mock" ? "\u26a0" : "\u2717";
              const statusLabel = info.status?.toUpperCase() || "N/A";
              let detail = "";
              if (source === "fred" && info.series) detail = `${info.series}: ${info.latest_value ?? "N/A"}`;
              else if (source === "yfinance" && info.ticker) detail = `${info.ticker}: $${info.close ?? "N/A"} (${(info.change_pct ?? 0) >= 0 ? "+" : ""}${(info.change_pct ?? 0).toFixed(2)}%)`;
              else if (source === "rss") detail = `${info.count ?? 0} articles, best T${info.best_tier ?? 3}`;
              return (
                <div key={source} className="flex items-center justify-between text-[10px] bg-gray-800 rounded px-2 py-1">
                  <div className="flex items-center gap-1.5">
                    <span className={statusColor}>{statusIcon}</span>
                    <span className="text-gray-300 font-medium uppercase">{source}</span>
                    <span className="text-gray-500">{detail}</span>
                  </div>
                  <span className={`text-[9px] ${statusColor}`}>{statusLabel}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {selectedNode.evidence && selectedNode.evidence.length > 0 && (
        <div className="mb-4">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">
            Evidence
          </h4>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {selectedNode.evidence.map((e, i) => (
              <div key={i} className={`text-xs text-gray-300 bg-gray-800 rounded p-2 ${i === 0 ? "border border-blue-800/50" : ""}`}>
                {e.text}
                <div className="flex items-center gap-1 mt-0.5 flex-wrap">
                  <span className="text-[10px] text-gray-500">
                    {parseUTCTimestamp(e.timestamp).toLocaleString()}
                  </span>
                  {i === 0 && (
                    <span className="text-[9px] bg-blue-900/50 text-blue-300 rounded px-1 py-px">latest</span>
                  )}
                  {e.sources?.map((src, j) => (
                    <span key={j} className="text-[9px] bg-blue-900/50 text-blue-300 rounded px-1 py-px">
                      {src}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analyst Notes */}
      <AnnotationsSection nodeId={selectedNode.id} />

      {/* Connected Edges */}
      {(() => {
        const connectedEdges = links.filter(
          (l) => {
            const src = typeof l.source === "string" ? l.source : (l.source as { id: string }).id;
            const tgt = typeof l.target === "string" ? l.target : (l.target as { id: string }).id;
            return src === selectedNode.id || tgt === selectedNode.id;
          }
        );
        if (connectedEdges.length === 0) return null;
        return (
          <div className="mb-4">
            <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">
              Causal Edges ({connectedEdges.length})
            </h4>
            <div className="space-y-1 max-h-36 overflow-y-auto">
              {connectedEdges.map((edge, i) => {
                const src = typeof edge.source === "string" ? edge.source : (edge.source as { id: string }).id;
                const tgt = typeof edge.target === "string" ? edge.target : (edge.target as { id: string }).id;
                const isOutgoing = src === selectedNode.id;
                const otherNode = isOutgoing ? tgt : src;
                const diverged = Math.abs(edge.baseWeight - edge.dynamicWeight) > 0.05;
                return (
                  <div key={i} className="text-xs bg-gray-800 rounded px-2 py-1.5">
                    <div className="flex items-center gap-1.5">
                      <span
                        className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                        style={{ backgroundColor: edgeDirectionColor(edge.direction) }}
                      />
                      <span className="text-gray-300 truncate">
                        {isOutgoing ? `→ ${otherNode}` : `${otherNode} →`}
                      </span>
                      <span className="text-gray-500 ml-auto flex-shrink-0">
                        {edge.direction}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-0.5 text-[10px]">
                      <span className="text-gray-500">
                        base: {edge.baseWeight.toFixed(2)}
                      </span>
                      <span className={diverged ? "text-yellow-400" : "text-gray-500"}>
                        dyn: {edge.dynamicWeight.toFixed(2)}
                        {diverged && " ⚡"}
                      </span>
                      <span className="text-gray-400">
                        eff: {edge.weight.toFixed(2)}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })()}

      <div className="flex gap-2">
        <button
          onClick={() => handleDeepDive(selectedNode.id)}
          disabled={agentRunning}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-sm py-2 px-3 rounded transition-colors"
        >
          {agentRunning ? "Analyzing..." : "Deep Dive"}
        </button>
      </div>

      <div className="mt-2 text-xs text-gray-500">
        Type: {selectedNode.nodeType} · Centrality:{" "}
        {selectedNode.centrality.toFixed(3)}
      </div>
    </div>
  );
}
