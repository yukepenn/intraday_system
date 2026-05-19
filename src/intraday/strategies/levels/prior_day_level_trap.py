"""Prior-day low liquidity trap / reclaim (long-only signal MVP)."""

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
    validate_optional_nonnegative_float,
    validate_optional_positive_float,
    validate_optional_probability,
)
from intraday.strategies.contracts import (
    SIGNAL_CONTRACT_VERSION,
    clip_finite,
    require_feature_columns,
)

STRATEGY_NAME = "prior_day_level_trap"
SETUP_CODE = 5001
FEATURE_SET = "gap_level_core_v1"
FEATURE_SETS = ("gap_level_core_v1", "gap_level_core_v2")

REQUIRED_COLUMNS: tuple[str, ...] = (
    "prior_session_low",
    "prior_session_high",
    "prior_session_close",
    "atr_like_20",
)


def validate_prior_day_level_trap_config(config: Mapping[str, Any]) -> None:
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="levels",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "prior_low_buffer", "atr_buffer"),
    )
    sig = config.get("signal", {})
    level_type = str(sig.get("level_type", "prior_low"))
    if level_type not in ("prior_low", "prior_close", "prior_high"):
        raise ConfigError("signal.level_type must be prior_low, prior_close, or prior_high")
    validate_optional_nonnegative_float(sig, "breach_buffer_atr", "signal.breach_buffer_atr")
    validate_optional_positive_float(sig, "breach_lookback_bars", "signal.breach_lookback_bars")
    validate_optional_positive_float(sig, "max_bars_since_breach", "signal.max_bars_since_breach")
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


def generate_prior_day_level_trap_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_prior_day_level_trap_config(config)

    sig = config["signal"]
    risk = config["risk"]
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    breach_atr = float(sig.get("breach_buffer_atr", 0.15))
    req_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )
    level_type = str(sig.get("level_type", "prior_low"))
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
    minute = bars.minute.astype(np.int32, copy=False)
    prior_low = features.column("prior_session_low")
    prior_high = features.column("prior_session_high")
    prior_close = features.column("prior_session_close")
    atr = features.column("atr_like_20")
    vwap = features.column("vwap") if "vwap" in features.columns else None

    if level_type == "prior_high":
        level = prior_high
    elif level_type == "prior_close":
        level = prior_close
    else:
        level = prior_low
    min_breach = float(sig.get("min_breach_buffer_atr", breach_atr))
    max_breach = float(sig.get("max_breach_buffer_atr", 1e18))
    breach_depth = (level - low) / atr
    breach_now = (
        np.isfinite(breach_depth) & (breach_depth >= min_breach) & (breach_depth <= max_breach)
    )
    breach_age = bars_since_prior_condition(breach_now, bars.session_id)
    in_window = (minute >= es) & (minute <= ee)
    if "breach_lookback_bars" in sig or "max_bars_since_breach" in sig:
        breached = breach_age >= 1
        if "breach_lookback_bars" in sig:
            breached &= breach_age <= int(sig["breach_lookback_bars"])
        if "max_bars_since_breach" in sig:
            breached &= breach_age <= int(sig["max_bars_since_breach"])
    else:
        breached = low < (level - breach_atr * atr)
    reclaimed = close > (level + float(sig.get("reclaim_buffer_atr", 0.0)) * atr)
    cand = in_window & breached & reclaimed & np.isfinite(level) & np.isfinite(atr) & (atr > 0)
    if req_vwap and vwap is not None:
        cand &= close > vwap
    if "close_position_min" in sig:
        cand &= features.column("close_position_in_range") >= float(sig["close_position_min"])

    stop_arr = compute_long_stop(
        bars,
        features,
        str(risk.get("stop_mode", "signal_low")),
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        prior_low=prior_low,
        prior_low_buffer_atr=float(sig.get("prior_low_buffer_atr", 0.1)),
    )
    entry = cand & np.isfinite(stop_arr) & (stop_arr < close)
    entry = thin_first_n_per_session(entry, bars.session_id, int(risk.get("max_trades_per_day", 1)))

    score = clip_finite((close - level) / atr, -3.0, 3.0)
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


PRIOR_DAY_LEVEL_TRAP_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="levels",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_prior_day_level_trap_signals,
    validate_config=validate_prior_day_level_trap_config,
)
