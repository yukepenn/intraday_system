"""Phase19 polish: direct current-10 short-side signal generation tests."""

from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
import pytest
from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.strategies.contracts import SIGNAL_CONTRACT_VERSION
from intraday.strategies.pa.buy_sell_close_trend import (
    SETUP_CODE_LONG as PA_LONG,
)
from intraday.strategies.pa.buy_sell_close_trend import (
    generate_pa_buy_sell_close_trend_signals,
)
from intraday.strategies.registry import get_strategy, register_builtin_strategies
from intraday.strategies.setup_codes import SETUP_CODES

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns


@dataclass(frozen=True)
class Current10Case:
    strategy: str
    config_factory: Callable[..., dict[str, Any]]
    fixture_factory: Callable[..., tuple[BarMatrix, FeatureMatrix]]
    missing_column: str
    first_row_entry_expected: bool


def _with_signal_overrides(base: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    cfg = copy.deepcopy(base)
    cfg["signal"].update(overrides)
    return cfg


def _base_config(strategy: str, family: str, signal: dict[str, Any], risk: dict[str, Any]) -> dict:
    return {
        "strategy": strategy,
        "family": family,
        "version": "strategy_v1",
        "signal_contract_version": SIGNAL_CONTRACT_VERSION,
        "signal": signal,
        "risk": {
            "target_mode": "fixed_r",
            "target_r": 1.35,
            "atr_buffer_mult": 0.35,
            **risk,
        },
    }


def _pa_short_config(**overrides: Any) -> dict[str, Any]:
    sig: dict[str, Any] = {
        "side_mode": "short_only",
        "entry_start_minute": 60,
        "entry_end_minute": 300,
        "body_pct_min": 0.5,
        "close_position_min": 0.5,
        "trend_slope_min": 0.0,
        "close_vs_mean_min": 0.0,
        "require_vwap_side": False,
    }
    sig.update(overrides)
    return _base_config("pa_buy_sell_close_trend", "pa", sig, {"stop_mode": "signal_low"})


def _pa_short_fixture(
    n: int = 6, *, session_id: list[int] | None = None
) -> tuple[BarMatrix, FeatureMatrix]:
    bars = make_bar_matrix(
        [100.0] * n,
        [105.0] * n,  # bar high above close for short stop
        [100.0] * n,  # bar low at close (bearish bar)
        [100.0] * n,
        minute=[120] * n,
        session_id=session_id,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "body_pct": np.full(n, 0.8),
            "close_position_in_range": np.full(n, 0.1),  # 1 - cp = 0.9
            "trend_slope_like_20": np.full(n, -1.0),  # bearish
            "close_vs_rolling_mean_20": np.full(n, -0.5),  # below mean
            "vwap_side": np.full(n, -1.0),  # below VWAP
            "atr_like_20": np.full(n, 1.0),
            "rolling_low_20": np.full(n, 95.0),
            "rolling_high_20": np.full(n, 110.0),
            "bar_range": np.full(n, 5.0),
        },
        feature_hash="fh_short",
    )
    return bars, feats


def _orb_continuation_config(**overrides: Any) -> dict[str, Any]:
    sig = {
        "side_mode": "short_only",
        "entry_start_minute": 0,
        "entry_end_minute": 300,
        "orb_open_minutes": 15,
        "min_vwap_slope": 0.0,
        "min_orb_width_pct": 0.0,
        "max_orb_width_pct": 1.0,
        "require_close_above_vwap": False,
    }
    sig.update(overrides)
    return _base_config("orb_continuation", "orb", sig, {"stop_mode": "signal_low"})


def _orb_continuation_fixture(
    n: int = 6, *, session_id: list[int] | None = None
) -> tuple[BarMatrix, FeatureMatrix]:
    bars = make_bar_matrix(
        [91.0] * n,
        [95.0] * n,
        [89.0] * n,
        [90.0] * n,
        minute=[20] * n,
        session_id=session_id,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "orb_high_15": np.full(n, 110.0),
            "orb_low_15": np.full(n, 100.0),
            "orb_mid_15": np.full(n, 105.0),
            "orb_range_15": np.full(n, 10.0),
            "orb_width_pct_15": np.full(n, 0.01),
            "vwap": np.full(n, 95.0),
            "vwap_slope_5": np.full(n, -1.0),
            "atr_like_20": np.full(n, 1.0),
        },
        feature_hash="fh_orb_cont",
    )
    return bars, feats


