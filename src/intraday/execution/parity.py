"""Parity helpers between reference and fast execution paths."""

from __future__ import annotations

import math
from typing import Any

from intraday.execution.records import TradeResult

_FLOAT_FIELDS = (
    "qty",
    "entry_price",
    "stop_price",
    "target_price",
    "exit_price",
    "gross_pnl",
    "net_pnl",
    "r_multiple",
)


def _float_close(a: Any, b: Any, *, atol: float) -> bool:
    af = float(a)
    bf = float(b)
    if math.isnan(af) and math.isnan(bf):
        return True
    return math.isclose(af, bf, rel_tol=0.0, abs_tol=atol)


def compare_trade_results(
    reference: TradeResult,
    fast: TradeResult,
    *,
    atol: float = 1e-10,
) -> list[str]:
    """Return a list of human-readable mismatch strings (empty if equal)."""
    errors: list[str] = []

    def check(name: str, a: Any, b: Any) -> None:
        if a != b:
            errors.append(f"{name}: reference={a!r} fast={b!r}")

    check("accepted", reference.accepted, fast.accepted)
    check("reject_reason", reference.reject_reason, fast.reject_reason)
    check("candidate_id", reference.candidate_id, fast.candidate_id)
    check("signal_bar", reference.signal_bar, fast.signal_bar)
    check("entry_bar", reference.entry_bar, fast.entry_bar)
    check("exit_bar", reference.exit_bar, fast.exit_bar)
    check("side", reference.side, fast.side)
    check("exit_reason", reference.exit_reason, fast.exit_reason)
    check("bars_held", reference.bars_held, fast.bars_held)

    for name in _FLOAT_FIELDS:
        av = getattr(reference, name)
        bv = getattr(fast, name)
        if not _float_close(av, bv, atol=atol):
            errors.append(f"{name}: reference={av!r} fast={bv!r}")

    return errors


def assert_trade_results_equal(
    reference: TradeResult,
    fast: TradeResult,
    *,
    atol: float = 1e-10,
) -> None:
    """Raise ``AssertionError`` with field-level detail if results differ."""
    mismatches = compare_trade_results(reference, fast, atol=atol)
    if mismatches:
        detail = "\n".join(mismatches)
        raise AssertionError(f"TradeResult parity mismatch:\n{detail}")
