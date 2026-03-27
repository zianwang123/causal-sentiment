"use client";

import { useEffect } from "react";
import { create } from "zustand";
import type {
  AgentRun,
  AnomalyInfo,
  CompareBranchEntry,
  ForceGraphLink,
  ForceGraphNode,
  GraphData,
  GraphNode,
  QuickTrigger,
  RegimeInfo,
  ScenarioProgress,
  ScenarioResult,
  ScenarioShock,
  ScenarioSummary,
  SimulationResult,
} from "@/types/graph";
import { transformGraphData } from "@/lib/graphTransforms";
import { wsClient } from "@/lib/websocket";

import { API_URL } from "@/lib/config";

// Module-level timeout ID for agent safety timeout (avoids `as any` on store)
let agentTimeoutId: ReturnType<typeof setTimeout> | null = null;

interface AgentProgress {
  round: number;
  maxRounds: number;
  totalToolCalls: number;
  toolCalls: string[];
  phase: string | null;
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
  edgeDisplayMode: "all" | "selected" | "none";
  edgeWeightThreshold: number;
  simulation: SimulationResult | null;
  loading: boolean;
  error: string | null;

  // Scenario engine
  scenarioResult: ScenarioResult | null;
  scenarioLoading: boolean;
  scenarioProgress: ScenarioProgress | null;
  scenarioHistory: ScenarioSummary[];
  quickTriggers: QuickTrigger[];

  focusNode: (nodeId: string) => void;
  fetchGraph: () => Promise<void>;
  fetchAnomalies: () => Promise<void>;
  fetchRegime: () => Promise<void>;
  fetchSnapshot: (timestamp: string) => Promise<void>;
  clearSnapshot: () => void;
  toggleClustered: () => void;
  setEdgeDisplayMode: (mode: "all" | "selected" | "none") => void;
  setEdgeWeightThreshold: (val: number) => void;
  setSelectedNode: (node: ForceGraphNode | null) => void;
  triggerAnalysis: (nodeIds?: string[]) => Promise<void>;
  updateFromWs: (data: GraphData) => void;
  runSimulation: (nodeId: string, sentiment: number) => Promise<void>;
  clearSimulation: () => void;

  // Scenario actions
  triggerScenario: (trigger: string, triggerType?: string) => Promise<void>;
  fetchScenario: (id: number) => Promise<void>;
  fetchScenarioHistory: () => Promise<void>;
  fetchQuickTriggers: () => Promise<void>;
  applyScenarioBranch: (scenarioId: number, branchIdx: number, overrides?: Array<{node_id: string; shock_value: number}>) => Promise<void>;
  evolveGraph: (scenarioId: number, branchIdx: number) => Promise<void>;
  resetEvolve: () => Promise<void>;
  hypotheticalNodeIds: string[];
  clearScenario: () => void;
  chainScenario: (parentId: number, branchIdx: number, followUpTrigger: string) => Promise<void>;

  // Scenario comparison
  scenarioCompareMode: boolean;
  scenarioCompareBranches: CompareBranchEntry[];
  toggleCompareMode: () => void;
  addCompareBranch: (scenarioId: number, branchIdx: number, title: string, shocks: ScenarioShock[]) => void;
  removeCompareBranch: (scenarioId: number, branchIdx: number) => void;
  clearCompareBranches: () => void;
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
  edgeDisplayMode: "selected",
  edgeWeightThreshold: 0.0,
  simulation: null,
  loading: false,
  error: null,

  // Scenario engine
  scenarioResult: null,
  scenarioLoading: false,
  scenarioProgress: null,
  scenarioHistory: [],
  quickTriggers: [],
  hypotheticalNodeIds: [],

  // Scenario comparison
  scenarioCompareMode: false,
  scenarioCompareBranches: [],

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

