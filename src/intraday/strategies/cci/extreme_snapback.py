"""CCI extreme oversold snapback (long-only signal MVP)."""

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
    validate_optional_nonnegative_float,
    validate_optional_positive_float,
    validate_optional_probability,
)
from intraday.strategies.contracts import (
    SIGNAL_CONTRACT_VERSION,
    clip_finite,
    require_feature_columns,
)

STRATEGY_NAME = "cci_extreme_snapback"
SETUP_CODE = 6001
FEATURE_SET = "indicator_core_v1"
FEATURE_SETS = ("indicator_core_v1", "indicator_core_v2")

REQUIRED_COLUMNS: tuple[str, ...] = ("cci_20", "atr_like_20")


def validate_cci_extreme_snapback_config(config: Mapping[str, Any]) -> None:
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="cci",
        required_feature_set=FEATURE_SETS,
        allowed_stop_modes=("signal_low", "rolling_low_20", "atr_buffer"),
    )
    sig = config.get("signal", {})
    validate_optional_positive_float(sig, "oversold_lookback_bars", "signal.oversold_lookback_bars")
    validate_optional_probability(sig, "close_position_min", "signal.close_position_min")
    validate_optional_nonnegative_float(sig, "max_vwap_dist_pct", "signal.max_vwap_dist_pct")
    parse_bool_like(
        sig.get("require_vwap_slope_positive", False),
        "signal.require_vwap_slope_positive",
    )


def generate_cci_extreme_snapback_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_cci_extreme_snapback_config(config)

    sig = config["signal"]
    risk = config["risk"]
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    oversold = float(sig.get("oversold_threshold", -100.0))
    cross_above = float(sig.get("cross_threshold", -80.0))
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
    cross = np.isfinite(prev_cci) & np.isfinite(cci) & oversold_ok & (cci > cross_above)

    in_window = (minute >= es) & (minute <= ee)
    cand = in_window & cross & np.isfinite(atr) & (atr > 0)
    if req_vwap and vwap is not None:
        cand &= close > vwap
    if "min_cci_slope" in sig:
        cand &= (cci - prev_cci) >= float(sig["min_cci_slope"])
    if req_vwap_slope:
        cand &= features.column("vwap_slope_5") > 0
    if "close_position_min" in sig:
        cand &= features.column("close_position_in_range") >= float(sig["close_position_min"])
    if "max_vwap_dist_pct" in sig:
        cand &= np.abs(features.column("vwap_dist_pct")) <= float(sig["max_vwap_dist_pct"])

    stop_arr = compute_long_stop(
        bars,
        features,
        str(risk.get("stop_mode", "signal_low")),
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
    )
    entry = cand & np.isfinite(stop_arr) & (stop_arr < close)
    entry = thin_first_n_per_session(entry, bars.session_id, int(risk.get("max_trades_per_day", 1)))

    score = clip_finite((cci - oversold) / 100.0, -3.0, 3.0)
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


CCI_EXTREME_SNAPBACK_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="cci",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_cci_extreme_snapback_signals,
    validate_config=validate_cci_extreme_snapback_config,
)
