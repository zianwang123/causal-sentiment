import type {
  ForceGraphLink,
  ForceGraphNode,
  GraphData,
} from "@/types/graph";

export function transformGraphData(data: GraphData): {
  nodes: ForceGraphNode[];
  links: ForceGraphLink[];
} {
  const nodes: ForceGraphNode[] = data.nodes.map((n) => ({
    id: n.id,
    label: n.label,
    nodeType: n.node_type,
    sentiment: n.composite_sentiment,
    confidence: n.confidence,
    centrality: n.centrality,
    description: n.description,
    evidence: n.evidence,
  }));

  const links: ForceGraphLink[] = data.edges.map((e) => ({
    source: e.source_id,
    target: e.target_id,
    direction: e.direction,
    weight: 0.6 * e.base_weight + 0.4 * e.dynamic_weight,
    baseWeight: e.base_weight,
    dynamicWeight: e.dynamic_weight,
    description: e.description,
  }));

  return { nodes, links };
}

// Risk nodes: positive sentiment = elevated risk = BAD for markets → show RED
// Color is inverted so green always means "market-friendly", red always means "market-threatening"
const RISK_NODE_IDS = new Set([
  "vix", "move_index", "put_call_ratio", "skew_index", "credit_default_swaps",
  "ig_credit_spread", "hy_credit_spread",
  "geopolitical_risk_index", "trade_policy_tariffs", "us_political_risk", "sanctions_pressure",
  "unemployment_rate", "us_cpi_yoy", "pce_deflator",
]);

export function isRiskNode(nodeId: string): boolean {
  return RISK_NODE_IDS.has(nodeId);
}

export function sentimentToColor(sentiment: number, nodeId?: string): string {
  // For risk nodes, invert: positive (elevated risk) → red, negative (low risk) → green
  const displaySentiment = nodeId && isRiskNode(nodeId) ? -sentiment : sentiment;

  // Red (bad) → Gray (neutral) → Green (good)
  // Apply sqrt curve to boost contrast for small sentiment values
  if (displaySentiment < -0.01) {
    const raw = Math.min(Math.abs(displaySentiment), 1);
    const intensity = Math.sqrt(raw);
    const r = Math.round(100 + 155 * intensity);
    const g = Math.round(100 * (1 - intensity));
    const b = Math.round(60 * (1 - intensity));
    return `rgb(${r},${g},${b})`;
  } else if (displaySentiment > 0.01) {
    const raw = Math.min(displaySentiment, 1);
    const intensity = Math.sqrt(raw);
    const r = Math.round(60 * (1 - intensity));
    const g = Math.round(100 + 155 * intensity);
    const b = Math.round(60 * (1 - intensity));
    return `rgb(${r},${g},${b})`;
  }
  return "rgb(120,120,120)";
}

export function edgeDirectionColor(direction: string): string {
  switch (direction) {
    case "positive":
      return "#22c55e";
    case "negative":
      return "#ef4444";
    case "complex":
      return "#eab308";
    default:
      return "#6b7280";
  }
}
