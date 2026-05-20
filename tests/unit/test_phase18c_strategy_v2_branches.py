"""Phase18C targeted branch behavior tests for current-10 v2 strategy options."""

from __future__ import annotations

import copy

import numpy as np
import pytest
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.strategies.loader import load_strategy_config
from intraday.strategies.registry import get_strategy, register_builtin_strategies

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns


def _cfg(strategy: str) -> dict:
    cfg = load_strategy_config(repo_root() / f"configs/strategies/base/phase18b/{strategy}_v2.yaml")
    cfg = copy.deepcopy(cfg)
    cfg["signal"]["entry_start_minute"] = 1
    cfg["signal"]["entry_end_minute"] = 5
    cfg["risk"]["max_trades_per_day"] = 10
    return cfg


def _bars(
    close: list[float] | None = None,
    *,
    low: list[float] | None = None,
    high: list[float] | None = None,
    open_: list[float] | None = None,
    session_id: list[int] | None = None,
    minute: list[int] | None = None,
):
    close = close or [100.0, 100.5, 101.0, 101.5, 102.0, 102.5]
    n = len(close)
    low = low or [x - 1.0 for x in close]
    high = high or [x + 1.0 for x in close]
    open_ = open_ or close
    minute = minute or list(range(n))
    return make_bar_matrix(
        open_,
        high,
        low,
        close,
        minute=minute,
        session_id=session_id or [0] * n,
        session_date=[20240102 if sid == 0 else 20240103 for sid in (session_id or [0] * n)],
    )


def _features(n: int, cols: dict[str, np.ndarray | float]):
    return make_feature_matrix_with_columns(n, cols, feature_hash="phase18c_features")


def _generate(strategy: str, cfg: dict, bars, cols: dict[str, np.ndarray | float]):
    register_builtin_strategies()
    return get_strategy(strategy).generate_reference(bars, _features(bars.n_bars, cols), cfg)


def _assert_has_entry(strategy: str, cfg: dict, bars, cols: dict[str, np.ndarray | float]) -> None:
    signals = _generate(strategy, cfg, bars, cols)
    assert signals.entry.any()


def _assert_no_entry(strategy: str, cfg: dict, bars, cols: dict[str, np.ndarray | float]) -> None:
    signals = _generate(strategy, cfg, bars, cols)
    assert not signals.entry.any()


def _pa_cols(n: int, **overrides):
    cols: dict[str, np.ndarray | float] = {
        "body_pct": 0.8,
        "close_position_in_range": 0.9,
        "trend_slope_like_20": 1.0,
        "close_vs_rolling_mean_20": 0.5,
        "vwap_side": 1.0,
        "atr_like_20": 1.0,
        "rolling_low_20": 95.0,
        "bar_range": 2.0,
        "vwap": 100.0,
        "vwap_dist_pct": 0.005,
        "rel_volume_20": 2.0,
        "rolling_high_20": np.full(n, 99.0),
        "range_mean_20": 1.0,
    }
    cols.update(overrides)
    return cols


def test_pa_v2_filters_and_stop_branches() -> None:
    bars = _bars(close=[101, 102, 103, 104, 105, 106], low=[100, 101, 102, 103, 104, 105])
    cfg = _cfg("pa_buy_sell_close_trend")
    cfg["signal"].update(
        {
            "require_close_above_vwap": True,
            "require_above_rolling_high_20": True,
            "max_vwap_dist_pct": 0.02,
            "min_rel_volume_20": 1.5,
            "min_range_mean_mult": 1.0,
            "max_range_mean_mult": 3.0,
        }
    )
    cols = _pa_cols(bars.n_bars)
    _assert_has_entry("pa_buy_sell_close_trend", cfg, bars, cols)
    _assert_no_entry("pa_buy_sell_close_trend", cfg, bars, _pa_cols(bars.n_bars, vwap=200.0))
    _assert_no_entry(
        "pa_buy_sell_close_trend", cfg, bars, _pa_cols(bars.n_bars, vwap_dist_pct=0.05)
    )
    _assert_no_entry("pa_buy_sell_close_trend", cfg, bars, _pa_cols(bars.n_bars, rel_volume_20=0.5))
    _assert_no_entry(
        "pa_buy_sell_close_trend", cfg, bars, _pa_cols(bars.n_bars, rolling_high_20=200.0)
    )
    _assert_no_entry("pa_buy_sell_close_trend", cfg, bars, _pa_cols(bars.n_bars, bar_range=0.2))
    _assert_no_entry("pa_buy_sell_close_trend", cfg, bars, _pa_cols(bars.n_bars, bar_range=5.0))

    cfg["risk"]["stop_mode"] = "vwap_atr_buffer"
    cfg["risk"]["atr_buffer_mult"] = 0.5
    signals = _generate("pa_buy_sell_close_trend", cfg, bars, cols)
    idx = int(np.flatnonzero(signals.entry)[0])
    assert signals.stop[idx] == pytest.approx(99.5)


