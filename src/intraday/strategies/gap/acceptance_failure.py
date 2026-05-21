"""Gap acceptance failure / reclaim with side-aware short retrofit.

Long (gap-down acceptance failure): gap-down open, reclaim above prior_close /
VWAP / prior_low.
Short (gap-up acceptance failure): gap-up open, rejection back below
prior_close / VWAP / prior_high.
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
    prior_condition_within_bars,
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

STRATEGY_NAME = "gap_acceptance_failure"
_SPEC = get_setup_codes(STRATEGY_NAME)
SETUP_CODE_LONG = _SPEC.long_code
SETUP_CODE_SHORT = _SPEC.short_code
SETUP_CODE = SETUP_CODE_LONG  # backward-compat alias
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
    validate_side_aware_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="gap",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "rolling_low_20", "atr_buffer"),
        allowed_side_modes=CURRENT10_SIDE_MODES,
    )
    sig = config.get("signal", {})
    mode = str(sig.get("reclaim_mode", "prior_close"))
    if mode not in ("prior_close", "vwap", "prior_low"):
        raise ConfigError("signal.reclaim_mode must be prior_close, vwap, or prior_low")
    short_mode = str(sig.get("short_reject_mode", "prior_close"))
    if short_mode not in ("prior_close", "vwap", "prior_high"):
        raise ConfigError("signal.short_reject_mode must be prior_close, vwap, or prior_high")
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
    parse_bool_like(
        sig.get("require_gap_up_open_above_reject", False),
        "signal.require_gap_up_open_above_reject",
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
    side_mode = normalize_side_mode(sig)
    short_enabled = side_mode != SIDE_MODE_LONG_ONLY
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    min_gap = float(sig.get("min_gap_pct", 0.005))
    max_gap = float(sig.get("max_gap_pct", 1e18))
    reclaim_mode = str(sig.get("reclaim_mode", "prior_close"))
    short_reject_mode = str(sig.get("short_reject_mode", "prior_close"))
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
    require_open_above = parse_bool_like(
        sig.get("require_gap_up_open_above_reject", False),
        "signal.require_gap_up_open_above_reject",
    )
    extra_cols: list[str] = []
    if reclaim_mode == "prior_low":
        extra_cols.append("prior_session_low")
    if short_enabled and short_reject_mode == "prior_high":
        extra_cols.append("prior_session_high")
    if "close_position_min" in sig:
        extra_cols.append("close_position_in_range")
    if short_enabled:
        extra_cols.append("rolling_high_20")
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
    prior_high = features.column("prior_session_high")
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")

    if reclaim_mode == "prior_close":
        long_reclaim = prior_close
    elif reclaim_mode == "prior_low":
        long_reclaim = prior_low
    else:
        long_reclaim = vwap
    reclaim_buf = float(sig.get("reclaim_buffer_atr", 0.0))
    long_reclaim_thr = long_reclaim + reclaim_buf * atr
    in_window = (minute >= es) & (minute <= ee)
    gap_abs_down = -gap_pct
    gap_down_ok = np.isfinite(gap_pct) & (gap_abs_down >= min_gap) & (gap_abs_down <= max_gap)
    long_reclaim_ok = close > long_reclaim_thr
    if require_reclaim_cross:
        prev_close = previous_same_session(close, bars.session_id)
        prev_long_thr = previous_same_session(long_reclaim_thr, bars.session_id)
        long_reclaim_ok &= (
            np.isfinite(prev_close) & np.isfinite(prev_long_thr) & (prev_close <= prev_long_thr)
        )
    if "reclaim_lookback_bars" in sig:
        was_below = close <= long_reclaim_thr
        long_reclaim_ok &= prior_condition_within_bars(
            was_below, bars.session_id, int(sig["reclaim_lookback_bars"])
        )
    long_cand = in_window & gap_down_ok & long_reclaim_ok & np.isfinite(atr) & (atr > 0)
    if require_open_below:
        long_cand &= open_ < long_reclaim
    if req_vwap:
        long_cand &= close > vwap
    if min_slope > -1e17:
        long_cand &= vwap_slope >= min_slope
    if "close_position_min" in sig:
        long_cand &= features.column("close_position_in_range") >= float(sig["close_position_min"])

    short_cand = np.zeros_like(long_cand, dtype=bool)
    short_reject_thr = np.full_like(close, np.nan, dtype=np.float64)
    if short_enabled:
        if short_reject_mode == "prior_close":
            short_reject = prior_close
        elif short_reject_mode == "prior_high":
            short_reject = prior_high
        else:
            short_reject = vwap
        short_reject_thr = short_reject - reclaim_buf * atr
        gap_up_ok = np.isfinite(gap_pct) & (gap_pct >= min_gap) & (gap_pct <= max_gap)
        short_reject_ok = close < short_reject_thr
        if require_reclaim_cross:
            prev_close = previous_same_session(close, bars.session_id)
            prev_short_thr = previous_same_session(short_reject_thr, bars.session_id)
            short_reject_ok &= (
                np.isfinite(prev_close)
                & np.isfinite(prev_short_thr)
                & (prev_close >= prev_short_thr)
            )
        if "reclaim_lookback_bars" in sig:
            was_above = close >= short_reject_thr
            short_reject_ok &= prior_condition_within_bars(
                was_above, bars.session_id, int(sig["reclaim_lookback_bars"])
            )
        short_cand = in_window & gap_up_ok & short_reject_ok & np.isfinite(atr) & (atr > 0)
        if require_open_above:
            short_cand &= open_ > short_reject
        if req_vwap:
            short_cand &= close < vwap
        if min_slope > -1e17:
            short_cand &= vwap_slope <= -min_slope
        if "close_position_min" in sig:
            short_cand &= (1.0 - features.column("close_position_in_range")) >= float(
                sig["close_position_min"]
            )

    long_stop_mode = str(risk.get("stop_mode", "signal_low"))
    long_stop = compute_long_stop(
        bars,
        features,
        long_stop_mode,
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
    )
    long_score = clip_finite(-gap_pct, 0.0, 5.0)
    if short_enabled:
        short_stop_mode = str(sig.get("short_stop_mode", _short_default_mode(long_stop_mode)))
        short_stop = compute_short_stop(
            bars,
            features,
            short_stop_mode,
            atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        )
        short_score = clip_finite(gap_pct, 0.0, 5.0)
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


def _short_default_mode(long_mode: str) -> str:
    if long_mode == "signal_low":
        return "signal_high"
    if long_mode == "rolling_low_20":
        return "rolling_high_20"
    if long_mode == "atr_buffer":
        return "atr_buffer"
    return "signal_high"


GAP_ACCEPTANCE_FAILURE_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="gap",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_gap_acceptance_failure_signals,
    validate_config=validate_gap_acceptance_failure_config,
    setup_code_long=SETUP_CODE_LONG,
    setup_code_short=SETUP_CODE_SHORT,
    allowed_side_modes=CURRENT10_SIDE_MODES,
    default_side_mode=SIDE_MODE_LONG_ONLY,
    required_feature_columns=REQUIRED_COLUMNS,
)
