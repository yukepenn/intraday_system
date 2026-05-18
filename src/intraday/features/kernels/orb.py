"""Opening range (ORB) reference kernel — session-local, no future bars."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix
from intraday.features.kernels.session_ops import session_start_indices


def compute_orb_group(bars: BarMatrix, cfg: Mapping[str, Any]) -> dict[str, np.ndarray]:
    """ORB high/low/mid/range for each ``open_minutes`` value.

    Deterministic rule (Phase 4):
    - Opening range uses bars in the current session with ``0 <= minute < open_minutes``.
    - While ``minute[i] < open_minutes - 1``, ORB outputs are NaN (range not complete).
    - Once ``minute[i] >= open_minutes - 1``, aggregate max(high)/min(low) over session
      bars ``j <= i`` with ``0 <= minute[j] < open_minutes``; values stay constant for
      the rest of the session as more bars arrive outside the OR minute window.
    - If no qualifying bars exist when the gate opens (pathological data), outputs are NaN.
    """
    n = bars.n_bars
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    open_minutes_list = cfg.get("open_minutes") or [15]
    if isinstance(open_minutes_list, int | float):
        open_minutes_list = [int(open_minutes_list)]
    else:
        open_minutes_list = [int(x) for x in open_minutes_list]

    minute = bars.minute.astype(np.int64, copy=False)
    high = bars.high.astype(np.float64, copy=False)
    low = bars.low.astype(np.float64, copy=False)
    sid = bars.session_id
    starts = session_start_indices(sid)

    out: dict[str, np.ndarray] = {}

    for om in open_minutes_list:
        suf = f"_{om}"
        orb_high = np.full(n, np.nan, dtype=np.float64)
        orb_low = np.full(n, np.nan, dtype=np.float64)
        orb_mid = np.full(n, np.nan, dtype=np.float64)
        orb_range = np.full(n, np.nan, dtype=np.float64)

        for i in range(n):
            m = int(minute[i])
            if m < om - 1:
                continue
            s0 = int(starts[i])
            hi = -np.inf
            acc_low = np.inf
            for j in range(s0, i + 1):
                mj = int(minute[j])
                if 0 <= mj < om:
                    hi = max(hi, float(high[j]))
                    acc_low = min(acc_low, float(low[j]))
            if not np.isfinite(hi) or not np.isfinite(acc_low):
                continue
            orb_high[i] = hi
            orb_low[i] = acc_low
            mid = 0.5 * (hi + acc_low)
            rng = hi - acc_low
            orb_mid[i] = mid
            orb_range[i] = rng

        if "orb_high" in outputs:
            out[f"orb_high{suf}"] = orb_high
        if "orb_low" in outputs:
            out[f"orb_low{suf}"] = orb_low
        if "orb_mid" in outputs:
            out[f"orb_mid{suf}"] = orb_mid
        if "orb_range" in outputs:
            out[f"orb_range{suf}"] = orb_range

        if "orb_width_pct" in outputs:
            width_pct = np.full(n, np.nan, dtype=np.float64)
            for i in range(n):
                mid = orb_mid[i]
                if not np.isfinite(mid) or mid == 0.0:
                    continue
                rng = orb_range[i]
                if np.isfinite(rng):
                    width_pct[i] = rng / mid
            out[f"orb_width_pct{suf}"] = width_pct

    return out
