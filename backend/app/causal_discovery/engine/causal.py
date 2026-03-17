"""Causal discovery algorithms.

Supported: PCMCI+ (tigramite), VARLiNGAM (lingam), PC (causal-learn),
GES (causal-learn), Granger causality network (statsmodels).

All functions use lazy imports so the module can be imported even when
optional packages are not installed.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def discover_edges_pcmci(
    df: pd.DataFrame,
    max_lag: int = 5,
    significance_level: float = 0.01,
) -> list[dict[str, Any]]:
    """Run PCMCI+ with ParCorr on a daily matrix and return discovered edges.

    Parameters
    ----------
    df : pd.DataFrame
        Aligned daily matrix (index=date, columns=node_id). NaNs should be
        forward-filled before calling.
    max_lag : int
        Maximum time lag to test.
    significance_level : float
        P-value threshold for significant links.

    Returns
    -------
    list[dict]
        Each dict has keys: source, target, weight (abs val_matrix entry),
        lag, direction ("positive" | "negative").
    """
    import tigramite
    from tigramite import data_processing as pp
    from tigramite.pcmci import PCMCI
    from tigramite.independence_tests.parcorr import ParCorr

    columns = list(df.columns)
    data = df.values.astype(np.float64)

    # Build tigramite dataframe
    dataframe = pp.DataFrame(data, var_names=columns)

    # Run PCMCI+
    parcorr = ParCorr(significance="analytic")
    pcmci = PCMCI(dataframe=dataframe, cond_ind_test=parcorr, verbosity=0)
    results = pcmci.run_pcmciplus(tau_min=0, tau_max=max_lag, pc_alpha=significance_level)

    # Extract significant edges
    p_matrix = results["p_matrix"]
    val_matrix = results["val_matrix"]
    n_vars = len(columns)

    edges: list[dict[str, Any]] = []
    for i in range(n_vars):
        for j in range(n_vars):
            if i == j:
                continue
            for lag in range(1, max_lag + 1):
                p_val = p_matrix[i, j, lag]
                val = val_matrix[i, j, lag]
                if p_val < significance_level and abs(val) > 0.0:
                    edges.append({
                        "source": columns[i],
                        "target": columns[j],
                        "weight": float(abs(val)),
                        "lag": int(lag),
                        "direction": "positive" if val > 0 else "negative",
                    })

    # Also check contemporaneous (lag=0) links — directed by PCMCI+
    for i in range(n_vars):
        for j in range(i + 1, n_vars):
            p_val = p_matrix[i, j, 0]
            val = val_matrix[i, j, 0]
            if p_val < significance_level and abs(val) > 0.0:
                edges.append({
                    "source": columns[i],
                    "target": columns[j],
                    "weight": float(abs(val)),
                    "lag": 0,
                    "direction": "positive" if val > 0 else "negative",
                })

    logger.info("PCMCI+ discovered %d edges from %d variables", len(edges), n_vars)
    return edges


def discover_edges_varlingam(
    df: pd.DataFrame,
    max_lag: int = 3,
    min_weight: float = 0.1,
) -> list[dict[str, Any]]:
    """Run VARLiNGAM on a daily matrix and return discovered edges.

    Parameters
    ----------
    df : pd.DataFrame
        Aligned daily matrix (index=date, columns=node_id).
    max_lag : int
        Maximum time lag for the VAR model.
    min_weight : float
        Minimum absolute weight to include an edge.

    Returns
    -------
    list[dict]
        Each dict has keys: source, target, weight, lag, direction.
    """
    import lingam

    columns = list(df.columns)
    data = df.values.astype(np.float64)

    model = lingam.VARLiNGAM(lags=max_lag)
    model.fit(data)

    edges: list[dict[str, Any]] = []
    n_vars = len(columns)

    # model.causal_order_ gives the causal ordering
    # model.adjacency_matrices_ is a list of (n_vars, n_vars) arrays for lag 0..max_lag
    for lag_idx, adj_matrix in enumerate(model.adjacency_matrices_):
        for i in range(n_vars):
            for j in range(n_vars):
                if i == j and lag_idx == 0:
                    continue
                val = adj_matrix[i, j]
                if abs(val) >= min_weight:
                    edges.append({
                        "source": columns[j],
                        "target": columns[i],
                        "weight": float(abs(val)),
                        "lag": int(lag_idx),
                        "direction": "positive" if val > 0 else "negative",
                    })

    logger.info("VARLiNGAM discovered %d edges from %d variables", len(edges), n_vars)
    return edges


def discover_edges_pc(
    df: pd.DataFrame,
    significance_level: float = 0.01,
    return_steps: bool = False,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Run PC algorithm (constraint-based, iterative edge elimination).

    Starts with a complete graph and removes edges that fail conditional
    independence tests. When return_steps=True, returns intermediate graphs
    at each conditioning set size — useful for animated visualization.

    Parameters
    ----------
    df : pd.DataFrame
        Aligned daily matrix (index=date, columns=node_id).
    significance_level : float
        P-value threshold for independence tests.
    return_steps : bool
        If True, returns {"final": edges, "steps": [edges_at_step_0, edges_at_step_1, ...]}
        where each step shows the graph after removing edges at that conditioning depth.

    Returns
    -------
    list[dict] or dict
        Edge list, or dict with "final" and "steps" if return_steps=True.
    """
    from causallearn.search.ConstraintBased.PC import pc
    from causallearn.utils.cit import fisherz

    columns = list(df.columns)
    data = df.values.astype(np.float64)
    n_vars = len(columns)

    if return_steps:
        # Run PC at increasing max conditioning set sizes to capture steps
        steps = []
        # Step 0: complete graph (all possible edges)
        all_edges = []
        for i in range(n_vars):
            for j in range(i + 1, n_vars):
                all_edges.append({
                    "source": columns[i], "target": columns[j],
                    "weight": 1.0, "lag": 0, "direction": "positive",
                })
        steps.append({"depth": -1, "label": "complete_graph", "edges": all_edges})

        for max_depth in range(0, min(n_vars - 1, 6)):
            try:
                cg = pc(data, alpha=significance_level, indep_test=fisherz,
                        depth=max_depth, verbose=False, show_progress=False)
                adj = cg.G.graph
                step_edges = _extract_pc_edges(adj, columns)
                steps.append({
                    "depth": max_depth,
                    "label": f"depth_{max_depth}",
                    "edges": step_edges,
                })
            except Exception as e:
                logger.warning("PC step depth=%d failed: %s", max_depth, e)
                break

        final_edges = steps[-1]["edges"] if steps else []
        logger.info("PC discovered %d edges from %d variables (%d steps)",
                     len(final_edges), n_vars, len(steps))
        return {"final": final_edges, "steps": steps}
    else:
        cg = pc(data, alpha=significance_level, indep_test=fisherz,
                verbose=False, show_progress=False)
        adj = cg.G.graph
        edges = _extract_pc_edges(adj, columns)
        logger.info("PC discovered %d edges from %d variables", len(edges), n_vars)
        return edges


