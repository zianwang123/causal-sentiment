"""DoWhy edge validation engine.

Validates discovered causal edges by computing arrow strength (causal
contribution) via DoWhy GCM and running conditional independence refutation
tests via partial correlation (OLS residualization + Pearson r).

Uses lazy imports so the module can be imported even when optional packages
are not installed.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Minimum data requirements
# ---------------------------------------------------------------------------
_MIN_ROWS = 30  # need enough rows for OLS residualization to be meaningful


def validate_edges(
    edges: list[dict[str, Any]],
    data_matrix: pd.DataFrame,
    dag: Any,
) -> list[dict[str, Any]]:
    """Validate discovered edges using DoWhy arrow strength and CI tests.

    For each edge, computes ``arrow_strength`` (causal contribution of the
    source to the target) and runs a conditional independence refutation test
    (partial correlation via OLS residualization).

    Parameters
    ----------
    edges : list[dict]
        Each dict must have at least ``source`` and ``target`` keys.
    data_matrix : pd.DataFrame
        Aligned daily matrix (index=date, columns=node_id).  NaNs should be
        forward-filled before calling.
    dag : networkx.DiGraph
        The directed acyclic graph that was used to discover the edges.

    Returns
    -------
    list[dict]
        A copy of *edges* where every dict is enriched with a ``validation``
        field.  On success the field is::

            {"arrow_strength": float,
             "refutation_passed": bool,
             "ci_test_p_value": float}

        On failure (too few rows, numerical issues, etc.) the field is
        ``None``.
    """
    import networkx as nx

    if len(data_matrix) < _MIN_ROWS:
        logger.warning(
            "Data matrix has only %d rows (need >= %d) — "
            "skipping validation, returning null for all edges",
            len(data_matrix),
            _MIN_ROWS,
        )
        return [_edge_with_validation(e, None) for e in edges]

    # ------------------------------------------------------------------
    # 1. Check if graph is a DAG (no cycles). DoWhy SCM requires a DAG.
    #    If cyclic, skip arrow_strength and use CI tests only.
    # ------------------------------------------------------------------
    is_dag = nx.is_directed_acyclic_graph(dag)
    scm = None
    strength_cache: dict[str, dict[tuple[str, str], float]] = {}

    if is_dag:
        scm = _build_and_fit_scm(dag, data_matrix)
        if scm is not None:
            _compute_arrow_strengths(scm, edges, data_matrix, strength_cache)
        else:
            logger.warning("SCM fitting failed on DAG — using CI tests only")
    else:
        logger.info(
            "Graph has cycles (%d nodes, %d edges) — "
            "skipping DoWhy SCM, using CI tests only",
            dag.number_of_nodes(), dag.number_of_edges(),
        )

    # ------------------------------------------------------------------
    # 2. For each edge: look up strength (if available) + run CI test
    # ------------------------------------------------------------------
    validated: list[dict[str, Any]] = []
    for edge in edges:
        try:
            src, tgt = edge["source"], edge["target"]

            # Arrow strength (only available if DAG + SCM succeeded)
            strength = None
            target_strengths = strength_cache.get(tgt)
            if target_strengths is not None:
                strength = target_strengths.get((src, tgt))

            # CI test via partial correlation (works regardless of cycles)
            p_value = _partial_correlation_test(
                src, tgt, dag, data_matrix,
            )
            if p_value is None:
                validated.append(_edge_with_validation(edge, None))
                continue

            # An edge passes if variables ARE dependent (p < 0.05)
            # AND (if we have arrow_strength) the causal contribution is non-trivial.
            if strength is not None:
                refutation_passed = abs(strength) > 0.01 and p_value < 0.05
            else:
                # No arrow_strength available — use CI test alone
                refutation_passed = p_value < 0.05

            validated.append(_edge_with_validation(edge, {
                "arrow_strength": round(float(strength), 4) if strength is not None else 0.0,
                "refutation_passed": bool(refutation_passed),
                "ci_test_p_value": float(p_value),
            }))
        except Exception:
            logger.exception("Validation failed for edge %s→%s", edge.get("source"), edge.get("target"))
            validated.append(_edge_with_validation(edge, None))

    logger.info(
        "Validated %d/%d edges (passed: %d)",
        sum(1 for e in validated if e["validation"] is not None),
        len(validated),
        sum(1 for e in validated if e["validation"] and e["validation"]["refutation_passed"]),
    )
    return validated


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _edge_with_validation(
    edge: dict[str, Any],
    validation: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return a shallow copy of *edge* with a ``validation`` field added."""
    out = dict(edge)
    out["validation"] = validation
    return out


