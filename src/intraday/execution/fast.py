"""Fast (Numba-accelerated) execution path.

Parity-tested against :func:`simulate_trade_path_reference`. Materialization stays
in Python (:func:`materialize_trade`) so entry/stop/target semantics remain
identical to the reference path; the Numba kernel mirrors only the post-entry
scan loop.
"""

from __future__ import annotations

import numpy as np
from numba import njit

from intraday.core.arrays import BarMatrix
from intraday.core.errors import IntradaySystemError
from intraday.core.types import ExitReason, RejectReason
from intraday.execution.intent import TradeIntent
from intraday.execution.materialize import MaterializedTrade, materialize_trade
from intraday.execution.records import TradeResult
from intraday.execution.spec import ExecutionSpec

# Same-bar policy codes passed to the kernel (stable contract).
SAME_BAR_STOP_FIRST = 0
SAME_BAR_TARGET_FIRST = 1
SAME_BAR_CONSERVATIVE = 2

# Kernel exit codes (match ExitReason ints used in reference path).
_EXIT_STOP = int(ExitReason.STOP)
_EXIT_TARGET = int(ExitReason.TARGET)
_EXIT_EOD = int(ExitReason.EOD)
_EXIT_MAX_HOLD = int(ExitReason.MAX_HOLD)
_EXIT_REJECTED = int(ExitReason.REJECTED)

_REJECT_MARKET = int(RejectReason.INVALID_MARKET_DATA)


def _same_bar_policy_code(spec: ExecutionSpec) -> int:
    p = spec.same_bar_policy
    if p == "target_first":
        return SAME_BAR_TARGET_FIRST
    if p == "conservative":
        return SAME_BAR_CONSERVATIVE
    return SAME_BAR_STOP_FIRST


