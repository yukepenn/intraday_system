"""ORB breakout retest continuation (long-only signal MVP)."""

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

STRATEGY_NAME = "orb_retest_continuation"
SETUP_CODE = 2002
FEATURE_SET = "opening_core_v1"

REQUIRED_COLUMNS: tuple[str, ...] = (
    "orb_high_15",
    "orb_low_15",
    "orb_mid_15",
    "orb_range_15",
    "orb_width_pct_15",
    "vwap",
    "vwap_slope_5",
    "atr_like_20",
)


def validate_orb_retest_continuation_config(config: Mapping[str, Any]) -> None:
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="orb",
        required_feature_set=FEATURE_SET,
        allowed_stop_modes=("orb_mid", "orb_low", "signal_low", "atr_buffer"),
    )


def _prior_breakout_above(
    close: np.ndarray,
    orb_high: np.ndarray,
    minute: np.ndarray,
    session_id: np.ndarray,
    om: int,
) -> np.ndarray:
    n = int(close.shape[0])
    out = np.zeros(n, dtype=bool)
    seen_breakout = False
    current_session: int | None = None
    for i in range(n):
        sid = int(session_id[i])
        if current_session is None or sid != current_session:
            current_session = sid
            seen_breakout = False

        if int(minute[i]) >= om - 1:
            out[i] = seen_breakout
            if np.isfinite(close[i]) and np.isfinite(orb_high[i]) and close[i] > orb_high[i]:
                seen_breakout = True
    return out


def generate_orb_retest_continuation_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_orb_retest_continuation_config(config)
    sig = config["signal"]
    risk = config["risk"]
    om = int(sig.get("orb_open_minutes", 15))
    suf = f"_{om}"
    cols = tuple(c.replace("_15", suf) if "_15" in c else c for c in REQUIRED_COLUMNS)
    require_feature_columns(features.columns, cols, strategy_name=STRATEGY_NAME)

    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    tol = float(sig.get("retest_tolerance_atr", 0.25))
    req_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )
    min_slope = float(sig.get("min_vwap_slope", -1e18))

    close = bars.close
    low = bars.low
    minute = bars.minute.astype(np.int32, copy=False)
    orb_high = features.column(f"orb_high{suf}")
    orb_low = features.column(f"orb_low{suf}")
    orb_mid = features.column(f"orb_mid{suf}")
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")

    prior_break = _prior_breakout_above(close, orb_high, minute, bars.session_id, om)
    orb_ready = minute >= (om - 1)
    in_window = (minute >= es) & (minute <= ee)
    retest = low <= (orb_high + tol * atr)
    cand = (
        in_window
        & orb_ready
        & prior_break
        & retest
        & (close > orb_high)
        & np.isfinite(atr)
        & (atr > 0)
    )
    if req_vwap:
        cand &= close > vwap
    if min_slope > -1e17:
        cand &= vwap_slope >= min_slope

    stop_arr = compute_long_stop(
        bars,
        features,
        str(risk.get("stop_mode", "signal_low")),
        atr_mult=float(risk.get("atr_buffer_mult", 0.35)),
        orb_low=orb_low,
        orb_mid=orb_mid,
    )
    entry = cand & np.isfinite(stop_arr) & (stop_arr < close)
    entry = thin_first_n_per_session(entry, bars.session_id, int(risk.get("max_trades_per_day", 1)))

    score = clip_finite((close - orb_high) / atr, -3.0, 3.0)
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


ORB_RETEST_CONTINUATION_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="orb",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_orb_retest_continuation_signals,
    validate_config=validate_orb_retest_continuation_config,
)
