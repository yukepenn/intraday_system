"""Feature engine integration."""

from __future__ import annotations

import copy

import numpy as np
import pytest
from intraday.core.errors import ConfigError, IntradaySystemError
from intraday.core.paths import repo_root
from intraday.features.engine import build_feature_matrix
from intraday.features.registry import clear_feature_registry
from intraday.features.specs import (
    collect_all_column_names,
    load_feature_config,
    resolve_feature_config,
)

from tests.helpers.bars import make_bar_matrix


@pytest.fixture(autouse=True)
def _reset_registry() -> None:
    clear_feature_registry()
    yield
    clear_feature_registry()


def _pa_raw() -> dict:
    return load_feature_config(repo_root() / "configs/features/pa_core_v1.yaml")


def _orb_raw() -> dict:
    return load_feature_config(repo_root() / "configs/features/orb_core_v1.yaml")


def test_build_synthetic_dtype_and_shape() -> None:
    n = 40
    raw = _pa_raw()
    cols = collect_all_column_names(resolve_feature_config(raw))
    bm = make_bar_matrix(
        [100.0] * n,
        [101.0] * n,
        [99.0] * n,
        [100.5] * n,
        session_id=[0] * 20 + [1] * 20,
        minute=list(range(20)) + list(range(20)),
        volume=[1000.0] * n,
        session_date=[20240102] * 20 + [20240103] * 20,
    )
    m = build_feature_matrix(bm, raw, store=None, use_cache=False, mode="reference")
    assert m.values.shape == (n, len(cols))
    assert m.values.dtype == np.float64
    assert m.feature_hash == build_feature_matrix(bm, raw, store=None, use_cache=False).feature_hash


def test_row_count_matches_bars() -> None:
    raw = _pa_raw()
    bm = make_bar_matrix([1.0, 2.0], [2.0, 3.0], [0.5, 1.0], [1.5, 2.5], minute=[14, 15])
    m = build_feature_matrix(bm, raw, store=None, use_cache=False)
    assert m.n_bars == bm.n_bars


def test_mode_fast_raises() -> None:
    bm = make_bar_matrix([1.0], [2.0], [0.5], [1.5], minute=[20])
    with pytest.raises(IntradaySystemError, match="fast"):
        build_feature_matrix(bm, _pa_raw(), store=None, use_cache=False, mode="fast")  # type: ignore[arg-type]


def test_zero_rows_rejected() -> None:
    raw = _pa_raw()
    bm = make_bar_matrix([], [], [], [])
    with pytest.raises(ConfigError):
        build_feature_matrix(bm, raw, store=None, use_cache=False)


def test_unknown_group_in_raw_config_errors_at_resolve() -> None:
    raw = copy.deepcopy(_pa_raw())
    raw["features"]["not_real"] = {"enabled": True, "outputs": ["x"]}
    with pytest.raises(ConfigError):
        resolve_feature_config(raw)


def test_orb_core_v1_build_columns_and_hash() -> None:
    raw = _orb_raw()
    resolved = resolve_feature_config(raw)
    cols = collect_all_column_names(resolved)
    assert "vwap_slope_5" in cols
    assert "orb_width_pct_15" in cols
    assert "vwap" in cols
    n = 40
    bm = make_bar_matrix(
        [100.0] * n,
        [101.0] * n,
        [99.0] * n,
        [100.5] * n,
        session_id=[0] * 20 + [1] * 20,
        minute=list(range(20)) + list(range(20)),
        volume=[1000.0] * n,
        session_date=[20240102] * 20 + [20240103] * 20,
    )
    m1 = build_feature_matrix(bm, raw, store=None, use_cache=False)
    m2 = build_feature_matrix(bm, raw, store=None, use_cache=False)
    assert m1.values.shape == (n, len(cols))
    assert m1.feature_hash == m2.feature_hash
    pa = build_feature_matrix(bm, _pa_raw(), store=None, use_cache=False)
    assert m1.feature_hash != pa.feature_hash


def test_pa_core_v1_hash_unchanged_after_orb_foundation() -> None:
    """pa_core_v1 resolved hash must not change when only orb_core_v1 adds new outputs."""
    from intraday.features.specs import hash_feature_config

    pa_resolved = resolve_feature_config(_pa_raw())
    h1 = hash_feature_config(pa_resolved)
    h2 = hash_feature_config(pa_resolved)
    assert h1 == h2


def test_cache_hit_second_build(tmp_path) -> None:
    from intraday.features.store import FeatureStore

    raw = _pa_raw()
    n = 30
    bm = make_bar_matrix(
        [100.0] * n,
        [101.0] * n,
        [99.0] * n,
        [100.5] * n,
        minute=list(range(n)),
    )
    store = FeatureStore(root=tmp_path / "fcache")
    m1 = build_feature_matrix(bm, raw, store=store, use_cache=True)
    m2 = build_feature_matrix(bm, raw, store=store, use_cache=True)
    np.testing.assert_array_equal(m1.values, m2.values)
    assert m1.feature_hash == m2.feature_hash
