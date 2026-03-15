"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { useGraphStore } from "@/hooks/useGraphData";
import { useNodeSelection } from "@/hooks/useNodeSelection";
import {
  edgeDirectionColor,
  sentimentToColor,
} from "@/lib/graphTransforms";
import type { ForceGraphNode } from "@/types/graph";

// react-force-graph-3d uses Three.js which needs window
const ForceGraph3D = dynamic(() => import("react-force-graph-3d"), {
  ssr: false,
});

// Cluster centroid positions (spread in 3D space)
const CLUSTER_CENTROIDS: Record<string, [number, number, number]> = {
  macro:              [  0,  150,   0],
  monetary_policy:    [150,  100,   0],
  geopolitics:        [-150, 100,   0],
  rates_credit:       [100,    0, 100],
  volatility:         [-100,   0, 100],
  commodities:        [100,    0, -100],
  equities:           [-100,   0, -100],
  equity_fundamentals:[  0,  -50, -150],
  currencies:         [  0,  -50,  150],
  flows_sentiment:    [150, -100,   0],
  global:             [-150,-100,   0],
};

export default function Graph3D({ portfolioNodeIds = [] }: { portfolioNodeIds?: string[] }) {
  const nodes = useGraphStore((s) => s.nodes);
  const links = useGraphStore((s) => s.links);
  const anomalies = useGraphStore((s) => s.anomalies);
  const fetchAnomalies = useGraphStore((s) => s.fetchAnomalies);
  const clustered = useGraphStore((s) => s.clustered);
  const focusNodeId = useGraphStore((s) => s.focusNodeId);
  const { handleNodeClick } = useNodeSelection();
  const graphRef = useRef<any>(null);

  const simulation = useGraphStore((s) => s.simulation);

  const anomalyNodeIds = useMemo(
    () => new Set(anomalies.map((a) => a.node_id)),
    [anomalies]
  );

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

  // Fetch anomalies on mount and periodically
  useEffect(() => {
    fetchAnomalies();
    const interval = setInterval(fetchAnomalies, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchAnomalies]);

  // Store nodes ref for cluster force callback (avoids reheating on data-only changes)
  const nodesRef = useRef(nodes);
  nodesRef.current = nodes;

  // Apply clustering force only when clustered mode toggles
  useEffect(() => {
    if (!graphRef.current) return;
    const fg = graphRef.current;

    if (clustered) {
      // Add a custom force that pulls nodes toward their cluster centroid
      fg.d3Force("cluster", (alpha: number) => {
        const strength = alpha * 0.3;
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
    } else {
      // Remove cluster force
      fg.d3Force("cluster", null);
    }
    fg.d3ReheatSimulation();
  }, [clustered]);

  // Handle focusNodeId from store (triggered by NodeLocator)
  useEffect(() => {
    if (!focusNodeId || !graphRef.current) return;
    const node = nodes.find((n) => n.id === focusNodeId) as any;
    if (node && node.x !== undefined) {
      const distance = 200;
      const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
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

  const graphData = useMemo(() => ({ nodes, links }), [nodes, links]);

  const handleClick = useCallback(
    (node: any) => {
      handleNodeClick(node as ForceGraphNode);
      // Focus camera on clicked node
      if (graphRef.current && node.x !== undefined) {
        const distance = 200;
        const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
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
    [handleNodeClick]
  );

  return (
    <div className="w-full h-full bg-gray-950">
      <ForceGraph3D
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
          if (portfolioSet.has(node.id)) return "#f59e0b"; // Amber for portfolio
          if (anomalyNodeIds.has(node.id)) return "#facc15"; // Yellow for anomaly
          return sentimentToColor(node.sentiment ?? 0);
        }}
        nodeVal={(node: any) => {
          const base = Math.max(2, (node.centrality ?? 0.02) * 100);
          if (simImpactMap) {
            if (simulation?.source_node === node.id) return base * 2; // Source node is large
            if (simImpactMap.has(node.id)) {
              const absImpact = Math.abs(simImpactMap.get(node.id)!);
              return base * (1 + absImpact * 2); // Scale by impact magnitude
            }
            return base * 0.5; // Shrink unaffected
          }
          return anomalyNodeIds.has(node.id) ? base * 1.5 : base;
        }}
        nodeOpacity={0.9}
        linkSource="source"
        linkTarget="target"
        linkColor={(link: any) => {
          if (simAffectedEdges) {
            const src = typeof link.source === "string" ? link.source : link.source?.id;
            const tgt = typeof link.target === "string" ? link.target : link.target?.id;
            if (simAffectedEdges.has(`${src}__${tgt}`)) return "#f97316"; // Orange for affected
            return "#1f2937"; // Very dim for unaffected
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
          return Math.max(0.5, (link.weight ?? 0.5) * 3);
        }}
        linkDirectionalParticles={(link: any) => {
          if (simAffectedEdges) {
            const src = typeof link.source === "string" ? link.source : link.source?.id;
            const tgt = typeof link.target === "string" ? link.target : link.target?.id;
            if (simAffectedEdges.has(`${src}__${tgt}`)) return 6;
            return 0;
          }
          return 2;
        }}
        linkDirectionalParticleWidth={(link: any) =>
          Math.max(0.5, (link.weight ?? 0.5) * 2)
        }
        linkDirectionalParticleSpeed={(link: any) => {
          if (simAffectedEdges) {
            const src = typeof link.source === "string" ? link.source : link.source?.id;
            const tgt = typeof link.target === "string" ? link.target : link.target?.id;
            if (simAffectedEdges.has(`${src}__${tgt}`)) return 0.015; // Faster on affected paths
          }
          return 0.005;
        }}
        onNodeClick={handleClick}
        backgroundColor="#030712"
        showNavInfo={false}
      />
    </div>
  );
}