def _orb_cols(n: int, **overrides):
    cols: dict[str, np.ndarray | float] = {
        "orb_high_3": 100.0,
        "orb_low_3": 98.0,
        "orb_mid_3": 99.0,
        "orb_range_3": 2.0,
        "orb_width_pct_3": 0.02,
        "vwap": 99.0,
        "vwap_slope_5": 0.05,
        "atr_like_20": 1.0,
        "close_position_in_range": 0.9,
        "rel_volume_20": 2.0,
        "vwap_dist_pct": 0.005,
    }
    cols.update(overrides)
    return cols


def test_orb_continuation_v2_filters() -> None:
    bars = _bars(close=[99, 99, 101, 101.5, 102, 102.5])
    cfg = _cfg("orb_continuation")
    cfg["signal"]["entry_end_minute"] = 3
    cfg["signal"].update(
        {
            "orb_open_minutes": 3,
            "breakout_buffer_atr": 0.2,
            "breakout_buffer_pct": 0.0,
            "close_position_min": 0.7,
            "min_rel_volume_20": 1.5,
            "max_vwap_dist_pct": 0.02,
            "min_vwap_slope": 0.01,
            "min_orb_width_pct": 0.01,
            "max_orb_width_pct": 0.05,
        }
    )
    cols = _orb_cols(bars.n_bars)
    _assert_has_entry("orb_continuation", cfg, bars, cols)
    cfg_pct = copy.deepcopy(cfg)
    cfg_pct["signal"]["breakout_buffer_pct"] = 0.02
    _assert_no_entry("orb_continuation", cfg_pct, bars, cols)
    cfg_atr = copy.deepcopy(cfg)
    cfg_atr["signal"]["breakout_buffer_atr"] = 2.0
    _assert_no_entry("orb_continuation", cfg_atr, bars, cols)
    _assert_no_entry("orb_continuation", cfg, bars, _orb_cols(bars.n_bars, vwap_slope_5=0.0))
    _assert_no_entry(
        "orb_continuation", cfg, bars, _orb_cols(bars.n_bars, close_position_in_range=0.2)
    )
    _assert_no_entry("orb_continuation", cfg, bars, _orb_cols(bars.n_bars, rel_volume_20=0.2))
    _assert_no_entry("orb_continuation", cfg, bars, _orb_cols(bars.n_bars, vwap_dist_pct=0.05))


