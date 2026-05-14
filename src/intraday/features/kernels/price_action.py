"""Price-action market facts (wicks, body, rolling high/low)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix
from intraday.features.kernels.session_ops import (
    rolling_max_session,
    rolling_min_session,
    session_start_indices,
)


def compute_price_action_group(bars: BarMatrix, cfg: Mapping[str, Any]) -> dict[str, np.ndarray]:
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    open_ = bars.open.astype(np.float64, copy=False)
    high = bars.high.astype(np.float64, copy=False)
    low = bars.low.astype(np.float64, copy=False)
    close = bars.close.astype(np.float64, copy=False)
    sid = bars.session_id
    starts = session_start_indices(sid)

    n = int(bars.n_bars)
    bar_range = high - low
    safe_range = bar_range > 0.0

    out: dict[str, np.ndarray] = {}

    if "body_pct" in outputs:
        body = np.abs(close - open_)
        arr = np.full(n, np.nan, dtype=np.float64)
        np.divide(body, bar_range, out=arr, where=safe_range)
        out["body_pct"] = arr

    if "upper_wick_pct" in outputs:
        top = np.maximum(open_, close)
        w = high - top
        arr = np.full(n, np.nan, dtype=np.float64)
        np.divide(w, bar_range, out=arr, where=safe_range)
        out["upper_wick_pct"] = arr

    if "lower_wick_pct" in outputs:
        bot = np.minimum(open_, close)
        w = bot - low
        arr = np.full(n, np.nan, dtype=np.float64)
        np.divide(w, bar_range, out=arr, where=safe_range)
        out["lower_wick_pct"] = arr

    if "close_position_in_range" in outputs:
        arr = np.full(n, np.nan, dtype=np.float64)
        np.divide(close - low, bar_range, out=arr, where=safe_range)
        out["close_position_in_range"] = arr

    roll_wins = [int(x) for x in (cfg.get("rolling_windows") or [])]
    if "rolling_high" in outputs:
        for w in roll_wins:
            out[f"rolling_high_{w}"] = rolling_max_session(high, sid, starts, w)
    if "rolling_low" in outputs:
        for w in roll_wins:
            out[f"rolling_low_{w}"] = rolling_min_session(low, sid, starts, w)

    return out
