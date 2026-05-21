"""No-lookahead tests for Phase19A Brooks Slice F1 features."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from intraday.core.config import load_yaml
from intraday.features.engine import build_feature_matrix

from tests.helpers.bars import make_bar_matrix

REPO = Path(__file__).resolve().parents[2]
CORE_CONFIG = REPO / "configs" / "features" / "pa_brooks_core_v1.yaml"
RANGE_CONFIG = REPO / "configs" / "features" / "pa_brooks_range_v1.yaml"


def _bars(n: int = 140):
    open_ = [100.0 + np.sin(i / 7.0) + i * 0.02 for i in range(n)]
    close = [o + (0.3 if i % 4 in (1, 2) else -0.25) for i, o in enumerate(open_)]
    high = [max(o, c) + 0.5 for o, c in zip(open_, close, strict=True)]
    low = [min(o, c) - 0.5 for o, c in zip(open_, close, strict=True)]
    return make_bar_matrix(open_, high, low, close, minute=list(range(n)))


def _perturb_future(bars, t: int):
    open_ = np.array(bars.open, copy=True)
    high = np.array(bars.high, copy=True)
    low = np.array(bars.low, copy=True)
    close = np.array(bars.close, copy=True)
    open_[t + 1 :] += 1000.0
    high[t + 1 :] += 1000.0
    low[t + 1 :] += 1000.0
    close[t + 1 :] += 1000.0
    return make_bar_matrix(
        open_.tolist(),
        high.tolist(),
        low.tolist(),
        close.tolist(),
        session_id=bars.session_id.tolist(),
        minute=bars.minute.tolist(),
        session_date=bars.session_date.tolist(),
        ts_ns=bars.ts_ns,
    )


def test_core_features_do_not_change_when_future_bars_are_perturbed() -> None:
    bars = _bars()
    t = 95
    base = build_feature_matrix(bars, load_yaml(CORE_CONFIG), use_cache=False)
    perturbed = build_feature_matrix(
        _perturb_future(bars, t), load_yaml(CORE_CONFIG), use_cache=False
    )
    np.testing.assert_allclose(base.values[: t + 1], perturbed.values[: t + 1], equal_nan=True)


def test_range_features_do_not_change_when_future_bars_are_perturbed() -> None:
    bars = _bars()
    t = 95
    base = build_feature_matrix(bars, load_yaml(RANGE_CONFIG), use_cache=False)
    perturbed = build_feature_matrix(
        _perturb_future(bars, t), load_yaml(RANGE_CONFIG), use_cache=False
    )
    np.testing.assert_allclose(base.values[: t + 1], perturbed.values[: t + 1], equal_nan=True)