def _orb_retest_config(**overrides: Any) -> dict[str, Any]:
    sig = {
        "side_mode": "short_only",
        "entry_start_minute": 0,
        "entry_end_minute": 300,
        "orb_open_minutes": 15,
        "retest_tolerance_atr": 0.5,
        "breakout_buffer_atr": 0.0,
        "require_close_above_vwap": False,
    }
    sig.update(overrides)
    return _base_config("orb_retest_continuation", "orb", sig, {"stop_mode": "signal_low"})


def _orb_retest_fixture(
    n: int = 6, *, session_id: list[int] | None = None
) -> tuple[BarMatrix, FeatureMatrix]:
    close = np.full(n, 101.0)
    high = np.full(n, 101.0)
    if n >= 3:
        close[1] = 98.0
        close[2] = 99.5
        high[2] = 100.1
    bars = make_bar_matrix(
        close.tolist(),
        high.tolist(),
        (close - 1.0).tolist(),
        close.tolist(),
        minute=[20] * n,
        session_id=session_id,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "orb_high_15": np.full(n, 110.0),
            "orb_low_15": np.full(n, 100.0),
            "orb_mid_15": np.full(n, 105.0),
            "orb_range_15": np.full(n, 10.0),
            "orb_width_pct_15": np.full(n, 0.01),
            "vwap": np.full(n, 101.0),
            "vwap_slope_5": np.full(n, -1.0),
            "atr_like_20": np.full(n, 1.0),
        },
        feature_hash="fh_orb_retest",
    )
    return bars, feats


def _failed_orb_config(**overrides: Any) -> dict[str, Any]:
    sig = {
        "side_mode": "short_only",
        "entry_start_minute": 0,
        "entry_end_minute": 300,
        "orb_open_minutes": 15,
        "reclaim_level": "orb_low",
        "require_close_above_vwap": False,
    }
    sig.update(overrides)
    return _base_config("failed_orb", "orb", sig, {"stop_mode": "signal_low"})


def _failed_orb_fixture(
    n: int = 6, *, session_id: list[int] | None = None
) -> tuple[BarMatrix, FeatureMatrix]:
    close = np.full(n, 109.0)
    high = np.full(n, 112.0)
    if n >= 3:
        close[1] = 111.0
        close[2] = 109.0
    bars = make_bar_matrix(
        close.tolist(),
        high.tolist(),
        (close - 2.0).tolist(),
        close.tolist(),
        minute=[20] * n,
        session_id=session_id,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "orb_low_15": np.full(n, 100.0),
            "orb_mid_15": np.full(n, 105.0),
            "orb_high_15": np.full(n, 110.0),
            "vwap": np.full(n, 108.0),
            "vwap_slope_5": np.full(n, -1.0),
            "atr_like_20": np.full(n, 1.0),
        },
        feature_hash="fh_failed_orb",
    )
    return bars, feats


def _gap_config(**overrides: Any) -> dict[str, Any]:
    sig = {
        "side_mode": "short_only",
        "entry_start_minute": 0,
        "entry_end_minute": 300,
        "min_gap_pct": 0.005,
        "max_gap_pct": 0.05,
        "short_reject_mode": "prior_close",
        "require_close_above_vwap": False,
    }
    sig.update(overrides)
    return _base_config("gap_acceptance_failure", "gap", sig, {"stop_mode": "signal_low"})


