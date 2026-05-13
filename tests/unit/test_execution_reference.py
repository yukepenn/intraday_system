"""simulate_trade_path_reference coverage."""

from __future__ import annotations

from pathlib import Path

import pytest
from intraday.core.config import load_yaml
from intraday.core.errors import IntradaySystemError
from intraday.core.types import ExitReason, RejectReason, Side
from intraday.execution.intent import TradeIntent
from intraday.execution.reference import simulate_trade_path_reference
from intraday.execution.spec import ExecutionSpec

from tests.helpers.bars import make_bar_matrix

REPO = Path(__file__).resolve().parents[2]
EXEC_YAML = REPO / "configs" / "execution" / "intraday_default.yaml"


def _spec(**overrides: object) -> ExecutionSpec:
    d = load_yaml(EXEC_YAML)
    d.update(overrides)
    return ExecutionSpec.from_config(d)


def _long_intent(
    signal_bar: int = 0,
    *,
    stop: float = 98.0,
    target_r: float = 1.0,
    qty: float = 1.0,
    max_hold_bars: int = 0,
) -> TradeIntent:
    return TradeIntent(
        candidate_id=1,
        signal_bar=signal_bar,
        side=int(Side.LONG),
        qty=qty,
        raw_stop_price=stop,
        target_r=target_r,
        max_hold_bars=max_hold_bars,
        score=0.0,
        setup_code=0,
    )


def test_long_target_hit() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 102.0],
        [100.0, 99.5, 99.5],
        [100.0, 100.0, 101.5],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    it = _long_intent(stop=99.0, target_r=1.0)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.accepted
    assert r.exit_reason == int(ExitReason.TARGET)
    assert r.exit_bar == 2
    assert r.entry_price == pytest.approx(100.0)


def test_long_stop_hit() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 100.5],
        [100.0, 99.5, 97.0],
        [100.0, 100.0, 97.5],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    it = _long_intent(stop=98.0, target_r=5.0)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.accepted
    assert r.exit_reason == int(ExitReason.STOP)


def test_same_bar_stop_first() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 110.0],
        [100.0, 99.5, 94.0],
        [100.0, 100.0, 100.0],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(
        same_bar_policy="stop_first",
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = _long_intent(stop=95.0, target_r=2.0)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.exit_reason == int(ExitReason.STOP)


def test_same_bar_target_first() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 110.0],
        [100.0, 99.5, 94.0],
        [100.0, 100.0, 100.0],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(
        same_bar_policy="target_first",
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = _long_intent(stop=95.0, target_r=2.0)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.exit_reason == int(ExitReason.TARGET)


def test_same_bar_conservative_matches_stop_first() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 110.0],
        [100.0, 99.5, 94.0],
        [100.0, 100.0, 100.0],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(
        same_bar_policy="conservative",
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = _long_intent(stop=95.0, target_r=2.0)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.exit_reason == int(ExitReason.STOP)


def test_eod_exit() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 100.0],
        [100.0, 99.9, 99.9],
        [100.0, 100.0, 101.0],
        minute=[0, 1, 389],
        session_id=[0, 0, 0],
    )
    spec = _spec(
        eod_exit_minute=389,
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = _long_intent(stop=90.0, target_r=10.0)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.exit_reason == int(ExitReason.EOD)
    assert r.exit_bar == 2


def test_max_hold_exit() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0, 100.0],
        [100.0, 100.0, 100.0, 100.0],
        [100.0, 99.9, 99.9, 99.9],
        [100.0, 100.0, 100.0, 100.0],
        minute=[0, 1, 2, 3],
        session_id=[0, 0, 0, 0],
    )
    spec = _spec(
        eod_exit_minute=389,
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = _long_intent(stop=90.0, target_r=10.0, max_hold_bars=2)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.exit_reason == int(ExitReason.MAX_HOLD)
    assert r.exit_bar == 2


def test_eod_priority_over_max_hold_same_bar() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.5],
        minute=[388, 389],
        session_id=[0, 0],
    )
    spec = _spec(
        eod_exit_minute=389,
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = _long_intent(stop=90.0, target_r=10.0, max_hold_bars=1)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.exit_bar == 1
    assert r.exit_reason == int(ExitReason.EOD)


def test_entry_on_eod_minute_exits_eod_without_stop_target() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.2],
        minute=[388, 389],
        session_id=[0, 0],
    )
    spec = _spec(
        eod_exit_minute=389,
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = TradeIntent(
        candidate_id=1,
        signal_bar=0,
        side=int(Side.LONG),
        qty=1.0,
        raw_stop_price=90.0,
        target_r=10.0,
        max_hold_bars=0,
        score=0.0,
        setup_code=0,
    )
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.accepted
    assert r.entry_bar == 1
    assert r.exit_reason == int(ExitReason.EOD)


def test_truncated_session_fallback_eod() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.1],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(
        eod_exit_minute=389,
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = _long_intent(stop=90.0, target_r=10.0)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.exit_reason == int(ExitReason.EOD)
    assert r.exit_bar == 1


def test_management_plan_raises() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    it = _long_intent()
    with pytest.raises(IntradaySystemError, match="management_plan"):
        simulate_trade_path_reference(bars, it, spec, management_plan=object())


def test_commission_slippage_affect_net_and_r() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 102.0],
        [100.0, 99.9, 99.9],
        [100.0, 100.0, 101.0],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(
        slippage_per_share=0.1,
        commission_per_trade=0.5,
        min_risk_per_share=0.01,
    )
    it = _long_intent(stop=99.0, target_r=1.0)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.accepted
    assert r.entry_price == pytest.approx(100.1)
    assert r.exit_reason == int(ExitReason.TARGET)
    assert r.net_pnl == pytest.approx(r.gross_pnl - 0.5)
    risk_dollars = (100.1 - 99.0) * 1.0
    assert r.r_multiple == pytest.approx(r.net_pnl / risk_dollars)


