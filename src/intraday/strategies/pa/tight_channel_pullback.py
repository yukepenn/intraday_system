"""Brooks PA tight-channel pullback strategy."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.strategies.base import StrategyDef
from intraday.strategies.contracts import SIGNAL_CONTRACT_VERSION
from intraday.strategies.pa.brooks_common import (
    build_brooks_signal_matrix,
    deterministic_score,
    in_entry_window,
    require_brooks_feature_columns,
    validate_brooks_strategy_config,
)

STRATEGY_NAME = "pa_tight_channel_pullback"
FEATURE_SET = "pa_brooks_core_v1"
SETUP_CODE_LONG = 1601
SETUP_CODE_SHORT = 1602

REQUIRED_COLUMNS: tuple[str, ...] = (
    "pa_tight_bull_channel_score_20",
    "pa_tight_bear_channel_score_20",
    "pa_pullback_depth_atr",
    "pa_always_in_side",
    "bull_signal_bar",
    "bear_signal_bar",
    "strong_bull_close",
    "strong_bear_close",
    "pa_late_trend_score_20",
    "bull_micro_channel_3",
    "bear_micro_channel_3",
)


def validate_pa_tight_channel_pullback_config(config: Mapping[str, Any]) -> None:
    validate_brooks_strategy_config(
        config,
        strategy_name=STRATEGY_NAME,
        required_feature_set=FEATURE_SET,
        allowed_stop_modes=("signal_extreme",),
    )


def generate_pa_tight_channel_pullback_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_pa_tight_channel_pullback_config(config)
    require_brooks_feature_columns(features, REQUIRED_COLUMNS, strategy_name=STRATEGY_NAME)

    sig = config["signal"]
    in_window = in_entry_window(bars, sig)
    tight_min = float(sig.get("tight_score_min", 0.65))
    max_depth = float(sig.get("pullback_max_depth_atr", 0.8))
    late_max = float(sig.get("late_trend_score_max", 0.95))
    require_micro = bool(sig.get("require_micro_channel", False))
    require_ai = bool(sig.get("require_always_in_with_side", False))

    depth_ok = features.column("pa_pullback_depth_atr") <= max_depth
    not_late = features.column("pa_late_trend_score_20") <= late_max
    long_entry = (
        in_window
        & (features.column("pa_tight_bull_channel_score_20") >= tight_min)
        & depth_ok
        & not_late
        & ((features.column("bull_signal_bar") > 0) | (features.column("strong_bull_close") > 0))
    )
    short_entry = (
        in_window
        & (features.column("pa_tight_bear_channel_score_20") >= tight_min)
        & depth_ok
        & not_late
        & ((features.column("bear_signal_bar") > 0) | (features.column("strong_bear_close") > 0))
    )
    if require_micro:
        long_entry &= features.column("bull_micro_channel_3") > 0
        short_entry &= features.column("bear_micro_channel_3") > 0
    if require_ai:
        long_entry &= features.column("pa_always_in_side") >= 0
        short_entry &= features.column("pa_always_in_side") <= 0

    long_score = deterministic_score(
        features.column("pa_tight_bull_channel_score_20"),
        1.0 - features.column("pa_pullback_depth_atr"),
    )
    short_score = deterministic_score(
        features.column("pa_tight_bear_channel_score_20"),
        1.0 - features.column("pa_pullback_depth_atr"),
    )
    return build_brooks_signal_matrix(
        bars=bars,
        features=features,
        config=config,
        strategy_name=STRATEGY_NAME,
        long_entry=long_entry,
        short_entry=short_entry,
        long_stop=bars.low,
        short_stop=bars.high,
        long_score=long_score,
        short_score=short_score,
        setup_code_long=SETUP_CODE_LONG,
        setup_code_short=SETUP_CODE_SHORT,
    )


PA_TIGHT_CHANNEL_PULLBACK_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="pa",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_pa_tight_channel_pullback_signals,
    validate_config=validate_pa_tight_channel_pullback_config,
)
