"""Cost (commission + slippage) helpers (skeleton)."""

from __future__ import annotations


def apply_slippage(entry_price: float, side: int, slippage_per_share: float) -> float:
    """Apply per-share slippage in the adverse direction.

    Reference truth: entry pays slippage. Phase 2 will integrate with reference engine.
    """
    if side > 0:
        return entry_price + slippage_per_share
    if side < 0:
        return entry_price - slippage_per_share
    return entry_price


def apply_commission(gross_pnl: float, commission_per_trade: float) -> float:
    """Subtract a fixed commission per trade from gross PnL."""
    return gross_pnl - commission_per_trade
