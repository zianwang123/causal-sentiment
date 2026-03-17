"use client";

import { useGraphStore } from "@/hooks/useGraphData";
import { sentimentToColor } from "@/lib/graphTransforms";

export default function SimulationPanel() {
  const simulation = useGraphStore((s) => s.simulation);
  const clearSimulation = useGraphStore((s) => s.clearSimulation);
  const focusNode = useGraphStore((s) => s.focusNode);

  if (!simulation) return null;

  return (
    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 w-[600px] max-w-[90vw] bg-gray-900/95 backdrop-blur border border-orange-700/50 rounded-lg shadow-xl p-4 text-white z-10">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-orange-400">
            What-If Impact Report
          </h3>
          <p className="text-xs text-gray-400">
            {simulation.source_label} shock: {simulation.current_sentiment.toFixed(2)} &rarr; {simulation.initial_signal.toFixed(2)}
            {" "}(delta: {simulation.shock_delta >= 0 ? "+" : ""}{simulation.shock_delta.toFixed(2)})
            {" "}&middot; regime: {simulation.regime.replace("_", " ")}
          </p>
        </div>
        <button
          onClick={clearSimulation}
          className="text-gray-400 hover:text-white text-sm px-2 py-1 border border-gray-700 rounded hover:border-gray-500 transition-colors"
        >
          Clear
        </button>
      </div>

      <div className="grid grid-cols-2 gap-1.5 max-h-48 overflow-y-auto">
        {simulation.impacts.map((imp) => (
          <button
            key={imp.node_id}
            onClick={() => focusNode(imp.node_id)}
            className="text-left bg-gray-800 hover:bg-gray-750 rounded px-2.5 py-1.5 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-300 truncate group-hover:text-white">
                {imp.label}
              </span>
              <span
                className="text-xs font-mono ml-2 flex-shrink-0"
                style={{ color: sentimentToColor(imp.impact, imp.node_id) }}
              >
                {imp.impact >= 0 ? "+" : ""}{imp.impact.toFixed(3)}
              </span>
            </div>
            <div className="text-[10px] text-gray-500 mt-0.5">
              {imp.hops} hop{imp.hops !== 1 ? "s" : ""} &middot; {imp.path.join(" → ")}
            </div>
          </button>
        ))}
      </div>

      <div className="mt-2 text-[10px] text-gray-500 text-center">
        {simulation.total_nodes_affected} nodes affected &middot; click any node to focus
      </div>
    </div>
  );
}
