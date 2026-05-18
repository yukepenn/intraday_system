"""Levels feature group tests."""

from __future__ import annotations

import numpy as np
import pytest
from intraday.core.paths import repo_root
from intraday.features.engine import build_feature_matrix
from intraday.features.kernels.levels import compute_levels_group
from intraday.features.registry import clear_feature_registry
from intraday.features.specs import (
    collect_all_column_names,
    load_feature_config,
    resolve_feature_config,
)

from tests.helpers.bars import make_bar_matrix


def _levels_cfg() -> dict:
    return load_feature_config(repo_root() / "configs/features/gap_level_core_v1.yaml")


def test_levels_columns_resolve() -> None:
    clear_feature_registry()
    resolved = resolve_feature_config(_levels_cfg())
    cols = collect_all_column_names(resolved)
    assert "prior_session_close" in cols
    assert "open_gap_pct" in cols
    assert len(cols) == len(set(cols))


def test_first_session_prior_nan() -> None:
    bm = make_bar_matrix(
        [10.0, 10.0],
        [11.0, 11.0],
        [9.0, 9.0],
        [10.0, 10.5],
        session_id=[0, 0],
        minute=[0, 1],
    )
    out = compute_levels_group(
        bm,
        {
            "outputs": [
                "prior_session_close",
                "prior_session_low",
                "open_gap_pct",
            ]
        },
    )
    assert np.isnan(out["prior_session_close"]).all()
    assert np.isnan(out["open_gap_pct"]).all()


def test_second_session_prior_ohlc() -> None:
    bm = make_bar_matrix(
        [10.0, 10.0, 20.0, 20.0],
        [12.0, 12.0, 22.0, 22.0],
        [8.0, 8.0, 18.0, 18.0],
        [11.0, 11.5, 21.0, 21.5],
        session_id=[0, 0, 1, 1],
        minute=[0, 1, 0, 1],
        session_date=[1, 1, 2, 2],
    )
    out = compute_levels_group(
        bm,
        {
            "outputs": [
                "prior_session_open",
                "prior_session_high",
                "prior_session_low",
                "prior_session_close",
            ]
        },
    )
    assert out["prior_session_close"][2] == 11.5
    assert out["prior_session_high"][2] == 12.0
    assert out["prior_session_low"][2] == 8.0
    assert out["prior_session_open"][2] == 10.0


def test_open_gap_pct_uses_session_open_and_prior_close() -> None:
    bm = make_bar_matrix(
        [10.0, 10.0, 30.0, 30.0],
        [11.0, 11.0, 31.0, 31.0],
        [9.0, 9.0, 29.0, 29.0],
        [10.0, 20.0, 30.0, 30.0],
        session_id=[0, 0, 1, 1],
        minute=[0, 1, 0, 1],
        session_date=[1, 1, 2, 2],
    )
    out = compute_levels_group(bm, {"outputs": ["open_gap_pct", "prior_session_close"]})
    assert out["open_gap_pct"][2] == pytest.approx((30.0 - 20.0) / 20.0)
    assert out["open_gap_pct"][3] == out["open_gap_pct"][2]


def test_no_future_leakage_in_levels() -> None:
    bm = make_bar_matrix(
        [10.0] * 6,
        [11.0] * 6,
        [9.0] * 6,
        [10.0, 10.5, 11.0, 11.5, 12.0, 12.5],
        session_id=[0, 0, 0, 1, 1, 1],
        minute=[0, 1, 2, 0, 1, 2],
        session_date=[1, 1, 1, 2, 2, 2],
    )
    out0 = compute_levels_group(bm, {"outputs": ["prior_session_close"]})
    close2 = bm.close.copy()
    close2[5] = 999.0
    bm2 = make_bar_matrix(
        bm.open.tolist(),
        bm.high.tolist(),
        bm.low.tolist(),
        close2.tolist(),
        session_id=bm.session_id.tolist(),
        minute=bm.minute.tolist(),
        session_date=bm.session_date.tolist(),
    )
    out1 = compute_levels_group(bm2, {"outputs": ["prior_session_close"]})
    assert np.allclose(
        out0["prior_session_close"][:4], out1["prior_session_close"][:4], equal_nan=True
    )


def test_levels_engine_no_inf() -> None:
    clear_feature_registry()
    raw = _levels_cfg()
    bm = make_bar_matrix(
        [100.0] * 8,
        [101.0] * 8,
        [99.0] * 8,
        [100.5] * 8,
        session_id=[0, 0, 0, 0, 1, 1, 1, 1],
        minute=list(range(4)) + list(range(4)),
        session_date=[20240102] * 4 + [20240103] * 4,
    )
    m = build_feature_matrix(bm, raw, store=None, use_cache=False)
    assert not np.isinf(m.values).any()
