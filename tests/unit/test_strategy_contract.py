"""SignalMatrix contract tests."""

from __future__ import annotations

import copy

import numpy as np
import pytest
from intraday.core.arrays import SignalMatrix
from intraday.core.errors import ConfigError
from intraday.strategies.contracts import (
    SIGNAL_CONTRACT_VERSION,
    compute_signal_hash,
    validate_signal_matrix,
)
from intraday.strategies.pa.buy_sell_close_trend import (
    generate_pa_buy_sell_close_trend_signals,
)

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns


def _pa_config() -> dict:
    return {
        "strategy": "pa_buy_sell_close_trend",
        "version": "strategy_v1",
        "signal_contract_version": SIGNAL_CONTRACT_VERSION,
        "signal": {
            "side": "long_only",
            "entry_start_minute": 0,
            "entry_end_minute": 389,
            "body_pct_min": 0.5,
            "close_position_min": 0.5,
            "trend_slope_min": 0.0,
            "close_vs_mean_min": 0.0,
            "require_vwap_side": False,
        },
        "risk": {"stop_mode": "signal_low", "target_mode": "fixed_r", "target_r": 1.2},
    }


def _passing_features(n: int = 3) -> dict[str, np.ndarray]:
    return {
        "body_pct": np.full(n, 0.8),
        "close_position_in_range": np.full(n, 0.9),
        "trend_slope_like_20": np.full(n, 1.0),
        "close_vs_rolling_mean_20": np.full(n, 0.5),
        "vwap_side": np.full(n, 1.0),
        "atr_like_20": np.full(n, 1.0),
        "rolling_low_20": np.full(n, 90.0),
        "bar_range": np.full(n, 2.0),
    }


def test_signal_matrix_shape_and_non_entry_convention() -> None:
    n = 4
    entry = np.array([False, True, False, False])
    sig = SignalMatrix(
        entry=entry,
        side=np.array([0, 1, 0, 0], dtype=np.int8),
        stop=np.array([np.nan, 99.0, np.nan, np.nan]),
        target_r=np.array([np.nan, 1.2, np.nan, np.nan]),
        score=np.array([np.nan, 1.5, np.nan, np.nan]),
        setup_code=np.array([0, 1001, 0, 0], dtype=np.int16),
        signal_hash="abc",
    )
    validate_signal_matrix(sig, n)


def test_non_entry_side_must_be_zero() -> None:
    sig = SignalMatrix(
        entry=np.array([True]),
        side=np.array([0], dtype=np.int8),
        stop=np.array([1.0]),
        target_r=np.array([1.0]),
        score=np.array([1.0]),
        setup_code=np.array([1], dtype=np.int16),
        signal_hash="x",
    )
    with pytest.raises(ValueError):
        validate_signal_matrix(sig, 1)


def test_missing_feature_column_raises() -> None:
    bars = make_bar_matrix([100.0], [101.0], [99.0], [100.5], minute=[120])
    feats = make_feature_matrix_with_columns(1, {"body_pct": np.array([0.9])})
    with pytest.raises(ConfigError, match="missing required feature"):
        generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config())


def test_signal_hash_stable() -> None:
    cfg = _pa_config()
    h1 = compute_signal_hash(
        strategy_name="pa_buy_sell_close_trend",
        strategy_version="strategy_v1",
        signal_contract_version=SIGNAL_CONTRACT_VERSION,
        config=cfg,
        feature_hash="feat_a",
    )
    h2 = compute_signal_hash(
        strategy_name="pa_buy_sell_close_trend",
        strategy_version="strategy_v1",
        signal_contract_version=SIGNAL_CONTRACT_VERSION,
        config=cfg,
        feature_hash="feat_a",
    )
    assert h1 == h2
    assert len(h1) == 64


def test_signal_hash_changes_on_config_or_feature_hash() -> None:
    cfg = _pa_config()
    base = compute_signal_hash(
        strategy_name="pa_buy_sell_close_trend",
        strategy_version="strategy_v1",
        signal_contract_version=SIGNAL_CONTRACT_VERSION,
        config=cfg,
        feature_hash="feat_a",
    )
    cfg2 = copy.deepcopy(cfg)
    cfg2["risk"]["target_r"] = 2.0
    changed_cfg = compute_signal_hash(
        strategy_name="pa_buy_sell_close_trend",
        strategy_version="strategy_v1",
        signal_contract_version=SIGNAL_CONTRACT_VERSION,
        config=cfg2,
        feature_hash="feat_a",
    )
    changed_feat = compute_signal_hash(
        strategy_name="pa_buy_sell_close_trend",
        strategy_version="strategy_v1",
        signal_contract_version=SIGNAL_CONTRACT_VERSION,
        config=cfg,
        feature_hash="feat_b",
    )
    assert base != changed_cfg
    assert base != changed_feat


def test_generated_signals_validate_and_no_execution_fields() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [101.0, 101.0, 101.0],
        [98.0, 98.0, 98.0],
        [100.5, 100.5, 100.5],
        minute=[120, 121, 122],
    )
    feats = make_feature_matrix_with_columns(3, _passing_features(3))
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config())
    validate_signal_matrix(sig, bars.n_bars)
    assert sig.n_bars == bars.n_bars
    assert not hasattr(sig, "pnl")
    assert len(sig.signal_hash) == 64