def test_invalid_stop_rejection() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    it = _long_intent(stop=101.0)
    r = simulate_trade_path_reference(bars, it, spec)
    assert not r.accepted
    assert r.reject_reason == int(RejectReason.INVALID_STOP)


def test_short_target_and_stop() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 100.5],
        [100.0, 99.9, 97.0],
        [100.0, 100.0, 97.5],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(allow_short=True, slippage_per_share=0.0, min_risk_per_share=0.01)
    short = TradeIntent(
        candidate_id=2,
        signal_bar=0,
        side=int(Side.SHORT),
        qty=1.0,
        raw_stop_price=102.0,
        target_r=1.0,
        max_hold_bars=0,
        score=0.0,
        setup_code=0,
    )
    rt = simulate_trade_path_reference(bars, short, spec)
    assert rt.accepted
    assert rt.exit_reason == int(ExitReason.TARGET)

    bars2 = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 103.0],
        [100.0, 99.9, 99.0],
        [100.0, 100.0, 102.5],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    rs = simulate_trade_path_reference(bars2, short, spec)
    assert rs.exit_reason == int(ExitReason.STOP)


def test_short_rejected_when_not_allowed() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(allow_short=False, slippage_per_share=0.0, min_risk_per_share=0.01)
    short = TradeIntent(
        candidate_id=2,
        signal_bar=0,
        side=int(Side.SHORT),
        qty=1.0,
        raw_stop_price=102.0,
        target_r=1.0,
        max_hold_bars=0,
        score=0.0,
        setup_code=0,
    )
    r = simulate_trade_path_reference(bars, short, spec)
    assert not r.accepted
    assert r.reject_reason == int(RejectReason.SHORT_NOT_ALLOWED)


def test_min_risk_rejection_end_to_end() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.95],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.5)
    it = _long_intent(stop=99.9)
    r = simulate_trade_path_reference(bars, it, spec)
    assert not r.accepted
    assert r.reject_reason == int(RejectReason.RISK_TOO_SMALL)


def test_cross_session_rejection() -> None:
    bars = make_bar_matrix(
        [100.0, 101.0],
        [100.0, 102.0],
        [100.0, 100.0],
        [100.0, 101.0],
        minute=[0, 0],
        session_id=[0, 1],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    it = _long_intent()
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.reject_reason == int(RejectReason.CROSS_SESSION_ENTRY)


def test_no_next_bar_rejection() -> None:
    bars = make_bar_matrix([100.0], [100.0], [100.0], [100.0], minute=[0])
    spec = _spec()
    it = _long_intent()
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.reject_reason == int(RejectReason.NO_NEXT_BAR)


def test_session_roll_exit_eod_at_prior_close() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 101.0],
        [100.0, 100.0, 102.0],
        [100.0, 99.9, 100.5],
        [100.0, 100.0, 101.0],
        minute=[0, 1, 0],
        session_id=[0, 0, 1],
    )
    spec = _spec(
        eod_exit_minute=389,
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = _long_intent(stop=90.0, target_r=10.0)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.accepted
    assert r.exit_bar == 1
    assert r.exit_reason == int(ExitReason.EOD)
    assert r.exit_price == pytest.approx(100.0)


def test_nan_qty_rejects_end_to_end() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    it = _long_intent()
    it_bad = TradeIntent(
        candidate_id=it.candidate_id,
        signal_bar=it.signal_bar,
        side=it.side,
        qty=float("nan"),
        raw_stop_price=it.raw_stop_price,
        target_r=it.target_r,
        max_hold_bars=it.max_hold_bars,
        score=it.score,
        setup_code=it.setup_code,
    )
    r = simulate_trade_path_reference(bars, it_bad, spec)
    assert not r.accepted
    assert r.reject_reason == int(RejectReason.INVALID_INTENT)


def test_nan_high_during_scan_rejects_market_data() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, float("nan")],
        [100.0, 99.9, 99.9],
        [100.0, 100.0, 100.0],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(
        eod_exit_minute=389,
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = _long_intent(stop=90.0, target_r=10.0)
    r = simulate_trade_path_reference(bars, it, spec)
    assert not r.accepted
    assert r.reject_reason == int(RejectReason.INVALID_MARKET_DATA)
