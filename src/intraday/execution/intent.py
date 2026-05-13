"""TradeIntent dataclass."""

from __future__ import annotations

import math
from dataclasses import dataclass

from intraday.core.types import RejectReason, Side


@dataclass(frozen=True)
class TradeIntent:
    """One intent emitted by a strategy. Execution consumes these."""

    candidate_id: int
    signal_bar: int
    side: int  # +1 LONG, -1 SHORT
    qty: float
    raw_stop_price: float
    target_r: float
    max_hold_bars: int
    score: float
    setup_code: int

    def validate_shape(self, *, n_bars: int) -> int | None:
        """Return a ``RejectReason`` code if invalid, else ``None``."""
        if self.signal_bar < 0 or self.signal_bar >= n_bars:
            return int(RejectReason.INVALID_INTENT)
        if self.side not in (int(Side.LONG), int(Side.SHORT)):
            return int(RejectReason.INVALID_INTENT)
        if not math.isfinite(self.qty) or self.qty <= 0.0:
            return int(RejectReason.INVALID_INTENT)
        if not math.isfinite(self.target_r) or self.target_r <= 0.0:
            return int(RejectReason.INVALID_INTENT)
        if not math.isfinite(self.raw_stop_price):
            return int(RejectReason.INVALID_STOP)
        return None
