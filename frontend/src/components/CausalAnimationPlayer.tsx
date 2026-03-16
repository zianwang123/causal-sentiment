"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useGraphStore } from "@/hooks/useGraphData";
import { useCausalStore } from "@/hooks/useCausalStore";
import { API_URL } from "@/lib/config";
import type { ForceGraphLink } from "@/types/graph";

interface AnimationFrameEdge {
  source: string;
  target: string;
  correlation: number;
  survives: boolean;
}

interface AnimationFrame {
  frame: number;
  edge_count: number;
  edges: AnimationFrameEdge[];
}

interface AnimationData {
  snapshot_id: number;
  algorithm: string;
  n_frames: number;
  total_edges: number;
  surviving_edges: number;
  frames: AnimationFrame[];
}

type SpeedLabel = "Slow" | "Normal" | "Fast";
const SPEED_OPTIONS: Record<SpeedLabel, number> = {
  Slow: 200,
  Normal: 80,
  Fast: 30,
};

function transformFrameEdges(edges: AnimationFrameEdge[]): ForceGraphLink[] {
  return edges.map((e) => ({
    source: e.source,
    target: e.target,
    direction: "positive",
    weight: e.correlation,
    baseWeight: e.correlation,
    dynamicWeight: e.correlation,
    description: e.survives ? "Causal edge" : "Correlation only",
  }));
}

