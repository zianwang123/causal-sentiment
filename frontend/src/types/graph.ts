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
  evidence: Array<{ text: string; timestamp: string; sources?: string[]; confidence_breakdown?: ConfidenceBreakdown }>;
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
  tool_calls: Array<{ tool: string; input: Record<string, unknown>; round: number; phase?: string }> | null;
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
  evidence: Array<{ text: string; timestamp: string; sources?: string[]; confidence_breakdown?: ConfidenceBreakdown }>;
  x?: number;
  y?: number;
  z?: number;
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
