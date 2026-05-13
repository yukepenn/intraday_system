"""Data validation tests."""

from __future__ import annotations

import numpy as np
from intraday.core.arrays import BarMatrix
from intraday.data.validate import validate_bar_matrix


def _bm(n: int = 2, **kwargs) -> BarMatrix:
    defaults = dict(
        open=np.ones(n, dtype=np.float64),
        high=np.ones(n, dtype=np.float64) * 1.1,
        low=np.ones(n, dtype=np.float64) * 0.9,
        close=np.linspace(1.05, 1.05 + 0.01 * (n - 1), n, dtype=np.float64),
        volume=np.ones(n, dtype=np.float64) * 10.0,
        session_id=np.zeros(n, dtype=np.int32),
        session_date=np.full(n, 20240102, dtype=np.int32),
        minute=np.arange(n, dtype=np.int16),
        ts_ns=np.arange(1, n + 1, dtype=np.int64),
        symbol_id=1,
        data_hash="x",
    )
    defaults.update(kwargs)
    return BarMatrix(**defaults)  # type: ignore[arg-type]


def test_validate_detects_duplicate_ts() -> None:
    bm = _bm(ts_ns=np.array([1, 1], dtype=np.int64), minute=np.array([0, 1], dtype=np.int16))
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-02")
    assert rep.duplicate_timestamp_count == 1
    assert rep.errors


def test_validate_detects_ohlc_violation() -> None:
    bm = _bm(high=np.array([0.5, 0.5], dtype=np.float64))
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-02")
    assert rep.ohlc_error_count > 0


def test_validate_allows_zero_volume() -> None:
    bm = _bm(
        volume=np.array([10.0, 0.0], dtype=np.float64), minute=np.array([0, 1], dtype=np.int16)
    )
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-02")
    assert rep.zero_volume_count == 1
    assert rep.negative_volume_count == 0


def test_validate_rejects_negative_volume() -> None:
    bm = _bm(volume=np.array([1.0, -1.0], dtype=np.float64))
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-02")
    assert rep.negative_volume_count == 1
    assert rep.errors


def test_validate_missing_minutes_warns_by_default() -> None:
    bm = _bm(
        minute=np.array([0, 2], dtype=np.int16),
        ts_ns=np.array([100, 200], dtype=np.int64),
    )
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-02")
    assert rep.missing_minute_count > 0
    assert rep.warnings


def test_validate_missing_minutes_strict_errors() -> None:
    bm = _bm(
        minute=np.array([0, 2], dtype=np.int16),
        ts_ns=np.array([100, 200], dtype=np.int64),
    )
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-02", strict=True)
    assert rep.errors


def test_validate_short_session_counts() -> None:
    bm = _bm(
        n=6,
        minute=np.array([0, 1, 2, 0, 1, 2], dtype=np.int16),
        session_id=np.array([0, 0, 0, 1, 1, 1], dtype=np.int32),
        session_date=np.array(
            [20240102, 20240102, 20240102, 20240103, 20240103, 20240103], dtype=np.int32
        ),
        ts_ns=np.array([1, 2, 3, 4, 5, 6], dtype=np.int64),
    )
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-04")
    assert rep.short_session_count == 2
    assert rep.full_session_count == 0


def test_validate_session_start_minute_must_be_zero() -> None:
    bm = _bm(
        n=4,
        minute=np.array([0, 1, 1, 2], dtype=np.int16),
        session_id=np.array([0, 0, 1, 1], dtype=np.int32),
        session_date=np.array([20240102, 20240102, 20240103, 20240103], dtype=np.int32),
        ts_ns=np.array([1, 2, 3, 4], dtype=np.int64),
    )
    rep = validate_bar_matrix(bm, symbol="QQQ", start="2024-01-01", end="2024-01-04")
    assert any("session_start_minute_not_zero" in e for e in rep.errors)
