"""VWAP trend pullback (long-only signal MVP)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.strategies.base import StrategyDef
from intraday.strategies.common import (
    build_signal_matrix,
    compute_long_stop,
    thin_first_n_per_session,
)
from intraday.strategies.config_validation import validate_long_only_strategy_base
from intraday.strategies.contracts import (
    SIGNAL_CONTRACT_VERSION,
    clip_finite,
    require_feature_columns,
)

STRATEGY_NAME = "vwap_trend_pullback"
SETUP_CODE = 4001
FEATURE_SET = "vwap_level_core_v1"

REQUIRED_COLUMNS: tuple[str, ...] = (
    "vwap",
    "vwap_dist",
    "vwap_dist_pct",
    "vwap_side",
    "vwap_slope_5",
    "atr_like_20",
    "range_mean_20",
    "close_position_in_range",
)


def validate_vwap_trend_pullback_config(config: Mapping[str, Any]) -> None:
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="vwap",
        required_feature_set=FEATURE_SET,
        allowed_stop_modes=("signal_low", "vwap_atr_buffer", "atr_buffer"),
    )


def generate_vwap_trend_pullback_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_vwap_trend_pullback_config(config)
    require_feature_columns(features.columns, REQUIRED_COLUMNS, strategy_name=STRATEGY_NAME)

    sig = config["signal"]
    risk = config["risk"]
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    min_slope = float(sig.get("min_vwap_slope", 0.0))
    max_pb = float(sig.get("max_pullback_atr", 0.35))
    cp_min = float(sig.get("close_position_min", 0.55))

    close = bars.close
    low = bars.low
    minute = bars.minute.astype(np.int32, copy=False)
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")
    close_pos = features.column("close_position_in_range")

    in_window = (minute >= es) & (minute <= ee)
    near_vwap = low <= (vwap + max_pb * atr)
    cand = (
        in_window
        & (close > vwap)
        & (vwap_slope >= min_slope)
        & near_vwap
        & (close_pos >= cp_min)
        & np.isfinite(atr)
        & (atr > 0)
    )

    stop_arr = compute_long_stop(
        bars,
        features,
        str(risk.get("stop_mode", "signal_low")),
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        vwap=vwap,
    )
    entry = cand & np.isfinite(stop_arr) & (stop_arr < close)
    entry = thin_first_n_per_session(entry, bars.session_id, int(risk.get("max_trades_per_day", 1)))

    score = clip_finite((close - vwap) / atr, -3.0, 3.0)
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


VWAP_TREND_PULLBACK_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="vwap",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_vwap_trend_pullback_signals,
    validate_config=validate_vwap_trend_pullback_config,
)
