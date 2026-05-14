"""Volume kernel tests."""

from __future__ import annotations

import numpy as np
from intraday.features.kernels.volume import compute_volume_group

from tests.helpers.bars import make_bar_matrix


def test_rel_volume_nan_when_mean_zero() -> None:
    bm = make_bar_matrix(
        [1.0] * 3,
        [2.0] * 3,
        [0.5] * 3,
        [1.0] * 3,
        volume=[0.0, 0.0, 0.0],
        minute=[0, 1, 2],
    )
    out = compute_volume_group(
        bm,
        {"outputs": ["volume_mean", "rel_volume"], "rolling_windows": [2]},
    )
    assert np.isnan(out["rel_volume_2"]).all()


def test_volume_no_lookahead() -> None:
    bm = make_bar_matrix(
        [1.0] * 5,
        [2.0] * 5,
        [0.5] * 5,
        [1.0] * 5,
        volume=[100.0] * 5,
        minute=list(range(5)),
    )
    cfg = {"outputs": ["volume_mean"], "rolling_windows": [3]}
    a = compute_volume_group(bm, cfg)["volume_mean_3"][:2].copy()
    bm2 = make_bar_matrix(
        [1.0] * 5,
        [2.0] * 5,
        [0.5] * 5,
        [1.0] * 5,
        volume=[100.0, 100.0, 100.0, 999.0, 999.0],
        minute=list(range(5)),
    )
    b = compute_volume_group(bm2, cfg)["volume_mean_3"][:2]
    np.testing.assert_allclose(a, b, rtol=0, atol=0, equal_nan=True)
