"""Phase19A signal-adapter side support tests."""

from __future__ import annotations

import numpy as np
from intraday.backtest.signal_adapter import build_trade_intents_from_signals
from intraday.core.arrays import SignalMatrix
from intraday.core.types import Side


def _sig(side_value: int) -> SignalMatrix:
    return SignalMatrix(
        entry=np.asarray([True], dtype=bool),
        side=np.asarray([side_value], dtype=np.int8),
        stop=np.asarray([99.0 if side_value != int(Side.SHORT) else 101.0]),
        target_r=np.asarray([1.0]),
        score=np.asarray([0.5]),
        setup_code=np.asarray([7101 if side_value != int(Side.SHORT) else 7201], dtype=np.int16),
        signal_hash="adapter",
    )


def test_adapter_accepts_long_by_default() -> None:
    out = build_trade_intents_from_signals(_sig(int(Side.LONG)), qty=1.0, max_hold_bars=5)
    assert out.valid_intents == 1
    assert out.intents[0].side == int(Side.LONG)


def test_adapter_rejects_short_by_default_without_marking_invalid_side() -> None:
    out = build_trade_intents_from_signals(_sig(int(Side.SHORT)), qty=1.0, max_hold_bars=5)
    assert out.valid_intents == 0
    assert out.skipped_invalid == 1
    assert out.skip_reasons == {"side_not_allowed": 1}


def test_adapter_accepts_short_when_allowed() -> None:
    out = build_trade_intents_from_signals(
        _sig(int(Side.SHORT)),
        qty=1.0,
        max_hold_bars=5,
        allowed_sides=(Side.LONG, Side.SHORT),
    )
    assert out.valid_intents == 1
    assert out.intents[0].side == int(Side.SHORT)
    assert out.intents[0].raw_stop_price == 101.0


def test_adapter_rejects_invalid_side() -> None:
    out = build_trade_intents_from_signals(_sig(2), qty=1.0, max_hold_bars=5)
    assert out.valid_intents == 0
    assert out.skip_reasons == {"invalid_side": 1}
