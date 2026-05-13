"""TradeIntent / TradeResult contract tests."""

from __future__ import annotations

import math

from intraday.core.types import ExitReason, RejectReason, Side
from intraday.execution.intent import TradeIntent
from intraday.execution.records import TradeResult


def _intent(**kwargs: object) -> TradeIntent:
    base = dict(
        candidate_id=1,
        signal_bar=0,
        side=int(Side.LONG),
        qty=1.0,
        raw_stop_price=99.0,
        target_r=1.0,
        max_hold_bars=0,
        score=0.0,
        setup_code=0,
    )
    base.update(kwargs)
    return TradeIntent(**base)  # type: ignore[arg-type]


def test_trade_intent_basic() -> None:
    it = _intent()
    assert it.candidate_id == 1
    assert it.signal_bar == 0


def test_trade_intent_validate_shape_ok() -> None:
    it = _intent(signal_bar=5)
    assert it.validate_shape(n_bars=10) is None


def test_trade_intent_validate_shape_oob() -> None:
    it = _intent(signal_bar=10)
    assert it.validate_shape(n_bars=10) == int(RejectReason.INVALID_INTENT)


def test_trade_intent_nonfinite_qty() -> None:
    it = _intent(qty=float("nan"))
    assert it.validate_shape(n_bars=10) == int(RejectReason.INVALID_INTENT)
    it2 = _intent(qty=float("inf"))
    assert it2.validate_shape(n_bars=10) == int(RejectReason.INVALID_INTENT)


def test_trade_intent_nonfinite_target_r() -> None:
    it = _intent(target_r=float("nan"))
    assert it.validate_shape(n_bars=10) == int(RejectReason.INVALID_INTENT)
    it2 = _intent(target_r=float("inf"))
    assert it2.validate_shape(n_bars=10) == int(RejectReason.INVALID_INTENT)


def test_trade_intent_nan_raw_stop() -> None:
    it = _intent(raw_stop_price=float("nan"))
    assert it.validate_shape(n_bars=10) == int(RejectReason.INVALID_STOP)


def test_rejected_trade_result_convention() -> None:
    r = TradeResult.rejected(
        reject_reason=int(RejectReason.NO_NEXT_BAR),
        candidate_id=7,
        signal_bar=3,
        side=int(Side.LONG),
        qty=2.0,
    )
    assert r.accepted is False
    assert r.reject_reason == int(RejectReason.NO_NEXT_BAR)
    assert r.exit_reason == int(ExitReason.REJECTED)
    assert r.entry_bar == -1
    assert r.exit_bar == -1
    assert r.bars_held == 0
    assert r.gross_pnl == 0.0
    assert r.net_pnl == 0.0
    assert r.r_multiple == 0.0
    assert math.isnan(r.entry_price)
    assert r.price_fields_are_nan() is True


def test_accepted_trade_result_not_nan() -> None:
    r = TradeResult.accepted_trade(
        candidate_id=1,
        signal_bar=0,
        entry_bar=1,
        exit_bar=2,
        side=int(Side.LONG),
        qty=1.0,
        entry_price=100.0,
        stop_price=99.0,
        target_price=101.0,
        exit_price=101.0,
        gross_pnl=1.0,
        net_pnl=1.0,
        r_multiple=1.0,
        exit_reason=int(ExitReason.TARGET),
        bars_held=2,
    )
    assert r.accepted is True
    assert r.reject_reason == int(RejectReason.NONE)
    assert r.price_fields_are_nan() is False
