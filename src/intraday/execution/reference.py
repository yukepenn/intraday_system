"""Reference execution path.

The reference engine is the canonical PnL truth. See docs/EXECUTION_CONTRACT.md.
"""

from __future__ import annotations

import math

from intraday.core.arrays import BarMatrix
from intraday.core.errors import IntradaySystemError
from intraday.core.types import ExitReason, RejectReason, Side
from intraday.execution.cost import (
    apply_exit_slippage,
    compute_gross_pnl,
    compute_net_pnl,
    compute_r_multiple,
)
from intraday.execution.intent import TradeIntent
from intraday.execution.materialize import MaterializedTrade, materialize_trade
from intraday.execution.records import TradeResult
from intraday.execution.spec import ExecutionSpec


def _same_bar_is_stop_first(policy: str) -> bool:
    """``conservative`` is defined as stop-first (same as ``stop_first``)."""
    return policy in ("stop_first", "conservative")


def _reject_invalid_market_data(mt: MaterializedTrade) -> TradeResult:
    return TradeResult.rejected(
        reject_reason=int(RejectReason.INVALID_MARKET_DATA),
        candidate_id=mt.candidate_id,
        signal_bar=mt.signal_bar,
        side=mt.side,
        qty=mt.qty,
    )


def simulate_trade_path_reference(
    bars: BarMatrix,
    intent: TradeIntent,
    spec: ExecutionSpec,
    management_plan: object | None = None,
) -> TradeResult:
    """Simulate one ``TradeIntent`` under reference semantics."""
    if management_plan is not None:
        raise IntradaySystemError(
            "management_plan is not supported in Phase 2 reference execution "
            "(scale-out / trailing / no-followthrough are Layer2 overlays)."
        )

    mat_or_reject = materialize_trade(bars, intent, spec)
    if isinstance(mat_or_reject, TradeResult):
        return mat_or_reject

    mt: MaterializedTrade = mat_or_reject
    entry_bar = mt.entry_bar
    entry_session = int(bars.session_id[entry_bar])
    side = mt.side
    stop_price = mt.stop_price
    target_price = mt.target_price
    entry_price = mt.entry_price
    qty = mt.qty
    risk_per_share = mt.risk_per_share
    max_hold = mt.max_hold_bars

    policy = spec.same_bar_policy
    slip = spec.slippage_per_share
    commission = spec.commission_per_trade

    def finalize(
        exit_bar: int,
        raw_exit: float,
        exit_reason: int,
    ) -> TradeResult:
        if not math.isfinite(raw_exit):
            return _reject_invalid_market_data(mt)
        exit_fill = apply_exit_slippage(raw_exit, side, slip)
        gross = compute_gross_pnl(side, entry_price, exit_fill, qty)
        net = compute_net_pnl(gross, commission)
        rmul = compute_r_multiple(net, risk_per_share, qty)
        bars_held = exit_bar - entry_bar + 1
        return TradeResult.accepted_trade(
            candidate_id=mt.candidate_id,
            signal_bar=mt.signal_bar,
            entry_bar=entry_bar,
            exit_bar=exit_bar,
            side=side,
            qty=qty,
            entry_price=entry_price,
            stop_price=stop_price,
            target_price=target_price,
            exit_price=exit_fill,
            gross_pnl=gross,
            net_pnl=net,
            r_multiple=rmul,
            exit_reason=exit_reason,
            bars_held=bars_held,
        )

    i = entry_bar
    n = bars.n_bars
    while i < n:
        if int(bars.session_id[i]) != entry_session:
            prev = i - 1
            raw = float(bars.close[prev])
            return finalize(prev, raw, int(ExitReason.EOD))

        hi = float(bars.high[i])
        lo = float(bars.low[i])
        if not (math.isfinite(hi) and math.isfinite(lo)):
            return _reject_invalid_market_data(mt)
        minute = int(bars.minute[i])
        bars_held = i - entry_bar + 1

        stop_touch = False
        target_touch = False
        if side == int(Side.LONG):
            stop_touch = lo <= stop_price
            target_touch = hi >= target_price
        else:
            stop_touch = hi >= stop_price
            target_touch = lo <= target_price

        if stop_touch and target_touch:
            if _same_bar_is_stop_first(policy):
                return finalize(i, stop_price, int(ExitReason.STOP))
            return finalize(i, target_price, int(ExitReason.TARGET))
        if stop_touch:
            return finalize(i, stop_price, int(ExitReason.STOP))
        if target_touch:
            return finalize(i, target_price, int(ExitReason.TARGET))

        if minute >= spec.eod_exit_minute:
            raw = float(bars.close[i])
            return finalize(i, raw, int(ExitReason.EOD))

        if max_hold is not None and bars_held >= max_hold:
            raw = float(bars.close[i])
            return finalize(i, raw, int(ExitReason.MAX_HOLD))

        i += 1

    last = n - 1
    raw = float(bars.close[last])
    return finalize(last, raw, int(ExitReason.EOD))
