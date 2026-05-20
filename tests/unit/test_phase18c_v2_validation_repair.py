"""Phase18C v2 runtime-field validation repair tests."""

from __future__ import annotations

import copy

import numpy as np
import pytest
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.strategies.loader import load_strategy_config, validate_strategy_config


def _v2_config(strategy: str) -> dict:
    return load_strategy_config(
        repo_root() / f"configs/strategies/base/phase18b/{strategy}_v2.yaml"
    )


def _set_path(config: dict, dotted: str, value: object) -> dict:
    out = copy.deepcopy(config)
    cursor = out
    parts = dotted.split(".")
    for part in parts[:-1]:
        cursor = cursor[part]
    cursor[parts[-1]] = value
    return out


@pytest.mark.parametrize(
    ("strategy", "field", "bad_value"),
    (
        ("cci_extreme_snapback", "signal.min_cci_slope", np.nan),
        ("cci_extreme_snapback", "signal.min_cci_slope", "bad"),
        ("stochastic_oversold_cross", "signal.min_k_slope", np.inf),
        ("stochastic_oversold_cross", "signal.min_k_slope", "bad"),
        ("orb_continuation", "signal.min_vwap_slope", "bad"),
        ("orb_continuation", "signal.min_orb_width_pct", np.nan),
        ("orb_continuation", "signal.min_orb_width_pct", 0.10),
        ("vwap_reclaim_reject", "signal.below_lookback_bars", 1.5),
        ("vwap_reclaim_reject", "signal.max_bars_since_below_vwap", 0),
        ("gap_acceptance_failure", "signal.min_gap_pct", 0.10),
        ("gap_acceptance_failure", "signal.reclaim_mode", "not_a_mode"),
        ("prior_day_level_trap", "signal.min_breach_buffer_atr", 2.0),
        ("prior_day_level_trap", "signal.level_type", "not_a_level"),
        ("orb_retest_continuation", "signal.min_breakout_age_bars", 99),
        ("orb_retest_continuation", "signal.retest_hold_level", "not_a_level"),
        ("failed_orb", "signal.min_breach_depth_atr", 9.0),
        ("failed_orb", "signal.reclaim_level", "not_a_level"),
        ("pa_buy_sell_close_trend", "signal.max_vwap_dist_pct", np.nan),
        ("pa_buy_sell_close_trend", "signal.min_rel_volume_20", "bad"),
        ("pa_buy_sell_close_trend", "risk.stop_mode", "not_a_mode"),
        ("vwap_trend_pullback", "signal.min_pullback_depth_atr", 2.0),
        ("vwap_trend_pullback", "signal.max_close_vwap_dist_atr", np.inf),
        ("orb_retest_continuation", "signal.min_vwap_slope", np.nan),
        ("failed_orb", "signal.min_vwap_slope", np.inf),
        ("gap_acceptance_failure", "signal.min_vwap_slope", "bad"),
        ("vwap_trend_pullback", "signal.min_vwap_slope", "bad"),
        ("vwap_reclaim_reject", "signal.min_vwap_slope", np.nan),
    ),
)
def test_phase18c_invalid_v2_runtime_values_reject(
    strategy: str, field: str, bad_value: object
) -> None:
    cfg = _set_path(_v2_config(strategy), field, bad_value)
    if strategy == "orb_continuation" and field == "signal.min_orb_width_pct":
        cfg["signal"]["max_orb_width_pct"] = 0.01
    if strategy == "gap_acceptance_failure" and field == "signal.min_gap_pct":
        cfg["signal"]["max_gap_pct"] = 0.01
    if strategy == "prior_day_level_trap" and field == "signal.min_breach_buffer_atr":
        cfg["signal"]["max_breach_buffer_atr"] = 1.0
    if strategy == "orb_retest_continuation" and field == "signal.min_breakout_age_bars":
        cfg["signal"]["max_breakout_age_bars"] = 2
    if strategy == "failed_orb" and field == "signal.min_breach_depth_atr":
        cfg["signal"]["max_breach_depth_atr"] = 1.0
    if strategy == "vwap_trend_pullback" and field == "signal.min_pullback_depth_atr":
        cfg["signal"]["max_pullback_atr"] = 0.5

    with pytest.raises(ConfigError):
        validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize(
    ("strategy", "field"),
    (
        ("orb_retest_continuation", "signal.min_breakout_age_bars"),
        ("failed_orb", "signal.max_bars_since_breach"),
        ("gap_acceptance_failure", "signal.reclaim_lookback_bars"),
        ("vwap_reclaim_reject", "signal.below_lookback_bars"),
        ("prior_day_level_trap", "signal.breach_lookback_bars"),
        ("cci_extreme_snapback", "signal.oversold_lookback_bars"),
        ("stochastic_oversold_cross", "signal.oversold_lookback_bars"),
    ),
)
def test_phase18c_bar_count_fields_reject_fractional_values(strategy: str, field: str) -> None:
    with pytest.raises(ConfigError):
        validate_strategy_config(strategy, _set_path(_v2_config(strategy), field, 1.5))
