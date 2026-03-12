"use client";

import { useGraphStore } from "./useGraphData";
import type { ForceGraphNode } from "@/types/graph";

export function useNodeSelection() {
  const selectedNode = useGraphStore((s) => s.selectedNode);
  const setSelectedNode = useGraphStore((s) => s.setSelectedNode);
  const triggerAnalysis = useGraphStore((s) => s.triggerAnalysis);

  const handleNodeClick = (node: ForceGraphNode) => {
    setSelectedNode(node);
  };

  const handleDeepDive = (nodeId: string) => {
    triggerAnalysis([nodeId]);
  };

  const clearSelection = () => {
    setSelectedNode(null);
  };

  return { selectedNode, handleNodeClick, handleDeepDive, clearSelection };
}
