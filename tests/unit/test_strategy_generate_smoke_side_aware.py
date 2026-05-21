"""Side-aware diagnostics for ``strategies generate-smoke``."""

from __future__ import annotations

import numpy as np
from intraday.cli.strategy_cmds import _signal_smoke_entry_diagnostics
from intraday.core.arrays import SignalMatrix

from tests.helpers.bars import make_bar_matrix


def _signals(side: list[int], stop: list[float]) -> SignalMatrix:
    n = len(side)
    entry = np.asarray([s != 0 for s in side], dtype=bool)
    target_r = np.full(n, np.nan, dtype=np.float64)
    score = np.full(n, np.nan, dtype=np.float64)
    setup_code = np.zeros(n, dtype=np.int16)
    for i, s in enumerate(side):
        if s:
            target_r[i] = 1.2
            score[i] = 1.0
            setup_code[i] = 1001 if s > 0 else 8001
    return SignalMatrix(
        entry=entry,
        side=np.asarray(side, dtype=np.int8),
        stop=np.asarray(stop, dtype=np.float64),
        target_r=target_r,
        score=score,
        setup_code=setup_code,
        signal_hash="synthetic",
    )


def _bars(n: int):
    return make_bar_matrix(
        [100.0] * n,
        [101.0] * n,
        [99.0] * n,
        [100.0] * n,
        minute=list(range(n)),
    )


def test_valid_long_stop_below_close_is_not_invalid() -> None:
    out = _signal_smoke_entry_diagnostics(_signals([1], [99.0]), _bars(1))
    assert out["invalid_stop_on_entry"] == 0
    assert out["invalid_stop_on_long_entry"] == 0
    assert out["entry_side_distribution"] == {"long": 1, "short": 0}


def test_invalid_long_stop_equal_or_above_close_is_invalid() -> None:
    out = _signal_smoke_entry_diagnostics(_signals([1, 1], [100.0, 101.0]), _bars(2))
    assert out["invalid_stop_on_entry"] == 2
    assert out["invalid_stop_on_long_entry"] == 2
    assert out["invalid_stop_on_short_entry"] == 0


def test_valid_short_stop_above_close_is_not_invalid() -> None:
    out = _signal_smoke_entry_diagnostics(_signals([-1], [101.0]), _bars(1))
    assert out["invalid_stop_on_entry"] == 0
    assert out["invalid_stop_on_short_entry"] == 0
    assert out["entry_side_distribution"] == {"long": 0, "short": 1}


def test_invalid_short_stop_equal_or_below_close_is_invalid() -> None:
    out = _signal_smoke_entry_diagnostics(_signals([-1, -1], [100.0, 99.0]), _bars(2))
    assert out["invalid_stop_on_entry"] == 2
    assert out["invalid_stop_on_long_entry"] == 0
    assert out["invalid_stop_on_short_entry"] == 2


def test_mixed_long_short_distribution_and_compat_field() -> None:
    out = _signal_smoke_entry_diagnostics(
        _signals([1, -1, 0, 1, -1], [99.0, 101.0, np.nan, 100.0, 99.0]),
        _bars(5),
    )
    assert out["entry_side_distribution"] == {"long": 2, "short": 2}
    assert out["invalid_stop_on_long_entry"] == 1
    assert out["invalid_stop_on_short_entry"] == 1
    assert out["invalid_stop_on_entry"] == 2
