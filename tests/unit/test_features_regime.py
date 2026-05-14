"""Regime kernel tests."""

from __future__ import annotations

import numpy as np
from intraday.features.kernels.regime import compute_regime_group

from tests.helpers.bars import make_bar_matrix


def test_trend_slope_nan_insufficient_session_history() -> None:
    bm = make_bar_matrix(
        [1.0] * 3,
        [2.0] * 3,
        [0.5] * 3,
        [1.0, 1.1, 1.2],
        minute=[0, 1, 2],
    )
    out = compute_regime_group(
        bm,
        {"outputs": ["trend_slope_like"], "windows": [5]},
    )
    assert np.isnan(out["trend_slope_like_5"]).all()


def test_regime_resets_across_sessions() -> None:
    bm = make_bar_matrix(
        [1.0] * 6,
        [2.0] * 6,
        [0.5] * 6,
        [1.0, 1.1, 1.2, 2.0, 2.1, 2.2],
        session_id=[0, 0, 0, 1, 1, 1],
        minute=[0, 1, 2, 0, 1, 2],
        session_date=[1, 1, 1, 2, 2, 2],
    )
    out = compute_regime_group(
        bm,
        {"outputs": ["trend_slope_like"], "windows": [2]},
    )
    ts = out["trend_slope_like_2"]
    assert np.isfinite(ts[2])
    assert np.isnan(ts[3])  # first bar new session: lag 2 unavailable


def test_regime_no_lookahead() -> None:
    bm = make_bar_matrix(
        [1.0] * 6,
        [2.0] * 6,
        [0.5] * 6,
        [1.0 + 0.1 * i for i in range(6)],
        minute=list(range(6)),
    )
    cfg = {"outputs": ["close_vs_rolling_mean"], "windows": [3]}
    a = compute_regime_group(bm, cfg)["close_vs_rolling_mean_3"][:3].copy()
    bm2 = make_bar_matrix(
        [1.0] * 6,
        [2.0] * 6,
        [0.5] * 6,
        [1.0 + 0.1 * i if i < 3 else 50.0 for i in range(6)],
        minute=list(range(6)),
    )
    b = compute_regime_group(bm2, cfg)["close_vs_rolling_mean_3"][:3]
    np.testing.assert_allclose(a, b, rtol=0, atol=0, equal_nan=True)
