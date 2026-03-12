"use client";

import { useGraphStore } from "@/hooks/useGraphData";
import { sentimentToColor } from "@/lib/graphTransforms";

export default function SentimentTimeline() {
  const nodes = useGraphStore((s) => s.nodes);

  // Sort by absolute sentiment to show most active nodes
  const sorted = [...nodes]
    .sort((a, b) => Math.abs(b.sentiment) - Math.abs(a.sentiment))
    .slice(0, 12);

  return (
    <div className="absolute bottom-16 left-4 right-4 z-[5] bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg p-3">
      <h3 className="text-white text-xs font-semibold uppercase mb-2">
        Top Sentiment Signals
      </h3>
      <div className="flex gap-2 overflow-x-auto pb-1">
        {sorted.map((node) => (
          <div
            key={node.id}
            className="flex-shrink-0 bg-gray-800 rounded px-3 py-1.5 text-xs"
          >
            <div className="text-gray-400 whitespace-nowrap">{node.label}</div>
            <div
              className="font-mono font-semibold"
              style={{ color: sentimentToColor(node.sentiment) }}
            >
              {node.sentiment > 0 ? "+" : ""}
              {node.sentiment.toFixed(2)}
            </div>
          </div>
        ))}
        {sorted.length === 0 && (
          <div className="text-gray-500 text-xs">
            No sentiment data yet. Run an analysis to populate.
          </div>
        )}
      </div>
    </div>
  );
}