def test_orb_retest_v2_stateful_branches() -> None:
    bars = _bars(close=[99, 99, 101.5, 99.8, 101.2, 101.4], low=[98, 98, 100.5, 101.0, 100, 100])
    cfg = _cfg("orb_retest_continuation")
    cfg["signal"]["entry_end_minute"] = 4
    cfg["signal"].update(
        {
            "orb_open_minutes": 3,
            "min_breakout_age_bars": 1,
            "max_breakout_age_bars": 2,
            "max_retest_depth_atr": 0.5,
            "retest_hold_level": "orb_high",
            "breakout_buffer_atr": 0.0,
            "close_position_min": 0.7,
            "min_rel_volume_20": 1.5,
        }
    )
    cols = _orb_cols(bars.n_bars)
    _assert_has_entry("orb_retest_continuation", cfg, bars, cols)
    too_early = copy.deepcopy(cfg)
    too_early["signal"]["min_breakout_age_bars"] = 3
    too_early["signal"]["max_breakout_age_bars"] = 4
    _assert_no_entry("orb_retest_continuation", too_early, bars, cols)
    stale = copy.deepcopy(cfg)
    stale["signal"]["max_breakout_age_bars"] = 1
    _assert_no_entry("orb_retest_continuation", stale, bars, cols)
    _assert_no_entry(
        "orb_retest_continuation", cfg, bars, _orb_cols(bars.n_bars, rel_volume_20=0.2)
    )
    mid = copy.deepcopy(cfg)
    mid["signal"]["retest_hold_level"] = "orb_mid"
    _assert_no_entry("orb_retest_continuation", mid, bars, cols)


def test_failed_orb_v2_stateful_branches() -> None:
    bars = _bars(close=[101, 101, 97.5, 98.0, 100.5, 101], low=[100, 100, 97, 97.5, 99, 100])
    cfg = _cfg("failed_orb")
    cfg["signal"].update(
        {
            "orb_open_minutes": 3,
            "reclaim_level": "orb_low",
            "min_breach_depth_atr": 0.2,
            "max_breach_depth_atr": 1.0,
            "max_bars_since_breach": 2,
            "reclaim_buffer_atr": 0.1,
            "close_position_min": 0.7,
            "min_rel_volume_20": 1.5,
        }
    )
    cols = _orb_cols(bars.n_bars)
    _assert_has_entry("failed_orb", cfg, bars, cols)
    too_deep = copy.deepcopy(cfg)
    too_deep["signal"]["max_breach_depth_atr"] = 0.3
    _assert_no_entry("failed_orb", too_deep, bars, cols)
    stale = copy.deepcopy(cfg)
    stale["signal"]["max_bars_since_breach"] = 1
    _assert_no_entry("failed_orb", stale, bars, cols)
    mid = copy.deepcopy(cfg)
    mid["signal"]["reclaim_level"] = "orb_mid"
    _assert_has_entry("failed_orb", mid, bars, cols)


def _gap_cols(n: int, **overrides):
    cols: dict[str, np.ndarray | float] = {
        "prior_session_close": 100.0,
        "prior_session_high": 102.0,
        "prior_session_low": 98.0,
        "open_gap_pct": -0.02,
        "vwap": 99.0,
        "vwap_slope_5": 0.05,
        "atr_like_20": 1.0,
        "rolling_low_20": 95.0,
        "close_position_in_range": 0.9,
    }
    cols.update(overrides)
    return cols


def test_gap_acceptance_v2_reclaim_branches() -> None:
    bars = _bars(close=[99, 99.5, 99.8, 100.5, 101, 101], open_=[97, 97, 97, 97, 97, 97])
    cfg = _cfg("gap_acceptance_failure")
    cfg["signal"].update(
        {
            "min_gap_pct": 0.01,
            "max_gap_pct": 0.05,
            "require_reclaim_cross": True,
            "reclaim_lookback_bars": 3,
            "reclaim_mode": "prior_close",
            "require_gap_down_open_below_reclaim": True,
            "close_position_min": 0.7,
            "min_vwap_slope": 0.01,
        }
    )
    cols = _gap_cols(bars.n_bars)
    _assert_has_entry("gap_acceptance_failure", cfg, bars, cols)
    _assert_no_entry(
        "gap_acceptance_failure", cfg, bars, _gap_cols(bars.n_bars, open_gap_pct=-0.20)
    )
    _assert_no_entry("gap_acceptance_failure", cfg, bars, _gap_cols(bars.n_bars, vwap_slope_5=0.0))
    prior_low = copy.deepcopy(cfg)
    prior_low["signal"]["reclaim_mode"] = "prior_low"
    prior_low["signal"]["require_reclaim_cross"] = False
    _assert_has_entry(
        "gap_acceptance_failure", prior_low, bars, _gap_cols(bars.n_bars, prior_session_low=99.8)
    )


