"""CCI extreme snapback with side-aware short retrofit.

Long: CCI was oversold, then crosses above ``cross_threshold``.
Short: CCI was overbought, then crosses below ``cross_below_threshold``.
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

STRATEGY_NAME = "cci_extreme_snapback"
_SPEC = get_setup_codes(STRATEGY_NAME)
SETUP_CODE_LONG = _SPEC.long_code
SETUP_CODE_SHORT = _SPEC.short_code
SETUP_CODE = SETUP_CODE_LONG  # backward-compat alias
FEATURE_SET = "indicator_core_v1"
FEATURE_SETS = ("indicator_core_v1", "indicator_core_v2")

REQUIRED_COLUMNS: tuple[str, ...] = ("cci_20", "atr_like_20")


def validate_cci_extreme_snapback_config(config: Mapping[str, Any]) -> None:
    validate_side_aware_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="cci",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "rolling_low_20", "atr_buffer"),
        allowed_side_modes=CURRENT10_SIDE_MODES,
    )
    sig = config.get("signal", {})
    validate_optional_finite_float(sig, "oversold_threshold", "signal.oversold_threshold")
    validate_optional_finite_float(sig, "cross_threshold", "signal.cross_threshold")
    validate_optional_finite_float(sig, "overbought_threshold", "signal.overbought_threshold")
    validate_optional_finite_float(sig, "cross_below_threshold", "signal.cross_below_threshold")
    validate_optional_positive_int(sig, "oversold_lookback_bars", "signal.oversold_lookback_bars")
    validate_optional_positive_int(
        sig, "overbought_lookback_bars", "signal.overbought_lookback_bars"
    )
    validate_optional_finite_float(sig, "min_cci_slope", "signal.min_cci_slope")
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")
    validate_optional_nonnegative_float(sig, "max_vwap_dist_pct", "signal.max_vwap_dist_pct")
    parse_bool_like(sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap")
    parse_bool_like(
        sig.get("require_vwap_slope_positive", False),
        "signal.require_vwap_slope_positive",
    )


_LONG_TO_SHORT_STOP: dict[str, str] = {
    "signal_low": "signal_high",
    "rolling_low_20": "rolling_high_20",
    "atr_buffer": "atr_buffer",
}


def generate_cci_extreme_snapback_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_cci_extreme_snapback_config(config)

    sig = config["signal"]
    risk = config["risk"]
    side_mode = normalize_side_mode(sig)
    short_enabled = side_mode != SIDE_MODE_LONG_ONLY
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    oversold = float(sig.get("oversold_threshold", -100.0))
    cross_above = float(sig.get("cross_threshold", -80.0))
    overbought = float(sig.get("overbought_threshold", 100.0))
    cross_below = float(sig.get("cross_below_threshold", 80.0))
    req_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )
    req_vwap_slope = parse_bool_like(
        sig.get("require_vwap_slope_positive", False),
        "signal.require_vwap_slope_positive",
    )
    extra_cols: list[str] = []
    if req_vwap:
        extra_cols.append("vwap")
    if req_vwap_slope:
        extra_cols.append("vwap_slope_5")
    if "close_position_min" in sig:
        extra_cols.append("close_position_in_range")
    if "max_vwap_dist_pct" in sig:
        extra_cols.append("vwap_dist_pct")
    if short_enabled:
        extra_cols.append("rolling_high_20")
    require_feature_columns(
        features.columns,
        (*REQUIRED_COLUMNS, *tuple(dict.fromkeys(extra_cols))),
        strategy_name=STRATEGY_NAME,
    )

    close = bars.close
    minute = bars.minute.astype(np.int32, copy=False)
    cci = features.column("cci_20")
    atr = features.column("atr_like_20")
    vwap = features.column("vwap") if "vwap" in features.columns else None

    prev_cci = previous_same_session(cci, bars.session_id)
    if "oversold_lookback_bars" in sig:
        oversold_seen = bars_since_prior_condition(cci <= oversold, bars.session_id)
        oversold_ok = (oversold_seen >= 1) & (oversold_seen <= int(sig["oversold_lookback_bars"]))
    else:
        oversold_ok = np.isfinite(prev_cci) & (prev_cci <= oversold)
    cross_long = np.isfinite(prev_cci) & np.isfinite(cci) & oversold_ok & (cci > cross_above)

    in_window = (minute >= es) & (minute <= ee)
    long_cand = in_window & cross_long & np.isfinite(atr) & (atr > 0)
    if req_vwap and vwap is not None:
        long_cand &= close > vwap
    if "min_cci_slope" in sig:
        long_cand &= (cci - prev_cci) >= float(sig["min_cci_slope"])
    if req_vwap_slope:
        long_cand &= features.column("vwap_slope_5") > 0
    if "close_position_min" in sig:
        long_cand &= features.column("close_position_in_range") >= float(sig["close_position_min"])
    if "max_vwap_dist_pct" in sig:
        long_cand &= np.abs(features.column("vwap_dist_pct")) <= float(sig["max_vwap_dist_pct"])

    short_cand = np.zeros_like(long_cand, dtype=bool)
    if short_enabled:
        if "overbought_lookback_bars" in sig:
            ob_seen = bars_since_prior_condition(cci >= overbought, bars.session_id)
            ob_ok = (ob_seen >= 1) & (ob_seen <= int(sig["overbought_lookback_bars"]))
        else:
            ob_ok = np.isfinite(prev_cci) & (prev_cci >= overbought)
        cross_short = np.isfinite(prev_cci) & np.isfinite(cci) & ob_ok & (cci < cross_below)
        short_cand = in_window & cross_short & np.isfinite(atr) & (atr > 0)
        if req_vwap and vwap is not None:
            short_cand &= close < vwap
        if "min_cci_slope" in sig:
            # Symmetric: negative slope at least as steep.
            short_cand &= (prev_cci - cci) >= float(sig["min_cci_slope"])
        if req_vwap_slope:
            short_cand &= features.column("vwap_slope_5") < 0
        if "close_position_min" in sig:
            short_cand &= (1.0 - features.column("close_position_in_range")) >= float(
                sig["close_position_min"]
            )
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
    )
    long_score = clip_finite((cci - oversold) / 100.0, -3.0, 3.0)
    if short_enabled:
        short_stop_mode = str(
            sig.get("short_stop_mode", _LONG_TO_SHORT_STOP.get(long_stop_mode, "signal_high"))
        )
        short_stop = compute_short_stop(
            bars,
            features,
            short_stop_mode,
            atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        )
        short_score = clip_finite((overbought - cci) / 100.0, -3.0, 3.0)
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


CCI_EXTREME_SNAPBACK_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="cci",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_cci_extreme_snapback_signals,
    validate_config=validate_cci_extreme_snapback_config,
    setup_code_long=SETUP_CODE_LONG,
    setup_code_short=SETUP_CODE_SHORT,
    allowed_side_modes=CURRENT10_SIDE_MODES,
    default_side_mode=SIDE_MODE_LONG_ONLY,
    required_feature_columns=REQUIRED_COLUMNS,
)