def _build_and_fit_scm(
    dag: Any,
    data_matrix: pd.DataFrame,
) -> Any | None:
    """Build a DoWhy StructuralCausalModel, assign mechanisms, and fit."""
    try:
        import dowhy.gcm as gcm

        scm = gcm.StructuralCausalModel(dag)
        gcm.auto.assign_causal_mechanisms(scm, based_on=data_matrix)
        gcm.fit(scm, data_matrix)
        return scm
    except Exception:
        logger.exception("Failed to build/fit DoWhy SCM")
        return None


def _compute_arrow_strengths(
    scm: Any,
    edges: list[dict[str, Any]],
    data_matrix: pd.DataFrame,
    cache: dict[str, dict[tuple[str, str], float]],
) -> None:
    """Compute arrow strengths, caching results by target node.

    DoWhy's ``arrow_strength`` returns strengths for *all* incoming edges
    of a target node at once, so we only call it once per unique target.
    """
    import dowhy.gcm as gcm

    targets_seen: set[str] = set()
    for edge in edges:
        tgt = edge["target"]
        if tgt in targets_seen:
            continue
        targets_seen.add(tgt)
        try:
            strengths = gcm.arrow_strength(
                scm,
                tgt,
                num_samples_conditional=500,
                max_num_runs=100,
                n_jobs=1,  # avoid multiprocessing overhead in small data
            )
            cache[tgt] = {k: float(v) for k, v in strengths.items()}
        except Exception:
            logger.exception("arrow_strength failed for target %s", tgt)
            cache[tgt] = None  # type: ignore[assignment]


def _partial_correlation_test(
    source: str,
    target: str,
    dag: Any,
    data_matrix: pd.DataFrame,
) -> float | None:
    """Conditional independence test via partial correlation.

    Conditions on all other parents of *target* in the DAG (excluding
    *source*).  Uses OLS residualization (numpy lstsq) followed by
    Pearson correlation (scipy pearsonr).

    Returns the p-value, or ``None`` on failure.  A low p-value (< 0.05)
    means the variables ARE dependent — i.e. the edge is real.
    """
    from scipy.stats import pearsonr

    try:
        # Conditioning set: other parents of target, excluding source
        parents = list(dag.predecessors(target))
        conditioning = [p for p in parents if p != source]

        src_vals = data_matrix[source].values.astype(np.float64)
        tgt_vals = data_matrix[target].values.astype(np.float64)

        if conditioning:
            # Residualize source and target on the conditioning set
            cond_matrix = data_matrix[conditioning].values.astype(np.float64)
            src_resid = _residualize(src_vals, cond_matrix)
            tgt_resid = _residualize(tgt_vals, cond_matrix)
        else:
            # No conditioning set — plain correlation
            src_resid = src_vals
            tgt_resid = tgt_vals

        _, p_value = pearsonr(src_resid, tgt_resid)
        return float(p_value)
    except Exception:
        logger.exception(
            "Partial correlation test failed for %s→%s", source, target,
        )
        return None


def _residualize(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    """OLS residualization: regress *y* on *X* and return residuals."""
    # Add intercept column
    n = X.shape[0]
    X_aug = np.column_stack([np.ones(n), X])
    coeffs, _, _, _ = np.linalg.lstsq(X_aug, y, rcond=None)
    return y - X_aug @ coeffs
