"""VWAP reclaim (long-only; no short reject in Phase 13)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.strategies.base import StrategyDef
from intraday.strategies.common import (
    bars_since_prior_condition,
    build_signal_matrix,
    compute_long_stop,
    previous_same_session,
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

STRATEGY_NAME = "vwap_reclaim_reject"
SETUP_CODE = 4002
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
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="vwap",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "vwap_atr_buffer", "atr_buffer"),
    )
    sig = config.get("signal", {})
    validate_optional_finite_float(sig, "min_vwap_slope", "signal.min_vwap_slope")
    validate_optional_positive_int(sig, "below_lookback_bars", "signal.below_lookback_bars")
    validate_optional_nonnegative_float(sig, "reclaim_buffer_atr", "signal.reclaim_buffer_atr")
    validate_optional_positive_int(
        sig, "max_bars_since_below_vwap", "signal.max_bars_since_below_vwap"
    )
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")
    validate_optional_positive_float(sig, "min_rel_volume_20", "signal.min_rel_volume_20")
    parse_bool_like(sig.get("require_vwap_touch", False), "signal.require_vwap_touch")


def generate_vwap_reclaim_reject_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_vwap_reclaim_reject_config(config)

    sig = config["signal"]
    risk = config["risk"]
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    min_slope = float(sig.get("min_vwap_slope", -1e18))
    req_touch = parse_bool_like(sig.get("require_vwap_touch", False), "signal.require_vwap_touch")
    cp_min = float(sig.get("close_position_min", 0.0))
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
    minute = bars.minute.astype(np.int32, copy=False)
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")
    close_pos = features.column("close_position_in_range")

    prev_close = previous_same_session(close, bars.session_id)
    prev_vwap = previous_same_session(vwap, bars.session_id)
    reclaim_threshold = vwap + float(sig.get("reclaim_buffer_atr", 0.0)) * atr
    below_vwap = close <= vwap
    below_age = bars_since_prior_condition(below_vwap, bars.session_id)
    if "below_lookback_bars" in sig:
        reclaim_state = (below_age >= 1) & (below_age <= int(sig["below_lookback_bars"]))
    else:
        reclaim_state = np.isfinite(prev_close) & np.isfinite(prev_vwap) & (prev_close <= prev_vwap)
    if "max_bars_since_below_vwap" in sig:
        reclaim_state &= below_age <= int(sig["max_bars_since_below_vwap"])
    reclaim = reclaim_state & (close > reclaim_threshold)

    in_window = (minute >= es) & (minute <= ee)
    cand = in_window & reclaim & (close_pos >= cp_min) & np.isfinite(atr) & (atr > 0)
    if req_touch:
        cand &= low <= vwap
    if min_slope > -1e17:
        cand &= vwap_slope >= min_slope
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

    score = clip_finite((close - reclaim_threshold) / atr, -3.0, 3.0)
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


VWAP_RECLAIM_REJECT_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="vwap",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_vwap_reclaim_reject_signals,
    validate_config=validate_vwap_reclaim_reject_config,
)