def _extract_pc_edges(adj_matrix: np.ndarray, columns: list[str]) -> list[dict[str, Any]]:
    """Extract edges from causal-learn's adjacency matrix.

    causal-learn uses: adj[i,j] = -1 and adj[j,i] = 1 means i → j
                       adj[i,j] = -1 and adj[j,i] = -1 means i — j (undirected)
    """
    n = len(columns)
    edges = []
    seen = set()
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            key = (min(i, j), max(i, j))
            if key in seen:
                continue

            if adj_matrix[i, j] != 0 and adj_matrix[j, i] != 0:
                seen.add(key)
                # Determine direction
                if adj_matrix[i, j] == -1 and adj_matrix[j, i] == 1:
                    src, tgt = columns[i], columns[j]
                elif adj_matrix[j, i] == -1 and adj_matrix[i, j] == 1:
                    src, tgt = columns[j], columns[i]
                else:
                    # Undirected — pick alphabetical order
                    src, tgt = sorted([columns[i], columns[j]])

                edges.append({
                    "source": src, "target": tgt,
                    "weight": 1.0,  # PC doesn't output weights
                    "lag": 0,
                    "direction": "positive",  # PC doesn't output sign
                })
    return edges


def discover_edges_ges(
    df: pd.DataFrame,
    score_func: str = "local_score_BIC",
) -> list[dict[str, Any]]:
    """Run GES (Greedy Equivalence Search) — score-based structure learning.

    GES searches over DAG equivalence classes by greedily adding then removing
    edges to optimize BIC score. Different philosophy from constraint-based PC.

    Parameters
    ----------
    df : pd.DataFrame
        Aligned daily matrix.
    score_func : str
        Scoring function: 'local_score_BIC' or 'local_score_BDeu'.

    Returns
    -------
    list[dict]
        Edge list with source, target, weight, lag, direction.
    """
    from causallearn.search.ScoreBased.GES import ges

    columns = list(df.columns)
    data = df.values.astype(np.float64)

    result = ges(data, score_func=score_func)
    adj = result["G"].graph

    edges = _extract_pc_edges(adj, columns)  # Same adjacency format as PC
    logger.info("GES discovered %d edges from %d variables", len(edges), len(columns))
    return edges


