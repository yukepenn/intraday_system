"""Prior-day low liquidity trap / reclaim (long-only signal MVP)."""

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
from intraday.strategies.config_validation import parse_bool_like, validate_long_only_strategy_base
from intraday.strategies.contracts import (
    SIGNAL_CONTRACT_VERSION,
    clip_finite,
    require_feature_columns,
)

STRATEGY_NAME = "prior_day_level_trap"
SETUP_CODE = 5001
FEATURE_SET = "gap_level_core_v1"

REQUIRED_COLUMNS: tuple[str, ...] = (
    "prior_session_low",
    "prior_session_high",
    "prior_session_close",
    "atr_like_20",
)


def validate_prior_day_level_trap_config(config: Mapping[str, Any]) -> None:
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="levels",
        required_feature_set=FEATURE_SET,
        allowed_stop_modes=("signal_low", "prior_low_buffer", "atr_buffer"),
    )


def generate_prior_day_level_trap_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_prior_day_level_trap_config(config)
    require_feature_columns(features.columns, REQUIRED_COLUMNS, strategy_name=STRATEGY_NAME)

    sig = config["signal"]
    risk = config["risk"]
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    breach_atr = float(sig.get("breach_buffer_atr", 0.15))
    req_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )

    close = bars.close
    low = bars.low
    minute = bars.minute.astype(np.int32, copy=False)
    prior_low = features.column("prior_session_low")
    atr = features.column("atr_like_20")
    vwap = features.column("vwap") if "vwap" in features.columns else None

    in_window = (minute >= es) & (minute <= ee)
    breached = low < (prior_low - breach_atr * atr)
    reclaimed = close > prior_low
    cand = in_window & breached & reclaimed & np.isfinite(prior_low) & np.isfinite(atr) & (atr > 0)
    if req_vwap and vwap is not None:
        cand &= close > vwap

    stop_arr = compute_long_stop(
        bars,
        features,
        str(risk.get("stop_mode", "signal_low")),
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        prior_low=prior_low,
        prior_low_buffer_atr=float(sig.get("prior_low_buffer_atr", 0.1)),
    )
    entry = cand & np.isfinite(stop_arr) & (stop_arr < close)
    entry = thin_first_n_per_session(entry, bars.session_id, int(risk.get("max_trades_per_day", 1)))

    score = clip_finite((close - prior_low) / atr, -3.0, 3.0)
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


PRIOR_DAY_LEVEL_TRAP_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="levels",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_prior_day_level_trap_signals,
    validate_config=validate_prior_day_level_trap_config,
)
