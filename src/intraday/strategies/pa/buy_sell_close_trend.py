"""PA buy-sell-close trend continuation (long-only signal MVP)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.strategies.base import StrategyDef
from intraday.strategies.config_validation import validate_pa_buy_sell_close_trend_config
from intraday.strategies.contracts import (
    LONG_SIDE,
    SIGNAL_CONTRACT_VERSION,
    clip_finite,
    compute_signal_hash,
    require_feature_columns,
    validate_signal_matrix,
)

STRATEGY_NAME = "pa_buy_sell_close_trend"
SETUP_CODE_LONG = 1001

PA_REQUIRED_FEATURE_COLUMNS: tuple[str, ...] = (
    "body_pct",
    "close_position_in_range",
    "trend_slope_like_20",
    "close_vs_rolling_mean_20",
    "vwap_side",
    "atr_like_20",
    "rolling_low_20",
    "bar_range",
)


def _compute_stop(
    bars: BarMatrix,
    features: FeatureMatrix,
    stop_mode: str,
    atr_buffer_mult: float,
) -> np.ndarray:
    close = bars.close
    low = bars.low
    atr = features.column("atr_like_20")
    if stop_mode == "signal_low":
        return low.astype(np.float64, copy=True)
    if stop_mode == "rolling_low":
        return features.column("rolling_low_20").astype(np.float64, copy=True)
    if stop_mode == "atr_buffer":
        return close - atr_buffer_mult * atr
    raise ValueError(f"unsupported stop_mode: {stop_mode!r}")


def _simple_pa_v1_score(
    body_pct: np.ndarray,
    close_pos: np.ndarray,
    trend_slope: np.ndarray,
    close_vs_mean: np.ndarray,
    atr: np.ndarray,
    vwap_side: np.ndarray,
) -> np.ndarray:
    trend_term = clip_finite(trend_slope / atr, -2.0, 2.0)
    mean_term = clip_finite(close_vs_mean / atr, -2.0, 2.0)
    vwap_bonus = np.where(vwap_side > 0, 0.10, 0.0)
    return body_pct + 0.25 * close_pos + 0.25 * trend_term + 0.25 * mean_term + vwap_bonus


def generate_pa_buy_sell_close_trend_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    """Generate long-only PA trend signals from BarMatrix + FeatureMatrix."""
    validate_pa_buy_sell_close_trend_config(config)
    require_feature_columns(
        features.columns, PA_REQUIRED_FEATURE_COLUMNS, strategy_name=STRATEGY_NAME
    )

    n = bars.n_bars
    sig = config["signal"]
    risk = config["risk"]

    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    body_min = float(sig.get("body_pct_min", 0))
    cp_min = float(sig.get("close_position_min", 0))
    trend_min = float(sig.get("trend_slope_min", 0))
    cv_min = float(sig.get("close_vs_mean_min", 0))
    req_vwap = bool(sig.get("require_vwap_side", False))
    stop_mode = str(risk.get("stop_mode", "signal_low"))
    target_r_val = float(risk["target_r"])
    atr_mult = float(risk.get("atr_buffer_mult", 0.35))

    body_pct = features.column("body_pct")
    close_pos = features.column("close_position_in_range")
    trend_slope = features.column("trend_slope_like_20")
    close_vs_mean = features.column("close_vs_rolling_mean_20")
    vwap_side = features.column("vwap_side")
    atr = features.column("atr_like_20")
    close = bars.close

    minute = bars.minute.astype(np.int32, copy=False)
    in_window = (minute >= es) & (minute <= ee)

    finite_req = (
        np.isfinite(body_pct)
        & np.isfinite(close_pos)
        & np.isfinite(trend_slope)
        & np.isfinite(close_vs_mean)
        & np.isfinite(vwap_side)
        & np.isfinite(atr)
        & (atr > 0)
    )

    cand = (
        in_window
        & finite_req
        & (body_pct >= body_min)
        & (close_pos >= cp_min)
        & (trend_slope >= trend_min)
        & (close_vs_mean >= cv_min)
    )
    if req_vwap:
        cand &= vwap_side > 0

    stop_arr = _compute_stop(bars, features, stop_mode, atr_mult)
    valid_stop = np.isfinite(stop_arr) & (stop_arr < close)
    entry = cand & valid_stop

    side = np.zeros(n, dtype=np.int8)
    stop = np.full(n, np.nan, dtype=np.float64)
    target_r = np.full(n, np.nan, dtype=np.float64)
    score = np.full(n, np.nan, dtype=np.float64)
    setup_code = np.zeros(n, dtype=np.int16)

    if entry.any():
        side[entry] = LONG_SIDE
        stop[entry] = stop_arr[entry]
        target_r[entry] = target_r_val
        setup_code[entry] = SETUP_CODE_LONG
        score_vals = _simple_pa_v1_score(
            body_pct, close_pos, trend_slope, close_vs_mean, atr, vwap_side
        )
        score[entry] = score_vals[entry]
        bad_score = entry & ~np.isfinite(score)
        if bad_score.any():
            entry = entry & np.isfinite(score)
            side[~entry] = 0
            stop[~entry] = np.nan
            target_r[~entry] = np.nan
            setup_code[~entry] = 0

    signal_hash = compute_signal_hash(
        strategy_name=STRATEGY_NAME,
        strategy_version=str(config.get("version", "strategy_v1")),
        signal_contract_version=str(config.get("signal_contract_version", SIGNAL_CONTRACT_VERSION)),
        config=config,
        feature_hash=features.feature_hash,
    )

    out = SignalMatrix(
        entry=entry.astype(np.bool_),
        side=side,
        stop=stop,
        target_r=target_r,
        score=score,
        setup_code=setup_code,
        signal_hash=signal_hash,
    )
    validate_signal_matrix(out, n)
    return out


PA_BUY_SELL_CLOSE_TREND_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="pa",
    version="strategy_v1",
    required_feature_set="pa_core_v1",
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_pa_buy_sell_close_trend_signals,
    validate_config=validate_pa_buy_sell_close_trend_config,
)
