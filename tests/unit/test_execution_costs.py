"""Execution cost and PnL helpers."""

from __future__ import annotations

import pytest
from intraday.core.types import Side
from intraday.execution.cost import (
    apply_commission,
    apply_entry_slippage,
    apply_exit_slippage,
    apply_slippage,
    compute_gross_pnl,
    compute_net_pnl,
    compute_r_multiple,
)


def test_entry_slippage_long_short() -> None:
    assert apply_entry_slippage(100.0, int(Side.LONG), 0.01) == pytest.approx(100.01)
    assert apply_entry_slippage(100.0, int(Side.SHORT), 0.01) == pytest.approx(99.99)


def test_exit_slippage_long_short() -> None:
    assert apply_exit_slippage(100.0, int(Side.LONG), 0.01) == pytest.approx(99.99)
    assert apply_exit_slippage(100.0, int(Side.SHORT), 0.01) == pytest.approx(100.01)


def test_apply_slippage_alias_matches_entry() -> None:
    p, s, slip = 50.0, int(Side.LONG), 0.02
    assert apply_slippage(p, s, slip) == apply_entry_slippage(p, s, slip)


def test_compute_gross_pnl() -> None:
    assert compute_gross_pnl(int(Side.LONG), 100.0, 102.0, 3.0) == pytest.approx(6.0)
    assert compute_gross_pnl(int(Side.SHORT), 100.0, 98.0, 2.0) == pytest.approx(4.0)


def test_compute_net_pnl_and_commission_alias() -> None:
    assert compute_net_pnl(10.0, 2.5) == pytest.approx(7.5)
    assert apply_commission(10.0, 2.5) == pytest.approx(7.5)


def test_compute_r_multiple() -> None:
    assert compute_r_multiple(2.0, 0.5, 4.0) == pytest.approx(1.0)


def test_compute_r_multiple_zero_risk_raises() -> None:
    with pytest.raises(ValueError, match="risk_dollars"):
        compute_r_multiple(1.0, 0.0, 1.0)


def test_side_zero_entry_slippage_raises() -> None:
    with pytest.raises(ValueError):
        apply_entry_slippage(1.0, 0, 0.01)
