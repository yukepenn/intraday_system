"""VWAP trend pullback with side-aware short retrofit.

Long: close above VWAP, positive VWAP slope, pullback near VWAP.
Short: close below VWAP, negative VWAP slope, rally back near VWAP.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.core.errors import ConfigError
from intraday.strategies.base import StrategyDef
from intraday.strategies.common import (
    build_side_aware_signal_matrix,
    compute_long_stop,
    compute_short_stop,
    previous_same_session,
)
from intraday.strategies.config_validation import (
    CURRENT10_SIDE_MODES,
    parse_bool_like,
    validate_optional_finite_float,
    validate_optional_nonnegative_float,
    validate_optional_positive_float,
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

STRATEGY_NAME = "vwap_trend_pullback"
_SPEC = get_setup_codes(STRATEGY_NAME)
SETUP_CODE_LONG = _SPEC.long_code
SETUP_CODE_SHORT = _SPEC.short_code
SETUP_CODE = SETUP_CODE_LONG  # backward-compat alias
FEATURE_SET = "vwap_level_core_v1"
FEATURE_SETS = ("vwap_level_core_v1", "vwap_level_core_v2")

REQUIRED_COLUMNS: tuple[str, ...] = (
    "vwap",
    "vwap_dist",
    "vwap_dist_pct",
    "vwap_side",
    "vwap_slope_5",
    "atr_like_20",
    "range_mean_20",
    "close_position_in_range",
)


def validate_vwap_trend_pullback_config(config: Mapping[str, Any]) -> None:
    validate_side_aware_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="vwap",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "vwap_atr_buffer", "atr_buffer", "rolling_low_20"),
        allowed_side_modes=CURRENT10_SIDE_MODES,
    )
    sig = config.get("signal", {})
    validate_optional_finite_float(sig, "min_vwap_slope", "signal.min_vwap_slope")
    validate_optional_nonnegative_float(sig, "max_pullback_atr", "signal.max_pullback_atr")
    validate_optional_nonnegative_float(
        sig, "min_pullback_depth_atr", "signal.min_pullback_depth_atr"
    )
    validate_optional_nonnegative_float(sig, "max_under_vwap_atr", "signal.max_under_vwap_atr")
    validate_optional_nonnegative_float(
        sig, "max_close_vwap_dist_atr", "signal.max_close_vwap_dist_atr"
    )
    parse_bool_like(
        sig.get("require_reclaim_above_vwap", False), "signal.require_reclaim_above_vwap"
    )
    parse_bool_like(sig.get("require_reject_below_vwap", False), "signal.require_reject_below_vwap")
    validate_optional_positive_float(sig, "min_rel_volume_20", "signal.min_rel_volume_20")
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")
    if (
        "min_pullback_depth_atr" in sig
        and "max_pullback_atr" in sig
        and float(sig["min_pullback_depth_atr"]) > float(sig["max_pullback_atr"])
    ):
        raise ConfigError("signal.min_pullback_depth_atr must be <= max_pullback_atr")


_LONG_TO_SHORT_STOP: dict[str, str] = {
    "signal_low": "signal_high",
    "vwap_atr_buffer": "vwap_atr_buffer",
    "atr_buffer": "atr_buffer",
    "rolling_low_20": "rolling_high_20",
}


def generate_vwap_trend_pullback_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_vwap_trend_pullback_config(config)

    sig = config["signal"]
    risk = config["risk"]
    side_mode = normalize_side_mode(sig)
    short_enabled = side_mode != SIDE_MODE_LONG_ONLY
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    min_slope = float(sig.get("min_vwap_slope", 0.0))
    max_pb = float(sig.get("max_pullback_atr", 0.35))
    cp_min = float(sig.get("close_position_min", 0.55))
    require_reclaim = parse_bool_like(
        sig.get("require_reclaim_above_vwap", False), "signal.require_reclaim_above_vwap"
    )
    require_reject = parse_bool_like(
        sig.get("require_reject_below_vwap", False), "signal.require_reject_below_vwap"
    )
    extra_cols: list[str] = []
    if "min_rel_volume_20" in sig:
        extra_cols.append("rel_volume_20")
    long_stop_mode = str(risk.get("stop_mode", "signal_low"))
    if long_stop_mode == "rolling_low_20":
        extra_cols.append("rolling_low_20")
    if short_enabled:
        extra_cols.append("rolling_high_20")
    require_feature_columns(
        features.columns,
        (*REQUIRED_COLUMNS, *tuple(dict.fromkeys(extra_cols))),
        strategy_name=STRATEGY_NAME,
    )

    close = bars.close
    low = bars.low
    high = bars.high
    minute = bars.minute.astype(np.int32, copy=False)
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")
    close_pos = features.column("close_position_in_range")

    in_window = (minute >= es) & (minute <= ee)
    near_vwap_long = low <= (vwap + max_pb * atr)
    pullback_depth_long = (vwap - low) / atr
    long_cand = (
        in_window
        & (close > vwap)
        & (vwap_slope >= min_slope)
        & near_vwap_long
        & (close_pos >= cp_min)
        & np.isfinite(atr)
        & (atr > 0)
    )
    if "min_pullback_depth_atr" in sig:
        long_cand &= pullback_depth_long >= float(sig["min_pullback_depth_atr"])
    if "max_under_vwap_atr" in sig:
        long_cand &= ((vwap - close) / atr) <= float(sig["max_under_vwap_atr"])
    if "max_close_vwap_dist_atr" in sig:
        long_cand &= np.abs(close - vwap) / atr <= float(sig["max_close_vwap_dist_atr"])
    if require_reclaim:
        prev_close = previous_same_session(close, bars.session_id)
        prev_vwap = previous_same_session(vwap, bars.session_id)
        long_cand &= np.isfinite(prev_close) & np.isfinite(prev_vwap) & (prev_close <= prev_vwap)
    if "min_rel_volume_20" in sig:
        long_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])

    short_cand = np.zeros_like(long_cand, dtype=bool)
    if short_enabled:
        near_vwap_short = high >= (vwap - max_pb * atr)
        pullback_depth_short = (high - vwap) / atr
        short_cand = (
            in_window
            & (close < vwap)
            & (vwap_slope <= -min_slope)
            & near_vwap_short
            & ((1.0 - close_pos) >= cp_min)
            & np.isfinite(atr)
            & (atr > 0)
        )
        if "min_pullback_depth_atr" in sig:
            short_cand &= pullback_depth_short >= float(sig["min_pullback_depth_atr"])
        if "max_under_vwap_atr" in sig:
            # Symmetric: how far close has rallied above VWAP, capped by user.
            short_cand &= ((close - vwap) / atr) <= float(sig["max_under_vwap_atr"])
        if "max_close_vwap_dist_atr" in sig:
            short_cand &= np.abs(close - vwap) / atr <= float(sig["max_close_vwap_dist_atr"])
        if require_reject:
            prev_close = previous_same_session(close, bars.session_id)
            prev_vwap = previous_same_session(vwap, bars.session_id)
            short_cand &= (
                np.isfinite(prev_close) & np.isfinite(prev_vwap) & (prev_close >= prev_vwap)
            )
        if "min_rel_volume_20" in sig:
            short_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])

    long_stop = compute_long_stop(
        bars,
        features,
        long_stop_mode,
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        vwap=vwap,
    )
    long_score = clip_finite((close - vwap) / atr, -3.0, 3.0)
    if short_enabled:
        short_stop_mode = str(
            sig.get("short_stop_mode", _LONG_TO_SHORT_STOP.get(long_stop_mode, "signal_high"))
        )
        short_stop = compute_short_stop(
            bars,
            features,
            short_stop_mode,
            atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
            vwap=vwap,
        )
        short_score = clip_finite((vwap - close) / atr, -3.0, 3.0)
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


VWAP_TREND_PULLBACK_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="vwap",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_vwap_trend_pullback_signals,
    validate_config=validate_vwap_trend_pullback_config,
    setup_code_long=SETUP_CODE_LONG,
    setup_code_short=SETUP_CODE_SHORT,
    allowed_side_modes=CURRENT10_SIDE_MODES,
    default_side_mode=SIDE_MODE_LONG_ONLY,
    required_feature_columns=REQUIRED_COLUMNS,
)
