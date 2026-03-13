"use client";

import { useEffect } from "react";
import { create } from "zustand";
import type {
  AgentRun,
  AnomalyInfo,
  ForceGraphLink,
  ForceGraphNode,
  GraphData,
  GraphNode,
  RegimeInfo,
} from "@/types/graph";
import { transformGraphData } from "@/lib/graphTransforms";
import { wsClient } from "@/lib/websocket";

import { API_URL } from "@/lib/config";

interface AgentProgress {
  round: number;
  maxRounds: number;
  totalToolCalls: number;
  toolCalls: string[];
}

interface GraphStore {
  nodes: ForceGraphNode[];
  links: ForceGraphLink[];
  selectedNode: ForceGraphNode | null;
  agentRunning: boolean;
  agentProgress: AgentProgress | null;
  lastRun: AgentRun | null;
  anomalies: AnomalyInfo[];
  regime: RegimeInfo | null;
  snapshotTimestamp: string | null;
  focusNodeId: string | null;
  clustered: boolean;
  loading: boolean;
  error: string | null;

  focusNode: (nodeId: string) => void;
  fetchGraph: () => Promise<void>;
  fetchAnomalies: () => Promise<void>;
  fetchRegime: () => Promise<void>;
  fetchSnapshot: (timestamp: string) => Promise<void>;
  clearSnapshot: () => void;
  toggleClustered: () => void;
  setSelectedNode: (node: ForceGraphNode | null) => void;
  triggerAnalysis: (nodeIds?: string[]) => Promise<void>;
  updateFromWs: (data: GraphData) => void;
}

export const useGraphStore = create<GraphStore>((set, get) => ({
  nodes: [],
  links: [],
  selectedNode: null,
  agentRunning: false,
  agentProgress: null,
  lastRun: null,
  anomalies: [],
  regime: null,
  snapshotTimestamp: null,
  focusNodeId: null,
  clustered: false,
  loading: false,
  error: null,

  fetchSnapshot: async (timestamp: string) => {
    try {
      const res = await fetch(`${API_URL}/api/graph/snapshot?timestamp=${encodeURIComponent(timestamp)}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: GraphData = await res.json();
      const { nodes, links } = transformGraphData(data);
      set({ nodes, links, snapshotTimestamp: timestamp });
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  clearSnapshot: () => {
    set({ snapshotTimestamp: null });
    // Re-fetch live data on next microtask to avoid setState-during-render
    queueMicrotask(() => {
      useGraphStore.getState().fetchGraph();
    });
  },

  toggleClustered: () => {
    set((s) => ({ clustered: !s.clustered }));
  },

  fetchRegime: async () => {
    try {
      const res = await fetch(`${API_URL}/api/graph/regime`);
      if (!res.ok) return;
      const data: RegimeInfo = await res.json();
      set({ regime: data });
    } catch {
      // Silently fail
    }
  },

  fetchAnomalies: async () => {
    try {
      const res = await fetch(`${API_URL}/api/graph/anomalies`);
      if (!res.ok) return;
      const data: AnomalyInfo[] = await res.json();
      set({ anomalies: data });
    } catch {
      // Silently fail — anomalies are supplementary
    }
  },

  fetchGraph: async () => {
    set({ loading: true, error: null });
    try {
      const res = await fetch(`${API_URL}/api/graph/full`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: GraphData = await res.json();
      const { nodes, links } = transformGraphData(data);
      set({ nodes, links, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  focusNode: (nodeId) => {
    const node = get().nodes.find((n) => n.id === nodeId) || null;
    set({ focusNodeId: nodeId, selectedNode: node });
  },

  setSelectedNode: (node) => set({ selectedNode: node }),

  triggerAnalysis: async (nodeIds) => {
    set({ agentRunning: true });
    try {
      const res = await fetch(`${API_URL}/api/agent/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_ids: nodeIds || null }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const run: AgentRun = await res.json();
      set({ lastRun: run, agentRunning: false, agentProgress: null });
      // Refresh graph after analysis
      get().fetchGraph();
    } catch (e) {
      set({ error: (e as Error).message, agentRunning: false, agentProgress: null });
    }
  },

  updateFromWs: (data) => {
    const { nodes, links } = transformGraphData(data);
    set({ nodes, links });
  },
}));

export function useGraphWebSocket() {
  const updateFromWs = useGraphStore((s) => s.updateFromWs);

  useEffect(() => {
    wsClient.connect();
    const unsub = wsClient.on("graph_update", (data) => {
      updateFromWs(data as GraphData);
    });
    const unsubRegime = wsClient.on("regime_update", (data) => {
      useGraphStore.setState({ regime: data as RegimeInfo });
    });
    const unsubProgress = wsClient.on("agent_progress", (data) => {
      const d = data as { round: number; max_rounds: number; tool_calls: string[]; total_tool_calls: number };
      useGraphStore.setState({
        agentProgress: {
          round: d.round,
          maxRounds: d.max_rounds,
          totalToolCalls: d.total_tool_calls,
          toolCalls: d.tool_calls,
        },
      });
    });
    return () => {
      unsub();
      unsubRegime();
      unsubProgress();
    };
  }, [updateFromWs]);
}
