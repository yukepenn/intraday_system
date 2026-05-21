"""Phase19 polish: current-10 short-branch no-lookahead/session tests."""

from __future__ import annotations

import numpy as np
import pytest
from intraday.core.arrays import BarMatrix, FeatureMatrix
from intraday.strategies.registry import get_strategy, register_builtin_strategies

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns
from tests.unit.test_current10_short_signal_generation import (
    CURRENT10_CASES,
    Current10Case,
    case_ids,
)


def _signals_unchanged_up_to(a, b, k: int) -> None:
    for name in ("entry", "side", "stop", "target_r", "score", "setup_code"):
        x = getattr(a, name)[: k + 1]
        y = getattr(b, name)[: k + 1]
        if name == "entry":
            assert np.array_equal(x.astype(bool), y.astype(bool))
        elif name in ("side", "setup_code"):
            assert np.array_equal(x, y)
        else:
            assert np.allclose(x, y, equal_nan=True)


def _copy_bars_with_future_perturbation(bars: BarMatrix, k: int) -> BarMatrix:
    open_ = bars.open.copy()
    high = bars.high.copy()
    low = bars.low.copy()
    close = bars.close.copy()
    if k + 1 < bars.n_bars:
        open_[k + 1 :] += 7.0
        high[k + 1 :] += 9.0
        low[k + 1 :] -= 9.0
        close[k + 1 :] += 5.0
    return make_bar_matrix(
        open_.tolist(),
        high.tolist(),
        low.tolist(),
        close.tolist(),
        session_id=bars.session_id.tolist(),
        minute=bars.minute.tolist(),
        session_date=bars.session_date.tolist(),
        ts_ns=bars.ts_ns.copy(),
        data_hash=bars.data_hash,
    )


def _copy_features_with_future_perturbation(features: FeatureMatrix, k: int) -> FeatureMatrix:
    cols = {}
    for name, idx in features.columns.items():
        arr = features.values[:, idx].copy()
        if k + 1 < arr.shape[0]:
            arr[k + 1 :] = np.where(np.isfinite(arr[k + 1 :]), arr[k + 1 :] + 3.0, arr[k + 1 :])
        cols[name] = arr
    return make_feature_matrix_with_columns(
        features.n_bars, cols, feature_hash=features.feature_hash
    )


def _duplicate_two_sessions(
    bars: BarMatrix,
    features: FeatureMatrix,
) -> tuple[BarMatrix, FeatureMatrix]:
    n = bars.n_bars
    two_bars = make_bar_matrix(
        np.concatenate([bars.open, bars.open]).tolist(),
        np.concatenate([bars.high, bars.high]).tolist(),
        np.concatenate([bars.low, bars.low]).tolist(),
        np.concatenate([bars.close, bars.close]).tolist(),
        session_id=([0] * n) + ([1] * n),
        minute=np.concatenate([bars.minute, bars.minute]).astype(int).tolist(),
        session_date=([20240102] * n) + ([20240103] * n),
    )
    cols = {
        name: np.concatenate([features.values[:, idx], features.values[:, idx]])
        for name, idx in features.columns.items()
    }
    return two_bars, make_feature_matrix_with_columns(
        2 * n, cols, feature_hash=features.feature_hash
    )


@pytest.fixture(scope="module", autouse=True)
def _register() -> None:
    register_builtin_strategies()


@pytest.mark.parametrize("case", CURRENT10_CASES, ids=case_ids)
def test_current10_short_branch_future_perturbation_does_not_change_prior_signal(
    case: Current10Case,
) -> None:
    bars, feats = case.fixture_factory()
    cfg = case.config_factory(side_mode="short_only")
    base = get_strategy(case.strategy).generate_reference(bars, feats, cfg)
    first_entry = int(np.flatnonzero(base.entry)[0])
    k = min(first_entry, bars.n_bars - 2)

    changed = get_strategy(case.strategy).generate_reference(
        _copy_bars_with_future_perturbation(bars, k),
        _copy_features_with_future_perturbation(feats, k),
        cfg,
    )
    _signals_unchanged_up_to(base, changed, k)


@pytest.mark.parametrize("case", CURRENT10_CASES, ids=case_ids)
def test_current10_short_branch_session_boundary_does_not_leak_state(
    case: Current10Case,
) -> None:
    bars, feats = case.fixture_factory()
    two_bars, two_feats = _duplicate_two_sessions(bars, feats)
    cfg = case.config_factory(side_mode="short_only")
    signals = get_strategy(case.strategy).generate_reference(two_bars, two_feats, cfg)

    sess0 = two_bars.session_id == 0
    sess1 = two_bars.session_id == 1
    assert int(signals.entry[sess0].sum()) > 0
    assert int(signals.entry[sess1].sum()) > 0
    assert (signals.side[signals.entry] == -1).all()
    if not case.first_row_entry_expected:
        assert not bool(signals.entry[bars.n_bars]), f"{case.strategy} leaked prior session state"
