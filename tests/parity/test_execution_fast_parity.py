"""Reference vs fast execution parity (synthetic BarMatrix only)."""

from __future__ import annotations

from pathlib import Path

import pytest
from intraday.core.config import load_yaml
from intraday.core.errors import IntradaySystemError
from intraday.core.types import Side
from intraday.execution.fast import simulate_trade_path_fast
from intraday.execution.intent import TradeIntent
from intraday.execution.parity import assert_trade_results_equal
from intraday.execution.reference import simulate_trade_path_reference
from intraday.execution.spec import ExecutionSpec

from tests.helpers.bars import make_bar_matrix

REPO = Path(__file__).resolve().parents[2]
EXEC_YAML = REPO / "configs" / "execution" / "intraday_default.yaml"


def _spec(**overrides: object) -> ExecutionSpec:
    d = load_yaml(EXEC_YAML)
    d.update(overrides)
    return ExecutionSpec.from_config(d)


def _long(
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


def _short(signal_bar: int = 0, **kwargs: object) -> TradeIntent:
    base = dict(
        candidate_id=2,
        signal_bar=signal_bar,
        side=int(Side.SHORT),
        qty=1.0,
        raw_stop_price=102.0,
        target_r=1.0,
        max_hold_bars=0,
        score=0.0,
        setup_code=0,
    )
    base.update(kwargs)
    return TradeIntent(**base)  # type: ignore[arg-type]


def _parity(bars, it: TradeIntent, spec: ExecutionSpec) -> None:
    ref = simulate_trade_path_reference(bars, it, spec)
    fast = simulate_trade_path_fast(bars, it, spec)
    assert_trade_results_equal(ref, fast)


def test_parity_no_next_bar() -> None:
    bars = make_bar_matrix([100.0], [100.0], [100.0], [100.0], minute=[0])
    spec = _spec()
    _parity(bars, _long(), spec)


def test_parity_cross_session_entry() -> None:
    bars = make_bar_matrix(
        [100.0, 101.0],
        [100.0, 102.0],
        [100.0, 100.0],
        [100.0, 101.0],
        minute=[0, 0],
        session_id=[0, 1],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _long(), spec)


def test_parity_outside_trading_window() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [101.0, 101.0],
        [99.0, 99.0],
        [100.0, 100.0],
        minute=[0, 390],
        session_id=[0, 0],
    )
    spec = _spec(eod_exit_minute=389, slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _long(), spec)


def test_parity_invalid_side() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec()
    it = TradeIntent(1, 0, 0, 1.0, 99.0, 1.0, 0, 0.0, 0)
    _parity(bars, it, spec)


def test_parity_invalid_qty_and_target_r() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec()
    _parity(
        bars,
        TradeIntent(1, 0, int(Side.LONG), float("nan"), 99.0, 1.0, 0, 0.0, 0),
        spec,
    )
    _parity(
        bars,
        TradeIntent(1, 0, int(Side.LONG), 1.0, 99.0, float("nan"), 0, 0.0, 0),
        spec,
    )


def test_parity_short_not_allowed() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(allow_short=False, slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _short(), spec)


def test_parity_short_allowed() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(allow_short=True, slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _short(), spec)


def test_parity_invalid_stop_long() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _long(stop=101.0), spec)


def test_parity_invalid_stop_short() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(allow_short=True, slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _short(raw_stop_price=99.0), spec)


def test_parity_min_risk_rejection() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.95],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.5)
    _parity(bars, _long(stop=99.9), spec)


def test_parity_nan_raw_stop() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec()
    it = TradeIntent(1, 0, int(Side.LONG), 1.0, float("nan"), 1.0, 0, 0.0, 0)
    _parity(bars, it, spec)


def test_parity_nan_entry_open() -> None:
    bars = make_bar_matrix(
        [100.0, float("nan")],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _long(stop=99.0), spec)


def test_parity_nan_scanned_ohlc_rejects() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 100.0],
        [100.0, 99.9, float("nan")],
        [100.0, 100.0, 100.0],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(eod_exit_minute=389, slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _long(stop=90.0, target_r=10.0), spec)

    bars2 = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 100.0],
        [100.0, 99.9, 99.9],
        [100.0, 100.0, float("nan")],
        minute=[0, 1, 389],
        session_id=[0, 0, 0],
    )
    _parity(bars2, _long(stop=90.0, target_r=10.0), spec)


def test_parity_long_target_hit() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 102.0],
        [100.0, 99.5, 99.5],
        [100.0, 100.0, 101.5],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _long(stop=99.0, target_r=1.0), spec)


def test_parity_long_stop_hit() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 100.5],
        [100.0, 99.5, 97.0],
        [100.0, 100.0, 97.5],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _long(stop=98.0, target_r=5.0), spec)


def test_parity_same_bar_stop_first() -> None:
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
    _parity(bars, _long(stop=95.0, target_r=2.0), spec)


def test_parity_same_bar_target_first() -> None:
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
    _parity(bars, _long(stop=95.0, target_r=2.0), spec)


