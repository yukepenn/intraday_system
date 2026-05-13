"""TradeResult dataclass."""

from __future__ import annotations

from dataclasses import dataclass


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
