"""ORB kernel tests."""

from __future__ import annotations

import numpy as np
from intraday.features.kernels.orb import compute_orb_group

from tests.helpers.bars import make_bar_matrix


def test_orb_nan_before_complete() -> None:
    om = 5
    bm = make_bar_matrix(
        [10.0] * 5,
        [11.0] * 5,
        [9.0] * 5,
        [10.0] * 5,
        minute=[0, 1, 2, 3, 4],
    )
    out = compute_orb_group(
        bm,
        {"outputs": ["orb_high", "orb_low"], "open_minutes": [om]},
    )
    # minute < om-1 -> nan (indices 0..3 for minutes 0..3)
    assert np.isnan(out["orb_high_5"][: om - 1]).all()
    assert np.isfinite(out["orb_high_5"][om - 1])


def test_orb_constant_after_completion() -> None:
    om = 3
    highs = [10.0, 12.0, 11.0, 50.0, 60.0]
    bm = make_bar_matrix(
        [10.0] * 5,
        highs,
        [9.0] * 5,
        [10.0] * 5,
        minute=[0, 1, 2, 3, 4],
    )
    out = compute_orb_group(bm, {"outputs": ["orb_high"], "open_minutes": [om]})
    h = out["orb_high_3"]
    assert h[2] == 12.0
    assert h[3] == 12.0
    assert h[4] == 12.0


def test_orb_resets_next_session() -> None:
    om = 2
    bm = make_bar_matrix(
        [1.0] * 4,
        [2.0, 3.0, 2.0, 5.0],
        [0.5] * 4,
        [1.0] * 4,
        session_id=[0, 0, 1, 1],
        minute=[0, 1, 0, 1],
        session_date=[1, 1, 2, 2],
    )
    out = compute_orb_group(bm, {"outputs": ["orb_high"], "open_minutes": [om]})
    assert out["orb_high_2"][1] == 3.0
    assert out["orb_high_2"][3] == 5.0


def test_orb_no_lookahead() -> None:
    om = 3
    bm = make_bar_matrix(
        [1.0] * 5,
        [2.0, 3.0, 4.0, 2.0, 2.0],
        [0.5] * 5,
        [1.0] * 5,
        minute=[0, 1, 2, 3, 4],
    )
    cfg = {"outputs": ["orb_high"], "open_minutes": [om]}
    a = compute_orb_group(bm, cfg)["orb_high_3"][:3].copy()
    bm2 = make_bar_matrix(
        [1.0] * 5,
        [2.0, 3.0, 4.0, 99.0, 99.0],
        [0.5] * 5,
        [1.0] * 5,
        minute=[0, 1, 2, 3, 4],
    )
    b = compute_orb_group(bm2, cfg)["orb_high_3"][:3]
    np.testing.assert_allclose(a, b, rtol=0, atol=0, equal_nan=True)
