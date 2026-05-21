"""Brooks PA second-entry pullback (side-aware Phase19B strategy)."""

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

STRATEGY_NAME = "pa_second_entry_pullback"
FEATURE_SET = "pa_brooks_core_v1"
SETUP_CODE_LONG = 1101
SETUP_CODE_SHORT = 1102

REQUIRED_COLUMNS: tuple[str, ...] = (
    "pa_always_in_side",
    "pa_pullback_depth_atr",
    "pa_two_leg_pullback_down",
    "pa_two_leg_pullback_up",
    "pa_second_entry_buy_proxy",
    "pa_second_entry_sell_proxy",
    "bull_signal_bar",
    "bear_signal_bar",
    "strong_bull_close",
    "strong_bear_close",
    "pa_trading_range_score_20",
)


def validate_pa_second_entry_pullback_config(config: Mapping[str, Any]) -> None:
    validate_brooks_strategy_config(
        config,
        strategy_name=STRATEGY_NAME,
        required_feature_set=FEATURE_SET,
        allowed_stop_modes=("signal_extreme",),
    )


def generate_pa_second_entry_pullback_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_pa_second_entry_pullback_config(config)
    require_brooks_feature_columns(features, REQUIRED_COLUMNS, strategy_name=STRATEGY_NAME)

    sig = config["signal"]
    in_window = in_entry_window(bars, sig)
    max_depth = float(sig.get("pullback_max_depth_atr", 1.5))
    tr_block = float(sig.get("block_trading_range_score_max", 0.85))
    require_second = bool(sig.get("require_second_entry", True))
    require_signal = bool(sig.get("require_signal_bar", True))

    always_in = features.column("pa_always_in_side")
    depth = features.column("pa_pullback_depth_atr")
    not_tight_tr = features.column("pa_trading_range_score_20") < tr_block

    long_entry = (
        in_window
        & (always_in >= 0)
        & (features.column("pa_two_leg_pullback_down") > 0)
        & (depth <= max_depth)
        & not_tight_tr
    )
    short_entry = (
        in_window
        & (always_in <= 0)
        & (features.column("pa_two_leg_pullback_up") > 0)
        & (depth <= max_depth)
        & not_tight_tr
    )
    if require_second:
        long_entry &= features.column("pa_second_entry_buy_proxy") > 0
        short_entry &= features.column("pa_second_entry_sell_proxy") > 0
    if require_signal:
        long_entry &= (features.column("bull_signal_bar") > 0) | (
            features.column("strong_bull_close") > 0
        )
        short_entry &= (features.column("bear_signal_bar") > 0) | (
            features.column("strong_bear_close") > 0
        )

    long_score = deterministic_score(1.0 - depth, features.column("strong_bull_close"))
    short_score = deterministic_score(1.0 - depth, features.column("strong_bear_close"))
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


PA_SECOND_ENTRY_PULLBACK_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="pa",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_pa_second_entry_pullback_signals,
    validate_config=validate_pa_second_entry_pullback_config,
)
