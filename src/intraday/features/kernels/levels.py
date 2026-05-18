"""Prior-session levels and gap market facts (session-local, no lookahead)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix


def compute_levels_group(bars: BarMatrix, cfg: Mapping[str, Any]) -> dict[str, np.ndarray]:
    """Prior-session OHLC and distance/gap facts.

    - First session in the series: prior_session_* are NaN.
    - Within a session, prior_session_* are constant (forward-filled from session open).
    - open_gap_pct uses session open (first bar) vs prior session close.
    - dist_to_prior_*_pct uses current close vs prior session level.
    """
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    n = bars.n_bars
    open_ = bars.open.astype(np.float64, copy=False)
    high = bars.high.astype(np.float64, copy=False)
    low = bars.low.astype(np.float64, copy=False)
    close = bars.close.astype(np.float64, copy=False)
    sid = bars.session_id

    session_order: list[int] = []
    stats: dict[int, dict[str, float]] = {}
    for i in range(n):
        s = int(sid[i])
        if s not in stats:
            session_order.append(s)
            stats[s] = {
                "open": float(open_[i]),
                "high": float(high[i]),
                "low": float(low[i]),
                "close": float(close[i]),
            }
        else:
            st = stats[s]
            st["high"] = max(st["high"], float(high[i]))
            st["low"] = min(st["low"], float(low[i]))
            st["close"] = float(close[i])

    prior_for_sid: dict[int, dict[str, float] | None] = {}
    for idx, s in enumerate(session_order):
        if idx == 0:
            prior_for_sid[s] = None
        else:
            prior_for_sid[s] = stats[session_order[idx - 1]]

    out: dict[str, np.ndarray] = {}
    if "prior_session_open" in outputs:
        out["prior_session_open"] = np.full(n, np.nan, dtype=np.float64)
    if "prior_session_high" in outputs:
        out["prior_session_high"] = np.full(n, np.nan, dtype=np.float64)
    if "prior_session_low" in outputs:
        out["prior_session_low"] = np.full(n, np.nan, dtype=np.float64)
    if "prior_session_close" in outputs:
        out["prior_session_close"] = np.full(n, np.nan, dtype=np.float64)
    if "open_gap_pct" in outputs:
        out["open_gap_pct"] = np.full(n, np.nan, dtype=np.float64)
    if "dist_to_prior_high_pct" in outputs:
        out["dist_to_prior_high_pct"] = np.full(n, np.nan, dtype=np.float64)
    if "dist_to_prior_low_pct" in outputs:
        out["dist_to_prior_low_pct"] = np.full(n, np.nan, dtype=np.float64)
    if "dist_to_prior_close_pct" in outputs:
        out["dist_to_prior_close_pct"] = np.full(n, np.nan, dtype=np.float64)

    for i in range(n):
        s = int(sid[i])
        prior = prior_for_sid[s]
        cur = stats[s]
        if prior is not None:
            if "prior_session_open" in out:
                out["prior_session_open"][i] = prior["open"]
            if "prior_session_high" in out:
                out["prior_session_high"][i] = prior["high"]
            if "prior_session_low" in out:
                out["prior_session_low"][i] = prior["low"]
            if "prior_session_close" in out:
                out["prior_session_close"][i] = prior["close"]

            pc = prior["close"]
            if "open_gap_pct" in out and np.isfinite(pc) and pc != 0.0:
                out["open_gap_pct"][i] = (cur["open"] - pc) / pc

            c = float(close[i])
            if "dist_to_prior_high_pct" in out:
                ph = prior["high"]
                if np.isfinite(ph) and ph != 0.0:
                    out["dist_to_prior_high_pct"][i] = (c - ph) / ph
            if "dist_to_prior_low_pct" in out:
                pl = prior["low"]
                if np.isfinite(pl) and pl != 0.0:
                    out["dist_to_prior_low_pct"][i] = (c - pl) / pl
            if "dist_to_prior_close_pct" in out:
                if np.isfinite(pc) and pc != 0.0:
                    out["dist_to_prior_close_pct"][i] = (c - pc) / pc

    return out
