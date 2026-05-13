"""Synthetic BarMatrix builders for unit tests."""

from __future__ import annotations

import numpy as np
from intraday.core.arrays import BarMatrix


def make_bar_matrix(
    open_: list[float],
    high: list[float],
    low: list[float],
    close: list[float],
    *,
    session_id: list[int] | None = None,
    minute: list[int] | None = None,
    volume: list[float] | None = None,
    session_date: list[int] | None = None,
    ts_ns: np.ndarray | None = None,
    symbol_id: int = 1,
    data_hash: str = "synthetic",
) -> BarMatrix:
    """Build a minimal valid ``BarMatrix`` (no real parquet)."""
    n = len(open_)
    if not (len(high) == len(low) == len(close) == n):
        raise ValueError("open_, high, low, close must have equal length")

    if session_id is None:
        session_id = [0] * n
    if minute is None:
        minute = list(range(n))
    if volume is None:
        volume = [1.0] * n
    if session_date is None:
        session_date = [20240102] * n
    if ts_ns is None:
        ts_ns = np.arange(n, dtype=np.int64) * 60_000_000_000

    return BarMatrix(
        open=np.asarray(open_, dtype=np.float64),
        high=np.asarray(high, dtype=np.float64),
        low=np.asarray(low, dtype=np.float64),
        close=np.asarray(close, dtype=np.float64),
        volume=np.asarray(volume, dtype=np.float64),
        session_id=np.asarray(session_id, dtype=np.int32),
        session_date=np.asarray(session_date, dtype=np.int32),
        minute=np.asarray(minute, dtype=np.int16),
        ts_ns=np.asarray(ts_ns, dtype=np.int64),
        symbol_id=symbol_id,
        data_hash=data_hash,
    )