def discover_edges_granger(
    df: pd.DataFrame,
    max_lag: int = 5,
    significance_level: float = 0.01,
) -> list[dict[str, Any]]:
    """Build a Granger causality network via pairwise VAR Granger tests.

    Tests every pair (A, B): does past A help predict B beyond B's own past?
    Simple baseline — doesn't control for confounders like PCMCI+ does.

    Parameters
    ----------
    df : pd.DataFrame
        Aligned daily matrix.
    max_lag : int
        Maximum lag for Granger test.
    significance_level : float
        P-value threshold.

    Returns
    -------
    list[dict]
        Edge list with source, target, weight (1 - p_value), lag, direction.
    """
    from statsmodels.tsa.stattools import grangercausalitytests

    columns = list(df.columns)
    n_vars = len(columns)
    edges: list[dict[str, Any]] = []

    for i in range(n_vars):
        for j in range(n_vars):
            if i == j:
                continue
            try:
                # Test: does column[i] Granger-cause column[j]?
                pair_data = df[[columns[j], columns[i]]].dropna()
                if len(pair_data) < max_lag + 10:
                    continue
                result = grangercausalitytests(pair_data.values, maxlag=max_lag, verbose=False)

                # Find the best (most significant) lag
                best_p = 1.0
                best_lag = 1
                for lag in range(1, max_lag + 1):
                    p_val = result[lag][0]["ssr_ftest"][1]  # F-test p-value
                    if p_val < best_p:
                        best_p = p_val
                        best_lag = lag

                if best_p < significance_level:
                    # Determine direction from correlation sign
                    corr = df[columns[i]].corr(df[columns[j]])
                    edges.append({
                        "source": columns[i],
                        "target": columns[j],
                        "weight": round(1.0 - best_p, 4),  # Higher = more significant
                        "lag": best_lag,
                        "direction": "positive" if corr > 0 else "negative",
                    })
            except Exception:
                continue  # Skip pairs that fail (singular matrices, etc.)

    logger.info("Granger network: %d edges from %d variables", len(edges), n_vars)
    return edges


