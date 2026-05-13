"""TradeResult dataclass."""

from __future__ import annotations

import math
from dataclasses import dataclass

from intraday.core.types import ExitReason, RejectReason, Side


@dataclass(frozen=True)
class TradeResult:
    """Per-trade result returned by the execution engine."""

    accepted: bool
    reject_reason: int
    candidate_id: int
    signal_bar: int
    entry_bar: int
    exit_bar: int
    side: int
    qty: float
    entry_price: float
    stop_price: float
    target_price: float
    exit_price: float
    gross_pnl: float
    net_pnl: float
    r_multiple: float
    exit_reason: int
    bars_held: int

    @classmethod
    def rejected(
        cls,
        *,
        reject_reason: int,
        candidate_id: int,
        signal_bar: int,
        side: int = int(Side.FLAT),
        qty: float = 0.0,
    ) -> TradeResult:
        """Rejected intent: prices are NaN; PnL and R are zero; ``ExitReason.REJECTED``."""
        nan = float("nan")
        return cls(
            accepted=False,
            reject_reason=int(reject_reason),
            candidate_id=candidate_id,
            signal_bar=signal_bar,
            entry_bar=-1,
            exit_bar=-1,
            side=int(side),
            qty=float(qty),
            entry_price=nan,
            stop_price=nan,
            target_price=nan,
            exit_price=nan,
            gross_pnl=0.0,
            net_pnl=0.0,
            r_multiple=0.0,
            exit_reason=int(ExitReason.REJECTED),
            bars_held=0,
        )

    @classmethod
    def accepted_trade(
        cls,
        *,
        candidate_id: int,
        signal_bar: int,
        entry_bar: int,
        exit_bar: int,
        side: int,
        qty: float,
        entry_price: float,
        stop_price: float,
        target_price: float,
        exit_price: float,
        gross_pnl: float,
        net_pnl: float,
        r_multiple: float,
        exit_reason: int,
        bars_held: int,
    ) -> TradeResult:
        return cls(
            accepted=True,
            reject_reason=int(RejectReason.NONE),
            candidate_id=candidate_id,
            signal_bar=signal_bar,
            entry_bar=entry_bar,
            exit_bar=exit_bar,
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

    def price_fields_are_nan(self) -> bool:
        """True if all four price fields are NaN (expected for rejected rows)."""
        for name in ("entry_price", "stop_price", "target_price", "exit_price"):
            v = getattr(self, name)
            if not isinstance(v, float | int):
                return False
            if not math.isnan(float(v)):
                return False
        return True