def test_parity_same_bar_conservative() -> None:
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
    _parity(bars, _long(stop=95.0, target_r=2.0), spec)


def test_parity_eod_exit() -> None:
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
    _parity(bars, _long(stop=90.0, target_r=10.0), spec)


def test_parity_max_hold_exit() -> None:
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
    _parity(bars, _long(stop=90.0, target_r=10.0, max_hold_bars=2), spec)


def test_parity_eod_priority_over_max_hold_same_bar() -> None:
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
    _parity(bars, _long(stop=90.0, target_r=10.0, max_hold_bars=1), spec)


def test_parity_entry_on_eod_minute_exits_eod() -> None:
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
    _parity(bars, it, spec)


def test_parity_truncated_session_fallback_eod() -> None:
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
    _parity(bars, _long(stop=90.0, target_r=10.0), spec)


def test_parity_session_roll_exit_eod_at_prior_close() -> None:
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
    _parity(bars, _long(stop=90.0, target_r=10.0), spec)


def test_parity_short_target_hit() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 100.5],
        [100.0, 99.9, 97.0],
        [100.0, 100.0, 97.5],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(allow_short=True, slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _short(), spec)


def test_parity_short_stop_hit() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 103.0],
        [100.0, 99.9, 99.0],
        [100.0, 100.0, 102.5],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(allow_short=True, slippage_per_share=0.0, min_risk_per_share=0.01)
    _parity(bars, _short(), spec)


def test_parity_short_same_bar_stop_first() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 110.0],
        [100.0, 99.9, 89.0],
        [100.0, 100.0, 100.0],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(
        allow_short=True,
        same_bar_policy="stop_first",
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = _short(raw_stop_price=105.0, target_r=2.0)
    _parity(bars, it, spec)


def test_parity_short_same_bar_target_first() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 110.0],
        [100.0, 99.9, 89.0],
        [100.0, 100.0, 100.0],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(
        allow_short=True,
        same_bar_policy="target_first",
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    it = _short(raw_stop_price=105.0, target_r=2.0)
    _parity(bars, it, spec)


def test_parity_short_eod() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 100.0],
        [100.0, 99.9, 99.9],
        [100.0, 100.0, 100.5],
        minute=[0, 1, 389],
        session_id=[0, 0, 0],
    )
    spec = _spec(
        allow_short=True,
        eod_exit_minute=389,
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    _parity(bars, _short(raw_stop_price=110.0, target_r=10.0), spec)


def test_parity_short_max_hold() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0, 100.0],
        [100.0, 100.0, 100.0, 100.0],
        [100.0, 99.9, 99.9, 99.9],
        [100.0, 100.0, 100.0, 100.0],
        minute=[0, 1, 2, 3],
        session_id=[0, 0, 0, 0],
    )
    spec = _spec(
        allow_short=True,
        eod_exit_minute=389,
        slippage_per_share=0.0,
        min_risk_per_share=0.01,
    )
    _parity(bars, _short(raw_stop_price=110.0, target_r=10.0, max_hold_bars=2), spec)


def test_parity_slippage_entry_and_exit() -> None:
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
        commission_per_trade=0.0,
        min_risk_per_share=0.01,
    )
    _parity(bars, _long(stop=99.0, target_r=1.0), spec)


def test_parity_commission_affects_net_and_r() -> None:
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
    it = _long(stop=99.0, target_r=1.0)
    ref = simulate_trade_path_reference(bars, it, spec)
    fast = simulate_trade_path_fast(bars, it, spec)
    assert_trade_results_equal(ref, fast)
    risk_dollars = (ref.entry_price - ref.stop_price) * ref.qty
    assert ref.r_multiple == pytest.approx(ref.net_pnl / risk_dollars)


def test_parity_target_from_slippaged_entry() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 102.0],
        [100.0, 99.9, 99.9],
        [100.0, 100.0, 101.0],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(slippage_per_share=0.1, min_risk_per_share=0.01)
    it = _long(stop=99.0, target_r=1.0)
    ref = simulate_trade_path_reference(bars, it, spec)
    fast = simulate_trade_path_fast(bars, it, spec)
    assert_trade_results_equal(ref, fast)
    assert ref.target_price == pytest.approx(ref.entry_price + 1.0 * (ref.entry_price - 99.0))


def test_parity_r_multiple_equals_net_over_risk_dollars() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 102.0],
        [100.0, 99.9, 99.9],
        [100.0, 100.0, 101.0],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(
        slippage_per_share=0.05,
        commission_per_trade=0.25,
        min_risk_per_share=0.01,
    )
    it = _long(stop=99.0, target_r=2.0)
    ref = simulate_trade_path_reference(bars, it, spec)
    fast = simulate_trade_path_fast(bars, it, spec)
    assert_trade_results_equal(ref, fast)
    risk_dollars = (ref.entry_price - ref.stop_price) * ref.qty
    assert ref.r_multiple == pytest.approx(ref.net_pnl / risk_dollars)


def test_parity_management_plan_raises() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
    it = _long()
    with pytest.raises(IntradaySystemError, match="management_plan"):
        simulate_trade_path_fast(bars, it, spec, management_plan=object())
