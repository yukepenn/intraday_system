"""Session-scoped NumPy helpers for feature kernels (Phase 4 reference)."""

from __future__ import annotations

import numpy as np


def session_start_indices(session_id: np.ndarray) -> np.ndarray:
    """For each bar index i, index of first bar in the same session."""
    n = int(session_id.shape[0])
    if n == 0:
        return np.zeros(0, dtype=np.int64)
    out = np.empty(n, dtype=np.int64)
    out[0] = 0
    sid = session_id
    for i in range(1, n):
        out[i] = i if sid[i] != sid[i - 1] else out[i - 1]
    return out


def rolling_mean_session(
    x: np.ndarray,
    session_id: np.ndarray,
    starts: np.ndarray,
    window: int,
) -> np.ndarray:
    n = int(x.shape[0])
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        s0 = int(starts[i])
        lo = max(s0, i - window + 1)
        out[i] = float(np.mean(x[lo : i + 1]))
    return out


def rolling_max_session(
    x: np.ndarray,
    session_id: np.ndarray,
    starts: np.ndarray,
    window: int,
) -> np.ndarray:
    n = int(x.shape[0])
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        s0 = int(starts[i])
        lo = max(s0, i - window + 1)
        out[i] = float(np.max(x[lo : i + 1]))
    return out


def rolling_min_session(
    x: np.ndarray,
    session_id: np.ndarray,
    starts: np.ndarray,
    window: int,
) -> np.ndarray:
    n = int(x.shape[0])
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        s0 = int(starts[i])
        lo = max(s0, i - window + 1)
        out[i] = float(np.min(x[lo : i + 1]))
    return out


def true_range_session(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    session_id: np.ndarray,
) -> np.ndarray:
    """True range with session-local prev_close (no cross-session lookback)."""
    n = int(high.shape[0])
    tr = np.empty(n, dtype=np.float64)
    for i in range(n):
        hl = float(high[i] - low[i])
        if i == 0 or session_id[i] != session_id[i - 1]:
            tr[i] = hl
        else:
            pc = float(close[i - 1])
            tr[i] = max(hl, abs(float(high[i]) - pc), abs(float(low[i]) - pc))
    return tr


def trend_slope_lag_session(
    close: np.ndarray,
    starts: np.ndarray,
    lag: int,
) -> np.ndarray:
    """close[i] - close[i-lag] when i-lag is in the same session, else NaN."""
    n = int(close.shape[0])
    out = np.full(n, np.nan, dtype=np.float64)
    for i in range(n):
        s0 = int(starts[i])
        j = i - lag
        if j < s0:
            continue
        out[i] = float(close[i] - close[j])
    return out