  setEdgeDisplayMode: (mode) => set({ edgeDisplayMode: mode }),
  setEdgeWeightThreshold: (val) => set({ edgeWeightThreshold: val }),

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
    // Reset hypothetical nodes before running analysis
    const hypo = get().hypotheticalNodeIds;
    if (hypo.length > 0) {
      await get().resetEvolve();
    }
    set({ agentRunning: true, agentProgress: null });
    try {
      const res = await fetch(`${API_URL}/api/agent/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_ids: nodeIds || null }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      // Response returns immediately — analysis runs in background
      // agentRunning stays true until WebSocket sends completion
      // Safety timeout: reset after 15 minutes if no agent_complete arrives
      const timeoutId = setTimeout(() => {
        if (useGraphStore.getState().agentRunning) {
          useGraphStore.setState({
            agentRunning: false,
            agentProgress: null,
            error: "Agent analysis timed out (15 min). Check backend logs.",
          });
        }
      }, 15 * 60 * 1000);
      // Store timeout so it can be cleared on normal completion
      agentTimeoutId = timeoutId;
    } catch (e) {
      set({ error: (e as Error).message, agentRunning: false, agentProgress: null });
    }
  },

  updateFromWs: (data) => {
    const { nodes, links } = transformGraphData(data);
    set({ nodes, links });
  },

  runSimulation: async (nodeId, sentiment) => {
    try {
      const res = await fetch(`${API_URL}/api/graph/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_id: nodeId, hypothetical_sentiment: sentiment }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: SimulationResult = await res.json();
      set({ simulation: data });
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  clearSimulation: () => set({ simulation: null }),

  // Scenario engine methods
  triggerScenario: async (trigger, triggerType) => {
    set({ scenarioLoading: true, scenarioProgress: null, scenarioResult: null, error: null });
    try {
      const res = await fetch(`${API_URL}/api/scenarios`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trigger: trigger || "", trigger_type: triggerType || "user_prompt" }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      // Runs in background — result arrives via WebSocket
    } catch (e) {
      set({ error: (e as Error).message, scenarioLoading: false, scenarioProgress: null });
    }
  },

  fetchScenario: async (id) => {
    try {
      const res = await fetch(`${API_URL}/api/scenarios/${id}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: ScenarioResult = await res.json();
      set({ scenarioResult: data, scenarioLoading: false });
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  fetchScenarioHistory: async () => {
    try {
      const res = await fetch(`${API_URL}/api/scenarios?limit=20`);
      if (!res.ok) return;
      const data: ScenarioSummary[] = await res.json();
      set({ scenarioHistory: data });
    } catch {
      // Silently fail
    }
  },

  fetchQuickTriggers: async () => {
    try {
      const res = await fetch(`${API_URL}/api/scenarios/quick-triggers`);
      if (!res.ok) return;
      const data: QuickTrigger[] = await res.json();
      set({ quickTriggers: data });
    } catch {
      // Silently fail
    }
  },

  applyScenarioBranch: async (scenarioId, branchIdx, overrides) => {
    try {
      const res = await fetch(`${API_URL}/api/scenarios/${scenarioId}/apply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ branch_idx: branchIdx, shock_overrides: overrides || null }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      // Store as simulation result for graph overlay
      set({
        simulation: {
          source_node: "scenario",
          source_label: data.branch_title || "Scenario",
          initial_signal: 0,
          current_sentiment: 0,
          shock_delta: 0,
          regime: "",
          impacts: data.impacts.map((i: { node_id: string; label: string; total_impact: number; contributing_shocks: string[]; hops: number }) => ({
            node_id: i.node_id,
            label: i.label,
            impact: i.total_impact,
            path: i.contributing_shocks,
            hops: i.hops,
          })),
          total_nodes_affected: data.total_nodes_affected,
        },
      });
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  evolveGraph: async (scenarioId, branchIdx) => {
    try {
      const res = await fetch(`${API_URL}/api/scenarios/${scenarioId}/evolve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ branch_idx: branchIdx }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      set({ hypotheticalNodeIds: data.nodes_added?.map((n: { id: string }) => n.id) || [] });
      // Graph auto-updates via WebSocket broadcast from backend
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  resetEvolve: async () => {
    try {
      const res = await fetch(`${API_URL}/api/scenarios/reset-evolve`, { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      set({ hypotheticalNodeIds: [] });
      // Graph auto-updates via WebSocket
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  clearScenario: () => set({ scenarioResult: null, scenarioLoading: false, scenarioProgress: null }),

  // Scenario chaining
  chainScenario: async (parentId: number, branchIdx: number, followUpTrigger: string) => {
    try {
      set({ scenarioLoading: true, scenarioProgress: null });
      const res = await fetch(`${API_URL}/api/scenarios/${parentId}/chain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ branch_idx: branchIdx, follow_up_trigger: followUpTrigger }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      // Result arrives via WebSocket — just like normal scenario trigger
    } catch (e) {
      set({ scenarioLoading: false, error: (e as Error).message });
    }
  },

  // Scenario comparison
  toggleCompareMode: () => set((s) => ({
    scenarioCompareMode: !s.scenarioCompareMode,
    scenarioCompareBranches: !s.scenarioCompareMode ? s.scenarioCompareBranches : [],
  })),
  addCompareBranch: (scenarioId: number, branchIdx: number, title: string, shocks: ScenarioShock[]) =>
    set((s) => {
      // Max 2 branches for comparison
      if (s.scenarioCompareBranches.length >= 2) return s;
      // Prevent duplicate
      if (s.scenarioCompareBranches.some((b) => b.scenarioId === scenarioId && b.branchIdx === branchIdx)) return s;
      return {
        scenarioCompareBranches: [...s.scenarioCompareBranches, { scenarioId, branchIdx, title, shocks }],
      };
    }),
  removeCompareBranch: (scenarioId: number, branchIdx: number) =>
    set((s) => ({
      scenarioCompareBranches: s.scenarioCompareBranches.filter(
        (b) => !(b.scenarioId === scenarioId && b.branchIdx === branchIdx)
      ),
    })),
  clearCompareBranches: () => set({ scenarioCompareBranches: [] }),
}));

export function useGraphWebSocket() {
  useEffect(() => {
    wsClient.connect();
    const unsub = wsClient.on("graph_update", (data) => {
      useGraphStore.getState().updateFromWs(data as GraphData);
    });
    const unsubRegime = wsClient.on("regime_update", (data) => {
      useGraphStore.setState({ regime: data as RegimeInfo });
    });
    const unsubProgress = wsClient.on("agent_progress", (data) => {
      const d = data as { round: number; max_rounds: number; tool_calls: string[]; total_tool_calls: number; phase?: string };
      useGraphStore.setState({
        agentRunning: true,
        agentProgress: {
          round: d.round,
          maxRounds: d.max_rounds,
          totalToolCalls: d.total_tool_calls,
          toolCalls: d.tool_calls,
          phase: d.phase || null,
        },
      });
    });
    const unsubComplete = wsClient.on("agent_complete", () => {
      // Clear safety timeout
      if (agentTimeoutId) {
        clearTimeout(agentTimeoutId);
        agentTimeoutId = null;
      }
      useGraphStore.setState({ agentRunning: false, agentProgress: null });
      useGraphStore.getState().fetchGraph();
    });
    // Scenario engine WebSocket listeners
    const unsubScenarioProgress = wsClient.on("scenario_progress", (data) => {
      const d = data as ScenarioProgress;
      useGraphStore.setState({
        scenarioLoading: true,
        scenarioProgress: d,
      });
    });
    const unsubScenarioComplete = wsClient.on("scenario_complete", (data) => {
      const d = data as { scenario_id: number; status: string; error?: string };
      if (d.status === "error") {
        useGraphStore.setState({
          scenarioLoading: false,
          scenarioProgress: null,
          error: d.error || "Scenario generation failed",
        });
      } else if (d.scenario_id > 0) {
        // Fetch the full result
        useGraphStore.getState().fetchScenario(d.scenario_id);
        useGraphStore.getState().fetchScenarioHistory();
      } else {
        useGraphStore.setState({ scenarioLoading: false, scenarioProgress: null });
      }
    });
    return () => {
      unsub();
      unsubRegime();
      unsubProgress();
      unsubComplete();
      unsubScenarioProgress();
      unsubScenarioComplete();
    };
  }, []);
}
