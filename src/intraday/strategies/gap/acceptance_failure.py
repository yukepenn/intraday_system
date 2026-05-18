"""Gap-down acceptance failure / reclaim (long-only signal MVP)."""

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
from intraday.strategies.config_validation import parse_bool_like, validate_long_only_strategy_base
from intraday.strategies.contracts import (
    SIGNAL_CONTRACT_VERSION,
    clip_finite,
    require_feature_columns,
)

STRATEGY_NAME = "gap_acceptance_failure"
SETUP_CODE = 3001
FEATURE_SET = "gap_level_core_v1"

REQUIRED_COLUMNS: tuple[str, ...] = (
    "prior_session_close",
    "prior_session_high",
    "prior_session_low",
    "open_gap_pct",
    "vwap",
    "vwap_slope_5",
    "atr_like_20",
)


def validate_gap_acceptance_failure_config(config: Mapping[str, Any]) -> None:
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="gap",
        required_feature_set=FEATURE_SET,
        allowed_stop_modes=("signal_low", "rolling_low_20", "atr_buffer"),
    )
    mode = str(config.get("signal", {}).get("reclaim_mode", "prior_close"))
    if mode not in ("prior_close", "vwap"):
        raise ConfigError("signal.reclaim_mode must be prior_close or vwap")


def generate_gap_acceptance_failure_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_gap_acceptance_failure_config(config)
    require_feature_columns(features.columns, REQUIRED_COLUMNS, strategy_name=STRATEGY_NAME)

    sig = config["signal"]
    risk = config["risk"]
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    min_gap = float(sig.get("min_gap_pct", 0.005))
    reclaim_mode = str(sig.get("reclaim_mode", "prior_close"))
    req_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )
    min_slope = float(sig.get("min_vwap_slope", -1e18))

    close = bars.close
    minute = bars.minute.astype(np.int32, copy=False)
    gap_pct = features.column("open_gap_pct")
    prior_close = features.column("prior_session_close")
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")

    reclaim = prior_close if reclaim_mode == "prior_close" else vwap
    in_window = (minute >= es) & (minute <= ee)
    gap_ok = np.isfinite(gap_pct) & (gap_pct <= -min_gap)
    cand = in_window & gap_ok & (close > reclaim) & np.isfinite(atr) & (atr > 0)
    if req_vwap:
        cand &= close > vwap
    if min_slope > -1e17:
        cand &= vwap_slope >= min_slope

    stop_arr = compute_long_stop(
        bars,
        features,
        str(risk.get("stop_mode", "signal_low")),
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
    )
    entry = cand & np.isfinite(stop_arr) & (stop_arr < close)
    entry = thin_first_n_per_session(entry, bars.session_id, int(risk.get("max_trades_per_day", 1)))

    score = clip_finite(-gap_pct, 0.0, 5.0)
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


GAP_ACCEPTANCE_FAILURE_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="gap",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_gap_acceptance_failure_signals,
    validate_config=validate_gap_acceptance_failure_config,
)
