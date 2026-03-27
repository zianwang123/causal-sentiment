"use client";

import { useCallback, useEffect, useState } from "react";
import Graph3D from "@/components/Graph3D";
import NodePanel from "@/components/NodePanel";
import CausalNodePanel from "@/components/CausalNodePanel";
import FilterBar from "@/components/FilterBar";
import SentimentTimeline from "@/components/SentimentTimeline";
import AgentRunLog from "@/components/AgentRunLog";
import PredictionsPanel from "@/components/PredictionsPanel";
import TimeSlider from "@/components/TimeSlider";
import PortfolioPanel from "@/components/PortfolioPanel";
import TopologySuggestions from "@/components/TopologySuggestions";
import UserGuide from "@/components/UserGuide";
import NodeLocator from "@/components/NodeLocator";
import SimulationPanel from "@/components/SimulationPanel";
import ScenarioPanel from "@/components/ScenarioPanel";
import ChainExplorer from "@/components/ChainExplorer";
import CategoryMatrix from "@/components/CategoryMatrix";
import CausalPanel from "@/components/CausalPanel";
import CausalAnimationPlayer from "@/components/CausalAnimationPlayer";
import AutomationToggles from "@/components/AutomationToggles";
import MorningBrief from "@/components/MorningBrief";
import ErrorBoundary from "@/components/ErrorBoundary";
import { useGraphStore, useGraphWebSocket } from "@/hooks/useGraphData";
import { useCausalStore } from "@/hooks/useCausalStore";

export default function Home() {
  const fetchGraph = useGraphStore((s) => s.fetchGraph);
  const loading = useGraphStore((s) => s.loading);
  const error = useGraphStore((s) => s.error);
  const [portfolioNodeIds, setPortfolioNodeIds] = useState<string[]>([]);
  const [chainExplorerOpen, setChainExplorerOpen] = useState(false);
  const [matrixOpen, setMatrixOpen] = useState(false);
  const graphSource = useCausalStore((s) => s.graphSource);
  const isExpert = graphSource === "expert";

  useGraphWebSocket();

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  const handlePortfolioNodes = useCallback((nodeIds: string[]) => {
    setPortfolioNodeIds(nodeIds);
  }, []);

  return (
    <ErrorBoundary>
      <main className="relative w-screen h-screen">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center z-50 bg-gray-950">
            <div className="text-gray-400 text-lg">Loading graph...</div>
          </div>
        )}
        {error && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50 bg-red-900/90 text-red-200 px-4 py-2 rounded text-sm">
            {error}
          </div>
        )}
        <Graph3D portfolioNodeIds={portfolioNodeIds} />
        {isExpert && <FilterBar />}
        <CausalPanel />
        {isExpert ? <NodePanel /> : <CausalNodePanel />}
        <UserGuide />
        {isExpert && <SimulationPanel />}
        {isExpert && <ScenarioPanel />}
        {isExpert && chainExplorerOpen && (
          <ChainExplorer onClose={() => setChainExplorerOpen(false)} />
        )}
        {isExpert && matrixOpen && (
          <CategoryMatrix onClose={() => setMatrixOpen(false)} />
        )}
        {isExpert && <SentimentTimeline />}

        {/* Animation player: above bottom toolbar in discovered mode */}
        {!isExpert && <CausalAnimationPlayer />}

        {/* Bottom toolbar: centered */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 flex items-end gap-2">
          {isExpert && <MorningBrief />}
          {isExpert && <AgentRunLog />}
          {isExpert && <PredictionsPanel />}
          <NodeLocator />
          {isExpert && <TopologySuggestions />}
          {isExpert && <TimeSlider />}
          {isExpert && <PortfolioPanel onPortfolioNodes={handlePortfolioNodes} />}
          {isExpert && (
            <button
              onClick={() => setChainExplorerOpen((p) => !p)}
              className={`px-3 py-2 rounded text-xs font-medium transition-colors ${
                chainExplorerOpen
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800/90 text-gray-300 hover:bg-gray-700 border border-gray-600"
              }`}
            >
              Chains
            </button>
          )}
          {isExpert && (
            <button
              onClick={() => setMatrixOpen((p) => !p)}
              className={`px-3 py-2 rounded text-xs font-medium transition-colors ${
                matrixOpen
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800/90 text-gray-300 hover:bg-gray-700 border border-gray-600"
              }`}
            >
              Matrix
            </button>
          )}
        </div>
      </main>
    </ErrorBoundary>
  );
}
