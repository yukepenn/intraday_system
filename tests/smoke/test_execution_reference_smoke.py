"""Smoke: reference execution imports and one synthetic path."""

from __future__ import annotations

from pathlib import Path

from intraday.core.config import load_yaml
from intraday.core.types import ExitReason, Side
from intraday.execution import (
    ExecutionSpec,
    TradeIntent,
    materialize_trade,
    simulate_trade_path_reference,
)
from intraday.execution.materialize import MaterializedTrade

from tests.helpers.bars import make_bar_matrix


def test_import_execution_modules() -> None:
    from intraday.execution import cost as c  # noqa: PLC0415
    from intraday.execution import materialize as m  # noqa: PLC0415
    from intraday.execution import reference as ref  # noqa: PLC0415

    assert callable(c.apply_entry_slippage)
    assert callable(m.materialize_trade)
    assert callable(ref.simulate_trade_path_reference)


def test_synthetic_long_target_accepted() -> None:
    repo = Path(__file__).resolve().parents[2]
    d = load_yaml(repo / "configs" / "execution" / "intraday_default.yaml")
    spec = ExecutionSpec.from_config(d)
    bars = make_bar_matrix(
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 102.0],
        [100.0, 99.5, 99.5],
        [100.0, 100.0, 101.5],
        minute=[0, 1, 2],
        session_id=[0, 0, 0],
    )
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
    mt = materialize_trade(bars, it, spec)
    assert isinstance(mt, MaterializedTrade)
    r = simulate_trade_path_reference(bars, it, spec)
    assert r.accepted
    assert r.exit_reason == int(ExitReason.TARGET)
    assert r.r_multiple > 0.0
