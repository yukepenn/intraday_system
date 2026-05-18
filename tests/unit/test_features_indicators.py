"""Indicators feature group tests."""

from __future__ import annotations

import numpy as np
from intraday.core.paths import repo_root
from intraday.features.engine import build_feature_matrix
from intraday.features.kernels.indicators import compute_indicators_group
from intraday.features.registry import clear_feature_registry
from intraday.features.specs import (
    collect_all_column_names,
    load_feature_config,
    resolve_feature_config,
)

from tests.helpers.bars import make_bar_matrix


def _ind_cfg() -> dict:
    return load_feature_config(repo_root() / "configs/features/indicator_core_v1.yaml")


def test_indicators_columns_resolve() -> None:
    resolved = resolve_feature_config(_ind_cfg())
    cols = collect_all_column_names(resolved)
    assert "cci_20" in cols
    assert "stoch_k_14" in cols
    assert "stoch_d_14_3" in cols


def test_cci_warmup_same_session() -> None:
    n = 25
    bm = make_bar_matrix(
        [100.0] * n,
        [101.0] * n,
        [99.0] * n,
        np.linspace(100, 110, n).tolist(),
        minute=list(range(n)),
    )
    out = compute_indicators_group(bm, {"outputs": ["cci"], "cci_windows": [20]})
    cci = out["cci_20"]
    assert np.isnan(cci[:18]).all()
    assert np.isfinite(cci[19])


def test_stochastic_session_reset() -> None:
    bm = make_bar_matrix(
        [1.0] * 4,
        [2.0, 3.0, 2.0, 5.0],
        [0.5] * 4,
        [1.0, 1.5, 1.0, 4.5],
        session_id=[0, 0, 1, 1],
        minute=[0, 1, 0, 1],
    )
    out = compute_indicators_group(
        bm,
        {
            "outputs": ["stoch_k", "stoch_d"],
            "stochastic_windows": [2],
            "stochastic_smooth_windows": [2],
        },
    )
    assert np.isfinite(out["stoch_k_2"][1])
    assert np.isfinite(out["stoch_k_2"][3])


def test_indicators_engine_no_inf() -> None:
    clear_feature_registry()
    bm = make_bar_matrix(
        [100.0] * 40,
        [101.0] * 40,
        [99.0] * 40,
        np.linspace(100, 105, 40).tolist(),
        session_id=[0] * 20 + [1] * 20,
        minute=list(range(20)) + list(range(20)),
        session_date=[20240102] * 20 + [20240103] * 20,
    )
    m = build_feature_matrix(bm, _ind_cfg(), store=None, use_cache=False)
    assert not np.isinf(m.values).any()
