"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { useGraphStore } from "@/hooks/useGraphData";
import { useNodeSelection } from "@/hooks/useNodeSelection";
import { useCausalStore } from "@/hooks/useCausalStore";
import {
  edgeDirectionColor,
  sentimentToColor,
} from "@/lib/graphTransforms";
import type { ForceGraphNode } from "@/types/graph";

// react-force-graph-3d uses Three.js which needs window
const ForceGraph3D = dynamic(() => import("react-force-graph-3d"), {
  ssr: false,
});

// Cluster centroid positions on a sphere — 17 categories
// Uses Fibonacci sphere to evenly distribute category centers on a sphere of radius R.
// Each category's nodes will cluster around their centroid, creating a grouped-sphere layout.
const SPHERE_RADIUS = 250;
const CATEGORY_ORDER = [
  // Arranged so related categories are adjacent on the sphere
  "macro", "monetary_policy", "fiscal_policy",        // policy cluster (top)
  "rates_credit", "financial_system", "money_markets", // plumbing cluster
  "volatility", "flows_sentiment", "private_credit",   // risk/positioning cluster
  "equities", "equity_fundamentals", "semiconductors", // equity cluster — note: "semiconductors" is under "equities" NodeType
  "commodities", "supply_chain", "housing",             // real economy cluster
  "currencies", "global", "geopolitics",                // international cluster (bottom)
];
const CLUSTER_CENTROIDS: Record<string, [number, number, number]> = (() => {
  const centroids: Record<string, [number, number, number]> = {};
  const n = CATEGORY_ORDER.length;
  const goldenRatio = (1 + Math.sqrt(5)) / 2;
  for (let i = 0; i < n; i++) {
    // Fibonacci sphere: even distribution of points
    const theta = Math.acos(1 - 2 * (i + 0.5) / n); // polar angle [0, pi]
    const phi = 2 * Math.PI * i / goldenRatio;        // azimuthal angle
    centroids[CATEGORY_ORDER[i]] = [
      SPHERE_RADIUS * Math.sin(theta) * Math.cos(phi),
      SPHERE_RADIUS * Math.cos(theta),
      SPHERE_RADIUS * Math.sin(theta) * Math.sin(phi),
    ];
  }
  return centroids;
})();

