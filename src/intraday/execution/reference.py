"""Reference execution path (skeleton).

The reference engine is the canonical PnL truth. Phase 2 implements it.
"""

from __future__ import annotations

from intraday.core.arrays import BarMatrix
from intraday.core.errors import IntradaySystemError
from intraday.execution.intent import TradeIntent
from intraday.execution.records import TradeResult
from intraday.execution.spec import ExecutionSpec


def simulate_trade_path_reference(
    bars: BarMatrix,
    intent: TradeIntent,
    spec: ExecutionSpec,
    management_plan: object | None = None,
) -> TradeResult:
    """Simulate one TradeIntent under reference semantics. NOT YET IMPLEMENTED (Phase 2)."""
    raise IntradaySystemError(
        "simulate_trade_path_reference is not implemented yet (Phase 2)."
    )