@njit(cache=True)
def _simulate_trade_path_fast_kernel(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    session_id: np.ndarray,
    minute: np.ndarray,
    candidate_id: int,
    signal_bar: int,
    entry_bar: int,
    entry_session: int,
    side: int,
    qty: float,
    entry_price: float,
    stop_price: float,
    target_price: float,
    risk_per_share: float,
    max_hold_bars: int,
    same_bar_policy_code: int,
    slippage_per_share: float,
    commission_per_trade: float,
    eod_exit_minute: int,
    n_bars: int,
) -> tuple[
    int,
    int,
    int,
    int,
    int,
    int,
    int,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    int,
    int,
]:
    """Return flat fields: ``(accepted, reject_reason, candidate_id, signal_bar,
    entry_bar, exit_bar, side, qty, entry_price, stop_price, target_price,
    exit_price, gross_pnl, net_pnl, r_multiple, exit_reason, bars_held)``.

    If ``accepted == 0``, only ``reject_reason`` and identity fields are valid;
    the caller maps that to :meth:`TradeResult.rejected`.
    """
    slip = slippage_per_share
    commission = commission_per_trade

    i = entry_bar
    while i < n_bars:
        if int(session_id[i]) != entry_session:
            prev = i - 1
            raw = float(close[prev])
            if not np.isfinite(raw):
                return (
                    0,
                    _REJECT_MARKET,
                    candidate_id,
                    signal_bar,
                    -1,
                    -1,
                    side,
                    qty,
                    entry_price,
                    stop_price,
                    target_price,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    _EXIT_REJECTED,
                    0,
                )
            if side > 0:
                exit_fill = raw - slip
            else:
                exit_fill = raw + slip
            gross = side * (exit_fill - entry_price) * qty
            net = gross - commission
            rmul = net / (risk_per_share * qty)
            bars_held = prev - entry_bar + 1
            return (
                1,
                0,
                candidate_id,
                signal_bar,
                entry_bar,
                prev,
                side,
                qty,
                entry_price,
                stop_price,
                target_price,
                exit_fill,
                gross,
                net,
                rmul,
                _EXIT_EOD,
                bars_held,
            )

        hi = float(high[i])
        lo = float(low[i])
        if not (np.isfinite(hi) and np.isfinite(lo)):
            return (
                0,
                _REJECT_MARKET,
                candidate_id,
                signal_bar,
                -1,
                -1,
                side,
                qty,
                entry_price,
                stop_price,
                target_price,
                0.0,
                0.0,
                0.0,
                0.0,
                _EXIT_REJECTED,
                0,
            )

        m = int(minute[i])
        bars_held = i - entry_bar + 1

        stop_touch = False
        target_touch = False
        if side == 1:
            stop_touch = lo <= stop_price
            target_touch = hi >= target_price
        else:
            stop_touch = hi >= stop_price
            target_touch = lo <= target_price

        if stop_touch and target_touch:
            raw_exit = stop_price
            exit_reason = _EXIT_STOP
            if same_bar_policy_code == SAME_BAR_TARGET_FIRST:
                raw_exit = target_price
                exit_reason = _EXIT_TARGET
            if side > 0:
                exit_fill = raw_exit - slip
            else:
                exit_fill = raw_exit + slip
            gross = side * (exit_fill - entry_price) * qty
            net = gross - commission
            rmul = net / (risk_per_share * qty)
            bh = i - entry_bar + 1
            return (
                1,
                0,
                candidate_id,
                signal_bar,
                entry_bar,
                i,
                side,
                qty,
                entry_price,
                stop_price,
                target_price,
                exit_fill,
                gross,
                net,
                rmul,
                exit_reason,
                bh,
            )
        if stop_touch:
            raw_exit = stop_price
            if side > 0:
                exit_fill = raw_exit - slip
            else:
                exit_fill = raw_exit + slip
            gross = side * (exit_fill - entry_price) * qty
            net = gross - commission
            rmul = net / (risk_per_share * qty)
            bh = i - entry_bar + 1
            return (
                1,
                0,
                candidate_id,
                signal_bar,
                entry_bar,
                i,
                side,
                qty,
                entry_price,
                stop_price,
                target_price,
                exit_fill,
                gross,
                net,
                rmul,
                _EXIT_STOP,
                bh,
            )
        if target_touch:
            raw_exit = target_price
            if side > 0:
                exit_fill = raw_exit - slip
            else:
                exit_fill = raw_exit + slip
            gross = side * (exit_fill - entry_price) * qty
            net = gross - commission
            rmul = net / (risk_per_share * qty)
            bh = i - entry_bar + 1
            return (
                1,
                0,
                candidate_id,
                signal_bar,
                entry_bar,
                i,
                side,
                qty,
                entry_price,
                stop_price,
                target_price,
                exit_fill,
                gross,
                net,
                rmul,
                _EXIT_TARGET,
                bh,
            )

        if m >= eod_exit_minute:
            raw = float(close[i])
            if not np.isfinite(raw):
                return (
                    0,
                    _REJECT_MARKET,
                    candidate_id,
                    signal_bar,
                    -1,
                    -1,
                    side,
                    qty,
                    entry_price,
                    stop_price,
                    target_price,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    _EXIT_REJECTED,
                    0,
                )
            if side > 0:
                exit_fill = raw - slip
            else:
                exit_fill = raw + slip
            gross = side * (exit_fill - entry_price) * qty
            net = gross - commission
            rmul = net / (risk_per_share * qty)
            bh = i - entry_bar + 1
            return (
                1,
                0,
                candidate_id,
                signal_bar,
                entry_bar,
                i,
                side,
                qty,
                entry_price,
                stop_price,
                target_price,
                exit_fill,
                gross,
                net,
                rmul,
                _EXIT_EOD,
                bh,
            )

        if max_hold_bars > 0 and bars_held >= max_hold_bars:
            raw = float(close[i])
            if not np.isfinite(raw):
                return (
                    0,
                    _REJECT_MARKET,
                    candidate_id,
                    signal_bar,
                    -1,
                    -1,
                    side,
                    qty,
                    entry_price,
                    stop_price,
                    target_price,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    _EXIT_REJECTED,
                    0,
                )
            if side > 0:
                exit_fill = raw - slip
            else:
                exit_fill = raw + slip
            gross = side * (exit_fill - entry_price) * qty
            net = gross - commission
            rmul = net / (risk_per_share * qty)
            bh = i - entry_bar + 1
            return (
                1,
                0,
                candidate_id,
                signal_bar,
                entry_bar,
                i,
                side,
                qty,
                entry_price,
                stop_price,
                target_price,
                exit_fill,
                gross,
                net,
                rmul,
                _EXIT_MAX_HOLD,
                bh,
            )

        i += 1

    last = n_bars - 1
    raw = float(close[last])
    if not np.isfinite(raw):
        return (
            0,
            _REJECT_MARKET,
            candidate_id,
            signal_bar,
            -1,
            -1,
            side,
            qty,
            entry_price,
            stop_price,
            target_price,
            0.0,
            0.0,
            0.0,
            0.0,
            _EXIT_REJECTED,
            0,
        )
    if side > 0:
        exit_fill = raw - slip
    else:
        exit_fill = raw + slip
    gross = side * (exit_fill - entry_price) * qty
    net = gross - commission
    rmul = net / (risk_per_share * qty)
    bh = last - entry_bar + 1
    return (
        1,
        0,
        candidate_id,
        signal_bar,
        entry_bar,
        last,
        side,
        qty,
        entry_price,
        stop_price,
        target_price,
        exit_fill,
        gross,
        net,
        rmul,
        _EXIT_EOD,
        bh,
    )