def _vwap_cols(n: int, **overrides):
    cols: dict[str, np.ndarray | float] = {
        "vwap": 100.0,
        "vwap_dist": 0.5,
        "vwap_dist_pct": 0.005,
        "vwap_side": 1.0,
        "vwap_slope_5": 0.05,
        "atr_like_20": 1.0,
        "range_mean_20": 1.0,
        "close_position_in_range": 0.9,
        "rel_volume_20": 2.0,
        "rolling_low_20": 98.0,
    }
    cols.update(overrides)
    return cols


def test_vwap_trend_pullback_v2_filters() -> None:
    bars = _bars(close=[101, 101, 101, 101, 101, 101], low=[100.0, 99.8, 99.7, 99.8, 99.8, 99.8])
    cfg = _cfg("vwap_trend_pullback")
    cfg["signal"].update(
        {
            "min_vwap_slope": 0.01,
            "max_pullback_atr": 0.4,
            "min_pullback_depth_atr": 0.1,
            "max_under_vwap_atr": 0.2,
            "max_close_vwap_dist_atr": 2.0,
            "require_reclaim_above_vwap": False,
            "min_rel_volume_20": 1.5,
        }
    )
    cols = _vwap_cols(bars.n_bars)
    _assert_has_entry("vwap_trend_pullback", cfg, bars, cols)
    _assert_no_entry("vwap_trend_pullback", cfg, bars, _vwap_cols(bars.n_bars, vwap_slope_5=0.0))
    _assert_no_entry("vwap_trend_pullback", cfg, bars, _vwap_cols(bars.n_bars, rel_volume_20=0.2))
    far = _bars(close=[105] * 6, low=[100.0] * 6)
    _assert_no_entry("vwap_trend_pullback", cfg, far, cols)


def test_vwap_reclaim_v2_stateful_branches() -> None:
    bars = _bars(close=[99, 99.5, 99.8, 100.05, 100.5, 101], low=[98, 99, 99.5, 99.8, 99.8, 100])
    cfg = _cfg("vwap_reclaim_reject")
    cfg["signal"].update(
        {
            "below_lookback_bars": 3,
            "max_bars_since_below_vwap": 3,
            "require_vwap_touch": True,
            "reclaim_buffer_atr": 0.1,
            "min_vwap_slope": 0.01,
            "close_position_min": 0.7,
            "min_rel_volume_20": 1.5,
        }
    )
    cols = _vwap_cols(bars.n_bars)
    _assert_has_entry("vwap_reclaim_reject", cfg, bars, cols)
    stale = copy.deepcopy(cfg)
    stale["signal"]["max_bars_since_below_vwap"] = 1
    _assert_no_entry("vwap_reclaim_reject", stale, bars, cols)
    _assert_no_entry("vwap_reclaim_reject", cfg, bars, _vwap_cols(bars.n_bars, vwap_slope_5=0.0))


def _level_cols(n: int, **overrides):
    cols: dict[str, np.ndarray | float] = {
        "prior_session_low": 100.0,
        "prior_session_high": 102.0,
        "prior_session_close": 101.0,
        "atr_like_20": 1.0,
        "vwap": 100.5,
        "close_position_in_range": 0.9,
    }
    cols.update(overrides)
    return cols


def test_prior_day_level_trap_v2_stateful_branches() -> None:
    bars = _bars(
        close=[100, 100.5, 99.5, 100.0, 101.0, 101.5], low=[100, 100, 99.0, 100.2, 100.2, 101]
    )
    cfg = _cfg("prior_day_level_trap")
    cfg["signal"].update(
        {
            "level_type": "prior_low",
            "breach_lookback_bars": 3,
            "max_bars_since_breach": 3,
            "min_breach_buffer_atr": 0.5,
            "max_breach_buffer_atr": 2.0,
            "reclaim_buffer_atr": 0.2,
            "require_close_above_vwap": True,
            "close_position_min": 0.7,
        }
    )
    cols = _level_cols(bars.n_bars)
    _assert_has_entry("prior_day_level_trap", cfg, bars, cols)
    stale = copy.deepcopy(cfg)
    stale["signal"]["max_bars_since_breach"] = 1
    _assert_no_entry("prior_day_level_trap", stale, bars, cols)
    high_level = copy.deepcopy(cfg)
    high_level["signal"]["level_type"] = "prior_high"
    _assert_no_entry("prior_day_level_trap", high_level, bars, cols)


