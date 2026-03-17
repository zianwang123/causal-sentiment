"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useCausalStore } from "@/hooks/useCausalStore";
import { useGraphStore } from "@/hooks/useGraphData";
import { API_URL } from "@/lib/config";
import { getNodeLabel } from "@/lib/nodeLabels";

interface Anchor {
  id: number;
  node_id: string;
  scoring: string;
  polarity: number;
}

export default function CausalPanel() {
  const [collapsed, setCollapsed] = useState(true);
  const [algorithm, setAlgorithm] = useState("pcmci");
  const [scoring, setScoring] = useState("zscore");
  const [sliderValue, setSliderValue] = useState(20);
  const [useTopN, setUseTopN] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Anchor state
  const [anchors, setAnchors] = useState<Anchor[]>([]);
  const [anchorsOpen, setAnchorsOpen] = useState(false);
  const [newAnchorNode, setNewAnchorNode] = useState("");
  const [newAnchorPolarity, setNewAnchorPolarity] = useState<number>(1);

  // Regime selector state
  const [selectedRegimeId, setSelectedRegimeId] = useState<number | null>(null);

  const graphSource = useCausalStore((s) => s.graphSource);
  const setGraphSource = useCausalStore((s) => s.setGraphSource);
  const snapshots = useCausalStore((s) => s.snapshots);
  const currentGraph = useCausalStore((s) => s.currentGraph);
  const loading = useCausalStore((s) => s.loading);
  const discovering = useCausalStore((s) => s.discovering);
  const error = useCausalStore((s) => s.error);
  const fetchSnapshots = useCausalStore((s) => s.fetchSnapshots);
  const loadGraph = useCausalStore((s) => s.loadGraph);
  const triggerDiscovery = useCausalStore((s) => s.triggerDiscovery);
  const pollDiscoveryStatus = useCausalStore((s) => s.pollDiscoveryStatus);
  const setTopN = useCausalStore((s) => s.setTopN);
  const setError = useCausalStore((s) => s.setError);
  const getForceGraphData = useCausalStore((s) => s.getForceGraphData);
  const fetchAnchors = useCausalStore((s) => s.fetchAnchors);

  const fetchExpertGraph = useGraphStore((s) => s.fetchGraph);
  const expertNodes = useGraphStore((s) => s.nodes);

  // Fetch snapshots on mount
  useEffect(() => {
    fetchSnapshots();
  }, [fetchSnapshots]);

  // Fetch anchors on mount and when scoring changes
  const loadAnchors = useCallback(async () => {
    const data = await fetchAnchors(scoring);
    setAnchors(data);
  }, [fetchAnchors, scoring]);

  useEffect(() => {
    loadAnchors();
  }, [loadAnchors]);

  // Inject discovered graph data into the main graph store when source is "discovered"
  useEffect(() => {
    if (graphSource === "discovered" && currentGraph) {
      const { nodes, links } = getForceGraphData();
      useGraphStore.setState({ nodes, links });
    }
  }, [graphSource, currentGraph, getForceGraphData]);

  // Reload expert graph when switching back
  const handleSourceChange = useCallback(
    (source: "expert" | "discovered") => {
      setGraphSource(source);
      if (source === "expert") {
        fetchExpertGraph();
      } else if (source === "discovered" && !currentGraph && snapshots.length > 0) {
        // Default to pcmci_zscore, or the first matching snapshot for current algorithm+scoring
        const defaultMatch = snapshots.find((s) => s.run_name === `${algorithm}_${scoring}`)
          || snapshots.find((s) => s.run_name === "pcmci_zscore")
          || snapshots[0];
        loadGraph(defaultMatch.id);
      }
    },
    [setGraphSource, fetchExpertGraph, currentGraph, snapshots, loadGraph, algorithm, scoring],
  );

  // Poll discovery status
  useEffect(() => {
    if (discovering && !pollRef.current) {
      pollRef.current = setInterval(async () => {
        const done = await pollDiscoveryStatus();
        if (done && pollRef.current) {
          clearInterval(pollRef.current);
          pollRef.current = null;
        }
      }, 2000);
    }
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [discovering, pollDiscoveryStatus]);

  // Handle top_n changes
  useEffect(() => {
    if (useTopN) {
      setTopN(sliderValue);
    } else {
      setTopN(null);
    }
  }, [useTopN, sliderValue, setTopN]);

  // Auto-load matching snapshot when algorithm or scoring changes in discovered mode
  useEffect(() => {
    if (graphSource !== "discovered") return;
    const runName = `${algorithm}_${scoring}`;
    // RPCMCI stores as rpcmci_zscore_regime0 etc — match by prefix
    const match = snapshots.find((s) => s.run_name === runName)
      || (algorithm === "rpcmci" ? snapshots.find((s) => s.run_name.startsWith(runName + "_regime")) : null);
    if (match) {
      loadGraph(match.id);
    } else {
      useCausalStore.setState({ currentGraph: null });
    }
  }, [algorithm, scoring, graphSource, snapshots, loadGraph]);

  const matchingRunName = `${algorithm}_${scoring}`;
  const hasExistingSnapshot = snapshots.some((s) =>
    s.run_name === matchingRunName || (algorithm === "rpcmci" && s.run_name.startsWith(matchingRunName + "_regime"))
  );

  const handleRunDiscovery = useCallback(async () => {
    const existing = snapshots.find((s) => s.run_name === matchingRunName);
    if (existing) {
      await loadGraph(existing.id);
    } else {
      await triggerDiscovery(algorithm, scoring);
    }
  }, [snapshots, matchingRunName, loadGraph, triggerDiscovery, algorithm, scoring]);

  const handleReloadWithTopN = useCallback(() => {
    if (currentGraph) {
      loadGraph(currentGraph.id);
    }
  }, [currentGraph, loadGraph]);

  // RPCMCI regime snapshots
  const regimeSnapshots = useMemo(() => {
    if (algorithm !== "rpcmci") return [];
    const prefix = `rpcmci_${scoring}_regime`;
    return snapshots.filter((s) => s.run_name.startsWith(prefix));
  }, [algorithm, scoring, snapshots]);

  // Deduplicated snapshots: latest (first) per run_name
  const uniqueSnapshots = useMemo(() => {
    const seen = new Set<string>();
    return snapshots.filter((s) => {
      if (seen.has(s.run_name)) return false;
      seen.add(s.run_name);
      return true;
    });
  }, [snapshots]);

  // Network stats: top 3 hubs by degree centrality
  const topHubs = useMemo(() => {
    if (!currentGraph) return [];
    const degreeMap: Record<string, number> = {};
    for (const edge of currentGraph.edges) {
      degreeMap[edge.source] = (degreeMap[edge.source] || 0) + 1;
      degreeMap[edge.target] = (degreeMap[edge.target] || 0) + 1;
    }
    return Object.entries(degreeMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([nodeId, degree]) => ({ nodeId, degree }));
  }, [currentGraph]);

  // Validation summary
  const validationSummary = useMemo(() => {
    if (!currentGraph) return null;
    const total = currentGraph.edges.length;
    const passed = currentGraph.edges.filter(
      (e) => e.validation?.refutation_passed === true
    ).length;
    return { passed, total };
  }, [currentGraph]);

  // Anchor CRUD helpers
  const handleAddAnchor = useCallback(async () => {
    if (!newAnchorNode.trim()) return;
    try {
      const res = await fetch(`${API_URL}/api/causal/anchors`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_id: newAnchorNode.trim(), scoring, polarity: newAnchorPolarity }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setNewAnchorNode("");
      await loadAnchors();
      if (currentGraph) {
        await fetch(`${API_URL}/api/causal/graph/repropagate?id=${currentGraph.id}`, { method: "POST" });
        await loadGraph(currentGraph.id);
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }, [newAnchorNode, scoring, newAnchorPolarity, loadAnchors, currentGraph, loadGraph, setError]);

  const handleFlipPolarity = useCallback(async (anchor: Anchor) => {
    try {
      const newPolarity = anchor.polarity === 1 ? -1 : 1;
      const res = await fetch(`${API_URL}/api/causal/anchors/${anchor.id}?polarity=${newPolarity}`, {
        method: "PUT",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAnchors();
      if (currentGraph) {
        await fetch(`${API_URL}/api/causal/graph/repropagate?id=${currentGraph.id}`, { method: "POST" });
        await loadGraph(currentGraph.id);
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }, [loadAnchors, currentGraph, loadGraph, setError]);

  const handleDeleteAnchor = useCallback(async (anchorId: number) => {
    try {
      const res = await fetch(`${API_URL}/api/causal/anchors/${anchorId}`, { method: "DELETE" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAnchors();
      if (currentGraph) {
        await fetch(`${API_URL}/api/causal/graph/repropagate?id=${currentGraph.id}`, { method: "POST" });
        await loadGraph(currentGraph.id);
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }, [loadAnchors, currentGraph, loadGraph, setError]);

  // Handle clicking a hub node (focus camera via graph store)
  const handleHubClick = useCallback((nodeId: string) => {
    useGraphStore.getState().focusNode(nodeId);
  }, []);

  return (
    <div className="absolute top-4 right-4 z-10">
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg px-3 py-2 text-gray-300 text-xs font-semibold hover:bg-gray-800/95 transition-colors flex items-center gap-2"
      >
        <span>Causal Discovery</span>
        <span className="text-[10px] text-gray-500">
          {collapsed ? "\u25BC" : "\u25B2"}
        </span>
      </button>

      {!collapsed && (
        <div className="mt-2 bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg p-3 w-64 max-h-[calc(100vh-5rem)] overflow-y-auto">
          {/* Graph Source */}
          <div className="mb-3">
            <label className="text-[10px] text-gray-500 uppercase block mb-1">
              Graph Source
            </label>
            <select
              value={graphSource}
              onChange={(e) =>
                handleSourceChange(e.target.value as "expert" | "discovered")
              }
              className="w-full bg-gray-800 border border-gray-600 text-gray-200 text-xs rounded px-2 py-1.5 focus:outline-none focus:border-gray-500"
            >
              <option value="expert">
                Expert ({expertNodes.length} nodes)
              </option>
              <option value="discovered">Discovered</option>
            </select>
          </div>

          {graphSource === "discovered" && (
            <>
              {/* Algorithm */}
              <div className="mb-2">
                <label className="text-[10px] text-gray-500 uppercase block mb-1">
                  Algorithm
                </label>
                <select
                  value={algorithm}
                  onChange={(e) => setAlgorithm(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-600 text-gray-200 text-xs rounded px-2 py-1.5 focus:outline-none focus:border-gray-500"
                >
                  <option value="pcmci">PCMCI+ (controls confounders)</option>
                  <option value="granger">Granger (pairwise, fast)</option>
                  <option value="rpcmci">RPCMCI (per-regime)</option>
                </select>
              </div>

              {/* Scoring */}
              <div className="mb-3">
                <label className="text-[10px] text-gray-500 uppercase block mb-1">
                  Scoring
                </label>
                <select
                  value={scoring}
                  onChange={(e) => setScoring(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-600 text-gray-200 text-xs rounded px-2 py-1.5 focus:outline-none focus:border-gray-500"
                >
                  <option value="zscore">Z-Score</option>
                  <option value="returns">Returns</option>
                  <option value="volatility">Volatility</option>
                </select>
              </div>

              {/* Compact legend */}
              <div className="text-[10px] text-gray-500 mb-3 space-y-0.5">
                <div>Edges = statistically discovered causal links</div>
                <div>
                  <span className="text-green-400">Green</span> node = above normal ·{" "}
                  <span className="text-red-400">Red</span> = below normal
                </div>
                <div>Larger node = more causal connections</div>
              </div>

              {/* Regime selector (RPCMCI only) */}
              {algorithm === "rpcmci" && regimeSnapshots.length > 0 && (
                <div className="mb-3">
                  <label className="text-[10px] text-gray-500 uppercase block mb-1">
                    Regime
                  </label>
                  <select
                    value={selectedRegimeId ?? ""}
                    onChange={(e) => {
                      const id = Number(e.target.value);
                      setSelectedRegimeId(id);
                      if (id) loadGraph(id);
                    }}
                    className="w-full bg-gray-800 border border-gray-600 text-gray-200 text-xs rounded px-2 py-1.5 focus:outline-none focus:border-gray-500"
                  >
                    <option value="">Select regime...</option>
                    {regimeSnapshots.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.run_name} ({s.node_count}n / {s.edge_count}e)
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Run Discovery */}
              <button
                onClick={handleRunDiscovery}
                disabled={discovering}
                className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-xs py-2 px-3 rounded transition-colors mb-3"
              >
                {discovering ? "Discovering..." : hasExistingSnapshot ? "Load Result" : "Run Discovery"}
              </button>

              {discovering && (
                <div className="mb-3">
                  <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-purple-500 rounded-full"
                      style={{
                        animation:
                          "causal-progress 1.5s ease-in-out infinite",
                        width: "40%",
                      }}
                    />
                  </div>
                  <div className="text-[10px] text-gray-400 mt-0.5">
                    Running {algorithm} with {scoring} scoring...
                  </div>
                  <style jsx>{`
                    @keyframes causal-progress {
                      0% {
                        margin-left: 0%;
                      }
                      50% {
                        margin-left: 60%;
                      }
                      100% {
                        margin-left: 0%;
                      }
                    }
                  `}</style>
                </div>
              )}

              {/* Node importance slider */}
              <div className="mb-3">
                <div className="flex items-center justify-between mb-1">
                  <label className="text-[10px] text-gray-500 uppercase">
                    Node Filter
                  </label>
                  <button
                    onClick={() => {
                      setUseTopN(!useTopN);
                    }}
                    className={`text-[10px] px-1.5 py-0.5 rounded transition-colors ${
                      useTopN
                        ? "bg-purple-700 text-white"
                        : "bg-gray-700 text-gray-400"
                    }`}
                  >
                    {useTopN ? `Top ${sliderValue}` : "All"}
                  </button>
                </div>
                {useTopN && (
                  <div className="flex items-center gap-2">
                    <input
                      type="range"
                      min={5}
                      max={35}
                      value={sliderValue}
                      onChange={(e) => setSliderValue(Number(e.target.value))}
                      onMouseUp={handleReloadWithTopN}
                      onTouchEnd={handleReloadWithTopN}
                      className="flex-1 h-1 accent-purple-500"
                    />
                    <span className="text-[10px] text-gray-400 w-5 text-right">
                      {sliderValue}
                    </span>
                  </div>
                )}
              </div>

              {/* Network Stats (merged) */}
              {currentGraph && (
                <div className="mb-3 bg-gray-800/80 rounded p-2">
                  <div className="text-[10px] text-gray-500 uppercase mb-1">
                    Network Stats
                  </div>
                  <div className="text-[11px] text-gray-300 space-y-1">
                    <div>
                      <span className="text-gray-200">{currentGraph.summary.node_count}</span>
                      <span className="text-gray-500"> factors, </span>
                      <span className="text-gray-200">{currentGraph.summary.edge_count}</span>
                      <span className="text-gray-500"> causal links found</span>
                    </div>
                    {currentGraph.parameters?.stats && (
                      <div className="text-[10px] text-gray-500">
                        {((currentGraph.parameters.stats.avg_degree as number)).toFixed(1)} connections per factor avg ·{" "}
                        {((currentGraph.parameters.stats.density as number) * 100).toFixed(1)}% of possible links exist
                      </div>
                    )}
                    {validationSummary && (
                      <div className="text-[10px]">
                        <span className="text-green-400">{validationSummary.passed}</span>
                        <span className="text-gray-500">/{validationSummary.total} links confirmed by statistical test</span>
                      </div>
                    )}
                    {topHubs.length > 0 && (
                      <div className="text-[10px]">
                        <span className="text-gray-500">Most connected: </span>
                        {topHubs.map((h, i) => (
                          <span key={h.nodeId}>
                            {i > 0 && ", "}
                            <button
                              onClick={() => handleHubClick(h.nodeId)}
                              className="text-purple-400 hover:text-purple-300 transition-colors"
                            >
                              {getNodeLabel(h.nodeId)}
                            </button>
                            <span className="text-gray-500 text-[9px]">({h.degree})</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Anchor Nodes */}
              {graphSource === "discovered" && (
                <div className="mb-3">
                  <button
                    onClick={() => setAnchorsOpen(!anchorsOpen)}
                    className="w-full flex items-center justify-between text-[10px] text-gray-500 uppercase mb-1"
                  >
                    <span>Anchor Nodes ({anchors.length})</span>
                    <span className="text-[9px]">{anchorsOpen ? "\u25B2" : "\u25BC"}</span>
                  </button>
                  {anchorsOpen && (
                    <div className="bg-gray-800/60 rounded p-1.5 space-y-1">
                      {/* Existing anchors */}
                      {anchors.length === 0 && (
                        <div className="text-[10px] text-gray-500 text-center py-1">No anchors</div>
                      )}
                      {anchors.map((a) => (
                        <div key={a.id} className="flex items-center gap-1 text-[10px]">
                          <span className="text-gray-300 truncate flex-1" title={a.node_id}>
                            {getNodeLabel(a.node_id)}
                          </span>
                          <button
                            onClick={() => handleFlipPolarity(a)}
                            className={`px-1 py-0.5 rounded text-[9px] font-bold ${
                              a.polarity === 1
                                ? "bg-green-900/60 text-green-400"
                                : "bg-red-900/60 text-red-400"
                            }`}
                            title="Click to flip polarity"
                          >
                            {a.polarity === 1 ? "+1" : "-1"}
                          </button>
                          <button
                            onClick={() => handleDeleteAnchor(a.id)}
                            className="text-gray-500 hover:text-red-400 px-0.5"
                            title="Remove anchor"
                          >
                            x
                          </button>
                        </div>
                      ))}

                      {/* Add anchor row */}
                      <div className="flex items-center gap-1 pt-1 border-t border-gray-700/50">
                        <select
                          value={newAnchorNode}
                          onChange={(e) => setNewAnchorNode(e.target.value)}
                          className="flex-1 bg-gray-900 border border-gray-600 text-gray-200 text-[10px] rounded px-1 py-0.5 min-w-0 focus:outline-none focus:border-gray-500"
                        >
                          <option value="">Select node...</option>
                          {currentGraph?.nodes.map((n) => (
                            <option key={n.id} value={n.id}>
                              {getNodeLabel(n.id)}
                            </option>
                          ))}
                        </select>
                        <button
                          onClick={() => setNewAnchorPolarity(newAnchorPolarity === 1 ? -1 : 1)}
                          className={`px-1 py-0.5 rounded text-[9px] font-bold flex-shrink-0 ${
                            newAnchorPolarity === 1
                              ? "bg-green-900/60 text-green-400"
                              : "bg-red-900/60 text-red-400"
                          }`}
                        >
                          {newAnchorPolarity === 1 ? "+1" : "-1"}
                        </button>
                        <button
                          onClick={handleAddAnchor}
                          className="bg-purple-700 hover:bg-purple-600 text-white text-[9px] px-1.5 py-0.5 rounded flex-shrink-0"
                        >
                          Add
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* About this graph — contextual explainer */}
              {currentGraph && (
                <div className="mb-3 bg-gray-800/40 rounded p-2 text-[10px] text-gray-400 space-y-1">
                  <div className="text-gray-500 uppercase font-semibold mb-0.5">About this graph</div>
                  {currentGraph.algorithm === "pcmci" && (
                    <div>Each edge means: past values of A <span className="text-gray-300">statistically predict</span> future B, even after controlling for all other factors. Spurious correlations are filtered out.</div>
                  )}
                  {currentGraph.algorithm === "granger" && (
                    <div>Each edge means: past values of A help predict B. Tested pairwise — some links may be indirect (A→C→B shows as A→B).</div>
                  )}
                  {currentGraph.algorithm === "rpcmci" && (
                    <div>Same as PCMCI+ but run on a specific market regime (normal/crisis). Causal relationships can differ across regimes.</div>
                  )}
                  {currentGraph.parameters.scoring === "zscore" && (
                    <div>Scored by <span className="text-gray-300">z-score</span>: how unusual is each factor vs its 90-day average? Edge = unusual moves in A predict unusual moves in B.</div>
                  )}
                  {currentGraph.parameters.scoring === "returns" && (
                    <div>Scored by <span className="text-gray-300">daily returns</span>: day-to-day price changes. Edge = A&apos;s move today predicts B&apos;s move tomorrow.</div>
                  )}
                  {currentGraph.parameters.scoring === "volatility" && (
                    <div>Scored by <span className="text-gray-300">20-day volatility</span>: how choppy is each factor? Edge = A getting volatile predicts B getting volatile.</div>
                  )}
                  <div>
                    <span className="text-gray-300">Most connected</span> = hub factors that influence or are influenced by many others.{" "}
                    <span className="text-gray-300">Confirmed</span> = edges that passed an independent statistical validation test.
                  </div>
                </div>
              )}

              {/* Saved snapshots (deduplicated: latest per run_name) */}
              {snapshots.length > 0 && (
                <div>
                  <div className="text-[10px] text-gray-500 uppercase mb-1">
                    Saved Snapshots
                  </div>
                  <div className="max-h-32 overflow-y-auto space-y-1">
                    {uniqueSnapshots.map((s) => (
                      <button
                        key={s.id}
                        onClick={() => loadGraph(s.id)}
                        className={`w-full text-left px-2 py-1.5 rounded text-[11px] transition-colors ${
                          currentGraph?.id === s.id
                            ? "bg-purple-900/50 text-purple-300 border border-purple-700/50"
                            : "bg-gray-800/60 text-gray-400 hover:bg-gray-700/60 hover:text-gray-300"
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-medium truncate">
                            {s.algorithm}_{String((s.parameters as Record<string, unknown>)?.scoring ?? "zscore")}
                          </span>
                          <span className="text-[9px] text-gray-500 ml-1 flex-shrink-0">
                            {s.node_count}n · {s.edge_count}e
                          </span>
                        </div>
                        <div className="text-[9px] text-gray-500">
                          {new Date(s.created_at).toLocaleString()}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Error */}
              {error && (
                <div className="mt-2 bg-red-900/50 border border-red-700/50 rounded p-2">
                  <div className="text-[10px] text-red-300 flex justify-between items-start">
                    <span>{error}</span>
                    <button
                      onClick={() => setError(null)}
                      className="text-red-500 hover:text-red-300 ml-1 flex-shrink-0"
                    >
                      x
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
