"""Data validation tests."""

from __future__ import annotations

import numpy as np
from intraday.core.arrays import BarMatrix
from intraday.data.validate import validate_bar_matrix


def _bm(**kwargs) -> BarMatrix:
    defaults = dict(
        open=np.array([1.0, 1.0], dtype=np.float64),
        high=np.array([1.1, 1.1], dtype=np.float64),
        low=np.array([0.9, 0.9], dtype=np.float64),
        close=np.array([1.05, 1.06], dtype=np.float64),
        volume=np.array([10.0, 0.0], dtype=np.float64),
        session_id=np.array([0, 0], dtype=np.int32),
        session_date=np.array([20240102, 20240102], dtype=np.int32),
        minute=np.array([0, 1], dtype=np.int16),
        ts_ns=np.array([1, 2], dtype=np.int64),
        symbol_id=1,
        data_hash="x",
    )
    defaults.update(kwargs)
    return BarMatrix(**defaults)  # type: ignore[arg-type]


def test_validate_detects_duplicate_ts() -> None:
    bm = _bm(ts_ns=np.array([1, 1], dtype=np.int64))
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-02")
    assert rep.duplicate_timestamp_count == 1
    assert rep.errors


def test_validate_detects_ohlc_violation() -> None:
    bm = _bm(high=np.array([0.5, 0.5], dtype=np.float64))
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-02")
    assert rep.ohlc_error_count > 0


def test_validate_allows_zero_volume() -> None:
    bm = _bm()
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-02")
    assert rep.zero_volume_count == 1
    assert rep.negative_volume_count == 0


def test_validate_rejects_negative_volume() -> None:
    bm = _bm(volume=np.array([1.0, -1.0], dtype=np.float64))
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-02")
    assert rep.negative_volume_count == 1
    assert rep.errors
