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


def test_orb_width_pct_after_complete() -> None:
    om = 3
    highs = [10.0, 12.0, 11.0, 50.0]
    lows = [9.0, 8.0, 9.5, 9.0]
    bm = make_bar_matrix(
        [10.0] * 4,
        highs,
        lows,
        [10.0] * 4,
        minute=[0, 1, 2, 3],
    )
    out = compute_orb_group(
        bm,
        {
            "outputs": ["orb_high", "orb_low", "orb_mid", "orb_range", "orb_width_pct"],
            "open_minutes": [om],
        },
    )
    w = out["orb_width_pct_3"]
    assert np.isnan(w[: om - 1]).all()
    i = om - 1
    hi, lo = out["orb_high_3"][i], out["orb_low_3"][i]
    mid = 0.5 * (hi + lo)
    expected = (hi - lo) / mid
    assert np.isfinite(w[i])
    np.testing.assert_allclose(w[i], expected, rtol=1e-12, atol=1e-12)


def test_orb_width_pct_nan_before_complete() -> None:
    om = 5
    bm = make_bar_matrix(
        [10.0] * 5,
        [11.0] * 5,
        [9.0] * 5,
        [10.0] * 5,
        minute=[0, 1, 2, 3, 4],
    )
    out = compute_orb_group(bm, {"outputs": ["orb_width_pct"], "open_minutes": [om]})
    assert np.isnan(out["orb_width_pct_5"][: om - 1]).all()


def test_orb_width_pct_zero_mid_nan() -> None:
    om = 2
    bm = make_bar_matrix(
        [0.0] * 3,
        [0.0] * 3,
        [0.0] * 3,
        [0.0] * 3,
        minute=[0, 1, 2],
    )
    out = compute_orb_group(bm, {"outputs": ["orb_width_pct"], "open_minutes": [om]})
    assert np.isnan(out["orb_width_pct_2"]).all()


def test_orb_width_pct_session_reset() -> None:
    om = 2
    bm = make_bar_matrix(
        [1.0] * 4,
        [3.0, 4.0, 2.0, 6.0],
        [1.0, 1.0, 1.0, 2.0],
        [2.0] * 4,
        session_id=[0, 0, 1, 1],
        minute=[0, 1, 0, 1],
        session_date=[1, 1, 2, 2],
    )
    out = compute_orb_group(bm, {"outputs": ["orb_width_pct"], "open_minutes": [om]})
    w = out["orb_width_pct_2"]
    assert np.isfinite(w[1])
    assert np.isfinite(w[3])
    assert w[1] != w[3]


def test_orb_width_pct_no_lookahead() -> None:
    om = 3
    bm = make_bar_matrix(
        [1.0] * 5,
        [2.0, 3.0, 4.0, 2.0, 2.0],
        [0.5, 0.5, 0.5, 0.5, 0.5],
        [1.0] * 5,
        minute=[0, 1, 2, 3, 4],
    )
    cfg = {"outputs": ["orb_width_pct"], "open_minutes": [om]}
    a = compute_orb_group(bm, cfg)["orb_width_pct_3"][:3].copy()
    bm2 = make_bar_matrix(
        [1.0] * 5,
        [2.0, 3.0, 4.0, 99.0, 99.0],
        [0.5] * 5,
        [1.0] * 5,
        minute=[0, 1, 2, 3, 4],
    )
    b = compute_orb_group(bm2, cfg)["orb_width_pct_3"][:3]
    np.testing.assert_allclose(a, b, rtol=0, atol=0, equal_nan=True)


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
