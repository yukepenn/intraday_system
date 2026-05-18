"""Failed ORB downside trap / reclaim (long-only signal MVP)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.core.errors import ConfigError
from intraday.features.kernels.session_ops import session_start_indices
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

STRATEGY_NAME = "failed_orb"
SETUP_CODE = 2003
FEATURE_SET = "opening_core_v1"

REQUIRED_COLUMNS: tuple[str, ...] = (
    "orb_low_15",
    "orb_mid_15",
    "orb_high_15",
    "vwap",
    "vwap_slope_5",
    "atr_like_20",
)


def validate_failed_orb_config(config: Mapping[str, Any]) -> None:
    validate_long_only_strategy_base(
        config,
        strategy_name=STRATEGY_NAME,
        family="orb",
        required_feature_set=FEATURE_SET,
        allowed_stop_modes=("signal_low", "orb_low", "atr_buffer"),
    )
    mode = str(config.get("signal", {}).get("reclaim_level", "orb_low"))
    if mode not in ("orb_low", "orb_mid"):
        raise ConfigError("signal.reclaim_level must be orb_low or orb_mid")


def _prior_breach_below(
    close: np.ndarray,
    orb_low: np.ndarray,
    minute: np.ndarray,
    session_id: np.ndarray,
    om: int,
) -> np.ndarray:
    n = int(close.shape[0])
    starts = session_start_indices(session_id)
    out = np.zeros(n, dtype=bool)
    for i in range(n):
        if int(minute[i]) < om - 1:
            continue
        s0 = int(starts[i])
        for j in range(s0, i):
            if int(minute[j]) >= om - 1 and np.isfinite(close[j]) and np.isfinite(orb_low[j]):
                if close[j] < orb_low[j]:
                    out[i] = True
                    break
    return out


def generate_failed_orb_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    validate_failed_orb_config(config)
    sig = config["signal"]
    risk = config["risk"]
    om = int(sig.get("orb_open_minutes", 15))
    suf = f"_{om}"
    cols = tuple(c.replace("_15", suf) if "_15" in c else c for c in REQUIRED_COLUMNS)
    require_feature_columns(features.columns, cols, strategy_name=STRATEGY_NAME)

    reclaim_level = str(sig.get("reclaim_level", "orb_low"))
    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    req_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )
    min_slope = float(sig.get("min_vwap_slope", -1e18))

    close = bars.close
    minute = bars.minute.astype(np.int32, copy=False)
    orb_low = features.column(f"orb_low{suf}")
    orb_mid = features.column(f"orb_mid{suf}")
    vwap = features.column("vwap")
    vwap_slope = features.column("vwap_slope_5")
    atr = features.column("atr_like_20")

    reclaim = orb_low if reclaim_level == "orb_low" else orb_mid
    prior_breach = _prior_breach_below(close, orb_low, minute, bars.session_id, om)
    orb_ready = minute >= (om - 1)
    in_window = (minute >= es) & (minute <= ee)
    cand = in_window & orb_ready & prior_breach & (close > reclaim) & np.isfinite(atr) & (atr > 0)
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
    )
    entry = cand & np.isfinite(stop_arr) & (stop_arr < close)
    entry = thin_first_n_per_session(entry, bars.session_id, int(risk.get("max_trades_per_day", 1)))

    score = clip_finite((close - reclaim) / atr, -3.0, 3.0)
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


FAILED_ORB_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="orb",
    version="strategy_v1",
    required_feature_set=FEATURE_SET,
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_failed_orb_signals,
    validate_config=validate_failed_orb_config,
)