def _indicator_cols(n: int, **overrides):
    cols: dict[str, np.ndarray | float] = {
        "cci_20": np.array([-120, -115, -70, -65, -60, -55], dtype=np.float64)[:n],
        "stoch_k_14": np.array([25, 10, 25, 30, 35, 40], dtype=np.float64)[:n],
        "stoch_d_14_3": np.array([30, 20, 15, 20, 25, 30], dtype=np.float64)[:n],
        "atr_like_20": 1.0,
        "vwap": 100.0,
        "vwap_slope_5": 0.05,
        "close_position_in_range": 0.9,
        "vwap_dist_pct": 0.005,
        "rolling_low_20": 98.0,
    }
    cols.update(overrides)
    return cols


def test_cci_v2_filters() -> None:
    bars = _bars(close=[101] * 6)
    cfg = _cfg("cci_extreme_snapback")
    cfg["signal"].update(
        {
            "oversold_lookback_bars": 3,
            "min_cci_slope": 20.0,
            "require_close_above_vwap": True,
            "require_vwap_slope_positive": True,
            "close_position_min": 0.7,
            "max_vwap_dist_pct": 0.02,
        }
    )
    cols = _indicator_cols(bars.n_bars)
    _assert_has_entry("cci_extreme_snapback", cfg, bars, cols)
    _assert_no_entry(
        "cci_extreme_snapback", cfg, bars, _indicator_cols(bars.n_bars, vwap_slope_5=0.0)
    )
    _assert_no_entry(
        "cci_extreme_snapback", cfg, bars, _indicator_cols(bars.n_bars, vwap_dist_pct=0.05)
    )
    weak_slope = _indicator_cols(
        bars.n_bars, cci_20=np.array([-120, -115, -100, -95, -90, -85], dtype=np.float64)
    )
    _assert_no_entry("cci_extreme_snapback", cfg, bars, weak_slope)


def test_stochastic_v2_filters() -> None:
    bars = _bars(close=[101] * 6)
    cfg = _cfg("stochastic_oversold_cross")
    cfg["signal"].update(
        {
            "oversold_lookback_bars": 3,
            "min_k_d_spread_after_cross": 5.0,
            "min_k_slope": 10.0,
            "require_close_above_vwap": True,
            "require_vwap_slope_positive": True,
            "close_position_min": 0.7,
            "max_vwap_dist_pct": 0.02,
        }
    )
    cols = _indicator_cols(bars.n_bars)
    _assert_has_entry("stochastic_oversold_cross", cfg, bars, cols)
    _assert_no_entry(
        "stochastic_oversold_cross", cfg, bars, _indicator_cols(bars.n_bars, vwap_slope_5=0.0)
    )
    weak_k = _indicator_cols(
        bars.n_bars, stoch_k_14=np.array([25, 10, 15, 16, 17, 18], dtype=np.float64)
    )
    _assert_no_entry("stochastic_oversold_cross", cfg, bars, weak_k)


