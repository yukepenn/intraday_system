"""Unit tests for SignalMatrix → TradeIntent adapter."""

from __future__ import annotations

import numpy as np
from intraday.backtest.signal_adapter import build_trade_intents_from_signals
from intraday.core.arrays import SignalMatrix
from intraday.core.types import Side


def _sig(
    *,
    n: int,
    entry_bars: list[int],
    stops: dict[int, float] | None = None,
    target_override: dict[int, float] | None = None,
) -> SignalMatrix:
    entry = np.zeros(n, dtype=bool)
    side = np.zeros(n, dtype=np.int8)
    stop = np.full(n, np.nan, dtype=np.float64)
    target_r = np.full(n, np.nan, dtype=np.float64)
    score = np.full(n, np.nan, dtype=np.float64)
    setup = np.zeros(n, dtype=np.int16)
    stops = stops or {}
    target_override = target_override or {}
    for i in entry_bars:
        entry[i] = True
        side[i] = int(Side.LONG)
        stop[i] = stops.get(i, 90.0)
        target_r[i] = target_override.get(i, 1.0)
        score[i] = 0.5
        setup[i] = 1001
    return SignalMatrix(
        entry=entry,
        side=side,
        stop=stop,
        target_r=target_r,
        score=score,
        setup_code=setup,
        signal_hash="unit",
    )


def test_non_entry_rows_skipped() -> None:
    s = _sig(n=5, entry_bars=[1, 3])
    out = build_trade_intents_from_signals(s, qty=1.0, max_hold_bars=5, candidate_id=1)
    assert out.total_entries == 2
    assert out.valid_intents == 2
    assert [i.signal_bar for i in out.intents] == [1, 3]


def test_valid_entry_fields_and_assignments() -> None:
    s = _sig(n=4, entry_bars=[2], stops={2: 88.5})
    out = build_trade_intents_from_signals(s, qty=2.0, max_hold_bars=7, candidate_id=42)
    assert len(out.intents) == 1
    it = out.intents[0]
    assert it.signal_bar == 2
    assert it.side == int(Side.LONG)
    assert it.raw_stop_price == 88.5
    assert it.target_r == 1.0
    assert it.score == 0.5
    assert it.setup_code == 1001
    assert it.qty == 2.0
    assert it.max_hold_bars == 7
    assert it.candidate_id == 42


def test_invalid_stop_skipped() -> None:
    s = _sig(n=3, entry_bars=[1], stops={1: float("nan")})
    out = build_trade_intents_from_signals(s, qty=1.0, max_hold_bars=1)
    assert out.valid_intents == 0
    assert out.skipped_invalid == 1
    assert out.skip_reasons.get("nonfinite_stop", 0) == 1


def test_invalid_target_r_skipped() -> None:
    s = _sig(n=3, entry_bars=[1], target_override={1: 0.0})
    out = build_trade_intents_from_signals(s, qty=1.0, max_hold_bars=1)
    assert out.skip_reasons.get("invalid_target_r", 0) == 1


def test_invalid_side_skipped() -> None:
    s = _sig(n=3, entry_bars=[1])
    side = np.array(s.side, copy=True)
    side[1] = 0
    s2 = SignalMatrix(
        entry=s.entry,
        side=side,
        stop=s.stop,
        target_r=s.target_r,
        score=s.score,
        setup_code=s.setup_code,
        signal_hash="u2",
    )
    out = build_trade_intents_from_signals(s2, qty=1.0, max_hold_bars=1)
    assert out.skip_reasons.get("invalid_side", 0) == 1


def test_max_hold_negative_skips() -> None:
    s = _sig(n=2, entry_bars=[0])
    out = build_trade_intents_from_signals(s, qty=1.0, max_hold_bars=-1)
    assert out.valid_intents == 0


def test_qty_non_positive() -> None:
    s = _sig(n=2, entry_bars=[0])
    out = build_trade_intents_from_signals(s, qty=0.0, max_hold_bars=1)
    assert out.intents == ()
    assert out.skipped_invalid == out.total_entries
