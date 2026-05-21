"""ORB breakout continuation with side-aware short retrofit."""

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

STRATEGY_NAME = "orb_continuation"
_SPEC = get_setup_codes(STRATEGY_NAME)
SETUP_CODE_LONG = _SPEC.long_code
SETUP_CODE_SHORT = _SPEC.short_code
# Backward-compat alias retained for tests / callers that imported the
# legacy single-code constant before Phase19 side-aware retrofit.
SETUP_CODE = SETUP_CODE_LONG
FEATURE_SET = "opening_core_v1"
FEATURE_SETS = ("opening_core_v1", "opening_core_v2")

REQUIRED_COLUMNS: tuple[str, ...] = (
    "orb_high_15",
    "orb_low_15",
    "orb_mid_15",
    "orb_range_15",
    "orb_width_pct_15",
    "vwap",
    "vwap_slope_5",
    "atr_like_20",
)


def validate_orb_continuation_config(config: Mapping[str, Any]) -> None:
    validate_side_aware_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="orb",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("orb_mid", "orb_low", "atr_buffer", "signal_low"),
        allowed_side_modes=CURRENT10_SIDE_MODES,
    )
    sig = config.get("signal", {})
    if int(sig.get("orb_open_minutes", 15)) <= 0:
        raise ConfigError("signal.orb_open_minutes must be > 0")
    validate_optional_positive_int(sig, "orb_open_minutes", "signal.orb_open_minutes")
    validate_optional_finite_float(sig, "min_vwap_slope", "signal.min_vwap_slope")
    validate_optional_nonnegative_float(sig, "min_orb_width_pct", "signal.min_orb_width_pct")
    validate_optional_nonnegative_float(sig, "max_orb_width_pct", "signal.max_orb_width_pct")
    min_w = float(sig.get("min_orb_width_pct", 0.0))
    max_w = float(sig.get("max_orb_width_pct", 1e18))
    if min_w < 0 or max_w < 0 or min_w > max_w:
        raise ConfigError("signal min/max ORB width must be nonnegative and ordered")
    validate_optional_nonnegative_float(sig, "breakout_buffer_atr", "signal.breakout_buffer_atr")
    validate_optional_nonnegative_float(sig, "breakout_buffer_pct", "signal.breakout_buffer_pct")
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")
    validate_optional_positive_float(sig, "min_rel_volume_20", "signal.min_rel_volume_20")
    validate_optional_nonnegative_float(sig, "max_vwap_dist_pct", "signal.max_vwap_dist_pct")


_LONG_TO_SHORT_STOP: dict[str, str] = {
    "signal_low": "signal_high",
    "atr_buffer": "atr_buffer",
    "orb_low": "orb_high",
    "orb_mid": "orb_mid",
}


def _orb_suffix(config: Mapping[str, Any]) -> str:
    om = int(config.get("signal", {}).get("orb_open_minutes", 15))
    return f"_{om}"


def generate_orb_continuation_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_orb_continuation_config(config)
    suf = _orb_suffix(config)
    cols = tuple(c.replace("_15", suf) if c.endswith("_15") else c for c in REQUIRED_COLUMNS)

    sig = config["signal"]
    risk = config["risk"]
    side_mode = normalize_side_mode(sig)
    short_enabled = side_mode != SIDE_MODE_LONG_ONLY
    om = int(sig.get("orb_open_minutes", 15))
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    req_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )
    min_slope = float(sig.get("min_vwap_slope", -1e18))
    min_w = float(sig.get("min_orb_width_pct", 0.0))
    max_w = float(sig.get("max_orb_width_pct", 1e18))
    extra_cols: list[str] = []
    if "close_position_min" in sig:
        extra_cols.append("close_position_in_range")
    if "min_rel_volume_20" in sig:
        extra_cols.append("rel_volume_20")
    if "max_vwap_dist_pct" in sig:
        extra_cols.append("vwap_dist_pct")
    require_feature_columns(
        features.columns, (*cols, *tuple(dict.fromkeys(extra_cols))), strategy_name=STRATEGY_NAME
    )

    close = bars.close
    minute = bars.minute.astype(np.int32, copy=False)
    orb_high = features.column(f"orb_high{suf}")
    orb_low = features.column(f"orb_low{suf}")
    orb_mid = features.column(f"orb_mid{suf}")
    orb_width = features.column(f"orb_width_pct{suf}")
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")

    orb_ready = minute >= (om - 1)
    in_window = (minute >= es) & (minute <= ee)
    finite = (
        np.isfinite(orb_high)
        & np.isfinite(close)
        & np.isfinite(atr)
        & (atr > 0)
        & np.isfinite(orb_width)
    )
    width_ok = (orb_width >= min_w) & (orb_width <= max_w)

    long_breakout = orb_high.copy()
    if "breakout_buffer_atr" in sig:
        long_breakout = long_breakout + float(sig["breakout_buffer_atr"]) * atr
    if "breakout_buffer_pct" in sig:
        long_breakout = long_breakout * (1.0 + float(sig["breakout_buffer_pct"]))
    long_cand = in_window & orb_ready & finite & width_ok & (close > long_breakout)
    if req_vwap:
        long_cand &= close > vwap
    if min_slope > -1e17:
        long_cand &= vwap_slope >= min_slope
    if "close_position_min" in sig:
        long_cand &= features.column("close_position_in_range") >= float(sig["close_position_min"])
    if "min_rel_volume_20" in sig:
        long_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])
    if "max_vwap_dist_pct" in sig:
        long_cand &= np.abs(features.column("vwap_dist_pct")) <= float(sig["max_vwap_dist_pct"])

    short_breakout = orb_low.copy()
    if "breakout_buffer_atr" in sig:
        short_breakout = short_breakout - float(sig["breakout_buffer_atr"]) * atr
    if "breakout_buffer_pct" in sig:
        short_breakout = short_breakout * (1.0 - float(sig["breakout_buffer_pct"]))
    short_cand = np.zeros_like(long_cand, dtype=bool)
    if short_enabled:
        short_cand = in_window & orb_ready & finite & width_ok & (close < short_breakout)
        if req_vwap:
            short_cand &= close < vwap
        if min_slope > -1e17:
            # Symmetric requirement: vwap_slope must be <= -min_slope for shorts.
            short_cand &= vwap_slope <= -min_slope
        if "close_position_min" in sig:
            short_cand &= (1.0 - features.column("close_position_in_range")) >= float(
                sig["close_position_min"]
            )
        if "min_rel_volume_20" in sig:
            short_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])
        if "max_vwap_dist_pct" in sig:
            short_cand &= np.abs(features.column("vwap_dist_pct")) <= float(
                sig["max_vwap_dist_pct"]
            )

    long_stop_mode = str(risk.get("stop_mode", "signal_low"))
    long_stop = compute_long_stop(
        bars,
        features,
        long_stop_mode,
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        orb_low=orb_low,
        orb_mid=orb_mid,
    )
    long_score = clip_finite((close - long_breakout) / atr, -3.0, 3.0)
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
            orb_mid=orb_mid,
        )
        short_score = clip_finite((short_breakout - close) / atr, -3.0, 3.0)
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


ORB_CONTINUATION_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="orb",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_orb_continuation_signals,
    validate_config=validate_orb_continuation_config,
    setup_code_long=SETUP_CODE_LONG,
    setup_code_short=SETUP_CODE_SHORT,
    allowed_side_modes=CURRENT10_SIDE_MODES,
    default_side_mode=SIDE_MODE_LONG_ONLY,
    required_feature_columns=REQUIRED_COLUMNS,
)
