"""Shared helpers for strategy signal generation (Phase 13)."""

from __future__ import annotations

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.strategies.contracts import (
    LONG_SIDE,
    SIGNAL_CONTRACT_VERSION,
    compute_signal_hash,
    validate_signal_matrix,
)


def previous_same_session(values: np.ndarray, session_id: np.ndarray) -> np.ndarray:
    """Value at bar i-1 when same session, else NaN."""
    n = int(values.shape[0])
    out = np.full(n, np.nan, dtype=np.float64)
    for i in range(1, n):
        if session_id[i] == session_id[i - 1]:
            out[i] = float(values[i - 1])
    return out


def crossed_above(
    prev_a: np.ndarray, curr_a: np.ndarray, prev_b: np.ndarray, curr_b: np.ndarray
) -> np.ndarray:
    return (
        np.isfinite(prev_a)
        & np.isfinite(curr_a)
        & np.isfinite(prev_b)
        & np.isfinite(curr_b)
        & (prev_a <= prev_b)
        & (curr_a > curr_b)
    )


def thin_first_n_per_session(
    entry: np.ndarray,
    session_id: np.ndarray,
    max_per_session: int,
) -> np.ndarray:
    """Keep only the first ``max_per_session`` entry bars per session."""
    if max_per_session <= 0:
        return np.zeros_like(entry, dtype=bool)
    out = entry.copy()
    counts: dict[int, int] = {}
    for i in range(int(session_id.shape[0])):
        if not out[i]:
            continue
        sid = int(session_id[i])
        counts[sid] = counts.get(sid, 0) + 1
        if counts[sid] > max_per_session:
            out[i] = False
    return out


def compute_long_stop(
    bars: BarMatrix,
    features: FeatureMatrix,
    stop_mode: str,
    *,
    atr_mult: float,
    orb_low: np.ndarray | None = None,
    orb_mid: np.ndarray | None = None,
    vwap: np.ndarray | None = None,
    prior_low: np.ndarray | None = None,
    prior_low_buffer_atr: float = 0.0,
) -> np.ndarray:
    close = bars.close.astype(np.float64, copy=False)
    low = bars.low.astype(np.float64, copy=False)
    atr = features.column("atr_like_20")

    if stop_mode == "signal_low":
        return low.copy()
    if stop_mode == "rolling_low_20":
        return features.column("rolling_low_20").astype(np.float64, copy=True)
    if stop_mode == "atr_buffer":
        return close - atr_mult * atr
    if stop_mode == "orb_low" and orb_low is not None:
        return orb_low.astype(np.float64, copy=True)
    if stop_mode == "orb_mid" and orb_mid is not None:
        return orb_mid.astype(np.float64, copy=True)
    if stop_mode == "vwap_atr_buffer" and vwap is not None:
        return vwap - atr_mult * atr
    if stop_mode == "prior_low_buffer" and prior_low is not None:
        return prior_low - prior_low_buffer_atr * atr
    raise ValueError(f"unsupported stop_mode: {stop_mode!r}")


def build_signal_matrix(
    *,
    bars: BarMatrix,
    entry: np.ndarray,
    stop: np.ndarray,
    target_r_val: float,
    setup_code_val: int,
    score: np.ndarray,
    strategy_name: str,
    config: dict,
    feature_hash: str,
) -> SignalMatrix:
    n = bars.n_bars
    side = np.zeros(n, dtype=np.int8)
    target_r = np.full(n, np.nan, dtype=np.float64)
    setup_code = np.zeros(n, dtype=np.int16)
    stop_out = np.full(n, np.nan, dtype=np.float64)
    score_out = np.full(n, np.nan, dtype=np.float64)

    if entry.any():
        side[entry] = LONG_SIDE
        stop_out[entry] = stop[entry]
        target_r[entry] = target_r_val
        setup_code[entry] = setup_code_val
        score_out[entry] = score[entry]

    signal_hash = compute_signal_hash(
        strategy_name=strategy_name,
        strategy_version=str(config.get("version", "strategy_v1")),
        signal_contract_version=str(config.get("signal_contract_version", SIGNAL_CONTRACT_VERSION)),
        config=config,
        feature_hash=feature_hash,
    )
    out = SignalMatrix(
        entry=entry.astype(np.bool_),
        side=side,
        stop=stop_out,
        target_r=target_r,
        score=score_out,
        setup_code=setup_code,
        signal_hash=signal_hash,
    )
    validate_signal_matrix(out, n)
    return out
