"""Failed ORB downside trap / reclaim with side-aware short retrofit.

Failed-ORB long: prior breach below ORB low then reclaim back above.
Failed-ORB short: prior breach above ORB high then reject back below.
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

STRATEGY_NAME = "failed_orb"
_SPEC = get_setup_codes(STRATEGY_NAME)
SETUP_CODE_LONG = _SPEC.long_code
SETUP_CODE_SHORT = _SPEC.short_code
SETUP_CODE = SETUP_CODE_LONG  # backward-compat alias
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
    validate_side_aware_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="orb",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "orb_low", "atr_buffer"),
        allowed_side_modes=CURRENT10_SIDE_MODES,
    )
    sig = config.get("signal", {})
    mode = str(sig.get("reclaim_level", "orb_low"))
    if mode not in ("orb_low", "orb_mid"):
        raise ConfigError("signal.reclaim_level must be orb_low or orb_mid")
    if int(sig.get("orb_open_minutes", 15)) <= 0:
        raise ConfigError("signal.orb_open_minutes must be > 0")
    validate_optional_positive_int(sig, "orb_open_minutes", "signal.orb_open_minutes")
    validate_optional_finite_float(sig, "min_vwap_slope", "signal.min_vwap_slope")
    validate_optional_nonnegative_float(sig, "min_breach_depth_atr", "signal.min_breach_depth_atr")
    validate_optional_nonnegative_float(sig, "max_breach_depth_atr", "signal.max_breach_depth_atr")
    if (
        "min_breach_depth_atr" in sig
        and "max_breach_depth_atr" in sig
        and float(sig["min_breach_depth_atr"]) > float(sig["max_breach_depth_atr"])
    ):
        raise ConfigError("signal.min_breach_depth_atr must be <= max_breach_depth_atr")
    validate_optional_positive_int(sig, "max_bars_since_breach", "signal.max_bars_since_breach")
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


def _breach_above(
    close: np.ndarray,
    orb_high: np.ndarray,
    atr: np.ndarray,
    minute: np.ndarray,
    om: int,
    min_depth_atr: float,
    max_depth_atr: float,
) -> np.ndarray:
    depth = (close - orb_high) / atr
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


_LONG_TO_SHORT_STOP: dict[str, str] = {
    "signal_low": "signal_high",
    "atr_buffer": "atr_buffer",
    "orb_low": "orb_high",
}


def generate_failed_orb_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_failed_orb_config(config)
    sig = config["signal"]
    risk = config["risk"]
    side_mode = normalize_side_mode(sig)
    short_enabled = side_mode != SIDE_MODE_LONG_ONLY
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
    orb_high = features.column(f"orb_high{suf}")
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")

    long_reclaim = orb_low if reclaim_level == "orb_low" else orb_mid
    breach_now_long = _breach_below(
        close,
        orb_low,
        atr,
        minute,
        om,
        float(sig.get("min_breach_depth_atr", 0.0)),
        float(sig.get("max_breach_depth_atr", 1e18)),
    )
    breach_age_long = bars_since_prior_condition(breach_now_long, bars.session_id)
    prior_breach_long = breach_age_long >= 1
    if "max_bars_since_breach" in sig:
        prior_breach_long &= breach_age_long <= int(sig["max_bars_since_breach"])
    orb_ready = minute >= (om - 1)
    in_window = (minute >= es) & (minute <= ee)
    reclaim_buf = float(sig.get("reclaim_buffer_atr", 0.0))
    long_reclaim_thr = long_reclaim + reclaim_buf * atr
    long_cand = (
        in_window
        & orb_ready
        & prior_breach_long
        & (close > long_reclaim_thr)
        & np.isfinite(atr)
        & (atr > 0)
    )
    if req_vwap:
        long_cand &= close > vwap
    if min_slope > -1e17:
        long_cand &= vwap_slope >= min_slope
    if "close_position_min" in sig:
        long_cand &= features.column("close_position_in_range") >= float(sig["close_position_min"])
    if "min_rel_volume_20" in sig:
        long_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])

    short_cand = np.zeros_like(long_cand, dtype=bool)
    short_reject_thr = orb_high.copy()
    if short_enabled:
        short_reject_level = orb_high if reclaim_level == "orb_low" else orb_mid
        short_reject_thr = short_reject_level - reclaim_buf * atr
        breach_now_short = _breach_above(
            close,
            orb_high,
            atr,
            minute,
            om,
            float(sig.get("min_breach_depth_atr", 0.0)),
            float(sig.get("max_breach_depth_atr", 1e18)),
        )
        breach_age_short = bars_since_prior_condition(breach_now_short, bars.session_id)
        prior_breach_short = breach_age_short >= 1
        if "max_bars_since_breach" in sig:
            prior_breach_short &= breach_age_short <= int(sig["max_bars_since_breach"])
        short_cand = (
            in_window
            & orb_ready
            & prior_breach_short
            & (close < short_reject_thr)
            & np.isfinite(atr)
            & (atr > 0)
        )
        if req_vwap:
            short_cand &= close < vwap
        if min_slope > -1e17:
            short_cand &= vwap_slope <= -min_slope
        if "close_position_min" in sig:
            short_cand &= (1.0 - features.column("close_position_in_range")) >= float(
                sig["close_position_min"]
            )
        if "min_rel_volume_20" in sig:
            short_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])

    long_stop_mode = str(risk.get("stop_mode", "signal_low"))
    long_stop = compute_long_stop(
        bars,
        features,
        long_stop_mode,
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        orb_low=orb_low,
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
            orb_high=orb_high,
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


FAILED_ORB_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="orb",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_failed_orb_signals,
    validate_config=validate_failed_orb_config,
    setup_code_long=SETUP_CODE_LONG,
    setup_code_short=SETUP_CODE_SHORT,
    allowed_side_modes=CURRENT10_SIDE_MODES,
    default_side_mode=SIDE_MODE_LONG_ONLY,
    required_feature_columns=REQUIRED_COLUMNS,
)
