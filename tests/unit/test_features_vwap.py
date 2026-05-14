"""VWAP kernel tests."""

from __future__ import annotations

import numpy as np
from intraday.features.kernels.vwap import compute_vwap_group

from tests.helpers.bars import make_bar_matrix


def test_vwap_resets_by_session() -> None:
    bm = make_bar_matrix(
        [10.0, 10.0, 10.0, 10.0],
        [11.0, 11.0, 11.0, 11.0],
        [9.0, 9.0, 9.0, 9.0],
        [10.0, 10.0, 10.0, 10.0],
        volume=[100.0, 100.0, 100.0, 100.0],
        session_id=[0, 0, 1, 1],
        minute=[0, 1, 0, 1],
        session_date=[1, 1, 2, 2],
    )
    cfg = {"outputs": ["vwap"], "price": "hlc3"}
    out = compute_vwap_group(bm, cfg)
    v = out["vwap"]
    assert np.isfinite(v[1])
    # new session resets cumulative
    assert v[2] == v[0]


def test_vwap_zero_volume_nan() -> None:
    bm = make_bar_matrix(
        [10.0, 10.0],
        [11.0, 11.0],
        [9.0, 9.0],
        [10.0, 10.0],
        volume=[0.0, 0.0],
        minute=[0, 1],
    )
    out = compute_vwap_group(bm, {"outputs": ["vwap"], "price": "hlc3"})
    assert np.isnan(out["vwap"]).all()


def test_vwap_side() -> None:
    bm = make_bar_matrix(
        [10.0, 10.0],
        [12.0, 12.0],
        [8.0, 8.0],
        [11.0, 9.0],
        volume=[100.0, 100.0],
        minute=[0, 1],
    )
    out = compute_vwap_group(bm, {"outputs": ["vwap", "vwap_side"], "price": "hlc3"})
    assert out["vwap_side"][0] == 1.0
    assert out["vwap_side"][1] == -1.0


def test_vwap_no_lookahead() -> None:
    bm = make_bar_matrix(
        [10.0] * 5,
        [11.0] * 5,
        [9.0] * 5,
        [10.0] * 5,
        volume=[100.0] * 5,
        minute=list(range(5)),
    )
    cfg = {"outputs": ["vwap"], "price": "hlc3"}
    a = compute_vwap_group(bm, cfg)["vwap"][:3].copy()
    bm2 = make_bar_matrix(
        [10.0] * 5,
        [11.0, 11.0, 11.0, 50.0, 50.0],
        [9.0] * 5,
        [10.0] * 5,
        volume=[100.0] * 5,
        minute=list(range(5)),
    )
    b = compute_vwap_group(bm2, cfg)["vwap"][:3]
    np.testing.assert_allclose(a, b, rtol=0, atol=0, equal_nan=True)
