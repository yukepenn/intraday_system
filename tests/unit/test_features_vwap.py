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


def test_vwap_slope_5_simple_sequence() -> None:
    """Slope = (vwap[t] - vwap[t-4]) / 4 on a rising VWAP path."""
    n = 8
    bm = make_bar_matrix(
        [10.0] * n,
        [11.0] * n,
        [9.0] * n,
        [10.0 + 0.1 * i for i in range(n)],
        volume=[100.0] * n,
        minute=list(range(n)),
    )
    out = compute_vwap_group(bm, {"outputs": ["vwap", "vwap_slope_5"], "price": "hlc3"})
    v = out["vwap"]
    s = out["vwap_slope_5"]
    assert np.isnan(s[:4]).all()
    i = 4
    expected = (v[i] - v[i - 4]) / 4.0
    assert np.isfinite(s[i])
    np.testing.assert_allclose(s[i], expected, rtol=1e-12, atol=1e-12)


def test_vwap_slope_5_nan_until_warmup() -> None:
    bm = make_bar_matrix(
        [10.0] * 6,
        [11.0] * 6,
        [9.0] * 6,
        [10.0] * 6,
        volume=[100.0] * 6,
        minute=list(range(6)),
    )
    out = compute_vwap_group(bm, {"outputs": ["vwap_slope_5"], "price": "hlc3"})
    assert np.isnan(out["vwap_slope_5"][:4]).all()


def test_vwap_slope_5_session_reset() -> None:
    bm = make_bar_matrix(
        [10.0] * 8,
        [11.0] * 8,
        [9.0] * 8,
        [10.0] * 8,
        volume=[100.0] * 8,
        session_id=[0] * 5 + [1] * 3,
        minute=[0, 1, 2, 3, 4, 0, 1, 2],
        session_date=[1] * 5 + [2] * 3,
    )
    out = compute_vwap_group(bm, {"outputs": ["vwap_slope_5"], "price": "hlc3"})
    s = out["vwap_slope_5"]
    # first bar of session 1 cannot use session 0 vwap
    assert np.isnan(s[5])


def test_vwap_slope_5_no_lookahead() -> None:
    n = 8
    bm = make_bar_matrix(
        [10.0] * n,
        [11.0] * n,
        [9.0] * n,
        [10.0] * n,
        volume=[100.0] * n,
        minute=list(range(n)),
    )
    cfg = {"outputs": ["vwap_slope_5"], "price": "hlc3"}
    a = compute_vwap_group(bm, cfg)["vwap_slope_5"][:5].copy()
    bm2 = make_bar_matrix(
        [10.0] * n,
        [11.0] * n,
        [9.0] * n,
        [10.0] * n,
        volume=[100.0] * n,
        minute=list(range(n)),
    )
    bm2.high[6:] = 99.0
    b = compute_vwap_group(bm2, cfg)["vwap_slope_5"][:5]
    np.testing.assert_allclose(a, b, rtol=0, atol=0, equal_nan=True)


def test_vwap_slope_5_nan_on_nonfinite_vwap() -> None:
    bm = make_bar_matrix(
        [10.0] * 6,
        [11.0] * 6,
        [9.0] * 6,
        [10.0] * 6,
        volume=[0.0, 0.0, 100.0, 100.0, 100.0, 100.0],
        minute=list(range(6)),
    )
    out = compute_vwap_group(bm, {"outputs": ["vwap_slope_5"], "price": "hlc3"})
    assert np.isnan(out["vwap_slope_5"][:4]).all()


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
