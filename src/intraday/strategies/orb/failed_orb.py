"""Failed ORB downside trap / reclaim (long-only signal MVP)."""

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

STRATEGY_NAME = "failed_orb"
SETUP_CODE = 2003
FEATURE_SET = "opening_core_v1"
FEATURE_SETS = ("opening_core_v1", "opening_core_v2")

REQUIRED_COLUMNS: tuple[str, ...] = (
    "orb_low_15",
    "orb_mid_15",
    "orb_high_15",
    "vwap",
    "vwap_slope_5",
    "atr_like_20",
)


def validate_failed_orb_config(config: Mapping[str, Any]) -> None:
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="orb",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "orb_low", "atr_buffer"),
    )
    sig = config.get("signal", {})
    mode = str(sig.get("reclaim_level", "orb_low"))
    if mode not in ("orb_low", "orb_mid"):
        raise ConfigError("signal.reclaim_level must be orb_low or orb_mid")
    if int(sig.get("orb_open_minutes", 15)) <= 0:
        raise ConfigError("signal.orb_open_minutes must be > 0")
    validate_optional_nonnegative_float(sig, "min_breach_depth_atr", "signal.min_breach_depth_atr")
    validate_optional_nonnegative_float(sig, "max_breach_depth_atr", "signal.max_breach_depth_atr")
    if (
        "min_breach_depth_atr" in sig
        and "max_breach_depth_atr" in sig
        and float(sig["min_breach_depth_atr"]) > float(sig["max_breach_depth_atr"])
    ):
        raise ConfigError("signal.min_breach_depth_atr must be <= max_breach_depth_atr")
    validate_optional_positive_float(sig, "max_bars_since_breach", "signal.max_bars_since_breach")
    validate_optional_nonnegative_float(sig, "reclaim_buffer_atr", "signal.reclaim_buffer_atr")
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")
    validate_optional_positive_float(sig, "min_rel_volume_20", "signal.min_rel_volume_20")


def _breach_below(
    close: np.ndarray,
    orb_low: np.ndarray,
    atr: np.ndarray,
    minute: np.ndarray,
    om: int,
    min_depth_atr: float,
    max_depth_atr: float,
) -> np.ndarray:
    depth = (orb_low - close) / atr
    return (
        (minute >= om - 1)
        & np.isfinite(depth)
        & (depth >= min_depth_atr)
        & (depth <= max_depth_atr)
    )


def _prior_breach_below(
    close: np.ndarray,
    orb_low: np.ndarray,
    minute: np.ndarray,
    session_id: np.ndarray,
    om: int,
) -> np.ndarray:
    """Backward-compatible Phase16B helper: prior close below ORB low only."""
    atr = np.ones_like(close, dtype=np.float64)
    breach_now = _breach_below(close, orb_low, atr, minute, om, 0.0, 1e18)
    return bars_since_prior_condition(breach_now, session_id) >= 1


def generate_failed_orb_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_failed_orb_config(config)
    sig = config["signal"]
    risk = config["risk"]
    om = int(sig.get("orb_open_minutes", 15))
    suf = f"_{om}"
    cols = tuple(c.replace("_15", suf) if "_15" in c else c for c in REQUIRED_COLUMNS)

    reclaim_level = str(sig.get("reclaim_level", "orb_low"))
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    req_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )
    min_slope = float(sig.get("min_vwap_slope", -1e18))
    extra_cols: list[str] = []
    if "close_position_min" in sig:
        extra_cols.append("close_position_in_range")
    if "min_rel_volume_20" in sig:
        extra_cols.append("rel_volume_20")
    require_feature_columns(
        features.columns, (*cols, *tuple(dict.fromkeys(extra_cols))), strategy_name=STRATEGY_NAME
    )

    close = bars.close
    minute = bars.minute.astype(np.int32, copy=False)
    orb_low = features.column(f"orb_low{suf}")
    orb_mid = features.column(f"orb_mid{suf}")
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")

    reclaim = orb_low if reclaim_level == "orb_low" else orb_mid
    breach_now = _breach_below(
        close,
        orb_low,
        atr,
        minute,
        om,
        float(sig.get("min_breach_depth_atr", 0.0)),
        float(sig.get("max_breach_depth_atr", 1e18)),
    )
    breach_age = bars_since_prior_condition(breach_now, bars.session_id)
    prior_breach = breach_age >= 1
    if "max_bars_since_breach" in sig:
        prior_breach &= breach_age <= int(sig["max_bars_since_breach"])
    orb_ready = minute >= (om - 1)
    in_window = (minute >= es) & (minute <= ee)
    reclaim_threshold = reclaim + float(sig.get("reclaim_buffer_atr", 0.0)) * atr
    cand = (
        in_window
        & orb_ready
        & prior_breach
        & (close > reclaim_threshold)
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


FAILED_ORB_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="orb",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_failed_orb_signals,
    validate_config=validate_failed_orb_config,
)
