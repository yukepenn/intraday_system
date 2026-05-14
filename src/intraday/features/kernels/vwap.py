"""Session VWAP reference kernel (Phase 4)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix


def _price_at(bars: BarMatrix, i: int, price: str) -> float:
    h = float(bars.high[i])
    lo_px = float(bars.low[i])
    c = float(bars.close[i])
    if price == "hlc3":
        return (h + lo_px + c) / 3.0
    if price == "close":
        return c
    raise ValueError(f"unsupported VWAP price mode: {price!r}")


def compute_vwap_group(bars: BarMatrix, cfg: Mapping[str, Any]) -> dict[str, np.ndarray]:
    """Session-reset VWAP and distance metrics (current bar included)."""
    n = bars.n_bars
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    price_mode = str(cfg.get("price", "hlc3"))

    vwap = np.full(n, np.nan, dtype=np.float64)
    cum_pv = 0.0
    cum_vol = 0.0
    cur_sid: int | None = None
    for i in range(n):
        sid = int(bars.session_id[i])
        if cur_sid is None or sid != cur_sid:
            cur_sid = sid
            cum_pv = 0.0
            cum_vol = 0.0
        p = _price_at(bars, i, price_mode)
        v = float(bars.volume[i])
        cum_pv += p * v
        cum_vol += v
        if cum_vol <= 0.0:
            vwap[i] = np.nan
        else:
            vwap[i] = cum_pv / cum_vol

    out: dict[str, np.ndarray] = {}
    if "vwap" in outputs:
        out["vwap"] = vwap.copy()

    close = bars.close.astype(np.float64, copy=False)
    if "vwap_dist" in outputs:
        out["vwap_dist"] = np.where(np.isfinite(vwap), close - vwap, np.nan)

    if "vwap_dist_pct" in outputs:
        pct = np.full(n, np.nan, dtype=np.float64)
        for i in range(n):
            vw = vwap[i]
            if not np.isfinite(vw) or vw == 0.0:
                continue
            pct[i] = (float(close[i]) - float(vw)) / float(vw)
        out["vwap_dist_pct"] = pct

    if "vwap_side" in outputs:
        side = np.full(n, np.nan, dtype=np.float64)
        for i in range(n):
            vw = vwap[i]
            if not np.isfinite(vw):
                continue
            ci = float(close[i])
            if ci > vw:
                side[i] = 1.0
            elif ci < vw:
                side[i] = -1.0
            else:
                side[i] = 0.0
        out["vwap_side"] = side

    return out
