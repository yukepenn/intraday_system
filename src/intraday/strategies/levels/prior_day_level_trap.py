"""Prior-day level trap with side-aware short retrofit.

Long (default level_type=prior_low): breach below prior_low then reclaim.
Short (configurable via short_level_type): breach above prior_high then reject.
"""

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
    validate_optional_nonnegative_float,
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

STRATEGY_NAME = "prior_day_level_trap"
_SPEC = get_setup_codes(STRATEGY_NAME)
SETUP_CODE_LONG = _SPEC.long_code
SETUP_CODE_SHORT = _SPEC.short_code
SETUP_CODE = SETUP_CODE_LONG  # backward-compat alias
FEATURE_SET = "gap_level_core_v1"
FEATURE_SETS = ("gap_level_core_v1", "gap_level_core_v2")

REQUIRED_COLUMNS: tuple[str, ...] = (
    "prior_session_low",
    "prior_session_high",
    "prior_session_close",
    "atr_like_20",
)


def validate_prior_day_level_trap_config(config: Mapping[str, Any]) -> None:
    validate_side_aware_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="levels",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "prior_low_buffer", "atr_buffer"),
        allowed_side_modes=CURRENT10_SIDE_MODES,
    )
    sig = config.get("signal", {})
    level_type = str(sig.get("level_type", "prior_low"))
    if level_type not in ("prior_low", "prior_close", "prior_high"):
        raise ConfigError("signal.level_type must be prior_low, prior_close, or prior_high")
    short_level_type = str(sig.get("short_level_type", "prior_high"))
    if short_level_type not in ("prior_low", "prior_close", "prior_high"):
        raise ConfigError("signal.short_level_type must be prior_low, prior_close, or prior_high")
    validate_optional_nonnegative_float(sig, "breach_buffer_atr", "signal.breach_buffer_atr")
    validate_optional_positive_int(sig, "breach_lookback_bars", "signal.breach_lookback_bars")
    validate_optional_positive_int(sig, "max_bars_since_breach", "signal.max_bars_since_breach")
    validate_optional_nonnegative_float(
        sig, "min_breach_buffer_atr", "signal.min_breach_buffer_atr"
    )
    validate_optional_nonnegative_float(
        sig, "max_breach_buffer_atr", "signal.max_breach_buffer_atr"
    )
    if (
        "min_breach_buffer_atr" in sig
        and "max_breach_buffer_atr" in sig
        and float(sig["min_breach_buffer_atr"]) > float(sig["max_breach_buffer_atr"])
    ):
        raise ConfigError("signal.min_breach_buffer_atr must be <= max_breach_buffer_atr")
    validate_optional_nonnegative_float(sig, "reclaim_buffer_atr", "signal.reclaim_buffer_atr")
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")
    validate_optional_nonnegative_float(sig, "prior_low_buffer_atr", "signal.prior_low_buffer_atr")
    validate_optional_nonnegative_float(
        sig, "prior_high_buffer_atr", "signal.prior_high_buffer_atr"
    )
    parse_bool_like(sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap")


_LONG_TO_SHORT_STOP: dict[str, str] = {
    "signal_low": "signal_high",
    "prior_low_buffer": "prior_high_buffer",
    "atr_buffer": "atr_buffer",
}


def generate_prior_day_level_trap_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_prior_day_level_trap_config(config)

    sig = config["signal"]
    risk = config["risk"]
    side_mode = normalize_side_mode(sig)
    short_enabled = side_mode != SIDE_MODE_LONG_ONLY
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    breach_atr = float(sig.get("breach_buffer_atr", 0.15))
    req_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )
    level_type = str(sig.get("level_type", "prior_low"))
    short_level_type = str(sig.get("short_level_type", "prior_high"))
    extra_cols: list[str] = []
    if req_vwap:
        extra_cols.append("vwap")
    if "close_position_min" in sig:
        extra_cols.append("close_position_in_range")
    require_feature_columns(
        features.columns,
        (*REQUIRED_COLUMNS, *tuple(dict.fromkeys(extra_cols))),
        strategy_name=STRATEGY_NAME,
    )

    close = bars.close
    low = bars.low
    high = bars.high
    minute = bars.minute.astype(np.int32, copy=False)
    prior_low = features.column("prior_session_low")
    prior_high = features.column("prior_session_high")
    prior_close = features.column("prior_session_close")
    atr = features.column("atr_like_20")
    vwap = features.column("vwap") if "vwap" in features.columns else None

    if level_type == "prior_high":
        long_level = prior_high
    elif level_type == "prior_close":
        long_level = prior_close
    else:
        long_level = prior_low
    if short_level_type == "prior_low":
        short_level = prior_low
    elif short_level_type == "prior_close":
        short_level = prior_close
    else:
        short_level = prior_high

    min_breach = float(sig.get("min_breach_buffer_atr", breach_atr))
    max_breach = float(sig.get("max_breach_buffer_atr", 1e18))
    breach_depth_long = (long_level - low) / atr
    breach_now_long = (
        np.isfinite(breach_depth_long)
        & (breach_depth_long >= min_breach)
        & (breach_depth_long <= max_breach)
    )
    breach_age_long = bars_since_prior_condition(breach_now_long, bars.session_id)
    in_window = (minute >= es) & (minute <= ee)
    if "breach_lookback_bars" in sig or "max_bars_since_breach" in sig:
        breached_long = breach_age_long >= 1
        if "breach_lookback_bars" in sig:
            breached_long &= breach_age_long <= int(sig["breach_lookback_bars"])
        if "max_bars_since_breach" in sig:
            breached_long &= breach_age_long <= int(sig["max_bars_since_breach"])
    else:
        breached_long = low < (long_level - breach_atr * atr)
    reclaim_buf = float(sig.get("reclaim_buffer_atr", 0.0))
    reclaimed_long = close > (long_level + reclaim_buf * atr)
    long_cand = (
        in_window
        & breached_long
        & reclaimed_long
        & np.isfinite(long_level)
        & np.isfinite(atr)
        & (atr > 0)
    )
    if req_vwap and vwap is not None:
        long_cand &= close > vwap
    if "close_position_min" in sig:
        long_cand &= features.column("close_position_in_range") >= float(sig["close_position_min"])

    short_cand = np.zeros_like(long_cand, dtype=bool)
    if short_enabled:
        breach_depth_short = (high - short_level) / atr
        breach_now_short = (
            np.isfinite(breach_depth_short)
            & (breach_depth_short >= min_breach)
            & (breach_depth_short <= max_breach)
        )
        breach_age_short = bars_since_prior_condition(breach_now_short, bars.session_id)
        if "breach_lookback_bars" in sig or "max_bars_since_breach" in sig:
            breached_short = breach_age_short >= 1
            if "breach_lookback_bars" in sig:
                breached_short &= breach_age_short <= int(sig["breach_lookback_bars"])
            if "max_bars_since_breach" in sig:
                breached_short &= breach_age_short <= int(sig["max_bars_since_breach"])
        else:
            breached_short = high > (short_level + breach_atr * atr)
        rejected_short = close < (short_level - reclaim_buf * atr)
        short_cand = (
            in_window
            & breached_short
            & rejected_short
            & np.isfinite(short_level)
            & np.isfinite(atr)
            & (atr > 0)
        )
        if req_vwap and vwap is not None:
            short_cand &= close < vwap
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
        prior_low=prior_low,
        prior_low_buffer_atr=float(sig.get("prior_low_buffer_atr", 0.1)),
    )
    long_score = clip_finite((close - long_level) / atr, -3.0, 3.0)
    if short_enabled:
        short_stop_mode = str(
            sig.get("short_stop_mode", _LONG_TO_SHORT_STOP.get(long_stop_mode, "signal_high"))
        )
        short_stop = compute_short_stop(
            bars,
            features,
            short_stop_mode,
            atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
            prior_high=prior_high,
            prior_high_buffer_atr=float(sig.get("prior_high_buffer_atr", 0.1)),
        )
        short_score = clip_finite((short_level - close) / atr, -3.0, 3.0)
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


PRIOR_DAY_LEVEL_TRAP_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="levels",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_prior_day_level_trap_signals,
    validate_config=validate_prior_day_level_trap_config,
    setup_code_long=SETUP_CODE_LONG,
    setup_code_short=SETUP_CODE_SHORT,
    allowed_side_modes=CURRENT10_SIDE_MODES,
    default_side_mode=SIDE_MODE_LONG_ONLY,
    required_feature_columns=REQUIRED_COLUMNS,
)
