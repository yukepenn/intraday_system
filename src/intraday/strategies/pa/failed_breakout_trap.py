"""Brooks PA failed rolling-range breakout trap strategy."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.strategies.base import StrategyDef
from intraday.strategies.contracts import SIDE_MODE_LONG_ONLY, SIGNAL_CONTRACT_VERSION
from intraday.strategies.pa.brooks_common import (
    BROOKS_SIDE_MODES,
    build_brooks_signal_matrix,
    deterministic_score,
    in_entry_window,
    long_short_stops,
    prior_condition_within,
    require_brooks_feature_columns,
    validate_brooks_strategy_config,
)
from intraday.strategies.setup_codes import get_setup_codes

STRATEGY_NAME = "pa_failed_breakout_trap"
FEATURE_SET = "pa_brooks_range_v1"
_SPEC = get_setup_codes(STRATEGY_NAME)
SETUP_CODE_LONG = _SPEC.long_code
SETUP_CODE_SHORT = _SPEC.short_code


def _columns(window: int) -> tuple[str, ...]:
    return (
        f"pa_range_breakout_down_{window}",
        f"pa_range_breakout_up_{window}",
        f"pa_close_back_inside_range_{window}",
        f"pa_tr_width_atr_{window}",
        f"pa_tr_low_{window}",
        f"pa_tr_high_{window}",
    )


def validate_pa_failed_breakout_trap_config(config: Mapping[str, Any]) -> None:
    validate_brooks_strategy_config(
        config,
        strategy_name=STRATEGY_NAME,
        required_feature_set=FEATURE_SET,
        allowed_stop_modes=("signal_extreme", "range_extreme"),
    )


def generate_pa_failed_breakout_trap_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_pa_failed_breakout_trap_config(config)
    sig = config["signal"]
    window = int(sig.get("range_window", 60))
    require_brooks_feature_columns(features, _columns(window), strategy_name=STRATEGY_NAME)

    max_age = int(sig.get("fail_back_inside_bars", 3))
    min_width = float(sig.get("min_range_width_atr", 0.8))
    in_window = in_entry_window(bars, sig)
    inside = features.column(f"pa_close_back_inside_range_{window}") > 0
    width_ok = features.column(f"pa_tr_width_atr_{window}") >= min_width

    prior_down = prior_condition_within(
        features.column(f"pa_range_breakout_down_{window}") > 0,
        bars.session_id,
        max_age,
    )
    prior_up = prior_condition_within(
        features.column(f"pa_range_breakout_up_{window}") > 0,
        bars.session_id,
        max_age,
    )
    long_entry = in_window & prior_down & inside & width_ok
    short_entry = in_window & prior_up & inside & width_ok

    long_stop, short_stop = long_short_stops(
        bars,
        features,
        stop_mode=str(config["risk"].get("stop_mode", "signal_extreme")),
        range_window=window,
    )
    score = deterministic_score(features.column(f"pa_tr_width_atr_{window}"), inside.astype(float))
    return build_brooks_signal_matrix(
        bars=bars,
        features=features,
        config=config,
        strategy_name=STRATEGY_NAME,
        long_entry=long_entry,
        short_entry=short_entry,
        long_stop=long_stop,
        short_stop=short_stop,
        long_score=score,
        short_score=score,
        setup_code_long=SETUP_CODE_LONG,
        setup_code_short=SETUP_CODE_SHORT,
    )


PA_FAILED_BREAKOUT_TRAP_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="pa",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_pa_failed_breakout_trap_signals,
    validate_config=validate_pa_failed_breakout_trap_config,
    setup_code_long=SETUP_CODE_LONG,
    setup_code_short=SETUP_CODE_SHORT,
    allowed_side_modes=BROOKS_SIDE_MODES,
    default_side_mode=SIDE_MODE_LONG_ONLY,
    required_feature_columns=_columns(60),
)
