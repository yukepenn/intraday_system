"""VWAP reclaim / reject with side-aware short retrofit.

Long (reclaim): prior below-VWAP state, current close above VWAP threshold.
Short (reject): prior above-VWAP state, current close below VWAP threshold.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.strategies.base import StrategyDef
from intraday.strategies.common import (
    bars_since_prior_condition,
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

STRATEGY_NAME = "vwap_reclaim_reject"
_SPEC = get_setup_codes(STRATEGY_NAME)
SETUP_CODE_LONG = _SPEC.long_code
SETUP_CODE_SHORT = _SPEC.short_code
SETUP_CODE = SETUP_CODE_LONG  # backward-compat alias
FEATURE_SET = "vwap_level_core_v1"
FEATURE_SETS = ("vwap_level_core_v1", "vwap_level_core_v2")

REQUIRED_COLUMNS: tuple[str, ...] = (
    "vwap",
    "vwap_side",
    "vwap_slope_5",
    "atr_like_20",
    "close_position_in_range",
)


def validate_vwap_reclaim_reject_config(config: Mapping[str, Any]) -> None:
    validate_side_aware_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="vwap",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "vwap_atr_buffer", "atr_buffer"),
        allowed_side_modes=CURRENT10_SIDE_MODES,
    )
    sig = config.get("signal", {})
    validate_optional_finite_float(sig, "min_vwap_slope", "signal.min_vwap_slope")
    validate_optional_positive_int(sig, "below_lookback_bars", "signal.below_lookback_bars")
    validate_optional_positive_int(sig, "above_lookback_bars", "signal.above_lookback_bars")
    validate_optional_nonnegative_float(sig, "reclaim_buffer_atr", "signal.reclaim_buffer_atr")
    validate_optional_positive_int(
        sig, "max_bars_since_below_vwap", "signal.max_bars_since_below_vwap"
    )
    validate_optional_positive_int(
        sig, "max_bars_since_above_vwap", "signal.max_bars_since_above_vwap"
    )
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")
    validate_optional_positive_float(sig, "min_rel_volume_20", "signal.min_rel_volume_20")
    parse_bool_like(sig.get("require_vwap_touch", False), "signal.require_vwap_touch")


_LONG_TO_SHORT_STOP: dict[str, str] = {
    "signal_low": "signal_high",
    "vwap_atr_buffer": "vwap_atr_buffer",
    "atr_buffer": "atr_buffer",
}


def generate_vwap_reclaim_reject_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_vwap_reclaim_reject_config(config)

    sig = config["signal"]
    risk = config["risk"]
    side_mode = normalize_side_mode(sig)
    short_enabled = side_mode != SIDE_MODE_LONG_ONLY
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    min_slope = float(sig.get("min_vwap_slope", -1e18))
    req_touch = parse_bool_like(sig.get("require_vwap_touch", False), "signal.require_vwap_touch")
    cp_min = float(sig.get("close_position_min", 0.0))
    reclaim_buf = float(sig.get("reclaim_buffer_atr", 0.0))
    extra_cols: list[str] = []
    if "min_rel_volume_20" in sig:
        extra_cols.append("rel_volume_20")
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

    prev_close = previous_same_session(close, bars.session_id)
    prev_vwap = previous_same_session(vwap, bars.session_id)
    long_reclaim_thr = vwap + reclaim_buf * atr
    below_vwap = close <= vwap
    below_age = bars_since_prior_condition(below_vwap, bars.session_id)
    if "below_lookback_bars" in sig:
        long_state = (below_age >= 1) & (below_age <= int(sig["below_lookback_bars"]))
    else:
        long_state = np.isfinite(prev_close) & np.isfinite(prev_vwap) & (prev_close <= prev_vwap)
    if "max_bars_since_below_vwap" in sig:
        long_state &= below_age <= int(sig["max_bars_since_below_vwap"])
    long_reclaim = long_state & (close > long_reclaim_thr)

    in_window = (minute >= es) & (minute <= ee)
    long_cand = in_window & long_reclaim & (close_pos >= cp_min) & np.isfinite(atr) & (atr > 0)
    if req_touch:
        long_cand &= low <= vwap
    if min_slope > -1e17:
        long_cand &= vwap_slope >= min_slope
    if "min_rel_volume_20" in sig:
        long_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])

    short_cand = np.zeros_like(long_cand, dtype=bool)
    short_reject_thr = vwap - reclaim_buf * atr
    if short_enabled:
        above_vwap = close >= vwap
        above_age = bars_since_prior_condition(above_vwap, bars.session_id)
        if "above_lookback_bars" in sig:
            short_state = (above_age >= 1) & (above_age <= int(sig["above_lookback_bars"]))
        else:
            short_state = (
                np.isfinite(prev_close) & np.isfinite(prev_vwap) & (prev_close >= prev_vwap)
            )
        if "max_bars_since_above_vwap" in sig:
            short_state &= above_age <= int(sig["max_bars_since_above_vwap"])
        short_reject = short_state & (close < short_reject_thr)
        short_cand = (
            in_window & short_reject & ((1.0 - close_pos) >= cp_min) & np.isfinite(atr) & (atr > 0)
        )
        if req_touch:
            short_cand &= high >= vwap
        if min_slope > -1e17:
            short_cand &= vwap_slope <= -min_slope
        if "min_rel_volume_20" in sig:
            short_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])

    long_stop_mode = str(risk.get("stop_mode", "signal_low"))
    long_stop = compute_long_stop(
        bars,
        features,
        long_stop_mode,
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        vwap=vwap,
    )
    long_score = clip_finite((close - long_reclaim_thr) / atr, -3.0, 3.0)
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
        short_score = clip_finite((short_reject_thr - close) / atr, -3.0, 3.0)
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


VWAP_RECLAIM_REJECT_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="vwap",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_vwap_reclaim_reject_signals,
    validate_config=validate_vwap_reclaim_reject_config,
    setup_code_long=SETUP_CODE_LONG,
    setup_code_short=SETUP_CODE_SHORT,
    allowed_side_modes=CURRENT10_SIDE_MODES,
    default_side_mode=SIDE_MODE_LONG_ONLY,
    required_feature_columns=REQUIRED_COLUMNS,
)
