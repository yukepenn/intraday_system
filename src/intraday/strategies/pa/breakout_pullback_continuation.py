"""Brooks PA breakout-pullback continuation strategy."""

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
    prior_condition_within,
    require_brooks_feature_columns,
    validate_brooks_strategy_config,
)

STRATEGY_NAME = "pa_breakout_pullback_continuation"
FEATURE_SET = "pa_brooks_core_v1"
SETUP_CODE_LONG = 1501
SETUP_CODE_SHORT = 1502

REQUIRED_COLUMNS: tuple[str, ...] = (
    "pa_strong_bull_bo_score_20",
    "pa_strong_bear_bo_score_20",
    "pa_pullback_bar_count",
    "pa_pullback_depth_atr",
    "pa_always_in_side",
    "bull_signal_bar",
    "bear_signal_bar",
)


def validate_pa_breakout_pullback_continuation_config(config: Mapping[str, Any]) -> None:
    validate_brooks_strategy_config(
        config,
        strategy_name=STRATEGY_NAME,
        required_feature_set=FEATURE_SET,
        allowed_stop_modes=("signal_extreme",),
    )


def generate_pa_breakout_pullback_continuation_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_pa_breakout_pullback_continuation_config(config)
    require_brooks_feature_columns(features, REQUIRED_COLUMNS, strategy_name=STRATEGY_NAME)

    sig = config["signal"]
    in_window = in_entry_window(bars, sig)
    bo_min = float(sig.get("bo_score_min", 0.55))
    bo_window = int(sig.get("breakout_window", 20))
    max_bars = float(sig.get("pullback_max_bars", 6))
    max_depth = float(sig.get("pullback_max_depth_atr", 1.2))
    require_signal = bool(sig.get("require_signal_bar", True))
    require_ai = bool(sig.get("require_always_in_with_side", False))

    prior_bull_bo = prior_condition_within(
        features.column("pa_strong_bull_bo_score_20") >= bo_min, bars.session_id, bo_window
    )
    prior_bear_bo = prior_condition_within(
        features.column("pa_strong_bear_bo_score_20") >= bo_min, bars.session_id, bo_window
    )
    pullback_ok = (features.column("pa_pullback_bar_count") <= max_bars) & (
        features.column("pa_pullback_depth_atr") <= max_depth
    )
    long_entry = in_window & prior_bull_bo & pullback_ok
    short_entry = in_window & prior_bear_bo & pullback_ok
    if require_signal:
        long_entry &= features.column("bull_signal_bar") > 0
        short_entry &= features.column("bear_signal_bar") > 0
    if require_ai:
        long_entry &= features.column("pa_always_in_side") >= 0
        short_entry &= features.column("pa_always_in_side") <= 0

    long_score = deterministic_score(
        features.column("pa_strong_bull_bo_score_20"),
        1.0 - features.column("pa_pullback_depth_atr"),
    )
    short_score = deterministic_score(
        features.column("pa_strong_bear_bo_score_20"),
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


PA_BREAKOUT_PULLBACK_CONTINUATION_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="pa",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_pa_breakout_pullback_continuation_signals,
    validate_config=validate_pa_breakout_pullback_continuation_config,
)
