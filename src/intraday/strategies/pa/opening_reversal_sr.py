"""Reduced Brooks PA opening reversal near range support/resistance."""

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

STRATEGY_NAME = "pa_opening_reversal_sr"
FEATURE_SET = "pa_brooks_range_v1"
SETUP_CODE_LONG = 1401
SETUP_CODE_SHORT = 1402


def _columns(window: int) -> tuple[str, ...]:
    return (
        f"pa_close_in_lower_third_{window}",
        f"pa_close_in_upper_third_{window}",
        f"pa_range_breakout_down_{window}",
        f"pa_range_breakout_up_{window}",
        f"pa_close_back_inside_range_{window}",
        f"pa_tr_width_atr_{window}",
    )


def validate_pa_opening_reversal_sr_config(config: Mapping[str, Any]) -> None:
    validate_brooks_strategy_config(
        config,
        strategy_name=STRATEGY_NAME,
        required_feature_set=FEATURE_SET,
        allowed_stop_modes=("signal_extreme",),
    )


def generate_pa_opening_reversal_sr_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_pa_opening_reversal_sr_config(config)
    sig = config["signal"]
    window = int(sig.get("range_window", 30))
    require_brooks_feature_columns(features, _columns(window), strategy_name=STRATEGY_NAME)

    in_window = in_entry_window(bars, sig)
    min_width = float(sig.get("min_range_width_atr", 0.5))
    require_failed = bool(sig.get("require_failed_breakout", False))
    width_ok = features.column(f"pa_tr_width_atr_{window}") >= min_width
    inside = features.column(f"pa_close_back_inside_range_{window}") > 0

    long_entry = in_window & width_ok & (features.column(f"pa_close_in_lower_third_{window}") > 0)
    short_entry = in_window & width_ok & (features.column(f"pa_close_in_upper_third_{window}") > 0)
    if require_failed:
        long_entry &= (features.column(f"pa_range_breakout_down_{window}") > 0) | inside
        short_entry &= (features.column(f"pa_range_breakout_up_{window}") > 0) | inside

    long_score = deterministic_score(
        features.column(f"pa_tr_width_atr_{window}"),
        features.column(f"pa_close_in_lower_third_{window}"),
    )
    short_score = deterministic_score(
        features.column(f"pa_tr_width_atr_{window}"),
        features.column(f"pa_close_in_upper_third_{window}"),
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


PA_OPENING_REVERSAL_SR_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="pa",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_pa_opening_reversal_sr_signals,
    validate_config=validate_pa_opening_reversal_sr_config,
)
