"""Cost (commission + slippage) helpers."""

from __future__ import annotations


def apply_entry_slippage(price: float, side: int, slippage_per_share: float) -> float:
    """Apply per-share slippage in the adverse direction at entry."""
    if side > 0:
        return price + slippage_per_share
    if side < 0:
        return price - slippage_per_share
    raise ValueError(f"entry slippage requires non-zero side, got {side}")


def apply_exit_slippage(price: float, side: int, slippage_per_share: float) -> float:
    """Apply per-share slippage in the adverse direction at exit."""
    if side > 0:
        return price - slippage_per_share
    if side < 0:
        return price + slippage_per_share
    raise ValueError(f"exit slippage requires non-zero side, got {side}")


def apply_slippage(entry_price: float, side: int, slippage_per_share: float) -> float:
    """Deprecated name for :func:`apply_entry_slippage` (backward compatible)."""
    return apply_entry_slippage(entry_price, side, slippage_per_share)


def compute_gross_pnl(side: int, entry_price: float, exit_price: float, qty: float) -> float:
    """``side * (exit - entry) * qty`` with ``side`` in ``{+1, -1}``."""
    return float(side) * (float(exit_price) - float(entry_price)) * float(qty)


def compute_net_pnl(gross_pnl: float, commission_per_trade: float) -> float:
    """Subtract fixed commission for one completed round-trip."""
    return float(gross_pnl) - float(commission_per_trade)


def compute_r_multiple(net_pnl: float, risk_per_share: float, qty: float) -> float:
    """Net PnL divided by risk dollars ``risk_per_share * qty``."""
    risk_dollars = float(risk_per_share) * float(qty)
    if risk_dollars <= 0.0:
        raise ValueError("risk_dollars must be positive for R-multiple")
    return float(net_pnl) / risk_dollars


def apply_commission(gross_pnl: float, commission_per_trade: float) -> float:
    """Subtract a fixed commission per trade from gross PnL (alias of ``compute_net_pnl``)."""
    return compute_net_pnl(gross_pnl, commission_per_trade)