export default function CausalAnimationPlayer() {
  const [animationData, setAnimationData] = useState<AnimationData | null>(null);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState<SpeedLabel>("Normal");
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [visible, setVisible] = useState(false);

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const frameRef = useRef(0); // mutable frame index for interval access

  // Active nerve signal wave (edges frozen while this propagates)
  const waveRef = useRef<{
    frontier: Set<string>;
    visited: Set<string>;
    adj: Map<string, string[]>;       // frozen adjacency
    edgeByNodes: Map<string, string>; // "a|b" → "a__b"
    hopsLeft: number;
    intensity: number;
    pendingFrame: number; // frame to advance to after wave completes
  } | null>(null);

  const setIsAnimating = useCausalStore((s) => s.setIsAnimating);
  const setAnimationProgress = useCausalStore((s) => s.setAnimationProgress);
  const setDyingEdges = useCausalStore((s) => s.setDyingEdges);
  const setSignalEdges = useCausalStore((s) => s.setSignalEdges);
  const graphSource = useCausalStore((s) => s.graphSource);
  const currentGraph = useCausalStore((s) => s.currentGraph);
  const getForceGraphData = useCausalStore((s) => s.getForceGraphData);

  // Only show in discovered mode
  const isDiscovered = graphSource === "discovered";

  // Fetch animation frames
  const fetchFrames = useCallback(async () => {
    setLoading(true);
    setFetchError(null);
    try {
      const graphId = useCausalStore.getState().currentGraph?.id;
      const params = new URLSearchParams({ n_frames: "9999" }); // backend caps to 1-edge-per-frame
      if (graphId) params.set("id", String(graphId));
      const res = await fetch(`${API_URL}/api/causal/graph/animate?${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: AnimationData = await res.json();
      setAnimationData(data);
      setCurrentFrame(0);
    } catch (e) {
      setFetchError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Inject a frame's edges into the graph store
  // Filter edges to only include nodes that exist in the current node set
  // (animation frames may reference more nodes than the discovered graph)
  const injectFrame = useCallback(
    (frameIndex: number) => {
      if (!animationData) return;
      const frame = animationData.frames[frameIndex];
      if (!frame) return;
      const currentNodes = new Set(useGraphStore.getState().nodes.map(n => n.id));
      const filteredEdges = frame.edges.filter(
        e => currentNodes.has(e.source) && currentNodes.has(e.target)
      );
      const links = transformFrameEdges(filteredEdges);
      useGraphStore.setState({ links });
    },
    [animationData],
  );

  // Fetch frames when player becomes visible or when graph changes
  useEffect(() => {
    if (visible && !loading) {
      fetchFrames();
    }
  }, [visible, currentGraph?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  // Two-mode tick: wave propagation (edges frozen) vs frame advancement
  //
  // Nerve signals only fire once the graph is sparse enough (<= WAVE_THRESHOLD
  // edges) that a BFS can't flood the whole network. In the dense phase we just
  // remove edges quickly. Once sparse, every WAVE_INTERVAL-th removal pauses
  // the animation and sends a visible pulse outward from the dying edge.
  const frameCooldownRef = useRef(0);
  const WAVE_THRESHOLD = 0; // disabled: set > 0 to enable nerve signal waves
  const WAVE_INTERVAL = 3;  // fire a wave every Nth removal in the sparse zone

  useEffect(() => {
    if (isPlaying && animationData) {
      const totalFrames = animationData.frames.length;

      const tick = () => {
        const wave = waveRef.current;

        if (wave) {
          // === WAVE MODE: edges frozen, advance signal 1 hop ===
          const signalMap = new Map<string, number>();
          const nextFrontier = new Set<string>();

          for (const node of wave.frontier) {
            const neighbors = wave.adj.get(node);
            if (!neighbors) continue;
            for (const neighbor of neighbors) {
              const edgeKey = wave.edgeByNodes.get(`${node}|${neighbor}`);
              if (edgeKey) {
                signalMap.set(edgeKey, Math.max(signalMap.get(edgeKey) ?? 0, wave.intensity));
              }
              if (!wave.visited.has(neighbor)) {
                nextFrontier.add(neighbor);
              }
            }
          }

          for (const n of nextFrontier) wave.visited.add(n);
          setSignalEdges(signalMap);

          wave.frontier = nextFrontier;
          wave.intensity *= 0.45;
          wave.hopsLeft--;

          if (wave.hopsLeft <= 0 || nextFrontier.size === 0) {
            // Wave done — clear signal and advance to the pending frame
            waveRef.current = null;
            setSignalEdges(new Map());
            const next = wave.pendingFrame;
            frameRef.current = next;
            setCurrentFrame(next);
            frameCooldownRef.current = 0;
          }
        } else {
          // === FRAME MODE: advance frames ===
          const prev = frameRef.current;
          const next = prev + 1;
          if (next >= totalFrames) {
            setIsPlaying(false);
            return;
          }

          // Get current edge count to decide if we're in the sparse zone
          const currentEdgeCount = animationData.frames[prev]?.edge_count ?? 999;
          const inSparseZone = currentEdgeCount <= WAVE_THRESHOLD;

          if (inSparseZone) {
            frameCooldownRef.current++;
          }

          // Only consider waves in the sparse zone, every WAVE_INTERVAL removals
          if (inSparseZone && frameCooldownRef.current >= WAVE_INTERVAL) {
            const currentNodes = new Set(useGraphStore.getState().nodes.map(n => n.id));
            const prevEdges = animationData.frames[prev]?.edges
              .filter(e => currentNodes.has(e.source) && currentNodes.has(e.target)) ?? [];
            const prevKeys = new Set(prevEdges.map(e => `${e.source}__${e.target}`));
            const nextKeys = new Set(
              (animationData.frames[next]?.edges ?? [])
                .filter(e => currentNodes.has(e.source) && currentNodes.has(e.target))
                .map(e => `${e.source}__${e.target}`)
            );

            const dying = new Set<string>();
            for (const key of prevKeys) {
              if (!nextKeys.has(key)) dying.add(key);
            }

            if (dying.size >= 1) {
              // Build adjacency from current frame's surviving edges
              const adj = new Map<string, string[]>();
              const edgeByNodes = new Map<string, string>();
              for (const e of prevEdges) {
                const key = `${e.source}__${e.target}`;
                if (dying.has(key)) continue;
                if (!adj.has(e.source)) adj.set(e.source, []);
                if (!adj.has(e.target)) adj.set(e.target, []);
                adj.get(e.source)!.push(e.target);
                adj.get(e.target)!.push(e.source);
                edgeByNodes.set(`${e.source}|${e.target}`, key);
                edgeByNodes.set(`${e.target}|${e.source}`, key);
              }

              const originNodes = new Set<string>();
              for (const key of dying) {
                const [src, tgt] = key.split("__");
                originNodes.add(src);
                originNodes.add(tgt);
              }

              waveRef.current = {
                frontier: originNodes,
                visited: new Set(originNodes),
                adj,
                edgeByNodes,
                hopsLeft: 3,
                intensity: 1.0,
                pendingFrame: next,
              };
              // Don't advance — next tick enters wave mode
              return;
            }
          }

          // Normal advance (no wave)
          frameRef.current = next;
          setCurrentFrame(next);
        }
      };

      intervalRef.current = setInterval(tick, SPEED_OPTIONS[speed]);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isPlaying, speed, animationData, setSignalEdges]);

  // Inject edges and update progress when frame changes
  useEffect(() => {
    if (!animationData) return;
    const totalFrames = animationData.frames.length;
    injectFrame(currentFrame);
    setAnimationProgress(totalFrames > 1 ? currentFrame / (totalFrames - 1) : 0);
    setDyingEdges(new Set()); // clear dying edges on frame change
  }, [currentFrame, animationData, injectFrame, setAnimationProgress, setDyingEdges]);

  // Track animating state in causal store
  useEffect(() => {
    const animating = visible && animationData !== null;
    setIsAnimating(animating);
    return () => setIsAnimating(false);
  }, [visible, animationData, setIsAnimating]);

  // When animation is closed, restore the discovered graph
  const handleClose = useCallback(() => {
    setIsPlaying(false);
    setVisible(false);
    setAnimationData(null);
    setCurrentFrame(0);
    setAnimationProgress(0);
    setDyingEdges(new Set());
    setSignalEdges(new Map());
    waveRef.current = null;
    // Restore the discovered graph edges
    if (currentGraph) {
      const { links } = getForceGraphData();
      useGraphStore.setState({ links });
    }
  }, [currentGraph, getForceGraphData]);

  const handleReset = useCallback(() => {
    setIsPlaying(false);
    setCurrentFrame(0);
    frameRef.current = 0;
    waveRef.current = null;
    setSignalEdges(new Map());
  }, [setSignalEdges]);

  const handlePlayPause = useCallback(() => {
    if (!animationData) return;
    // If at the end, reset to start before playing
    if (currentFrame >= animationData.frames.length - 1) {
      frameRef.current = 0;
      waveRef.current = null;
      setSignalEdges(new Map());
      setCurrentFrame(0);
      setIsPlaying(true);
    } else {
      setIsPlaying((prev) => !prev);
    }
  }, [animationData, currentFrame, setSignalEdges]);

  const handleScrub = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = Number(e.target.value);
      frameRef.current = value;
      waveRef.current = null;
      setSignalEdges(new Map());
      setCurrentFrame(value);
      setIsPlaying(false);
    },
    [setSignalEdges],
  );

  if (!isDiscovered) return null;

  // Toggle button when player is hidden
  if (!visible) {
    return (
      <div className="absolute bottom-14 left-1/2 -translate-x-1/2 z-20">
        <button
          onClick={() => setVisible(true)}
          className="bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg px-3 py-2 text-gray-300 text-xs font-semibold hover:bg-gray-800/95 transition-colors"
        >
          ▶ Edge Discovery Animation
        </button>
      </div>
    );
  }

  const totalFrames = animationData?.frames.length ?? 0;
  const frame = animationData?.frames[currentFrame];
  const edgeCount = frame?.edge_count ?? 0;
  const totalEdges = animationData?.total_edges ?? 0;
  const survivingEdges = animationData?.surviving_edges ?? 0;
  const atEnd = animationData ? currentFrame >= totalFrames - 1 : false;

  return (
    <div className="absolute bottom-14 left-1/2 -translate-x-1/2 z-20 bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg px-3 py-2 flex items-center gap-3 min-w-[520px]">
      {loading && (
        <div className="text-gray-400 text-xs">Loading frames...</div>
      )}

      {fetchError && (
        <div className="text-red-400 text-xs flex items-center gap-2">
          <span>Error: {fetchError}</span>
          <button
            onClick={fetchFrames}
            className="text-gray-400 hover:text-gray-200 underline"
          >
            Retry
          </button>
        </div>
      )}

      {animationData && !loading && (
        <>
          {/* Play/Pause */}
          <button
            onClick={handlePlayPause}
            className="text-gray-200 hover:text-white text-sm w-6 h-6 flex items-center justify-center flex-shrink-0"
            title={isPlaying ? "Pause" : atEnd ? "Replay" : "Play"}
          >
            {isPlaying ? "\u23F8" : "\u25B6"}
          </button>

          {/* Scrubber */}
          <input
            type="range"
            min={0}
            max={totalFrames - 1}
            value={currentFrame}
            onChange={handleScrub}
            className="flex-1 h-1 accent-purple-500 cursor-pointer"
          />

          {/* Edge count */}
          <div className="text-gray-200 text-xs font-mono flex-shrink-0 w-24 text-center">
            <span className={edgeCount <= survivingEdges ? "text-purple-400" : ""}>
              {edgeCount}
            </span>
            <span className="text-gray-500"> / {totalEdges}</span>
            <span className="text-gray-500 text-[10px]"> edges</span>
          </div>

          {/* Speed control */}
          <select
            value={speed}
            onChange={(e) => setSpeed(e.target.value as SpeedLabel)}
            className="bg-gray-800 border border-gray-600 text-gray-300 text-xs rounded px-1.5 py-1 focus:outline-none focus:border-gray-500 flex-shrink-0"
          >
            {Object.keys(SPEED_OPTIONS).map((label) => (
              <option key={label} value={label}>
                {label}
              </option>
            ))}
          </select>

          {/* Reset */}
          <button
            onClick={handleReset}
            className="text-gray-400 hover:text-gray-200 text-xs flex-shrink-0"
            title="Reset to frame 0"
          >
            Reset
          </button>

          {/* Close */}
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-300 text-xs flex-shrink-0 ml-1"
            title="Close animation player"
          >
            ✕
          </button>
        </>
      )}
    </div>
  );
}