def discover_edges_rpcmci(
    df: pd.DataFrame,
    max_lag: int = 5,
    significance_level: float = 0.01,
) -> list[tuple[int, list[dict[str, Any]], tuple[int, int]]]:
    """Run regime-aware PCMCI+: detect change points, then run PCMCI+ per segment.

    Uses ``ruptures.Pelt`` (RBF kernel) to automatically detect regime change
    points in the raw data, splits into segments, and runs
    :func:`discover_edges_pcmci` independently on each segment.

    Parameters
    ----------
    df : pd.DataFrame
        Aligned daily matrix (index=date, columns=node_id). NaNs should be
        forward-filled before calling.
    max_lag : int
        Maximum time lag passed to PCMCI+ for each segment.
    significance_level : float
        P-value threshold for significant links in PCMCI+.

    Returns
    -------
    list[tuple[int, list[dict], tuple[int, int]]]
        Each tuple is ``(regime_index, edges, (start_idx, end_idx))``.
        ``edges`` is the list of edge dicts returned by :func:`discover_edges_pcmci`.
    """
    import ruptures

    # Forward-fill NaNs and drop any remaining (leading) NaN rows
    df = df.ffill().dropna()
    data = df.values.astype(np.float64)
    n_rows = len(data)

    # MIN_SEGMENT: PCMCI+ needs enough rows for statistical tests.
    # With max_lag=5 and ~40 variables, 30 rows is the practical floor.
    MIN_SEGMENT = max(30, max_lag * 3)

    # --- Detect change points with PELT (RBF kernel) -----------------------
    # pen=5 balances sensitivity vs overfitting for financial data
    algo = ruptures.Pelt(model="rbf").fit(data)
    breakpoints = algo.predict(pen=5)

    # ruptures returns breakpoints as indices where segments end; the last
    # element is always n_rows.  Convert to segment boundaries.
    if breakpoints and breakpoints[-1] == n_rows:
        breakpoints = breakpoints[:-1]

    # Build raw segment boundaries
    if not breakpoints:
        raw_bounds = [(0, n_rows)]
    else:
        raw_bounds = []
        prev = 0
        for bp in breakpoints:
            raw_bounds.append((prev, bp))
            prev = bp
        raw_bounds.append((prev, n_rows))

    # --- Merge tiny segments with neighbours --------------------------------
    merged_bounds: list[tuple[int, int]] = []
    for start, end in raw_bounds:
        if merged_bounds and (end - start) < MIN_SEGMENT:
            # Merge with the previous segment
            prev_start, _ = merged_bounds.pop()
            merged_bounds.append((prev_start, end))
        else:
            merged_bounds.append((start, end))

    # Check if the last segment ended up too small after merging
    if len(merged_bounds) > 1:
        last_start, last_end = merged_bounds[-1]
        if (last_end - last_start) < MIN_SEGMENT:
            prev_start, _ = merged_bounds[-2]
            merged_bounds = merged_bounds[:-2]
            merged_bounds.append((prev_start, last_end))

    # --- Fallback: single segment → run PCMCI+ on full data -----------------
    if len(merged_bounds) <= 1:
        edges = discover_edges_pcmci(df, max_lag=max_lag, significance_level=significance_level)
        logger.info("RPCMCI: no regime splits — single-regime fallback (%d edges)", len(edges))
        return [(0, edges, (0, n_rows))]

    # --- Run PCMCI+ per segment ---------------------------------------------
    results: list[tuple[int, list[dict[str, Any]], tuple[int, int]]] = []
    for regime_idx, (seg_start, seg_end) in enumerate(merged_bounds):
        seg_df = df.iloc[seg_start:seg_end]
        if len(seg_df) < MIN_SEGMENT:
            logger.warning("RPCMCI: skipping regime %d — only %d rows", regime_idx, len(seg_df))
            continue
        try:
            edges = discover_edges_pcmci(seg_df, max_lag=max_lag, significance_level=significance_level)
        except Exception:
            logger.exception("RPCMCI: PCMCI+ failed on regime %d (%d–%d)", regime_idx, seg_start, seg_end)
            edges = []
        results.append((regime_idx, edges, (seg_start, seg_end)))

    logger.info("RPCMCI: %d regimes, %d total edges",
                len(results), sum(len(e) for _, e, _ in results))
    return results