@pytest.mark.parametrize(
    ("strategy", "cfg_update", "missing_column", "cols"),
    (
        (
            "pa_buy_sell_close_trend",
            {"signal": {"min_rel_volume_20": 1.5}},
            "rel_volume_20",
            _pa_cols,
        ),
        ("pa_buy_sell_close_trend", {"risk": {"stop_mode": "vwap_atr_buffer"}}, "vwap", _pa_cols),
        ("orb_continuation", {"signal": {"orb_open_minutes": 3}}, "orb_high_3", _orb_cols),
        (
            "gap_acceptance_failure",
            {"signal": {"require_close_above_vwap": True}},
            "vwap",
            _gap_cols,
        ),
        (
            "vwap_trend_pullback",
            {"signal": {"min_rel_volume_20": 1.5}},
            "rel_volume_20",
            _vwap_cols,
        ),
        (
            "prior_day_level_trap",
            {"signal": {"require_close_above_vwap": True}},
            "vwap",
            _level_cols,
        ),
        (
            "cci_extreme_snapback",
            {"signal": {"require_vwap_slope_positive": True}},
            "vwap_slope_5",
            _indicator_cols,
        ),
        (
            "stochastic_oversold_cross",
            {"signal": {"require_vwap_slope_positive": True}},
            "vwap_slope_5",
            _indicator_cols,
        ),
    ),
)
def test_phase18c_missing_optional_feature_columns_fail_closed(
    strategy: str,
    cfg_update: dict,
    missing_column: str,
    cols,
) -> None:
    bars = _bars()
    cfg = _cfg(strategy)
    for section, updates in cfg_update.items():
        cfg[section].update(updates)
    feature_cols = cols(bars.n_bars)
    feature_cols.pop(missing_column, None)

    with pytest.raises((ConfigError, KeyError)):
        _generate(strategy, cfg, bars, feature_cols)


def _assert_entries_unchanged_up_to(a, b, idx: int) -> None:
    assert np.array_equal(a.entry[: idx + 1], b.entry[: idx + 1])
    assert np.array_equal(a.side[: idx + 1], b.side[: idx + 1])
    assert np.allclose(a.stop[: idx + 1], b.stop[: idx + 1], equal_nan=True)


def test_phase18c_vwap_reclaim_future_perturbation_does_not_change_current_signal() -> None:
    bars = _bars(close=[99, 99.5, 99.8, 100.05, 100.5, 101], low=[98, 99, 99.5, 99.8, 99.8, 100])
    cfg = _cfg("vwap_reclaim_reject")
    cfg["signal"].update(
        {
            "below_lookback_bars": 3,
            "max_bars_since_below_vwap": 3,
            "require_vwap_touch": True,
            "reclaim_buffer_atr": 0.1,
            "min_vwap_slope": 0.01,
        }
    )
    cols = _vwap_cols(bars.n_bars)
    base = _generate("vwap_reclaim_reject", cfg, bars, cols)
    perturbed_cols = _vwap_cols(bars.n_bars, vwap=np.array([100, 100, 100, 100, 100, 999.0]))
    perturbed = _generate("vwap_reclaim_reject", cfg, bars, perturbed_cols)
    _assert_entries_unchanged_up_to(base, perturbed, 4)


def test_phase18c_vwap_reclaim_current_bar_self_count_prevented_and_session_reset() -> None:
    cfg = _cfg("vwap_reclaim_reject")
    cfg["signal"].update({"below_lookback_bars": 3, "reclaim_buffer_atr": 0.1})
    current_only = _bars(close=[101], low=[99], minute=[3])
    _assert_no_entry("vwap_reclaim_reject", cfg, current_only, _vwap_cols(1))

    reset_bars = _bars(
        close=[99.0, 100.5],
        low=[98.0, 99.5],
        session_id=[0, 1],
        minute=[3, 3],
    )
    _assert_no_entry("vwap_reclaim_reject", cfg, reset_bars, _vwap_cols(reset_bars.n_bars))


def test_phase18c_oscillator_lookback_uses_prior_only_and_resets_session() -> None:
    cfg = _cfg("cci_extreme_snapback")
    cfg["signal"].update({"oversold_lookback_bars": 3, "min_cci_slope": 5.0})
    current_only = _bars(close=[101], minute=[3])
    current_cols = _indicator_cols(1, cci_20=np.array([-70.0]))
    _assert_no_entry("cci_extreme_snapback", cfg, current_only, current_cols)

    reset_bars = _bars(close=[101, 101], session_id=[0, 1], minute=[3, 3])
    reset_cols = _indicator_cols(2, cci_20=np.array([-120.0, -70.0]))
    _assert_no_entry("cci_extreme_snapback", cfg, reset_bars, reset_cols)
