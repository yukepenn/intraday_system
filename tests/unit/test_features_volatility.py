"""Volatility kernel tests."""

from __future__ import annotations

import numpy as np
from intraday.features.kernels.volatility import compute_volatility_group

from tests.helpers.bars import make_bar_matrix


def test_true_range_first_bar_session_uses_hl_only() -> None:
    bm = make_bar_matrix(
        [10.0, 10.0],
        [11.0, 12.0],
        [9.0, 8.0],
        [10.0, 9.0],
        session_id=[0, 1],
        minute=[0, 0],
        session_date=[1, 2],
    )
    out = compute_volatility_group(
        bm, {"outputs": ["true_range"], "atr_like_windows": [], "range_windows": []}
    )
    tr = out["true_range"]
    assert tr[0] == 2.0
    # second session first bar: no prev_close from prior session
    assert tr[1] == 4.0  # high-low


def test_true_range_uses_prev_close_same_session() -> None:
    bm = make_bar_matrix(
        [10.0, 10.0],
        [12.0, 12.0],
        [8.0, 7.0],
        [10.0, 9.0],
        minute=[0, 1],
    )
    out = compute_volatility_group(
        bm, {"outputs": ["true_range"], "atr_like_windows": [], "range_windows": []}
    )
    tr = out["true_range"]
    assert tr[1] == max(5.0, 2.0, 3.0)  # hl=5, |h-pc|=2, |l-pc|=3


def test_atr_resets_session() -> None:
    bm = make_bar_matrix(
        [1.0] * 6,
        [2.0, 3.0, 4.0, 2.0, 3.0, 4.0],
        [0.5] * 6,
        [1.5] * 6,
        session_id=[0, 0, 0, 1, 1, 1],
        minute=[0, 1, 2, 0, 1, 2],
        session_date=[1, 1, 1, 2, 2, 2],
    )
    out = compute_volatility_group(
        bm,
        {"outputs": ["true_range", "atr_like"], "atr_like_windows": [2], "range_windows": []},
    )
    atr = out["atr_like_2"]
    tr = out["true_range"]
    # First bar of session 1: rolling uses only current-session TR
    assert atr[3] == tr[3]


def test_volatility_no_lookahead() -> None:
    bm = make_bar_matrix(
        [1.0] * 5,
        [2.0, 3.0, 2.0, 2.0, 2.0],
        [0.5] * 5,
        [1.5] * 5,
        minute=list(range(5)),
    )
    cfg = {"outputs": ["atr_like", "true_range"], "atr_like_windows": [2], "range_windows": []}
    a = compute_volatility_group(bm, cfg)["atr_like_2"][:3].copy()
    bm2 = make_bar_matrix(
        [1.0] * 5,
        [2.0, 3.0, 2.0, 50.0, 50.0],
        [0.5] * 5,
        [1.5] * 5,
        minute=list(range(5)),
    )
    b = compute_volatility_group(bm2, cfg)["atr_like_2"][:3]
    np.testing.assert_allclose(a, b, rtol=0, atol=0, equal_nan=True)
