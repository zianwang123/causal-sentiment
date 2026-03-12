"use client";

import { useCallback, useEffect, useMemo, useRef } from "react";
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
  const { handleNodeClick } = useNodeSelection();
  const graphRef = useRef<any>(null);

  const anomalyNodeIds = useMemo(
    () => new Set(anomalies.map((a) => a.node_id)),
    [anomalies]
  );

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

  // Apply clustering force when mode changes
  useEffect(() => {
    if (!graphRef.current) return;
    const fg = graphRef.current;

    if (clustered) {
      // Add a custom force that pulls nodes toward their cluster centroid
      fg.d3Force("cluster", (alpha: number) => {
        const strength = alpha * 0.3;
        for (const node of nodes) {
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
  }, [clustered, nodes]);

  const graphData = { nodes, links };

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
          return label;
        }}
        nodeColor={(node: any) => {
          if (portfolioSet.has(node.id)) return "#f59e0b"; // Amber for portfolio
          if (anomalyNodeIds.has(node.id)) return "#facc15"; // Yellow for anomaly
          return sentimentToColor(node.sentiment ?? 0);
        }}
        nodeVal={(node: any) => {
          const base = Math.max(2, (node.centrality ?? 0.02) * 100);
          return anomalyNodeIds.has(node.id) ? base * 1.5 : base;
        }}
        nodeOpacity={0.9}
        linkSource="source"
        linkTarget="target"
        linkColor={(link: any) => edgeDirectionColor(link.direction)}
        linkWidth={(link: any) => Math.max(0.5, (link.weight ?? 0.5) * 3)}
        linkDirectionalParticles={2}
        linkDirectionalParticleWidth={(link: any) =>
          Math.max(0.5, (link.weight ?? 0.5) * 2)
        }
        linkDirectionalParticleSpeed={0.005}
        onNodeClick={handleClick}
        backgroundColor="#030712"
        showNavInfo={false}
      />
    </div>
  );
}
