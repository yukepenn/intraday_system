"""Gap-down acceptance failure / reclaim (long-only signal MVP)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.core.errors import ConfigError
from intraday.strategies.base import StrategyDef
from intraday.strategies.common import (
    build_signal_matrix,
    compute_long_stop,
    previous_same_session,
    prior_condition_within_bars,
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

STRATEGY_NAME = "gap_acceptance_failure"
SETUP_CODE = 3001
FEATURE_SET = "gap_level_core_v1"
FEATURE_SETS = ("gap_level_core_v1", "gap_level_core_v2")

REQUIRED_COLUMNS: tuple[str, ...] = (
    "prior_session_close",
    "prior_session_high",
    "prior_session_low",
    "open_gap_pct",
    "vwap",
    "vwap_slope_5",
    "atr_like_20",
)


def validate_gap_acceptance_failure_config(config: Mapping[str, Any]) -> None:
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="gap",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "rolling_low_20", "atr_buffer"),
    )
    sig = config.get("signal", {})
    mode = str(sig.get("reclaim_mode", "prior_close"))
    if mode not in ("prior_close", "vwap", "prior_low"):
        raise ConfigError("signal.reclaim_mode must be prior_close, vwap, or prior_low")
    validate_optional_positive_float(sig, "min_gap_pct", "signal.min_gap_pct")
    validate_optional_positive_float(sig, "max_gap_pct", "signal.max_gap_pct")
    if (
        "min_gap_pct" in sig
        and "max_gap_pct" in sig
        and float(sig["min_gap_pct"]) > float(sig["max_gap_pct"])
    ):
        raise ConfigError("signal.min_gap_pct must be <= max_gap_pct")
    validate_optional_nonnegative_float(sig, "reclaim_buffer_atr", "signal.reclaim_buffer_atr")
    validate_optional_positive_int(sig, "reclaim_lookback_bars", "signal.reclaim_lookback_bars")
    validate_optional_finite_float(sig, "min_vwap_slope", "signal.min_vwap_slope")
    parse_bool_like(sig.get("require_reclaim_cross", False), "signal.require_reclaim_cross")
    parse_bool_like(
        sig.get("require_gap_down_open_below_reclaim", False),
        "signal.require_gap_down_open_below_reclaim",
    )
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")
    parse_bool_like(sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap")


def generate_gap_acceptance_failure_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_gap_acceptance_failure_config(config)

    sig = config["signal"]
    risk = config["risk"]
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    min_gap = float(sig.get("min_gap_pct", 0.005))
    max_gap = float(sig.get("max_gap_pct", 1e18))
    reclaim_mode = str(sig.get("reclaim_mode", "prior_close"))
    req_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )
    min_slope = float(sig.get("min_vwap_slope", -1e18))
    require_reclaim_cross = parse_bool_like(
        sig.get("require_reclaim_cross", False), "signal.require_reclaim_cross"
    )
    require_open_below = parse_bool_like(
        sig.get("require_gap_down_open_below_reclaim", False),
        "signal.require_gap_down_open_below_reclaim",
    )
    extra_cols: list[str] = []
    if reclaim_mode == "prior_low":
        extra_cols.append("prior_session_low")
    if "close_position_min" in sig:
        extra_cols.append("close_position_in_range")
    require_feature_columns(
        features.columns,
        (*REQUIRED_COLUMNS, *tuple(dict.fromkeys(extra_cols))),
        strategy_name=STRATEGY_NAME,
    )

    open_ = bars.open
    close = bars.close
    minute = bars.minute.astype(np.int32, copy=False)
    gap_pct = features.column("open_gap_pct")
    prior_close = features.column("prior_session_close")
    prior_low = features.column("prior_session_low")
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")

    if reclaim_mode == "prior_close":
        reclaim = prior_close
    elif reclaim_mode == "prior_low":
        reclaim = prior_low
    else:
        reclaim = vwap
    reclaim_threshold = reclaim + float(sig.get("reclaim_buffer_atr", 0.0)) * atr
    in_window = (minute >= es) & (minute <= ee)
    gap_abs = -gap_pct
    gap_ok = np.isfinite(gap_pct) & (gap_abs >= min_gap) & (gap_abs <= max_gap)
    reclaim_ok = close > reclaim_threshold
    if require_reclaim_cross:
        prev_close = previous_same_session(close, bars.session_id)
        prev_reclaim = previous_same_session(reclaim_threshold, bars.session_id)
        reclaim_ok &= (
            np.isfinite(prev_close) & np.isfinite(prev_reclaim) & (prev_close <= prev_reclaim)
        )
    if "reclaim_lookback_bars" in sig:
        was_below = close <= reclaim_threshold
        reclaim_ok &= prior_condition_within_bars(
            was_below, bars.session_id, int(sig["reclaim_lookback_bars"])
        )
    cand = in_window & gap_ok & reclaim_ok & np.isfinite(atr) & (atr > 0)
    if require_open_below:
        cand &= open_ < reclaim
    if req_vwap:
        cand &= close > vwap
    if min_slope > -1e17:
        cand &= vwap_slope >= min_slope
    if "close_position_min" in sig:
        cand &= features.column("close_position_in_range") >= float(sig["close_position_min"])

    stop_arr = compute_long_stop(
        bars,
        features,
        str(risk.get("stop_mode", "signal_low")),
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
    )
    entry = cand & np.isfinite(stop_arr) & (stop_arr < close)
    entry = thin_first_n_per_session(entry, bars.session_id, int(risk.get("max_trades_per_day", 1)))

    score = clip_finite(-gap_pct, 0.0, 5.0)
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


GAP_ACCEPTANCE_FAILURE_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="gap",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_gap_acceptance_failure_signals,
    validate_config=validate_gap_acceptance_failure_config,
)
