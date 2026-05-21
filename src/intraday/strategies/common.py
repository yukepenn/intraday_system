"""Shared helpers for strategy signal generation (Phase 13).

The Phase19 immediate fix adds generic side-aware helpers
(``compute_short_stop`` and ``build_side_aware_signal_matrix``) so that
non-Brooks current-10 strategies can produce side-aware ``SignalMatrix``
output without depending on the PA Brooks-specific helper module.
"""

from __future__ import annotations

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.core.types import Side
from intraday.strategies.contracts import (
    LONG_SIDE,
    SHORT_SIDE,
    SIGNAL_CONTRACT_VERSION,
    allowed_sides_for_mode,
    compute_signal_hash,
    normalize_side_mode,
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


def bars_since_prior_condition(condition: np.ndarray, session_id: np.ndarray) -> np.ndarray:
    """Bars since ``condition`` was true earlier in the same session.

    The current bar is deliberately excluded: if ``condition[i]`` is true,
    ``out[i]`` still reflects the prior occurrence before bar ``i``.
    """
    n = int(condition.shape[0])
    out = np.full(n, -1, dtype=np.int32)
    current_session: int | None = None
    last_seen = -1
    for i in range(n):
        sid = int(session_id[i])
        if current_session is None or sid != current_session:
            current_session = sid
            last_seen = -1
        if last_seen >= 0:
            out[i] = i - last_seen
        if bool(condition[i]):
            last_seen = i
    return out


def prior_condition_within_bars(
    condition: np.ndarray,
    session_id: np.ndarray,
    max_bars: int,
) -> np.ndarray:
    """Whether a condition occurred within ``max_bars`` prior same-session bars."""
    if max_bars <= 0:
        return np.zeros(condition.shape[0], dtype=bool)
    age = bars_since_prior_condition(condition, session_id)
    return (age >= 1) & (age <= max_bars)


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


def crossed_below(
    prev_a: np.ndarray, curr_a: np.ndarray, prev_b: np.ndarray, curr_b: np.ndarray
) -> np.ndarray:
    return (
        np.isfinite(prev_a)
        & np.isfinite(curr_a)
        & np.isfinite(prev_b)
        & np.isfinite(curr_b)
        & (prev_a >= prev_b)
        & (curr_a < curr_b)
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
    if stop_mode in ("rolling_low", "rolling_low_20"):
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


def compute_short_stop(
    bars: BarMatrix,
    features: FeatureMatrix,
    stop_mode: str,
    *,
    atr_mult: float,
    orb_high: np.ndarray | None = None,
    orb_mid: np.ndarray | None = None,
    vwap: np.ndarray | None = None,
    prior_high: np.ndarray | None = None,
    prior_high_buffer_atr: float = 0.0,
) -> np.ndarray:
    """Resolve a raw short stop price (must end up > reference close per side filter).

    Mirrors :func:`compute_long_stop`. The strategy is responsible for ensuring
    that the produced stop is finite and above the reference close on emitted
    short-entry bars; :func:`build_side_aware_signal_matrix` filters out short
    rows whose stop is not above close.
    """
    close = bars.close.astype(np.float64, copy=False)
    high = bars.high.astype(np.float64, copy=False)
    atr = features.column("atr_like_20")

    if stop_mode == "signal_high":
        return high.copy()
    if stop_mode == "rolling_high_20":
        return features.column("rolling_high_20").astype(np.float64, copy=True)
    if stop_mode == "atr_buffer":
        return close + atr_mult * atr
    if stop_mode == "orb_high" and orb_high is not None:
        return orb_high.astype(np.float64, copy=True)
    if stop_mode == "orb_mid" and orb_mid is not None:
        return orb_mid.astype(np.float64, copy=True)
    if stop_mode == "vwap_atr_buffer" and vwap is not None:
        return vwap + atr_mult * atr
    if stop_mode == "prior_high_buffer" and prior_high is not None:
        return prior_high + prior_high_buffer_atr * atr
    raise ValueError(f"unsupported short stop_mode: {stop_mode!r}")


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


def build_side_aware_signal_matrix(
    *,
    bars: BarMatrix,
    features: FeatureMatrix,
    config: dict,
    strategy_name: str,
    long_entry: np.ndarray,
    short_entry: np.ndarray,
    long_stop: np.ndarray,
    short_stop: np.ndarray,
    long_score: np.ndarray,
    short_score: np.ndarray,
    target_r_val: float,
    setup_code_long: int,
    setup_code_short: int | None,
    side_mode: str | None = None,
    max_trades_per_day: int | None = None,
) -> SignalMatrix:
    """Build a side-aware ``SignalMatrix`` for non-Brooks strategies.

    Filters long/short rows by ``signal.side_mode`` (or the explicit
    ``side_mode`` arg), enforces ``long_stop < close`` / ``short_stop > close``,
    and emits long/short setup codes from the runtime registry. The strategy
    is still responsible for computing entries, stops, and scores; this helper
    handles only the side-aware filtering and ``SignalMatrix`` construction.
    """
    n = bars.n_bars
    if side_mode is None:
        side_mode = normalize_side_mode(config.get("signal") or {})
    allowed = set(allowed_sides_for_mode(side_mode))
    long_enabled = int(Side.LONG) in allowed
    short_enabled = int(Side.SHORT) in allowed

    long_entry = np.asarray(long_entry, dtype=bool) & long_enabled
    short_entry = np.asarray(short_entry, dtype=bool) & short_enabled

    close = bars.close.astype(np.float64, copy=False)
    long_stop_arr = np.asarray(long_stop, dtype=np.float64)
    short_stop_arr = np.asarray(short_stop, dtype=np.float64)
    long_score_arr = np.asarray(long_score, dtype=np.float64)
    short_score_arr = np.asarray(short_score, dtype=np.float64)

    long_entry &= np.isfinite(long_stop_arr) & (long_stop_arr < close) & np.isfinite(long_score_arr)
    short_entry &= (
        np.isfinite(short_stop_arr) & (short_stop_arr > close) & np.isfinite(short_score_arr)
    )
    # Defensive: an emission must commit to exactly one side per bar; longs win.
    short_entry &= ~long_entry

    if max_trades_per_day is not None and int(max_trades_per_day) >= 1:
        combined = long_entry | short_entry
        thinned = thin_first_n_per_session(combined, bars.session_id, int(max_trades_per_day))
        long_entry &= thinned
        short_entry &= thinned

    entry = long_entry | short_entry
    side = np.zeros(n, dtype=np.int8)
    stop = np.full(n, np.nan, dtype=np.float64)
    target_r = np.full(n, np.nan, dtype=np.float64)
    score = np.full(n, np.nan, dtype=np.float64)
    setup_code = np.zeros(n, dtype=np.int16)

    if long_entry.any():
        side[long_entry] = LONG_SIDE
        stop[long_entry] = long_stop_arr[long_entry]
        target_r[long_entry] = target_r_val
        score[long_entry] = long_score_arr[long_entry]
        setup_code[long_entry] = int(setup_code_long)
    if short_entry.any():
        if setup_code_short is None:
            raise ValueError(
                f"strategy {strategy_name!r} emitted short entries but has no short setup code"
            )
        side[short_entry] = SHORT_SIDE
        stop[short_entry] = short_stop_arr[short_entry]
        target_r[short_entry] = target_r_val
        score[short_entry] = short_score_arr[short_entry]
        setup_code[short_entry] = int(setup_code_short)

    signal_hash = compute_signal_hash(
        strategy_name=strategy_name,
        strategy_version=str(config.get("version", "strategy_v1")),
        signal_contract_version=str(config.get("signal_contract_version", SIGNAL_CONTRACT_VERSION)),
        config=dict(config),
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
    validate_signal_matrix(out, n, reference_close=bars.close)
    return out
