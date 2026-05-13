"""arrays.py unit tests for BarMatrix / FeatureMatrix / SignalMatrix."""

from __future__ import annotations

import numpy as np
import pytest
from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix


def _make_bar_matrix(n: int = 5) -> BarMatrix:
    return BarMatrix(
        open=np.linspace(100.0, 101.0, n, dtype=np.float64),
        high=np.linspace(100.5, 101.5, n, dtype=np.float64),
        low=np.linspace(99.5, 100.5, n, dtype=np.float64),
        close=np.linspace(100.1, 101.1, n, dtype=np.float64),
        volume=np.full(n, 1000.0, dtype=np.float64),
        session_id=np.zeros(n, dtype=np.int32),
        session_date=np.full(n, 20240101, dtype=np.int32),
        minute=np.arange(n, dtype=np.int16),
        ts_ns=np.arange(n, dtype=np.int64) * 60_000_000_000,
        symbol_id=1,
        data_hash="hash-test",
    )


def test_bar_matrix_construction() -> None:
    bm = _make_bar_matrix(10)
    assert bm.n_bars == 10
    assert bm.symbol_id == 1
    assert bm.data_hash == "hash-test"
    bm.validate()


def test_bar_matrix_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError):
        BarMatrix(
            open=np.zeros(5),
            high=np.zeros(5),
            low=np.zeros(5),
            close=np.zeros(5),
            volume=np.zeros(5),
            session_id=np.zeros(4, dtype=np.int32),  # wrong length
            session_date=np.zeros(5, dtype=np.int32),
            minute=np.zeros(5, dtype=np.int16),
            ts_ns=np.arange(5, dtype=np.int64),
            symbol_id=0,
            data_hash="x",
        )


def test_bar_matrix_validate_catches_non_monotonic_ts() -> None:
    n = 5
    bm = BarMatrix(
        open=np.zeros(n),
        high=np.zeros(n),
        low=np.zeros(n),
        close=np.zeros(n),
        volume=np.zeros(n),
        session_id=np.zeros(n, dtype=np.int32),
        session_date=np.zeros(n, dtype=np.int32),
        minute=np.arange(n, dtype=np.int16),
        ts_ns=np.array([5, 4, 3, 2, 1], dtype=np.int64),
        symbol_id=0,
        data_hash="x",
    )
    with pytest.raises(ValueError):
        bm.validate()


def test_feature_matrix_column_mapping() -> None:
    values = np.arange(12, dtype=np.float64).reshape(4, 3)
    columns = {"vwap": 0, "atr": 1, "regime": 2}
    fm = FeatureMatrix(values=values, columns=columns, feature_hash="fh")
    assert fm.n_bars == 4
    assert fm.n_columns == 3
    assert np.array_equal(fm.column("atr"), np.array([1.0, 4.0, 7.0, 10.0]))


def test_feature_matrix_rejects_bad_columns() -> None:
    values = np.zeros((4, 3), dtype=np.float64)
    bad_columns = {"a": 0, "b": 1, "c": 5}  # non-contiguous indices
    with pytest.raises(ValueError):
        FeatureMatrix(values=values, columns=bad_columns, feature_hash="fh")


def test_signal_matrix_basic_shapes() -> None:
    n = 6
    sm = SignalMatrix(
        entry=np.zeros(n, dtype=np.int8),
        side=np.zeros(n, dtype=np.int8),
        stop=np.zeros(n, dtype=np.float64),
        target_r=np.zeros(n, dtype=np.float64),
        score=np.zeros(n, dtype=np.float64),
        setup_code=np.zeros(n, dtype=np.int16),
        signal_hash="sh",
    )
    assert sm.n_bars == n


def test_signal_matrix_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError):
        SignalMatrix(
            entry=np.zeros(5),
            side=np.zeros(5),
            stop=np.zeros(4),  # wrong length
            target_r=np.zeros(5),
            score=np.zeros(5),
            setup_code=np.zeros(5),
            signal_hash="sh",
        )