def _gap_fixture(
    n: int = 6, *, session_id: list[int] | None = None
) -> tuple[BarMatrix, FeatureMatrix]:
    bars = make_bar_matrix(
        [104.0] * n,
        [102.0] * n,
        [98.0] * n,
        [99.0] * n,
        minute=[20] * n,
        session_id=session_id,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "prior_session_close": np.full(n, 100.0),
            "prior_session_high": np.full(n, 103.0),
            "prior_session_low": np.full(n, 97.0),
            "open_gap_pct": np.full(n, 0.02),
            "vwap": np.full(n, 100.0),
            "vwap_slope_5": np.full(n, -1.0),
            "atr_like_20": np.full(n, 1.0),
            "rolling_high_20": np.full(n, 104.0),
        },
        feature_hash="fh_gap",
    )
    return bars, feats


def _vwap_trend_config(**overrides: Any) -> dict[str, Any]:
    sig = {
        "side_mode": "short_only",
        "entry_start_minute": 0,
        "entry_end_minute": 300,
        "min_vwap_slope": 0.0,
        "max_pullback_atr": 0.5,
        "close_position_min": 0.5,
    }
    sig.update(overrides)
    return _base_config("vwap_trend_pullback", "vwap", sig, {"stop_mode": "signal_low"})


def _vwap_trend_fixture(
    n: int = 6, *, session_id: list[int] | None = None
) -> tuple[BarMatrix, FeatureMatrix]:
    bars = make_bar_matrix(
        [99.5] * n,
        [100.2] * n,
        [98.5] * n,
        [99.0] * n,
        minute=[20] * n,
        session_id=session_id,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "vwap": np.full(n, 100.0),
            "vwap_dist": np.full(n, -1.0),
            "vwap_dist_pct": np.full(n, -0.01),
            "vwap_side": np.full(n, -1.0),
            "vwap_slope_5": np.full(n, -1.0),
            "atr_like_20": np.full(n, 1.0),
            "range_mean_20": np.full(n, 1.0),
            "close_position_in_range": np.full(n, 0.1),
            "rolling_high_20": np.full(n, 101.0),
        },
        feature_hash="fh_vwap_trend",
    )
    return bars, feats


def _vwap_reclaim_config(**overrides: Any) -> dict[str, Any]:
    sig = {
        "side_mode": "short_only",
        "entry_start_minute": 0,
        "entry_end_minute": 300,
        "close_position_min": 0.5,
    }
    sig.update(overrides)
    return _base_config("vwap_reclaim_reject", "vwap", sig, {"stop_mode": "signal_low"})


def _vwap_reclaim_fixture(
    n: int = 6, *, session_id: list[int] | None = None
) -> tuple[BarMatrix, FeatureMatrix]:
    close = np.full(n, 99.0)
    if n >= 2:
        close[0] = 101.0
        close[1] = 99.0
    bars = make_bar_matrix(
        close.tolist(),
        (close + 2.0).tolist(),
        (close - 1.0).tolist(),
        close.tolist(),
        minute=[20] * n,
        session_id=session_id,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "vwap": np.full(n, 100.0),
            "vwap_side": np.full(n, -1.0),
            "vwap_slope_5": np.full(n, -1.0),
            "atr_like_20": np.full(n, 1.0),
            "close_position_in_range": np.full(n, 0.1),
        },
        feature_hash="fh_vwap_reclaim",
    )
    return bars, feats


def _prior_day_config(**overrides: Any) -> dict[str, Any]:
    sig = {
        "side_mode": "short_only",
        "entry_start_minute": 0,
        "entry_end_minute": 300,
        "short_level_type": "prior_high",
        "breach_buffer_atr": 0.1,
    }
    sig.update(overrides)
    return _base_config("prior_day_level_trap", "levels", sig, {"stop_mode": "signal_low"})


def _prior_day_fixture(
    n: int = 6, *, session_id: list[int] | None = None
) -> tuple[BarMatrix, FeatureMatrix]:
    bars = make_bar_matrix(
        [100.0] * n,
        [101.0] * n,
        [98.0] * n,
        [99.0] * n,
        minute=[20] * n,
        session_id=session_id,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "prior_session_low": np.full(n, 95.0),
            "prior_session_high": np.full(n, 100.0),
            "prior_session_close": np.full(n, 98.0),
            "atr_like_20": np.full(n, 1.0),
        },
        feature_hash="fh_prior_day",
    )
    return bars, feats


