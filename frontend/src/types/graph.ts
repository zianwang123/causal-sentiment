export interface ConfidenceBreakdown {
  data_freshness: number;
  source_agreement: number;
  signal_strength: number;
}

export interface GraphNode {
  id: string;
  label: string;
  node_type: string;
  description: string;
  composite_sentiment: number;
  confidence: number;
  evidence: Array<{ text: string; timestamp: string; sources?: string[]; confidence_breakdown?: ConfidenceBreakdown; data_sources?: Record<string, Record<string, unknown>> }>;
  centrality: number;
}

export interface GraphEdge {
  id: number;
  source_id: string;
  target_id: string;
  direction: "positive" | "negative" | "complex";
  base_weight: number;
  dynamic_weight: number;
  description: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface AgentRun {
  id: number;
  trigger: string;
  status: string;
  nodes_analyzed: string[];
  tool_calls: Array<{ tool: string; input: Record<string, unknown>; output?: string; round: number; phase?: string }> | null;
  summary: string | null;
  started_at: string;
  finished_at: string | null;
  error: string | null;
}

// react-force-graph-3d expects these shapes
export interface ForceGraphNode {
  id: string;
  label: string;
  nodeType: string;
  sentiment: number;
  confidence: number;
  centrality: number;
  description: string;
  evidence: Array<{ text: string; timestamp: string; sources?: string[]; confidence_breakdown?: ConfidenceBreakdown; data_sources?: Record<string, Record<string, unknown>> }>;
  x?: number;
  y?: number;
  z?: number;
  fx?: number;
  fy?: number;
  fz?: number;
}

export interface ForceGraphLink {
  source: string;
  target: string;
  direction: string;
  weight: number;
  baseWeight: number;
  dynamicWeight: number;
  description: string;
}

export interface RegimeInfo {
  state: "risk_on" | "risk_off" | "transitioning";
  confidence: number;
  composite_score: number;
  contributing_signals: Record<string, number>;
}

export interface AnomalyInfo {
  node_id: string;
  z_score: number;
  latest_value: number;
  mean: number;
  std: number;
  direction: "up" | "down";
  detected_at: string;
}

// What-if simulation
export interface SimulationImpact {
  node_id: string;
  label: string;
  impact: number;
  path: string[];
  hops: number;
}

export interface SimulationResult {
  source_node: string;
  source_label: string;
  initial_signal: number;
  current_sentiment: number;
  shock_delta: number;
  regime: string;
  impacts: SimulationImpact[];
  total_nodes_affected: number;
}

// Analyst annotations
export interface Annotation {
  id: number;
  node_id: string;
  text: string;
  pinned: boolean;
  created_at: string;
  updated_at: string;
}

// Scenario extrapolation engine
export interface ScenarioShock {
  node_id: string;
  shock_value: number; // [-1, 1]
  reasoning: string;
  original_impact?: string; // free-form pre-mapping description
}

export interface ScenarioNodeSuggestion {
  suggested_id: string;
  suggested_label: string;
  suggested_type: string;
  description: string;
  reasoning?: string;
}

export interface ScenarioEdgeSuggestion {
  source_id: string;
  target_id: string;
  direction: string;
  reasoning: string;
}

export interface ScenarioPrediction {
  prediction: string;
  confidence: number;
  time_window?: string;
  ticker?: string;        // present for market-checkable predictions
  direction?: "above" | "below";
  threshold?: number;
}

export interface ScenarioBranch {
  title: string;
  probability: number; // 0-1
  probability_reasoning?: string;
  narrative: string;
  causal_chain: string[];
  structural_outcome?: string;
  shocks: ScenarioShock[];
  time_horizon: string; // "days" | "weeks" | "months"
  invalidation?: string;
  key_assumption?: string;
  specific_predictions?: ScenarioPrediction[];
  node_suggestions?: ScenarioNodeSuggestion[];
  edge_suggestions?: ScenarioEdgeSuggestion[];
}

export interface ScenarioResult {
  id: number;
  trigger: string;
  trigger_type: string;
  status: string;
  branches: ScenarioBranch[];
  research_summary: string | null;
  historical_parallels: string | null;
  selected_branch_idx: number | null;
  simulation_result: Record<string, unknown> | null;
  error: string | null;
  created_at: string;
  finished_at: string | null;
  parent_scenario_id?: number | null;
  parent_branch_idx?: number | null;
}

export interface ScenarioSummary {
  id: number;
  trigger: string;
  trigger_type: string;
  status: string;
  branch_count: number;
  created_at: string;
  parent_scenario_id?: number | null;
}

// Scenario comparison
export interface CompareBranchEntry {
  scenarioId: number;
  branchIdx: number;
  title: string;
  shocks: ScenarioShock[];
}

export interface CompareNodeRow {
  nodeId: string;
  label: string;
  valA: number | undefined;
  valB: number | undefined;
  color: "green" | "red" | "blue" | "gray"; // both+, both-, opposite, unique
}

export interface QuickTrigger {
  headline: string;
  source: string;
  suggested_prompt: string;
  vulnerability?: string;
}

export interface ScenarioProgress {
  scenario_id: number;
  round: number;
  max_rounds: number;
  phase: string;
  total_tool_calls: number;
}

export type NodeTypeShape = "sphere" | "cube" | "octahedron";

export const NODE_TYPE_SHAPES: Record<string, NodeTypeShape> = {
  macro: "sphere",
  monetary_policy: "octahedron",
  geopolitics: "octahedron",
  rates_credit: "sphere",
  volatility: "sphere",
  commodities: "cube",
  equities: "cube",
  equity_fundamentals: "cube",
  currencies: "sphere",
  flows_sentiment: "sphere",
  global: "sphere",
};

// Causal Discovery types
export interface CausalNode {
  id: string;
  zscore: number;
  polarity: number;
  display_sentiment: number;
  importance: number;
}

export interface EdgeValidation {
  arrow_strength: number;
  refutation_passed: boolean;
  ci_test_p_value: number;
}

export interface CausalEdge {
  source: string;
  target: string;
  weight: number;
  lag: number;
  direction: "positive" | "negative";
  validation?: EdgeValidation | null;
}

export interface CausalGraphSnapshot {
  id: number;
  run_name: string;
  algorithm: string;
  created_at: string;
  parameters: {
    scoring: string;
    max_lag: number;
    significance_level: number;
    days: number;
    zscore_window: number;
    stats?: { density: number; avg_degree: number; clustering: number };
    [key: string]: unknown;  // allow additional params like regime_index
  };
  nodes: CausalNode[];
  edges: CausalEdge[];
  summary: {
    node_count: number;
    edge_count: number;
  };
}

export interface CausalGraphListItem {
  id: number;
  run_name: string;
  algorithm: string;
  created_at: string;
  node_count: number;
  edge_count: number;
  parameters: Record<string, unknown>;
}