def _kernel_tuple_to_trade_result(
    tup: tuple[int, ...],
    *,
    reject_reason_on_fail: int = _REJECT_MARKET,
) -> TradeResult:
    (
        accepted,
        rej,
        candidate_id,
        signal_bar,
        entry_bar,
        exit_bar,
        side,
        qty,
        entry_price,
        stop_price,
        target_price,
        exit_price,
        gross_pnl,
        net_pnl,
        r_multiple,
        exit_reason,
        bars_held,
    ) = tup
    if accepted == 0:
        return TradeResult.rejected(
            reject_reason=int(rej) if rej else reject_reason_on_fail,
            candidate_id=int(candidate_id),
            signal_bar=int(signal_bar),
            side=int(side),
            qty=float(qty),
        )
    return TradeResult.accepted_trade(
        candidate_id=int(candidate_id),
        signal_bar=int(signal_bar),
        entry_bar=int(entry_bar),
        exit_bar=int(exit_bar),
        side=int(side),
        qty=float(qty),
        entry_price=float(entry_price),
        stop_price=float(stop_price),
        target_price=float(target_price),
        exit_price=float(exit_price),
        gross_pnl=float(gross_pnl),
        net_pnl=float(net_pnl),
        r_multiple=float(r_multiple),
        exit_reason=int(exit_reason),
        bars_held=int(bars_held),
    )


def simulate_trade_path_fast(
    bars: BarMatrix,
    intent: TradeIntent,
    spec: ExecutionSpec,
    management_plan: object | None = None,
) -> TradeResult:
    """Simulate one ``TradeIntent`` using the fast kernel (parity vs reference)."""
    if management_plan is not None:
        raise IntradaySystemError(
            "management_plan is not supported in Phase 2 reference execution "
            "(scale-out / trailing / no-followthrough are Layer2 overlays)."
        )

    mat_or_reject = materialize_trade(bars, intent, spec)
    if isinstance(mat_or_reject, TradeResult):
        return mat_or_reject

    mt: MaterializedTrade = mat_or_reject
    entry_bar = mt.entry_bar
    entry_session = int(bars.session_id[entry_bar])
    max_hold = mt.max_hold_bars
    max_hold_k = -1 if max_hold is None else int(max_hold)

    tup = _simulate_trade_path_fast_kernel(
        bars.high.astype(np.float64, copy=False),
        bars.low.astype(np.float64, copy=False),
        bars.close.astype(np.float64, copy=False),
        bars.session_id.astype(np.int32, copy=False),
        bars.minute.astype(np.int16, copy=False),
        int(mt.candidate_id),
        int(mt.signal_bar),
        int(entry_bar),
        int(entry_session),
        int(mt.side),
        float(mt.qty),
        float(mt.entry_price),
        float(mt.stop_price),
        float(mt.target_price),
        float(mt.risk_per_share),
        int(max_hold_k),
        int(_same_bar_policy_code(spec)),
        float(spec.slippage_per_share),
        float(spec.commission_per_trade),
        int(spec.eod_exit_minute),
        int(bars.n_bars),
    )
    return _kernel_tuple_to_trade_result(tup)


def simulate_trade_paths_fast(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    session_id: np.ndarray,
    minute: np.ndarray,
    intents: np.ndarray,
    spec_array: np.ndarray,
    management_array: np.ndarray | None = None,
) -> np.ndarray:
    """Batch-simulate intents using packed NumPy arrays. NOT YET IMPLEMENTED (Phase 3+).

    Output: structured array with shape (N_intents,) matching TradeResult fields.
    """
    raise IntradaySystemError(
        "simulate_trade_paths_fast is not implemented yet (Phase 3). "
        "Must parity-match simulate_trade_path_reference once implemented."
    )
