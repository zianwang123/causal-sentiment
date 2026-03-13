"use client";

import { useCallback, useEffect, useState } from "react";
import Graph3D from "@/components/Graph3D";
import NodePanel from "@/components/NodePanel";
import FilterBar from "@/components/FilterBar";
import SentimentTimeline from "@/components/SentimentTimeline";
import AgentRunLog from "@/components/AgentRunLog";
import TimeSlider from "@/components/TimeSlider";
import PortfolioPanel from "@/components/PortfolioPanel";
import TopologySuggestions from "@/components/TopologySuggestions";
import UserGuide from "@/components/UserGuide";
import NodeLocator from "@/components/NodeLocator";
import { useGraphStore, useGraphWebSocket } from "@/hooks/useGraphData";

export default function Home() {
  const fetchGraph = useGraphStore((s) => s.fetchGraph);
  const loading = useGraphStore((s) => s.loading);
  const error = useGraphStore((s) => s.error);
  const [portfolioNodeIds, setPortfolioNodeIds] = useState<string[]>([]);

  useGraphWebSocket();

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  const handlePortfolioNodes = useCallback((nodeIds: string[]) => {
    setPortfolioNodeIds(nodeIds);
  }, []);

  return (
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
      <FilterBar />
      <NodePanel />
      <UserGuide />
      <SentimentTimeline />

      {/* Bottom toolbar: centered */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 flex items-end gap-2">
        <AgentRunLog />
        <NodeLocator />
        <TopologySuggestions />
        <TimeSlider />
        <PortfolioPanel onPortfolioNodes={handlePortfolioNodes} />
      </div>
    </main>
  );
}
