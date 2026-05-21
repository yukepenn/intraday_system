"""Phase19A short execution boundary tests."""

from __future__ import annotations

from pathlib import Path

from intraday.core.config import load_yaml
from intraday.core.types import ExitReason, RejectReason, Side
from intraday.execution.intent import TradeIntent
from intraday.execution.reference import simulate_trade_path_reference
from intraday.execution.spec import ExecutionSpec

from tests.helpers.bars import make_bar_matrix

REPO = Path(__file__).resolve().parents[2]
DEFAULT_EXECUTION = REPO / "configs" / "execution" / "intraday_default.yaml"


def _spec(**overrides: object) -> ExecutionSpec:
    raw = load_yaml(DEFAULT_EXECUTION)
    raw.update(overrides)
    return ExecutionSpec.from_config(raw)


def _short_intent() -> TradeIntent:
    return TradeIntent(
        candidate_id=19,
        signal_bar=0,
        side=int(Side.SHORT),
        qty=1.0,
        raw_stop_price=102.0,
        target_r=1.0,
        max_hold_bars=0,
        score=0.7,
        setup_code=7201,
    )


def test_default_execution_rejects_short() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0],
        [100.0, 100.5],
        [100.0, 99.5],
        [100.0, 100.0],
        minute=[0, 1],
    )
    result = simulate_trade_path_reference(
        bars,
        _short_intent(),
        _spec(allow_short=False, slippage_per_share=0.0, min_risk_per_share=0.01),
    )
    assert not result.accepted
    assert result.reject_reason == int(RejectReason.SHORT_NOT_ALLOWED)


def test_execution_accepts_and_materializes_short_when_allowed() -> None:
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.5, 100.5],
        [100.0, 99.5, 97.0],
        [100.0, 100.0, 98.0],
        minute=[0, 1, 2],
    )
    result = simulate_trade_path_reference(
        bars,
        _short_intent(),
        _spec(allow_short=True, slippage_per_share=0.0, min_risk_per_share=0.01),
    )
    assert result.accepted
    assert result.side == int(Side.SHORT)
    assert result.target_price == 98.0
    assert result.exit_reason == int(ExitReason.TARGET)
