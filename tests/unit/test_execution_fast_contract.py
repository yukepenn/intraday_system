"""Fast execution public API and parity helper smoke tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from intraday.core.config import load_yaml
from intraday.core.errors import IntradaySystemError
from intraday.core.types import ExitReason, RejectReason, Side
from intraday.execution.fast import simulate_trade_path_fast
from intraday.execution.intent import TradeIntent
from intraday.execution.parity import assert_trade_results_equal, compare_trade_results
from intraday.execution.records import TradeResult
from intraday.execution.reference import simulate_trade_path_reference
from intraday.execution.spec import ExecutionSpec

from tests.helpers.bars import make_bar_matrix

REPO = Path(__file__).resolve().parents[2]
EXEC_YAML = REPO / "configs" / "execution" / "intraday_default.yaml"


def _spec(**overrides: object) -> ExecutionSpec:
    d = load_yaml(EXEC_YAML)
    d.update(overrides)
    return ExecutionSpec.from_config(d)


def test_compare_trade_results_empty_when_equal() -> None:
    r = TradeResult.rejected(
        reject_reason=int(RejectReason.NO_NEXT_BAR),
        candidate_id=1,
        signal_bar=0,
        side=int(Side.LONG),
        qty=1.0,
    )
    assert compare_trade_results(r, r) == []


def test_management_plan_raises_like_reference() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.0],
        [100.0, 99.9],
        [100.0, 100.0],
        minute=[0, 1],
        session_id=[0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
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
    with pytest.raises(IntradaySystemError, match="management_plan"):
        simulate_trade_path_fast(bars, it, spec, management_plan=object())


def test_fast_matches_reference_trivial_long_target() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 102.0],
        [100.0, 99.5, 99.5],
        [100.0, 100.0, 101.5],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
    spec = _spec(slippage_per_share=0.0, min_risk_per_share=0.01)
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
    ref = simulate_trade_path_reference(bars, it, spec)
    fast = simulate_trade_path_fast(bars, it, spec)
    assert_trade_results_equal(ref, fast)
    assert ref.accepted and ref.exit_reason == int(ExitReason.TARGET)
