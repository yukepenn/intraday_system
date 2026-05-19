"""ORB breakout continuation (long-only signal MVP)."""

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

STRATEGY_NAME = "orb_continuation"
SETUP_CODE = 2001
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
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="orb",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("orb_mid", "orb_low", "atr_buffer", "signal_low"),
    )
    sig = config.get("signal", {})
    if int(sig.get("orb_open_minutes", 15)) <= 0:
        raise ConfigError("signal.orb_open_minutes must be > 0")
    min_w = float(sig.get("min_orb_width_pct", 0.0))
    max_w = float(sig.get("max_orb_width_pct", 1e18))
    if min_w < 0 or max_w < 0 or min_w > max_w:
        raise ConfigError("signal min/max ORB width must be nonnegative and ordered")
    validate_optional_nonnegative_float(sig, "breakout_buffer_atr", "signal.breakout_buffer_atr")
    validate_optional_nonnegative_float(sig, "breakout_buffer_pct", "signal.breakout_buffer_pct")
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")
    validate_optional_positive_float(sig, "min_rel_volume_20", "signal.min_rel_volume_20")
    validate_optional_nonnegative_float(sig, "max_vwap_dist_pct", "signal.max_vwap_dist_pct")


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
    breakout_level = orb_high.copy()
    if "breakout_buffer_atr" in sig:
        breakout_level = breakout_level + float(sig["breakout_buffer_atr"]) * atr
    if "breakout_buffer_pct" in sig:
        breakout_level = breakout_level * (1.0 + float(sig["breakout_buffer_pct"]))
    cand = in_window & orb_ready & finite & (close > breakout_level)
    cand &= (orb_width >= min_w) & (orb_width <= max_w)
    if req_vwap:
        cand &= close > vwap
    if min_slope > -1e17:
        cand &= vwap_slope >= min_slope
    if "close_position_min" in sig:
        cand &= features.column("close_position_in_range") >= float(sig["close_position_min"])
    if "min_rel_volume_20" in sig:
        cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])
    if "max_vwap_dist_pct" in sig:
        cand &= np.abs(features.column("vwap_dist_pct")) <= float(sig["max_vwap_dist_pct"])

    stop_arr = compute_long_stop(
        bars,
        features,
        str(risk.get("stop_mode", "signal_low")),
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        orb_low=orb_low,
        orb_mid=orb_mid,
    )
    valid_stop = np.isfinite(stop_arr) & (stop_arr < close)
    entry = cand & valid_stop

    max_trades = int(risk.get("max_trades_per_day", 1))
    entry = thin_first_n_per_session(entry, bars.session_id, max_trades)

    score = clip_finite((close - breakout_level) / atr, -3.0, 3.0)
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


ORB_CONTINUATION_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="orb",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_orb_continuation_signals,
    validate_config=validate_orb_continuation_config,
)