def _cci_config(**overrides: Any) -> dict[str, Any]:
    sig = {
        "side_mode": "short_only",
        "entry_start_minute": 0,
        "entry_end_minute": 300,
        "overbought_threshold": 100.0,
        "cross_below_threshold": 80.0,
    }
    sig.update(overrides)
    return _base_config("cci_extreme_snapback", "cci", sig, {"stop_mode": "signal_low"})


def _cci_fixture(
    n: int = 6, *, session_id: list[int] | None = None
) -> tuple[BarMatrix, FeatureMatrix]:
    cci = np.full(n, 70.0)
    if n >= 2:
        cci[0] = 120.0
        cci[1] = 70.0
    bars = make_bar_matrix(
        [100.0] * n,
        [101.0] * n,
        [98.0] * n,
        [99.0] * n,
        minute=[20] * n,
        session_id=session_id,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "cci_20": cci,
            "atr_like_20": np.full(n, 1.0),
            "rolling_high_20": np.full(n, 102.0),
        },
        feature_hash="fh_cci",
    )
    return bars, feats


def _stoch_config(**overrides: Any) -> dict[str, Any]:
    sig = {
        "side_mode": "short_only",
        "entry_start_minute": 0,
        "entry_end_minute": 300,
        "overbought_threshold": 80.0,
    }
    sig.update(overrides)
    return _base_config("stochastic_oversold_cross", "stochastic", sig, {"stop_mode": "signal_low"})


def _stoch_fixture(
    n: int = 6, *, session_id: list[int] | None = None
) -> tuple[BarMatrix, FeatureMatrix]:
    k = np.full(n, 70.0)
    d = np.full(n, 75.0)
    if n >= 2:
        k[0] = 90.0
        d[0] = 80.0
        k[1] = 70.0
        d[1] = 75.0
    bars = make_bar_matrix(
        [100.0] * n,
        [101.0] * n,
        [98.0] * n,
        [99.0] * n,
        minute=[20] * n,
        session_id=session_id,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "stoch_k_14": k,
            "stoch_d_14_3": d,
            "atr_like_20": np.full(n, 1.0),
            "rolling_high_20": np.full(n, 102.0),
        },
        feature_hash="fh_stoch",
    )
    return bars, feats


CURRENT10_CASES: tuple[Current10Case, ...] = (
    Current10Case(
        "pa_buy_sell_close_trend", _pa_short_config, _pa_short_fixture, "rolling_high_20", True
    ),
    Current10Case(
        "orb_continuation", _orb_continuation_config, _orb_continuation_fixture, "orb_low_15", True
    ),
    Current10Case(
        "orb_retest_continuation", _orb_retest_config, _orb_retest_fixture, "orb_low_15", False
    ),
    Current10Case("failed_orb", _failed_orb_config, _failed_orb_fixture, "orb_high_15", False),
    Current10Case("gap_acceptance_failure", _gap_config, _gap_fixture, "prior_session_close", True),
    Current10Case("vwap_trend_pullback", _vwap_trend_config, _vwap_trend_fixture, "vwap", True),
    Current10Case(
        "vwap_reclaim_reject", _vwap_reclaim_config, _vwap_reclaim_fixture, "vwap", False
    ),
    Current10Case(
        "prior_day_level_trap", _prior_day_config, _prior_day_fixture, "prior_session_high", True
    ),
    Current10Case("cci_extreme_snapback", _cci_config, _cci_fixture, "cci_20", False),
    Current10Case("stochastic_oversold_cross", _stoch_config, _stoch_fixture, "stoch_k_14", False),
)


def case_ids(case: Current10Case) -> str:
    return case.strategy


@pytest.fixture(scope="module", autouse=True)
def _register() -> None:
    register_builtin_strategies()


