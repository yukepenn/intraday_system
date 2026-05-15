"""Tests for TradeResult-only backtest metrics."""

from __future__ import annotations

import math

import pytest
from intraday.backtest.metrics import summarize_trade_results
from intraday.core.types import ExitReason, RejectReason, Side
from intraday.execution.records import TradeResult


def _acc(**kwargs: object) -> TradeResult:
    base = dict(
        candidate_id=1,
        signal_bar=0,
        entry_bar=1,
        exit_bar=2,
        side=int(Side.LONG),
        qty=1.0,
        entry_price=100.0,
        stop_price=99.0,
        target_price=101.0,
        exit_price=100.5,
        gross_pnl=0.5,
        net_pnl=0.5,
        r_multiple=0.5,
        exit_reason=int(ExitReason.TARGET),
        bars_held=2,
    )
    base.update(kwargs)
    return TradeResult.accepted_trade(**base)


def test_no_results() -> None:
    m = summarize_trade_results(())
    assert m.total_results == 0
    assert m.accepted_trades == 0
    assert m.rejected_trades == 0
    assert m.total_r == 0.0
    assert m.profit_factor_r == 0.0


def test_only_rejected() -> None:
    r = TradeResult.rejected(
        reject_reason=int(RejectReason.INVALID_STOP),
        candidate_id=1,
        signal_bar=3,
        side=int(Side.LONG),
        qty=1.0,
    )
    m = summarize_trade_results([r])
    assert m.rejected_trades == 1
    assert m.accepted_trades == 0
    assert "INVALID_STOP" in m.reject_reason_counts


def test_all_winners_profit_factor_inf() -> None:
    m = summarize_trade_results([_acc(r_multiple=1.0), _acc(r_multiple=0.5, signal_bar=1)])
    assert m.profit_factor_r == math.inf
    assert m.win_rate == 1.0


def test_mixed_profit_factor() -> None:
    m = summarize_trade_results([_acc(r_multiple=2.0), _acc(r_multiple=-1.0, signal_bar=1)])
    assert m.profit_factor_r == pytest.approx(2.0)
    assert m.win_rate == pytest.approx(0.5)


def test_max_drawdown_known_sequence() -> None:
    m = summarize_trade_results(
        [
            _acc(r_multiple=1.0, signal_bar=0),
            _acc(r_multiple=-2.0, signal_bar=1),
            _acc(r_multiple=1.0, signal_bar=2),
        ]
    )
    # cum: 1, -1, 0 → peak 1, max drop from peak 1 to -1 = 2
    assert m.max_drawdown_r == pytest.approx(2.0)


def test_exit_and_reject_distribution_keys_use_enum_names() -> None:
    m = summarize_trade_results(
        [
            _acc(exit_reason=int(ExitReason.STOP)),
            TradeResult.rejected(
                reject_reason=int(RejectReason.NO_NEXT_BAR),
                candidate_id=1,
                signal_bar=9,
            ),
        ]
    )
    assert m.exit_reason_counts.get("STOP", 0) == 1
    assert m.reject_reason_counts.get("NO_NEXT_BAR", 0) == 1


def test_metrics_use_trade_result_fields_only() -> None:
    """Sanity: summarize_trade_results has no bar-matrix parameters (API shape)."""
    import inspect

    sig = inspect.signature(summarize_trade_results)
    assert len(sig.parameters) == 1
