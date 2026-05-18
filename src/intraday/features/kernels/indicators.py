"""Generic CCI and stochastic indicators (same-session, current-inclusive)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix
from intraday.features.kernels.session_ops import (
    rolling_mean_session,
    session_start_indices,
)


def compute_indicators_group(bars: BarMatrix, cfg: Mapping[str, Any]) -> dict[str, np.ndarray]:
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    n = bars.n_bars
    high = bars.high.astype(np.float64, copy=False)
    low = bars.low.astype(np.float64, copy=False)
    close = bars.close.astype(np.float64, copy=False)
    sid = bars.session_id
    starts = session_start_indices(sid)

    typical = (high + low + close) / 3.0

    cci_windows = [int(x) for x in (cfg.get("cci_windows") or [])]
    stoch_windows = [int(x) for x in (cfg.get("stochastic_windows") or [])]
    stoch_smooth = [int(x) for x in (cfg.get("stochastic_smooth_windows") or [])]

    out: dict[str, np.ndarray] = {}

    if "cci" in outputs:
        for w in cci_windows:
            mean_tp = rolling_mean_session(typical, sid, starts, w)
            cci_arr = np.full(n, np.nan, dtype=np.float64)
            for i in range(n):
                s0 = int(starts[i])
                lo = max(s0, i - w + 1)
                seg = typical[lo : i + 1]
                if seg.size < w:
                    continue
                m = float(mean_tp[i])
                if not np.isfinite(m):
                    continue
                dev = float(np.mean(np.abs(seg - m)))
                if dev <= 0.0 or not np.isfinite(dev):
                    continue
                cci_arr[i] = (float(typical[i]) - m) / (0.015 * dev)
            out[f"cci_{w}"] = cci_arr

    if "stoch_k" in outputs or "stoch_d" in outputs:
        for w in stoch_windows:
            stoch_k = np.full(n, np.nan, dtype=np.float64)
            for i in range(n):
                s0 = int(starts[i])
                lo = max(s0, i - w + 1)
                seg_h = high[lo : i + 1]
                seg_l = low[lo : i + 1]
                if seg_h.size < w:
                    continue
                hh = float(np.max(seg_h))
                ll = float(np.min(seg_l))
                rng = hh - ll
                if rng <= 0.0 or not np.isfinite(rng):
                    continue
                stoch_k[i] = 100.0 * (float(close[i]) - ll) / rng

            if "stoch_k" in outputs:
                out[f"stoch_k_{w}"] = stoch_k

            if "stoch_d" in outputs:
                for sm in stoch_smooth:
                    stoch_d = rolling_mean_session(stoch_k, sid, starts, sm)
                    out[f"stoch_d_{w}_{sm}"] = stoch_d

    return out
