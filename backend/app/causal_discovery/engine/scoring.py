"""Scoring functions for daily matrix columns.

Each function transforms raw daily values into a score suitable for causal
discovery. Different scores produce different networks — z-score captures
deviation from normal, returns capture day-to-day movement, volatility
captures fear/contagion transmission.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def compute_rolling_zscore(
    df: pd.DataFrame,
    window: int = 90,
    clamp: float | None = 3.0,
) -> pd.DataFrame:
    """Rolling z-score: how unusual is the current value relative to recent history.

    Network meaning: "when A is unusually high, does B become unusually high?"
    """
    min_periods = max(1, window // 4)
    rolling_mean = df.rolling(window=window, min_periods=min_periods).mean()
    rolling_std = df.rolling(window=window, min_periods=min_periods).std()
    rolling_std = rolling_std.replace(0, float("nan"))
    zscores = (df - rolling_mean) / rolling_std
    zscores = zscores.fillna(0.0)
    if clamp is not None:
        zscores = zscores.clip(lower=-clamp, upper=clamp)
    return zscores


def compute_log_returns(
    df: pd.DataFrame,
    clamp: float | None = 0.2,
) -> pd.DataFrame:
    """Log returns: daily percentage change (log-scaled).

    Network meaning: "when A moves up today, does B move up tomorrow?"
    Standard in quantitative finance — handles compounding and large moves better
    than simple returns.
    """
    log_ret = np.log(df / df.shift(1))
    log_ret = log_ret.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if clamp is not None:
        log_ret = log_ret.clip(lower=-clamp, upper=clamp)
    return log_ret


def compute_rolling_volatility(
    df: pd.DataFrame,
    window: int = 20,
    annualize: bool = False,
) -> pd.DataFrame:
    """Rolling volatility: how jumpy each factor is (rolling std of log returns).

    Network meaning: "when A gets volatile, does B get volatile?" — captures
    fear contagion and risk transmission. VIX and credit spreads become central hubs.
    """
    log_ret = np.log(df / df.shift(1))
    log_ret = log_ret.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    min_periods = max(1, window // 4)
    vol = log_ret.rolling(window=window, min_periods=min_periods).std()
    if annualize:
        vol = vol * np.sqrt(252)
    vol = vol.fillna(0.0)
    return vol


# Registry of available scoring functions
SCORING_FUNCTIONS = {
    "zscore": compute_rolling_zscore,
    "returns": compute_log_returns,
    "volatility": compute_rolling_volatility,
}


def compute_scores(
    df: pd.DataFrame,
    method: str = "zscore",
    **kwargs,
) -> pd.DataFrame:
    """Compute scores using the named method.

    Parameters
    ----------
    df : pd.DataFrame
        Raw daily matrix (index=date, columns=node_id).
    method : str
        One of: 'zscore', 'returns', 'volatility'.
    **kwargs
        Passed to the scoring function (e.g., window=90, clamp=3.0).

    Returns
    -------
    pd.DataFrame
        Scored matrix, same shape as input.
    """
    func = SCORING_FUNCTIONS.get(method)
    if func is None:
        raise ValueError(f"Unknown scoring method '{method}'. Available: {list(SCORING_FUNCTIONS.keys())}")
    return func(df, **kwargs)
