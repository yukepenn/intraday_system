"""Volatility-related market facts (session-contained rolling)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix
from intraday.features.kernels.session_ops import (
    rolling_mean_session,
    session_start_indices,
    true_range_session,
)


def compute_volatility_group(bars: BarMatrix, cfg: Mapping[str, Any]) -> dict[str, np.ndarray]:
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    high = bars.high.astype(np.float64, copy=False)
    low = bars.low.astype(np.float64, copy=False)
    close = bars.close.astype(np.float64, copy=False)
    sid = bars.session_id
    starts = session_start_indices(sid)

    bar_range = high - low
    tr = true_range_session(high, low, close, sid)

    out: dict[str, np.ndarray] = {}
    if "bar_range" in outputs:
        out["bar_range"] = bar_range.astype(np.float64, copy=True)
    if "true_range" in outputs:
        out["true_range"] = tr

    atr_windows = [int(x) for x in (cfg.get("atr_like_windows") or [])]
    range_windows = [int(x) for x in (cfg.get("range_windows") or [])]

    if "atr_like" in outputs:
        for w in atr_windows:
            rm = rolling_mean_session(tr, sid, starts, w)
            out[f"atr_like_{w}"] = rm

    if "range_mean" in outputs:
        for w in range_windows:
            rm = rolling_mean_session(bar_range, sid, starts, w)
            out[f"range_mean_{w}"] = rm

    return out
