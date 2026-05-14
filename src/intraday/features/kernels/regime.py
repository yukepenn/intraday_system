"""Simple regime-style market facts (no strategy decisions)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix
from intraday.features.kernels.session_ops import (
    rolling_mean_session,
    session_start_indices,
    trend_slope_lag_session,
)


def compute_regime_group(bars: BarMatrix, cfg: Mapping[str, Any]) -> dict[str, np.ndarray]:
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    close = bars.close.astype(np.float64, copy=False)
    sid = bars.session_id
    starts = session_start_indices(sid)

    windows = [int(x) for x in (cfg.get("windows") or [])]
    out: dict[str, np.ndarray] = {}

    for w in windows:
        if "close_vs_rolling_mean" in outputs:
            rm = rolling_mean_session(close, sid, starts, w)
            out[f"close_vs_rolling_mean_{w}"] = close - rm
        if "trend_slope_like" in outputs:
            out[f"trend_slope_like_{w}"] = trend_slope_lag_session(close, starts, w)

    return out
