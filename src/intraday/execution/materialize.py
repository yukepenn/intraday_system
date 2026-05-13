"""Materialize executable levels from TradeIntent + BarMatrix + ExecutionSpec."""

from __future__ import annotations

from dataclasses import dataclass

from intraday.core.arrays import BarMatrix
from intraday.core.types import RejectReason, Side
from intraday.execution.cost import apply_entry_slippage
from intraday.execution.intent import TradeIntent
from intraday.execution.records import TradeResult
from intraday.execution.spec import ExecutionSpec


@dataclass(frozen=True)
class MaterializedTrade:
    """Post-entry deterministic levels for the reference simulator."""

    candidate_id: int
    signal_bar: int
    entry_bar: int
    side: int
    qty: float
    entry_price: float
    stop_price: float
    target_price: float
    risk_per_share: float
    max_hold_bars: int | None


def _max_hold_effective(intent: TradeIntent, spec: ExecutionSpec) -> int | None:
    if intent.max_hold_bars > 0:
        return int(intent.max_hold_bars)
    if spec.max_hold_bars_default is not None:
        return int(spec.max_hold_bars_default)
    return None


def materialize_trade(
    bars: BarMatrix,
    intent: TradeIntent,
    spec: ExecutionSpec,
) -> MaterializedTrade | TradeResult:
    """Next-open materialization or a rejected :class:`TradeResult`."""
    bad = intent.validate_shape(n_bars=bars.n_bars)
    if bad is not None:
        return TradeResult.rejected(
            reject_reason=bad,
            candidate_id=intent.candidate_id,
            signal_bar=intent.signal_bar,
            side=intent.side,
            qty=intent.qty,
        )

    entry_bar = intent.signal_bar + 1
    if entry_bar >= bars.n_bars:
        return TradeResult.rejected(
            reject_reason=int(RejectReason.NO_NEXT_BAR),
            candidate_id=intent.candidate_id,
            signal_bar=intent.signal_bar,
            side=intent.side,
            qty=intent.qty,
        )

    if int(bars.session_id[entry_bar]) != int(bars.session_id[intent.signal_bar]):
        return TradeResult.rejected(
            reject_reason=int(RejectReason.CROSS_SESSION_ENTRY),
            candidate_id=intent.candidate_id,
            signal_bar=intent.signal_bar,
            side=intent.side,
            qty=intent.qty,
        )

    entry_minute = int(bars.minute[entry_bar])
    if entry_minute > spec.eod_exit_minute:
        return TradeResult.rejected(
            reject_reason=int(RejectReason.OUTSIDE_TRADING_WINDOW),
            candidate_id=intent.candidate_id,
            signal_bar=intent.signal_bar,
            side=intent.side,
            qty=intent.qty,
        )

    side = int(intent.side)
    if side == int(Side.SHORT) and not spec.allow_short:
        return TradeResult.rejected(
            reject_reason=int(RejectReason.SHORT_NOT_ALLOWED),
            candidate_id=intent.candidate_id,
            signal_bar=intent.signal_bar,
            side=side,
            qty=intent.qty,
        )

    raw_open = float(bars.open[entry_bar])
    entry_price = apply_entry_slippage(raw_open, side, spec.slippage_per_share)
    stop_price = float(intent.raw_stop_price)

    if side == int(Side.LONG):
        if stop_price >= entry_price:
            return TradeResult.rejected(
                reject_reason=int(RejectReason.INVALID_STOP),
                candidate_id=intent.candidate_id,
                signal_bar=intent.signal_bar,
                side=side,
                qty=intent.qty,
            )
        risk_per_share = entry_price - stop_price
    else:
        if stop_price <= entry_price:
            return TradeResult.rejected(
                reject_reason=int(RejectReason.INVALID_STOP),
                candidate_id=intent.candidate_id,
                signal_bar=intent.signal_bar,
                side=side,
                qty=intent.qty,
            )
        risk_per_share = stop_price - entry_price

    if risk_per_share <= 0.0:
        return TradeResult.rejected(
            reject_reason=int(RejectReason.INVALID_STOP),
            candidate_id=intent.candidate_id,
            signal_bar=intent.signal_bar,
            side=side,
            qty=intent.qty,
        )

    if risk_per_share < spec.min_risk_per_share:
        return TradeResult.rejected(
            reject_reason=int(RejectReason.RISK_TOO_SMALL),
            candidate_id=intent.candidate_id,
            signal_bar=intent.signal_bar,
            side=side,
            qty=intent.qty,
        )

    tr = float(intent.target_r)
    if side == int(Side.LONG):
        target_price = entry_price + tr * risk_per_share
    else:
        target_price = entry_price - tr * risk_per_share

    return MaterializedTrade(
        candidate_id=intent.candidate_id,
        signal_bar=intent.signal_bar,
        entry_bar=entry_bar,
        side=side,
        qty=float(intent.qty),
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        risk_per_share=risk_per_share,
        max_hold_bars=_max_hold_effective(intent, spec),
    )
