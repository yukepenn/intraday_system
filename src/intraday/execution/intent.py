"""TradeIntent dataclass."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TradeIntent:
    """One intent emitted by a strategy. Execution consumes these."""

    candidate_id: int
    signal_bar: int
    side: int                # +1 LONG, -1 SHORT
    qty: float
    raw_stop_price: float
    target_r: float
    max_hold_bars: int
    score: float
    setup_code: int