export default function Graph3D({ portfolioNodeIds = [] }: { portfolioNodeIds?: string[] }) {
  const nodes = useGraphStore((s) => s.nodes);
  const links = useGraphStore((s) => s.links);
  const anomalies = useGraphStore((s) => s.anomalies);
  const fetchAnomalies = useGraphStore((s) => s.fetchAnomalies);
  const clustered = useGraphStore((s) => s.clustered);
  const focusNodeId = useGraphStore((s) => s.focusNodeId);
  const { handleNodeClick, clearSelection } = useNodeSelection();
  const graphSource = useCausalStore((s) => s.graphSource);
  const isDiscovered = graphSource === "discovered";
  const isAnimating = useCausalStore((s) => s.isAnimating);
  const animationProgress = useCausalStore((s) => s.animationProgress);
  const dyingEdges = useCausalStore((s) => s.dyingEdges);
  const signalEdges = useCausalStore((s) => s.signalEdges);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- ForceGraphMethods generic requires matching node/link types
  const graphRef = useRef<any>(null);

  // Click-to-highlight neighbors in discovered mode
  const [highlightedNode, setHighlightedNode] = useState<string | null>(null);

  // Multi-hop BFS: track which nodes are reachable and at what distance
  const highlightData = useMemo(() => {
    if (!highlightedNode || !isDiscovered) return null;
    const currentGraph = useCausalStore.getState().currentGraph;
    if (!currentGraph) return null;

    // BFS outward from clicked node, max 3 hops
    const MAX_HOPS = 3;
    const distances = new Map<string, number>([[highlightedNode, 0]]);
    const queue: [string, number][] = [[highlightedNode, 0]];
    const connectedEdges = new Set<string>(); // "source__target" keys

    while (queue.length > 0) {
      const [node, depth] = queue.shift()!;
      if (depth >= MAX_HOPS) continue;
      for (const e of currentGraph.edges) {
        if (e.source === node && !distances.has(e.target)) {
          distances.set(e.target, depth + 1);
          queue.push([e.target, depth + 1]);
          connectedEdges.add(`${e.source}__${e.target}`);
        }
        if (e.target === node && !distances.has(e.source)) {
          distances.set(e.source, depth + 1);
          queue.push([e.source, depth + 1]);
          connectedEdges.add(`${e.source}__${e.target}`);
        }
      }
    }
    // Also add edges between already-discovered nodes
    for (const e of currentGraph.edges) {
      if (distances.has(e.source) && distances.has(e.target)) {
        connectedEdges.add(`${e.source}__${e.target}`);
      }
    }
    return { distances, connectedEdges };
  }, [highlightedNode, isDiscovered]);

  const simulation = useGraphStore((s) => s.simulation);

  const anomalyNodeIds = useMemo(
    () => new Set(anomalies.map((a) => a.node_id)),
    [anomalies]
  );

  // Pre-compute node lookup map to avoid O(n) scans in per-frame callbacks
  const nodeMap = useMemo(() => {
    const map = new Map<string, ForceGraphNode>();
    for (const n of nodes) map.set(n.id, n);
    return map;
  }, [nodes]);

  // Build simulation impact lookup: node_id → impact magnitude
  const simImpactMap = useMemo(() => {
    if (!simulation) return null;
    const map = new Map<string, number>();
    map.set(simulation.source_node, simulation.shock_delta);
    for (const imp of simulation.impacts) {
      map.set(imp.node_id, imp.impact);
    }
    return map;
  }, [simulation]);

  // Build set of edges on affected paths
  const simAffectedEdges = useMemo(() => {
    if (!simulation) return null;
    const edges = new Set<string>();
    for (const imp of simulation.impacts) {
      for (let i = 0; i < imp.path.length - 1; i++) {
        edges.add(`${imp.path[i]}__${imp.path[i + 1]}`);
      }
    }
    return edges;
  }, [simulation]);

  const portfolioSet = useMemo(
    () => new Set(portfolioNodeIds),
    [portfolioNodeIds]
  );

  const hypotheticalNodeIds = useGraphStore((s) => s.hypotheticalNodeIds);
  const hypotheticalSet = useMemo(
    () => new Set(hypotheticalNodeIds),
    [hypotheticalNodeIds]
  );

  // Fetch anomalies on mount and periodically
  useEffect(() => {
    fetchAnomalies();
    const interval = setInterval(fetchAnomalies, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchAnomalies]);

  // Ref for nodes so cluster force reads current nodes without re-triggering the effect
  const nodesRef = useRef(nodes);
  nodesRef.current = nodes;

  // Tune d3 force layout for 111 nodes — spread them out
  // Disable link force entirely so edges don't affect node positions
  // (edges are visual-only, node layout is driven by charge + clustering)
  useEffect(() => {
    const fg = graphRef.current;
    if (!fg) return;
    const charge = fg.d3Force("charge");
    if (charge) charge.strength(-200).distanceMax(500);
    // Remove link force — edges should NOT pull nodes together
    fg.d3Force("link", null);
  }, []);

  // Always apply clustering force — nodes grouped by category on the sphere.
  // "Clustered" toggle controls tightness: tight (nodes snap to centroid) vs loose (spread around it).
  useEffect(() => {
    if (!graphRef.current) return;
    const fg = graphRef.current;

    fg.d3Force("cluster", (alpha: number) => {
      // Tight mode: strong pull to centroid. Loose mode: gentle pull for organic grouping.
      const strength = alpha * (clustered ? 0.6 : 0.15);
      for (const node of nodesRef.current) {
        const centroid = CLUSTER_CENTROIDS[(node as any).nodeType] || [0, 0, 0];
        const n = node as any;
        if (n.x !== undefined) {
          n.vx = (n.vx || 0) + (centroid[0] - n.x) * strength;
          n.vy = (n.vy || 0) + (centroid[1] - n.y) * strength;
          n.vz = (n.vz || 0) + (centroid[2] - n.z) * strength;
        }
      }
    });
    fg.d3ReheatSimulation();
  }, [clustered]);

  // Handle focusNodeId from store (triggered by NodeLocator)
  useEffect(() => {
    if (!focusNodeId || !graphRef.current) return;
    const node = nodes.find((n) => n.id === focusNodeId) as any;
    if (node && node.x !== undefined) {
      const distance = 200;
      const distRatio = 1 + distance / Math.hypot(node.x, node.y ?? 0, node.z ?? 0);
      graphRef.current.cameraPosition(
        {
          x: node.x * distRatio,
          y: node.y * distRatio,
          z: node.z * distRatio,
        },
        node,
        1500
      );
    }
    // Clear focusNodeId after handling
    useGraphStore.setState({ focusNodeId: null });
  }, [focusNodeId, nodes]);

  const edgeDisplayMode = useGraphStore((s) => s.edgeDisplayMode);
  const selectedNodeForEdges = useGraphStore((s) => s.selectedNode);

  // Always pass ALL links to the force simulation so node positions stay stable.
  // Edge VISIBILITY is controlled separately via linkVisibility callback.
  const graphData = useMemo(() => ({ nodes, links }), [nodes, links]);

  // Compute which edges should be visible based on display mode
  const visibleEdgeKeys = useMemo(() => {
    if (simulation) return null; // null = show all (simulation overlay handles it)

    if (edgeDisplayMode === "none") return new Set<string>();

    if (edgeDisplayMode === "selected") {
      if (!selectedNodeForEdges) return new Set<string>();

      // Full BFS: follow OUTBOUND directed edges from selected node (no hop limit)
      const selId = selectedNodeForEdges.id;
      const reachable = new Set<string>([selId]);
      const queue: string[] = [selId];

      const outbound = new Map<string, string[]>();
      for (const l of links) {
        const src = typeof l.source === "object" ? (l.source as ForceGraphNode).id : l.source;
        const tgt = typeof l.target === "object" ? (l.target as ForceGraphNode).id : l.target;
        if (!outbound.has(src)) outbound.set(src, []);
        outbound.get(src)!.push(tgt);
      }

      while (queue.length > 0) {
        const nodeId = queue.shift()!;
        const neighbors = outbound.get(nodeId) || [];
        for (const tgt of neighbors) {
          if (!reachable.has(tgt)) {
            reachable.add(tgt);
            queue.push(tgt);
          }
        }
      }

      const keys = new Set<string>();
      for (const l of links) {
        const src = typeof l.source === "object" ? (l.source as ForceGraphNode).id : l.source;
        const tgt = typeof l.target === "object" ? (l.target as ForceGraphNode).id : l.target;
        if (reachable.has(src) && reachable.has(tgt)) {
          keys.add(`${src}__${tgt}`);
        }
      }
      return keys;
    }

    // "all" mode
    return null; // null = show all
  }, [links, edgeDisplayMode, selectedNodeForEdges, simulation]);

  // Pre-compute centrality rank map (avoids O(n² log n) sort inside per-node-per-frame callback)
  const centralityRankMap = useMemo(() => {
    const sorted = [...nodes].sort((a, b) => (a.centrality ?? 0) - (b.centrality ?? 0));
    const map = new Map<string, number>();
    const total = sorted.length || 1;
    sorted.forEach((n, i) => map.set(n.id, i / (total - 1 || 1)));
    return map;
  }, [nodes]);

  // Force clean remount when graph identity changes (prevents Three.js tick crash
  // when node count changes drastically, e.g. regime switch)
  const currentGraphId = useCausalStore((s) => s.currentGraph?.id);
  const graphKey = `${graphSource}-${currentGraphId ?? "expert"}`;

  const handleClick = useCallback(
    (node: any) => {
      handleNodeClick(node as ForceGraphNode);
      // Toggle neighbor highlight in discovered mode
      if (isDiscovered) {
        const nodeId = (node as any).id;
        setHighlightedNode((prev) => (prev === nodeId ? null : nodeId));
      }
      // Focus camera on clicked node
      if (graphRef.current && node.x !== undefined) {
        const distance = 200;
        const distRatio = 1 + distance / Math.hypot(node.x, node.y ?? 0, node.z ?? 0);
        graphRef.current.cameraPosition(
          {
            x: node.x * distRatio,
            y: node.y * distRatio,
            z: node.z * distRatio,
          },
          node,
          1500
        );
      }
    },
    [handleNodeClick, isDiscovered]
  );

  const handleBackgroundClick = useCallback(() => {
    setHighlightedNode(null);
    clearSelection();
    if (isDiscovered) {
      useCausalStore.getState().clearCausalSimulation();
    }
    // Reset camera to default overview position
    if (graphRef.current) {
      graphRef.current.cameraPosition(
        { x: 0, y: 0, z: 600 },
        { x: 0, y: 0, z: 0 },
        1000
      );
    }
  }, [isDiscovered, clearSelection]);

  return (
    <div className="w-full h-full bg-gray-950">
      <ForceGraph3D
        key={graphKey}
        ref={graphRef}
        graphData={graphData}
        nodeId="id"
        nodeLabel={(node: any) => {
          const isAnomaly = anomalyNodeIds.has(node.id);
          const anomaly = isAnomaly ? anomalies.find((a) => a.node_id === node.id) : null;
          const inPortfolio = portfolioSet.has(node.id);
          let label = `${inPortfolio ? "★ " : ""}${node.label}\nSentiment: ${node.sentiment?.toFixed(2) ?? "N/A"}`;
          if (anomaly) label += `\n⚠ Anomaly: ${anomaly.z_score > 0 ? "+" : ""}${anomaly.z_score.toFixed(1)}σ`;
          if (simImpactMap?.has(node.id)) {
            const impact = simImpactMap.get(node.id)!;
            label += `\n⚡ Impact: ${impact >= 0 ? "+" : ""}${impact.toFixed(3)}`;
          }
          return label;
        }}
        nodeColor={(node: any) => {
          // Simulation mode: orange for affected, dim for unaffected
          if (simImpactMap) {
            if (simulation?.source_node === node.id) return "#f97316"; // Orange: shock source
            if (simImpactMap.has(node.id)) {
              const impact = simImpactMap.get(node.id)!;
              return impact > 0 ? "#4ade80" : "#f87171"; // Green/red based on impact direction
            }
            return "#374151"; // Dim gray for unaffected
          }
          // Multi-hop highlight: dim unreachable nodes, strong fade by distance
          if (isDiscovered && highlightData) {
            const dist = highlightData.distances.get(node.id);
            if (dist === undefined) return "#111111"; // unreachable: nearly black
            if (dist === 0) return sentimentToColor(node.sentiment ?? 0, node.id); // source: full color
            // Strong fade: hop 1 = 70%, hop 2 = 35%, hop 3 = 15%
            const fade = [1, 0.7, 0.35, 0.15][dist] ?? 0.1;
            return sentimentToColor((node.sentiment ?? 0) * fade, node.id);
          }
          if (hypotheticalSet.has(node.id)) return "#a855f7"; // Purple for hypothetical scenario nodes
          if (portfolioSet.has(node.id)) return "#f59e0b"; // Amber for portfolio
          if (anomalyNodeIds.has(node.id)) return "#facc15"; // Yellow for anomaly
          // During animation: gradually transition from grey to sentiment color
          // Use cubic curve so properties stay grey early and ramp up in final third
          if (isDiscovered && isAnimating) {
            const phase = Math.pow(animationProgress, 3);
            if (phase < 0.01) return "#555555";
            return sentimentToColor((node.sentiment ?? 0) * phase, node.id);
          }
          return sentimentToColor(node.sentiment ?? 0, node.id);
        }}
        nodeVal={(node: any) => {
          if (isDiscovered) {
            const normalizedRank = centralityRankMap.get(node.id) ?? 0;
            const UNIFORM_SIZE = 5;
            const expSize = 1 + (Math.exp(4 * normalizedRank) - 1) / (Math.exp(4) - 1) * 60;

            // During animation: transition from uniform → exponential (cubic ramp)
            let baseVal: number;
            if (isAnimating) {
              const sizePhase = Math.pow(animationProgress, 3);
              baseVal = UNIFORM_SIZE + (expSize - UNIFORM_SIZE) * sizePhase;
            } else {
              baseVal = expSize;
            }

            if (highlightData && !highlightData.distances.has(node.id)) return baseVal * 0.2;
            return baseVal;
          }
          const base = Math.max(2, (node.centrality ?? 0.02) * 100);
          if (simImpactMap) {
            if (simulation?.source_node === node.id) return base * 2;
            if (simImpactMap.has(node.id)) {
              const absImpact = Math.abs(simImpactMap.get(node.id)!);
              return base * (1 + absImpact * 2);
            }
            return base * 0.5;
          }
          return anomalyNodeIds.has(node.id) ? base * 1.5 : base;
        }}
        nodeOpacity={0.9}
        linkSource="source"
        linkTarget="target"
        linkOpacity={isDiscovered ? 1.0 : 0.6}
        linkVisibility={(link: any) => {
          if (!visibleEdgeKeys) return true; // null = show all
          const src = typeof link.source === "string" ? link.source : link.source?.id;
          const tgt = typeof link.target === "string" ? link.target : link.target?.id;
          return visibleEdgeKeys.has(`${src}__${tgt}`);
        }}
        linkColor={(link: any) => {
          if (simAffectedEdges) {
            const src = typeof link.source === "string" ? link.source : link.source?.id;
            const tgt = typeof link.target === "string" ? link.target : link.target?.id;
            if (simAffectedEdges.has(`${src}__${tgt}`)) return "#f97316";
            return "#1f2937";
          }
          if (isDiscovered) {
            const srcId = typeof link.source === "string" ? link.source : link.source?.id;
            const tgtId = typeof link.target === "string" ? link.target : link.target?.id;

            // During animation: uniform grey → colored edges, with nerve signal glow
            if (isAnimating) {
              // Check for nerve signal on this edge
              const sigIntensity = signalEdges.get(`${srcId}__${tgtId}`) ?? signalEdges.get(`${tgtId}__${srcId}`) ?? 0;
              if (sigIntensity > 0.3) return `rgba(34, 211, 238, ${0.3 + sigIntensity * 0.5})`; // cyan glow
              if (sigIntensity > 0) return `rgba(103, 232, 249, ${0.2 + sigIntensity * 0.3})`; // faint cyan

              const edgePhase = Math.pow(animationProgress, 3);
              if (edgePhase < 0.01) return "#444444";
              const srcNode = nodeMap.get(srcId);
              const srcSentiment = srcNode?.sentiment ?? 0;
              const effectiveSentiment = link.direction === "negative" ? -srcSentiment : srcSentiment;
              return sentimentToColor(effectiveSentiment * 0.5 * edgePhase);
            }

            // Dim edges not in the propagation path, fade connected edges by distance
            if (highlightData) {
              const edgeKey = `${srcId}__${tgtId}`;
              if (!highlightData.connectedEdges.has(edgeKey)) return "#0a0a0a";
              const srcDist = highlightData.distances.get(srcId) ?? 99;
              const tgtDist = highlightData.distances.get(tgtId) ?? 99;
              const maxDist = Math.max(srcDist, tgtDist);
              const fade = [1, 0.8, 0.4, 0.2][maxDist] ?? 0.1;
              const srcNode = nodeMap.get(srcId);
              const srcSentiment = srcNode?.sentiment ?? 0;
              const effectiveSentiment = link.direction === "negative" ? -srcSentiment : srcSentiment;
              return sentimentToColor(effectiveSentiment * fade);
            }
            // Normal: edge color = source sentiment, dimmed
            const srcNode = nodeMap.get(srcId);
            const srcSentiment = srcNode?.sentiment ?? 0;
            const effectiveSentiment = link.direction === "negative" ? -srcSentiment : srcSentiment;
            return sentimentToColor(effectiveSentiment * 0.5);
          }
          return edgeDirectionColor(link.direction);
        }}
        linkWidth={(link: any) => {
          if (simAffectedEdges) {
            const src = typeof link.source === "string" ? link.source : link.source?.id;
            const tgt = typeof link.target === "string" ? link.target : link.target?.id;
            if (simAffectedEdges.has(`${src}__${tgt}`)) return 2.5;
            return 0.3;
          }
          if (isDiscovered) {
            const w = link.weight ?? 0.5;
            const UNIFORM_WIDTH = 0.4;
            const normalWidth = link.direction === "negative" ? Math.max(0.3, w * 1.5) : Math.max(0.5, w * 2);

            // During animation: uniform thin → weight-based across full duration, with signal boost
            if (isAnimating) {
              const srcId = typeof link.source === "string" ? link.source : link.source?.id;
              const tgtId = typeof link.target === "string" ? link.target : link.target?.id;
              const sigIntensity = signalEdges.get(`${srcId}__${tgtId}`) ?? signalEdges.get(`${tgtId}__${srcId}`) ?? 0;
              const widthPhase = Math.pow(animationProgress, 3);
              const base = UNIFORM_WIDTH + (normalWidth - UNIFORM_WIDTH) * widthPhase;
              return sigIntensity > 0 ? base + sigIntensity * 1.5 : base;
            }

            // Multi-hop highlight: thicken connected edges, near-zero for others
            if (highlightData) {
              const srcId = typeof link.source === "string" ? link.source : link.source?.id;
              const tgtId = typeof link.target === "string" ? link.target : link.target?.id;
              const edgeKey = `${srcId}__${tgtId}`;
              if (!highlightData.connectedEdges.has(edgeKey)) return 0.05;
              return Math.max(1.5, w * 4);
            }
            return normalWidth;
          }
          const w = link.weight ?? 0.5;
          return 0.4 + w * w * 5;
        }}
        linkDirectionalParticles={(link: any) => {
          if (simAffectedEdges) {
            const src = typeof link.source === "string" ? link.source : link.source?.id;
            const tgt = typeof link.target === "string" ? link.target : link.target?.id;
            if (simAffectedEdges.has(`${src}__${tgt}`)) return 6;
            return 0;
          }
          if (isDiscovered && highlightData) {
            const src = typeof link.source === "string" ? link.source : link.source?.id;
            const tgt = typeof link.target === "string" ? link.target : link.target?.id;
            if (!highlightData.connectedEdges.has(`${src}__${tgt}`)) return 0;
            return 5;
          }
          // Nerve signal: surge particles on signaled edges
          if (isDiscovered && isAnimating && signalEdges.size > 0) {
            const src = typeof link.source === "string" ? link.source : link.source?.id;
            const tgt = typeof link.target === "string" ? link.target : link.target?.id;
            const intensity = signalEdges.get(`${src}__${tgt}`) ?? signalEdges.get(`${tgt}__${src}`) ?? 0;
            if (intensity > 0) return Math.round(4 + intensity * 12); // up to 16 particles
          }
          return isDiscovered ? 4 : 2;
        }}
        linkDirectionalParticleWidth={(link: any) => {
          if (isDiscovered) {
            // Nerve signal: bigger particles on signaled edges
            if (isAnimating && signalEdges.size > 0) {
              const src = typeof link.source === "string" ? link.source : link.source?.id;
              const tgt = typeof link.target === "string" ? link.target : link.target?.id;
              const intensity = signalEdges.get(`${src}__${tgt}`) ?? signalEdges.get(`${tgt}__${src}`) ?? 0;
              if (intensity > 0) return 2 + intensity * 4; // up to 6px wide
            }
            return Math.max(2, (link.weight ?? 0.5) * 4);
          }
          return Math.max(0.5, (link.weight ?? 0.5) * 2);
        }}
        linkDirectionalParticleColor={isDiscovered ? ((link: any) => {
          // Nerve signal: bright cyan pulse
          if (isAnimating && signalEdges.size > 0) {
            const srcId = typeof link.source === "string" ? link.source : link.source?.id;
            const tgtId = typeof link.target === "string" ? link.target : link.target?.id;
            const intensity = signalEdges.get(`${srcId}__${tgtId}`) ?? signalEdges.get(`${tgtId}__${srcId}`) ?? 0;
            if (intensity > 0.3) return "#22d3ee"; // bright cyan for strong signal
            if (intensity > 0) return "#67e8f9"; // lighter cyan for fading signal
          }
          // During animation: grey → colored particles (cubic ramp, grey until late)
          if (isAnimating && animationProgress < 1) {
            const pPhase = Math.pow(animationProgress, 3);
            if (pPhase < 0.3) return "#888888";
            const srcId2 = typeof link.source === "string" ? link.source : link.source?.id;
            const srcNode2 = nodes.find((n: any) => n.id === srcId2);
            const s2 = srcNode2?.sentiment ?? 0;
            const sign2 = link.direction === "negative" ? -s2 : s2;
            if (sign2 > 0.001) return "#4ade80";
            if (sign2 < -0.001) return "#f87171";
            return "#aaaaaa";
          }
          // Normal: force strong color based on sign
          const srcId = typeof link.source === "string" ? link.source : link.source?.id;
          const srcNode = nodes.find((n: any) => n.id === srcId);
          const srcSentiment = srcNode?.sentiment ?? 0;
          const effectiveSign = link.direction === "negative" ? -srcSentiment : srcSentiment;
          if (effectiveSign > 0.001) return "#4ade80";
          if (effectiveSign < -0.001) return "#f87171";
          return "#ffffff";
        }) : undefined}
        linkDirectionalParticleSpeed={(link: any) => {
          if (simAffectedEdges) {
            const src = typeof link.source === "string" ? link.source : link.source?.id;
            const tgt = typeof link.target === "string" ? link.target : link.target?.id;
            if (simAffectedEdges.has(`${src}__${tgt}`)) return 0.015;
          }
          // Nerve signal: boost speed on signaled edges
          if (isDiscovered && isAnimating && signalEdges.size > 0) {
            const src = typeof link.source === "string" ? link.source : link.source?.id;
            const tgt = typeof link.target === "string" ? link.target : link.target?.id;
            const intensity = signalEdges.get(`${src}__${tgt}`) ?? signalEdges.get(`${tgt}__${src}`) ?? 0;
            if (intensity > 0) return 0.005 + intensity * 0.025; // up to 0.030
          }
          return 0.005;
        }}
        onNodeClick={handleClick}
        onBackgroundClick={handleBackgroundClick}
        backgroundColor="#030712"
        showNavInfo={false}
      />
    </div>
  );
}
