"""Price action kernel tests."""

from __future__ import annotations

import numpy as np
from intraday.features.kernels.price_action import compute_price_action_group

from tests.helpers.bars import make_bar_matrix


def test_zero_bar_range_nan_percentages() -> None:
    bm = make_bar_matrix(
        [10.0, 10.0],
        [10.0, 11.0],
        [10.0, 9.0],
        [10.0, 10.0],
        minute=[0, 1],
    )
    out = compute_price_action_group(
        bm,
        {
            "outputs": ["body_pct", "upper_wick_pct", "lower_wick_pct", "close_position_in_range"],
            "rolling_windows": [],
        },
    )
    assert np.isnan(out["body_pct"][0])
    assert np.isfinite(out["body_pct"][1])


def test_rolling_high_resets_session() -> None:
    bm = make_bar_matrix(
        [1.0] * 4,
        [5.0, 6.0, 2.0, 10.0],
        [0.5] * 4,
        [1.0] * 4,
        session_id=[0, 0, 1, 1],
        minute=[0, 1, 0, 1],
        session_date=[1, 1, 2, 2],
    )
    out = compute_price_action_group(
        bm,
        {"outputs": ["rolling_high"], "rolling_windows": [2]},
    )
    rh = out["rolling_high_2"]
    assert rh[2] == 2.0  # session 2 starts fresh


def test_price_action_no_lookahead() -> None:
    bm = make_bar_matrix(
        [1.0] * 5,
        [3.0, 3.0, 3.0, 3.0, 3.0],
        [0.5] * 5,
        [1.5] * 5,
        minute=list(range(5)),
    )
    cfg = {"outputs": ["rolling_high"], "rolling_windows": [3]}
    a = compute_price_action_group(bm, cfg)["rolling_high_3"][:2].copy()
    bm2 = make_bar_matrix(
        [1.0] * 5,
        [3.0, 3.0, 3.0, 99.0, 99.0],
        [0.5] * 5,
        [1.5] * 5,
        minute=list(range(5)),
    )
    b = compute_price_action_group(bm2, cfg)["rolling_high_3"][:2]
    np.testing.assert_allclose(a, b, rtol=0, atol=0, equal_nan=True)
