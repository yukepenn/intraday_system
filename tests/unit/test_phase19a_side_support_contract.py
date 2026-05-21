"""Phase19A side-aware SignalMatrix contract tests."""

from __future__ import annotations

import numpy as np
import pytest
from intraday.core.arrays import SignalMatrix
from intraday.core.errors import ConfigError
from intraday.core.types import Side
from intraday.strategies.contracts import (
    SIDE_MODE_BOTH,
    SIDE_MODE_LONG_ONLY,
    SIDE_MODE_SHORT_ONLY,
    allowed_sides_for_mode,
    normalize_side_mode,
    validate_signal_matrix,
)


def _signal(
    *,
    entry: list[bool],
    side: list[int],
    stop: list[float],
    close: list[float],
    target_r: list[float] | None = None,
    setup: list[int] | None = None,
) -> tuple[SignalMatrix, np.ndarray]:
    sig = SignalMatrix(
        entry=np.asarray(entry, dtype=bool),
        side=np.asarray(side, dtype=np.int8),
        stop=np.asarray(stop, dtype=np.float64),
        target_r=np.asarray(target_r or [np.nan if not e else 1.0 for e in entry]),
        score=np.asarray([np.nan if not e else 0.5 for e in entry], dtype=np.float64),
        setup_code=np.asarray(setup or [0 if not e else 7101 for e in entry], dtype=np.int16),
        signal_hash="phase19a",
    )
    return sig, np.asarray(close, dtype=np.float64)


def test_signal_matrix_long_entry_convention() -> None:
    sig, close = _signal(
        entry=[False, True],
        side=[0, int(Side.LONG)],
        stop=[np.nan, 99.0],
        close=[100.0, 100.0],
        setup=[0, 7101],
    )
    validate_signal_matrix(sig, 2, reference_close=close)


def test_signal_matrix_short_entry_convention() -> None:
    sig, close = _signal(
        entry=[False, True],
        side=[0, int(Side.SHORT)],
        stop=[np.nan, 101.0],
        close=[100.0, 100.0],
        setup=[0, 7201],
    )
    validate_signal_matrix(sig, 2, reference_close=close)


def test_signal_matrix_non_entry_convention() -> None:
    sig, close = _signal(
        entry=[False],
        side=[0],
        stop=[np.nan],
        close=[100.0],
        target_r=[np.nan],
        setup=[0],
    )
    validate_signal_matrix(sig, 1, reference_close=close)


def test_signal_matrix_mixed_long_short() -> None:
    sig, close = _signal(
        entry=[True, False, True],
        side=[int(Side.LONG), 0, int(Side.SHORT)],
        stop=[99.0, np.nan, 103.0],
        close=[100.0, 101.0, 102.0],
        setup=[7101, 0, 7201],
    )
    validate_signal_matrix(sig, 3, reference_close=close)


def test_signal_matrix_rejects_invalid_side() -> None:
    sig, close = _signal(
        entry=[True],
        side=[0],
        stop=[99.0],
        close=[100.0],
        setup=[7101],
    )
    with pytest.raises(ValueError, match="side in"):
        validate_signal_matrix(sig, 1, reference_close=close)


def test_signal_matrix_enforces_side_specific_stop_geometry() -> None:
    long_bad, close = _signal(
        entry=[True],
        side=[int(Side.LONG)],
        stop=[101.0],
        close=[100.0],
    )
    with pytest.raises(ValueError, match="below reference close"):
        validate_signal_matrix(long_bad, 1, reference_close=close)

    short_bad, close = _signal(
        entry=[True],
        side=[int(Side.SHORT)],
        stop=[99.0],
        close=[100.0],
        setup=[7201],
    )
    with pytest.raises(ValueError, match="above reference close"):
        validate_signal_matrix(short_bad, 1, reference_close=close)


def test_side_mode_default_and_legacy_compatibility() -> None:
    assert normalize_side_mode({}) == SIDE_MODE_LONG_ONLY
    assert normalize_side_mode({"side": "long_only"}) == SIDE_MODE_LONG_ONLY
    assert normalize_side_mode({"side_mode": "both"}) == SIDE_MODE_BOTH
    assert allowed_sides_for_mode(SIDE_MODE_SHORT_ONLY) == (int(Side.SHORT),)


def test_side_mode_rejects_invalid_or_conflicting_values() -> None:
    with pytest.raises(ConfigError):
        normalize_side_mode({"side_mode": "diagonal"})
    with pytest.raises(ConfigError, match="conflicts"):
        normalize_side_mode({"side": "long_only", "side_mode": "both"})
