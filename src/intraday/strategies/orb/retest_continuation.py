"""ORB breakout retest continuation with side-aware short retrofit."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.core.errors import ConfigError
from intraday.strategies.base import StrategyDef
from intraday.strategies.common import (
    bars_since_prior_condition,
    build_side_aware_signal_matrix,
    compute_long_stop,
    compute_short_stop,
)
from intraday.strategies.config_validation import (
    CURRENT10_SIDE_MODES,
    parse_bool_like,
    validate_optional_finite_float,
    validate_optional_nonnegative_float,
    validate_optional_positive_float,
    validate_optional_positive_int,
    validate_optional_probability,
    validate_side_aware_strategy_base,
)
from intraday.strategies.contracts import (
    SIDE_MODE_LONG_ONLY,
    SIGNAL_CONTRACT_VERSION,
    clip_finite,
    normalize_side_mode,
    require_feature_columns,
)
from intraday.strategies.setup_codes import get_setup_codes

STRATEGY_NAME = "orb_retest_continuation"
_SPEC = get_setup_codes(STRATEGY_NAME)
SETUP_CODE_LONG = _SPEC.long_code
SETUP_CODE_SHORT = _SPEC.short_code
SETUP_CODE = SETUP_CODE_LONG  # backward-compat alias
FEATURE_SET = "opening_core_v1"
FEATURE_SETS = ("opening_core_v1", "opening_core_v2")

REQUIRED_COLUMNS: tuple[str, ...] = (
    "orb_high_15",
    "orb_low_15",
    "orb_mid_15",
    "orb_range_15",
    "orb_width_pct_15",
    "vwap",
    "vwap_slope_5",
    "atr_like_20",
)


def validate_orb_retest_continuation_config(config: Mapping[str, Any]) -> None:
    validate_side_aware_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="orb",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("orb_mid", "orb_low", "signal_low", "atr_buffer"),
        allowed_side_modes=CURRENT10_SIDE_MODES,
    )
    sig = config.get("signal", {})
    if int(sig.get("orb_open_minutes", 15)) <= 0:
        raise ConfigError("signal.orb_open_minutes must be > 0")
    validate_optional_positive_int(sig, "orb_open_minutes", "signal.orb_open_minutes")
    validate_optional_finite_float(sig, "min_vwap_slope", "signal.min_vwap_slope")
    validate_optional_positive_float(sig, "retest_tolerance_atr", "signal.retest_tolerance_atr")
    validate_optional_positive_int(sig, "min_breakout_age_bars", "signal.min_breakout_age_bars")
    validate_optional_positive_int(sig, "max_breakout_age_bars", "signal.max_breakout_age_bars")
    if (
        "min_breakout_age_bars" in sig
        and "max_breakout_age_bars" in sig
        and int(sig["min_breakout_age_bars"]) > int(sig["max_breakout_age_bars"])
    ):
        raise ConfigError("signal.min_breakout_age_bars must be <= max_breakout_age_bars")
    validate_optional_nonnegative_float(sig, "max_retest_depth_atr", "signal.max_retest_depth_atr")
    validate_optional_nonnegative_float(sig, "breakout_buffer_atr", "signal.breakout_buffer_atr")
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")
    validate_optional_positive_float(sig, "min_rel_volume_20", "signal.min_rel_volume_20")
    hold_level = str(sig.get("retest_hold_level", "orb_high"))
    if hold_level not in ("orb_high", "orb_mid"):
        raise ConfigError("signal.retest_hold_level must be orb_high or orb_mid")


def _breakout_above(
    close: np.ndarray,
    orb_high: np.ndarray,
    atr: np.ndarray,
    minute: np.ndarray,
    om: int,
    breakout_buffer_atr: float,
) -> np.ndarray:
    return (
        (minute >= om - 1)
        & np.isfinite(close)
        & np.isfinite(orb_high)
        & np.isfinite(atr)
        & (atr > 0)
        & (close > orb_high + breakout_buffer_atr * atr)
    )


def _breakdown_below(
    close: np.ndarray,
    orb_low: np.ndarray,
    atr: np.ndarray,
    minute: np.ndarray,
    om: int,
    breakout_buffer_atr: float,
) -> np.ndarray:
    return (
        (minute >= om - 1)
        & np.isfinite(close)
        & np.isfinite(orb_low)
        & np.isfinite(atr)
        & (atr > 0)
        & (close < orb_low - breakout_buffer_atr * atr)
    )


def _prior_breakout_above(
    close: np.ndarray,
    orb_high: np.ndarray,
    minute: np.ndarray,
    session_id: np.ndarray,
    om: int,
) -> np.ndarray:
    """Backward-compatible Phase16B helper: prior close above ORB high only."""
    atr = np.ones_like(close, dtype=np.float64)
    breakout_now = _breakout_above(close, orb_high, atr, minute, om, 0.0)
    return bars_since_prior_condition(breakout_now, session_id) >= 1


_LONG_TO_SHORT_STOP: dict[str, str] = {
    "signal_low": "signal_high",
    "atr_buffer": "atr_buffer",
    "orb_low": "orb_high",
    "orb_mid": "orb_mid",
}


def generate_orb_retest_continuation_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_orb_retest_continuation_config(config)
    sig = config["signal"]
    risk = config["risk"]
    side_mode = normalize_side_mode(sig)
    short_enabled = side_mode != SIDE_MODE_LONG_ONLY
    om = int(sig.get("orb_open_minutes", 15))
    suf = f"_{om}"
    cols = tuple(c.replace("_15", suf) if "_15" in c else c for c in REQUIRED_COLUMNS)

    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    tol = float(sig.get("retest_tolerance_atr", 0.25))
    req_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )
    min_slope = float(sig.get("min_vwap_slope", -1e18))
    retest_hold_level = str(sig.get("retest_hold_level", "orb_high"))
    breakout_buffer_atr = float(sig.get("breakout_buffer_atr", 0.0))
    extra_cols: list[str] = []
    if "close_position_min" in sig:
        extra_cols.append("close_position_in_range")
    if "min_rel_volume_20" in sig:
        extra_cols.append("rel_volume_20")
    require_feature_columns(
        features.columns, (*cols, *tuple(dict.fromkeys(extra_cols))), strategy_name=STRATEGY_NAME
    )

    close = bars.close
    low = bars.low
    high = bars.high
    minute = bars.minute.astype(np.int32, copy=False)
    orb_high = features.column(f"orb_high{suf}")
    orb_low = features.column(f"orb_low{suf}")
    orb_mid = features.column(f"orb_mid{suf}")
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")

    breakout_now = _breakout_above(close, orb_high, atr, minute, om, breakout_buffer_atr)
    breakout_age = bars_since_prior_condition(breakout_now, bars.session_id)
    prior_break = breakout_age >= 1
    if "min_breakout_age_bars" in sig:
        prior_break &= breakout_age >= int(sig["min_breakout_age_bars"])
    if "max_breakout_age_bars" in sig:
        prior_break &= breakout_age <= int(sig["max_breakout_age_bars"])
    orb_ready = minute >= (om - 1)
    in_window = (minute >= es) & (minute <= ee)
    long_hold_level = orb_high if retest_hold_level == "orb_high" else orb_mid
    retest_long = low <= (long_hold_level + tol * atr)
    if "max_retest_depth_atr" in sig:
        retest_depth = (orb_high - low) / atr
        retest_long &= retest_depth <= float(sig["max_retest_depth_atr"])
    long_cand = (
        in_window
        & orb_ready
        & prior_break
        & retest_long
        & (close > orb_high)
        & np.isfinite(atr)
        & (atr > 0)
    )
    if req_vwap:
        long_cand &= close > vwap
    if min_slope > -1e17:
        long_cand &= vwap_slope >= min_slope
    if "close_position_min" in sig:
        long_cand &= features.column("close_position_in_range") >= float(sig["close_position_min"])
    if "min_rel_volume_20" in sig:
        long_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])

    short_cand = np.zeros_like(long_cand, dtype=bool)
    if short_enabled:
        breakdown_now = _breakdown_below(close, orb_low, atr, minute, om, breakout_buffer_atr)
        breakdown_age = bars_since_prior_condition(breakdown_now, bars.session_id)
        prior_bd = breakdown_age >= 1
        if "min_breakout_age_bars" in sig:
            prior_bd &= breakdown_age >= int(sig["min_breakout_age_bars"])
        if "max_breakout_age_bars" in sig:
            prior_bd &= breakdown_age <= int(sig["max_breakout_age_bars"])
        short_hold_level = orb_low if retest_hold_level == "orb_high" else orb_mid
        retest_short = high >= (short_hold_level - tol * atr)
        if "max_retest_depth_atr" in sig:
            retest_depth_short = (high - orb_low) / atr
            retest_short &= retest_depth_short <= float(sig["max_retest_depth_atr"])
        short_cand = (
            in_window
            & orb_ready
            & prior_bd
            & retest_short
            & (close < orb_low)
            & np.isfinite(atr)
            & (atr > 0)
        )
        if req_vwap:
            short_cand &= close < vwap
        if min_slope > -1e17:
            short_cand &= vwap_slope <= -min_slope
        if "close_position_min" in sig:
            short_cand &= (1.0 - features.column("close_position_in_range")) >= float(
                sig["close_position_min"]
            )
        if "min_rel_volume_20" in sig:
            short_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])

    long_stop_mode = str(risk.get("stop_mode", "signal_low"))
    long_stop = compute_long_stop(
        bars,
        features,
        long_stop_mode,
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        orb_low=orb_low,
        orb_mid=orb_mid,
    )
    long_score = clip_finite((close - orb_high) / atr, -3.0, 3.0)
    if short_enabled:
        short_stop_mode = str(
            sig.get("short_stop_mode", _LONG_TO_SHORT_STOP.get(long_stop_mode, "signal_high"))
        )
        short_stop = compute_short_stop(
            bars,
            features,
            short_stop_mode,
            atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
            orb_high=orb_high,
            orb_mid=orb_mid,
        )
        short_score = clip_finite((orb_low - close) / atr, -3.0, 3.0)
    else:
        short_stop = np.full(bars.n_bars, np.nan, dtype=np.float64)
        short_score = np.full(bars.n_bars, np.nan, dtype=np.float64)

    max_trades = int(risk.get("max_trades_per_day", 1))
    return build_side_aware_signal_matrix(
        bars=bars,
        features=features,
        config=dict(config),
        strategy_name=STRATEGY_NAME,
        long_entry=long_cand,
        short_entry=short_cand,
        long_stop=long_stop,
        short_stop=short_stop,
        long_score=long_score,
        short_score=short_score,
        target_r_val=float(risk["target_r"]),
        setup_code_long=SETUP_CODE_LONG,
        setup_code_short=SETUP_CODE_SHORT,
        side_mode=side_mode,
        max_trades_per_day=max_trades,
    )


ORB_RETEST_CONTINUATION_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="orb",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_orb_retest_continuation_signals,
    validate_config=validate_orb_retest_continuation_config,
    setup_code_long=SETUP_CODE_LONG,
    setup_code_short=SETUP_CODE_SHORT,
    allowed_side_modes=CURRENT10_SIDE_MODES,
    default_side_mode=SIDE_MODE_LONG_ONLY,
    required_feature_columns=REQUIRED_COLUMNS,
)
