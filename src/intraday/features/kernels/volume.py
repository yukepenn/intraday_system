"""Volume market facts (session-contained rolling mean, relative volume)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix
from intraday.features.kernels.session_ops import rolling_mean_session, session_start_indices


def compute_volume_group(bars: BarMatrix, cfg: Mapping[str, Any]) -> dict[str, np.ndarray]:
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    vol = bars.volume.astype(np.float64, copy=False)
    sid = bars.session_id
    starts = session_start_indices(sid)

    out: dict[str, np.ndarray] = {}
    roll_wins = [int(x) for x in (cfg.get("rolling_windows") or [])]

    for w in roll_wins:
        vm = rolling_mean_session(vol, sid, starts, w)
        if "volume_mean" in outputs:
            out[f"volume_mean_{w}"] = vm
        if "rel_volume" in outputs:
            rel = np.full_like(vol, np.nan, dtype=np.float64)
            for i in range(int(vol.shape[0])):
                m = float(vm[i])
                if m > 0.0:
                    rel[i] = float(vol[i]) / m
            out[f"rel_volume_{w}"] = rel

    return out