def generate_case(
    case: Current10Case, side_mode: str
) -> tuple[BarMatrix, FeatureMatrix, dict[str, Any], SignalMatrix]:
    bars, feats = case.fixture_factory()
    cfg = case.config_factory(side_mode=side_mode)
    signals = get_strategy(case.strategy).generate_reference(bars, feats, cfg)
    return bars, feats, cfg, signals


def assert_non_entry_convention(signals: SignalMatrix) -> None:
    non_entry = ~signals.entry.astype(bool)
    if not non_entry.any():
        return
    assert (signals.side[non_entry] == 0).all()
    assert np.isnan(signals.stop[non_entry]).all()
    assert np.isnan(signals.target_r[non_entry]).all()
    assert np.isnan(signals.score[non_entry]).all()
    assert (signals.setup_code[non_entry] == 0).all()


@pytest.mark.parametrize("case", CURRENT10_CASES, ids=case_ids)
def test_short_only_emits_short_with_approved_setup_code(case: Current10Case) -> None:
    bars, _feats, _cfg, sig = generate_case(case, "short_only")
    assert sig.entry.any(), "expected short entries on bearish synthetic fixture"
    entries = sig.entry.astype(bool)
    assert (sig.side[entries] == -1).all()
    assert not (sig.side == 1).any()
    assert (sig.setup_code[entries] == SETUP_CODES[case.strategy].short_code).all()
    assert (sig.stop[entries] > bars.close[entries]).all()
    assert np.isfinite(sig.target_r[entries]).all()
    assert (sig.target_r[entries] > 0).all()
    assert np.isfinite(sig.score[entries]).all()
    assert_non_entry_convention(sig)


@pytest.mark.parametrize("case", CURRENT10_CASES, ids=case_ids)
def test_long_only_emits_no_short_on_bearish_fixture(case: Current10Case) -> None:
    _bars, _feats, _cfg, sig = generate_case(case, "long_only")
    assert not sig.entry.any() or (sig.side[sig.entry] == 1).all()
    assert not (sig.side == -1).any()


@pytest.mark.parametrize("case", CURRENT10_CASES, ids=case_ids)
def test_both_mode_does_not_suppress_valid_short_side(case: Current10Case) -> None:
    bars, _feats, _cfg, sig = generate_case(case, "both")
    short_entries = sig.entry.astype(bool) & (sig.side == -1)
    assert short_entries.any()
    assert (sig.stop[short_entries] > bars.close[short_entries]).all()


def test_both_mode_can_emit_long_on_bullish_fixture() -> None:
    # Use bullish fixture from baseline long-only tests.
    n = 4
    bars = make_bar_matrix(
        [100.0] * n,
        [100.0] * n,
        [95.0] * n,
        [100.0] * n,
        minute=[120] * n,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "body_pct": np.full(n, 0.8),
            "close_position_in_range": np.full(n, 0.9),
            "trend_slope_like_20": np.full(n, 1.0),
            "close_vs_rolling_mean_20": np.full(n, 0.5),
            "vwap_side": np.full(n, 1.0),
            "atr_like_20": np.full(n, 1.0),
            "rolling_low_20": np.full(n, 90.0),
            "rolling_high_20": np.full(n, 110.0),
            "bar_range": np.full(n, 5.0),
        },
        feature_hash="fh_bull",
    )
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_short_config(side_mode="both"))
    assert sig.entry.any()
    idx = int(np.flatnonzero(sig.entry)[0])
    assert sig.side[idx] == 1
    assert sig.setup_code[idx] == PA_LONG


def test_short_non_entry_convention() -> None:
    _bars, feats = _pa_short_fixture(n=4)
    # Entry window 60..300 but minute 30 is outside.
    bars = make_bar_matrix(
        [100.0] * 4, [105.0] * 4, [100.0] * 4, [100.0] * 4, minute=[30, 30, 30, 30]
    )
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_short_config())
    assert sig.side[0] == 0
    assert np.isnan(sig.stop[0])
    assert np.isnan(sig.target_r[0])
    assert np.isnan(sig.score[0])
    assert sig.setup_code[0] == 0
