"""VWAP trend pullback (long-only signal MVP)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.strategies.base import StrategyDef
from intraday.strategies.common import (
    build_signal_matrix,
    compute_long_stop,
    previous_same_session,
    thin_first_n_per_session,
)
from intraday.strategies.config_validation import (
    parse_bool_like,
    validate_long_only_strategy_base,
    validate_optional_nonnegative_float,
    validate_optional_positive_float,
    validate_optional_probability,
)
from intraday.strategies.contracts import (
    SIGNAL_CONTRACT_VERSION,
    clip_finite,
    require_feature_columns,
)

STRATEGY_NAME = "vwap_trend_pullback"
SETUP_CODE = 4001
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
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="vwap",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "vwap_atr_buffer", "atr_buffer", "rolling_low_20"),
    )
    sig = config.get("signal", {})
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
    validate_optional_positive_float(sig, "min_rel_volume_20", "signal.min_rel_volume_20")
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")


def generate_vwap_trend_pullback_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_vwap_trend_pullback_config(config)

    sig = config["signal"]
    risk = config["risk"]
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    min_slope = float(sig.get("min_vwap_slope", 0.0))
    max_pb = float(sig.get("max_pullback_atr", 0.35))
    cp_min = float(sig.get("close_position_min", 0.55))
    require_reclaim = parse_bool_like(
        sig.get("require_reclaim_above_vwap", False), "signal.require_reclaim_above_vwap"
    )
    extra_cols: list[str] = []
    if "min_rel_volume_20" in sig:
        extra_cols.append("rel_volume_20")
    if str(risk.get("stop_mode", "signal_low")) == "rolling_low_20":
        extra_cols.append("rolling_low_20")
    require_feature_columns(
        features.columns,
        (*REQUIRED_COLUMNS, *tuple(dict.fromkeys(extra_cols))),
        strategy_name=STRATEGY_NAME,
    )

    close = bars.close
    low = bars.low
    minute = bars.minute.astype(np.int32, copy=False)
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")
    close_pos = features.column("close_position_in_range")

    in_window = (minute >= es) & (minute <= ee)
    near_vwap = low <= (vwap + max_pb * atr)
    pullback_depth = (vwap - low) / atr
    cand = (
        in_window
        & (close > vwap)
        & (vwap_slope >= min_slope)
        & near_vwap
        & (close_pos >= cp_min)
        & np.isfinite(atr)
        & (atr > 0)
    )
    if "min_pullback_depth_atr" in sig:
        cand &= pullback_depth >= float(sig["min_pullback_depth_atr"])
    if "max_under_vwap_atr" in sig:
        cand &= ((vwap - close) / atr) <= float(sig["max_under_vwap_atr"])
    if "max_close_vwap_dist_atr" in sig:
        cand &= np.abs(close - vwap) / atr <= float(sig["max_close_vwap_dist_atr"])
    if require_reclaim:
        prev_close = previous_same_session(close, bars.session_id)
        prev_vwap = previous_same_session(vwap, bars.session_id)
        cand &= np.isfinite(prev_close) & np.isfinite(prev_vwap) & (prev_close <= prev_vwap)
    if "min_rel_volume_20" in sig:
        cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])

    stop_arr = compute_long_stop(
        bars,
        features,
        str(risk.get("stop_mode", "signal_low")),
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        vwap=vwap,
    )
    entry = cand & np.isfinite(stop_arr) & (stop_arr < close)
    entry = thin_first_n_per_session(entry, bars.session_id, int(risk.get("max_trades_per_day", 1)))

    score = clip_finite((close - vwap) / atr, -3.0, 3.0)
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


VWAP_TREND_PULLBACK_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="vwap",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_vwap_trend_pullback_signals,
    validate_config=validate_vwap_trend_pullback_config,
)
