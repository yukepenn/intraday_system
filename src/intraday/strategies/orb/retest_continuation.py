"""ORB breakout retest continuation (long-only signal MVP)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.core.errors import ConfigError
from intraday.strategies.base import StrategyDef
from intraday.strategies.common import (
    bars_since_prior_condition,
    build_signal_matrix,
    compute_long_stop,
    thin_first_n_per_session,
)
from intraday.strategies.config_validation import (
    parse_bool_like,
    validate_long_only_strategy_base,
    validate_optional_finite_float,
    validate_optional_nonnegative_float,
    validate_optional_positive_float,
    validate_optional_positive_int,
    validate_optional_probability,
)
from intraday.strategies.contracts import (
    SIGNAL_CONTRACT_VERSION,
    clip_finite,
    require_feature_columns,
)

STRATEGY_NAME = "orb_retest_continuation"
SETUP_CODE = 2002
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
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="orb",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("orb_mid", "orb_low", "signal_low", "atr_buffer"),
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


def generate_orb_retest_continuation_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_orb_retest_continuation_config(config)
    sig = config["signal"]
    risk = config["risk"]
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
    hold_level = orb_high if retest_hold_level == "orb_high" else orb_mid
    retest = low <= (hold_level + tol * atr)
    if "max_retest_depth_atr" in sig:
        retest_depth = (orb_high - low) / atr
        retest &= retest_depth <= float(sig["max_retest_depth_atr"])
    cand = (
        in_window
        & orb_ready
        & prior_break
        & retest
        & (close > orb_high)
        & np.isfinite(atr)
        & (atr > 0)
    )
    if req_vwap:
        cand &= close > vwap
    if min_slope > -1e17:
        cand &= vwap_slope >= min_slope
    if "close_position_min" in sig:
        cand &= features.column("close_position_in_range") >= float(sig["close_position_min"])
    if "min_rel_volume_20" in sig:
        cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])

    stop_arr = compute_long_stop(
        bars,
        features,
        str(risk.get("stop_mode", "signal_low")),
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        orb_low=orb_low,
        orb_mid=orb_mid,
    )
    entry = cand & np.isfinite(stop_arr) & (stop_arr < close)
    entry = thin_first_n_per_session(entry, bars.session_id, int(risk.get("max_trades_per_day", 1)))

    score = clip_finite((close - orb_high) / atr, -3.0, 3.0)
    return build_signal_matrix(
        bars=bars,
        entry=entry,
        stop=stop_arr,
        target_r_val=float(risk["target_r"]),
        setup_code_val=SETUP_CODE,
        score=score,
        strategy_name=STRATEGY_NAME,
        config=dict(config),
        feature_hash=features.feature_hash,
    )


ORB_RETEST_CONTINUATION_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="orb",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_orb_retest_continuation_signals,
    validate_config=validate_orb_retest_continuation_config,
)
