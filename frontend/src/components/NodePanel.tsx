"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { useNodeSelection } from "@/hooks/useNodeSelection";
import { sentimentToColor, edgeDirectionColor } from "@/lib/graphTransforms";
import { useGraphStore } from "@/hooks/useGraphData";

const SentimentChart = dynamic(() => import("./SentimentChart"), { ssr: false });
const BacktestChart = dynamic(() => import("./BacktestChart"), { ssr: false });

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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
  const { selectedNode, handleDeepDive, clearSelection } = useNodeSelection();
  const agentRunning = useGraphStore((s) => s.agentRunning);
  const links = useGraphStore((s) => s.links);
  const anomalies = useGraphStore((s) => s.anomalies);

  const [rawData, setRawData] = useState<RawDataPoint[]>([]);
  const [rawLoading, setRawLoading] = useState(false);

  useEffect(() => {
    if (!selectedNode) {
      setRawData([]);
      return;
    }
    let cancelled = false;
    setRawLoading(true);
    fetch(`${API}/api/graph/raw-data/${selectedNode.id}?limit=5`)
      .then((r) => r.json())
      .then((data: RawDataPoint[]) => {
        if (!cancelled) setRawData(data);
      })
      .catch(() => {
        if (!cancelled) setRawData([]);
      })
      .finally(() => {
        if (!cancelled) setRawLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedNode?.id]);

  if (!selectedNode) return null;

  const sentimentColor = sentimentToColor(selectedNode.sentiment);
  const sentimentLabel =
    selectedNode.sentiment > 0.2
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

      <p className="text-sm text-gray-400 mb-3">{selectedNode.description}</p>

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
        </div>
      </div>

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
                    {new Date(rd.timestamp).toLocaleDateString()}
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

      {selectedNode.evidence && selectedNode.evidence.length > 0 && (
        <div className="mb-4">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">
            Evidence
          </h4>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {selectedNode.evidence.map((e, i) => (
              <div key={i} className="text-xs text-gray-300 bg-gray-800 rounded p-2">
                {e.text}
                <div className="text-gray-500 mt-0.5">
                  {new Date(e.timestamp).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

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
