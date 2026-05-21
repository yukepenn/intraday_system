"""Session-reset tests for Phase19A Brooks Slice F1 features."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from intraday.core.config import load_yaml
from intraday.features.engine import build_feature_matrix

from tests.helpers.bars import make_bar_matrix

REPO = Path(__file__).resolve().parents[2]
CORE_CONFIG = REPO / "configs" / "features" / "pa_brooks_core_v1.yaml"
RANGE_CONFIG = REPO / "configs" / "features" / "pa_brooks_range_v1.yaml"


def _two_session_bars():
    n_per = 100
    n = n_per * 2
    open_ = [100.0 + (i % n_per) * 0.05 for i in range(n)]
    close = [o + 0.2 for o in open_]
    high = [c + 0.4 for c in close]
    low = [o - 0.4 for o in open_]
    return make_bar_matrix(
        open_,
        high,
        low,
        close,
        session_id=[0] * n_per + [1] * n_per,
        session_date=[20240102] * n_per + [20240103] * n_per,
        minute=list(range(n_per)) + list(range(n_per)),
    )


def test_range_features_reset_at_session_boundary() -> None:
    matrix = build_feature_matrix(_two_session_bars(), load_yaml(RANGE_CONFIG), use_cache=False)
    col = matrix.column("pa_tr_high_30")
    assert np.isfinite(col[30])
    assert np.isnan(col[100:130]).all()
    assert np.isfinite(col[130])


def test_core_micro_channel_and_swing_features_reset_at_session_boundary() -> None:
    matrix = build_feature_matrix(_two_session_bars(), load_yaml(CORE_CONFIG), use_cache=False)
    assert np.isnan(matrix.column("bull_micro_channel_3")[100:102]).all()
    assert np.isfinite(matrix.column("bull_micro_channel_3")[102])
    assert np.isnan(matrix.column("pa_leg_direction")[100:105]).all()
    assert np.isfinite(matrix.column("pa_leg_direction")[105])
