"""materialize_trade semantics."""

from __future__ import annotations

from pathlib import Path

import pytest
from intraday.core.config import load_yaml
from intraday.core.types import RejectReason, Side
from intraday.execution.materialize import materialize_trade
from intraday.execution.records import TradeResult
from intraday.execution.spec import ExecutionSpec

from tests.helpers.bars import make_bar_matrix

REPO = Path(__file__).resolve().parents[2]
EXEC_YAML = REPO / "configs" / "execution" / "intraday_default.yaml"


def _spec(**overrides: object) -> ExecutionSpec:
    d = load_yaml(EXEC_YAML)
    d.update(overrides)
    return ExecutionSpec.from_config(d)


def test_long_materialization_entry_slippage() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [101.0, 101.0],
        [99.5, 99.5],
        [100.5, 100.5],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.05, min_risk_per_share=0.01)
    from intraday.execution.intent import TradeIntent

    it = TradeIntent(
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
    m = materialize_trade(bars, it, spec)
    assert not isinstance(m, TradeResult)
    assert m.entry_price == pytest.approx(100.05)
    assert m.stop_price == pytest.approx(99.0)
    assert m.target_price == pytest.approx(100.05 + 1.0 * (100.05 - 99.0))


def test_short_allowed() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [101.0, 101.0],
        [99.0, 99.0],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(allow_short=True, slippage_per_share=0.0, min_risk_per_share=0.01)
    from intraday.execution.intent import TradeIntent

    it = TradeIntent(
        candidate_id=1,
        signal_bar=0,
        side=int(Side.SHORT),
        qty=1.0,
        raw_stop_price=102.0,
        target_r=1.0,
        max_hold_bars=0,
        score=0.0,
        setup_code=0,
    )
    m = materialize_trade(bars, it, spec)
    assert not isinstance(m, TradeResult)
    assert m.entry_price == pytest.approx(100.0)
    assert m.risk_per_share == pytest.approx(2.0)


def test_short_not_allowed_rejects() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [101.0, 101.0],
        [99.0, 99.0],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(allow_short=False)
    from intraday.execution.intent import TradeIntent

    it = TradeIntent(
        candidate_id=1,
        signal_bar=0,
        side=int(Side.SHORT),
        qty=1.0,
        raw_stop_price=102.0,
        target_r=1.0,
        max_hold_bars=0,
        score=0.0,
        setup_code=0,
    )
    r = materialize_trade(bars, it, spec)
    assert isinstance(r, TradeResult)
    assert r.reject_reason == int(RejectReason.SHORT_NOT_ALLOWED)


def test_no_next_bar() -> None:
    bars = make_bar_matrix([100.0], [100.0], [100.0], [100.0], minute=[389])
    spec = _spec()
    from intraday.execution.intent import TradeIntent

    it = TradeIntent(
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
    r = materialize_trade(bars, it, spec)
    assert isinstance(r, TradeResult)
    assert r.reject_reason == int(RejectReason.NO_NEXT_BAR)


def test_cross_session_entry() -> None:
    bars = make_bar_matrix(
        [100.0, 101.0],
        [101.0, 102.0],
        [99.0, 100.0],
        [100.0, 101.0],
        minute=[0, 0],
        session_id=[0, 1],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    from intraday.execution.intent import TradeIntent

    it = TradeIntent(
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
    r = materialize_trade(bars, it, spec)
    assert isinstance(r, TradeResult)
    assert r.reject_reason == int(RejectReason.CROSS_SESSION_ENTRY)


def test_outside_trading_window_entry_minute() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [101.0, 101.0],
        [99.0, 99.0],
        [100.0, 100.0],
        minute=[0, 390],
        session_id=[0, 0],
    )
    spec = _spec(eod_exit_minute=389, slippage_per_share=0.0, min_risk_per_share=0.01)
    from intraday.execution.intent import TradeIntent

    it = TradeIntent(
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
    r = materialize_trade(bars, it, spec)
    assert isinstance(r, TradeResult)
    assert r.reject_reason == int(RejectReason.OUTSIDE_TRADING_WINDOW)


def test_invalid_stop_long() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [101.0, 101.0],
        [99.0, 99.0],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    from intraday.execution.intent import TradeIntent

    it = TradeIntent(
        candidate_id=1,
        signal_bar=0,
        side=int(Side.LONG),
        qty=1.0,
        raw_stop_price=101.0,
        target_r=1.0,
        max_hold_bars=0,
        score=0.0,
        setup_code=0,
    )
    r = materialize_trade(bars, it, spec)
    assert isinstance(r, TradeResult)
    assert r.reject_reason == int(RejectReason.INVALID_STOP)


def test_risk_too_small() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [101.0, 101.0],
        [99.9, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.5)
    from intraday.execution.intent import TradeIntent

    it = TradeIntent(
        candidate_id=1,
        signal_bar=0,
        side=int(Side.LONG),
        qty=1.0,
        raw_stop_price=99.8,
        target_r=1.0,
        max_hold_bars=0,
        score=0.0,
        setup_code=0,
    )
    r = materialize_trade(bars, it, spec)
    assert isinstance(r, TradeResult)
    assert r.reject_reason == int(RejectReason.RISK_TOO_SMALL)


def test_max_hold_from_intent() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [101.0, 101.0],
        [99.0, 99.0],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    from intraday.execution.intent import TradeIntent

    it = TradeIntent(
        candidate_id=1,
        signal_bar=0,
        side=int(Side.LONG),
        qty=1.0,
        raw_stop_price=99.0,
        target_r=1.0,
        max_hold_bars=7,
        score=0.0,
        setup_code=0,
    )
    m = materialize_trade(bars, it, spec)
    assert not isinstance(m, TradeResult)
    assert m.max_hold_bars == 7


def test_max_hold_from_spec_default() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [101.0, 101.0],
        [99.0, 99.0],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
        max_hold_bars_default=4,
    )
    from intraday.execution.intent import TradeIntent

    it = TradeIntent(
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
    m = materialize_trade(bars, it, spec)
    assert not isinstance(m, TradeResult)
    assert m.max_hold_bars == 4


def test_nan_entry_open_rejects_invalid_market_data() -> None:
    bars = make_bar_matrix(
        [100.0, float("nan")],
        [101.0, 101.0],
        [99.0, 99.0],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    from intraday.execution.intent import TradeIntent

    it = TradeIntent(
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
    r = materialize_trade(bars, it, spec)
    assert isinstance(r, TradeResult)
    assert r.reject_reason == int(RejectReason.INVALID_MARKET_DATA)
