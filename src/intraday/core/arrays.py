"""Hot-path NumPy container dataclasses.

These containers are passed across layers. They are frozen, so callers cannot
mutate the underlying arrays through the container; the arrays themselves are
expected to be treated as immutable post-construction.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np


def _ensure_1d(name: str, arr: np.ndarray) -> None:
    if not isinstance(arr, np.ndarray):
        raise TypeError(f"{name} must be a numpy ndarray, got {type(arr)!r}")
    if arr.ndim != 1:
        raise ValueError(f"{name} must be 1-D, got shape {arr.shape}")


@dataclass(frozen=True)
class BarMatrix:
    """Canonical hot-path bar container.

    All arrays share length N. Arrays are 1-D. ``ts_ns`` is strictly increasing.
    ``session_id`` is monotonically non-decreasing. ``minute`` is the
    minute-of-session index (0..389 for US equity RTH 1-min).
    """

    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    volume: np.ndarray
    session_id: np.ndarray
    session_date: np.ndarray
    minute: np.ndarray
    ts_ns: np.ndarray
    symbol_id: int
    data_hash: str

    def __post_init__(self) -> None:
        n = self.open.shape[0]
        for name in ("open", "high", "low", "close", "volume",
                     "session_id", "session_date", "minute", "ts_ns"):
            arr = getattr(self, name)
            _ensure_1d(name, arr)
            if arr.shape[0] != n:
                raise ValueError(
                    f"BarMatrix length mismatch: open={n} {name}={arr.shape[0]}"
                )

    @property
    def n_bars(self) -> int:
        return int(self.open.shape[0])

    def validate(self) -> None:
        """Run light invariant checks. Heavier checks live in data/validate.py."""
        if self.n_bars == 0:
            return
        if self.session_id.dtype.kind not in ("i", "u"):
            raise TypeError(f"session_id must be integer, got {self.session_id.dtype}")
        if not (self.session_id[1:] >= self.session_id[:-1]).all():
            raise ValueError("session_id must be monotonically non-decreasing")
        if not (self.ts_ns[1:] > self.ts_ns[:-1]).all():
            raise ValueError("ts_ns must be strictly increasing")


@dataclass(frozen=True)
class FeatureMatrix:
    """Feature values keyed by column name.

    ``values`` has shape (N, K). ``columns`` maps column name -> column index.
    """

    values: np.ndarray
    columns: Mapping[str, int]
    feature_hash: str

    def __post_init__(self) -> None:
        if not isinstance(self.values, np.ndarray):
            raise TypeError("values must be a numpy ndarray")
        if self.values.ndim != 2:
            raise ValueError(f"values must be 2-D, got shape {self.values.shape}")
        n_cols_arr = self.values.shape[1]
        n_cols_map = len(self.columns)
        if n_cols_arr != n_cols_map:
            raise ValueError(
                f"columns map size {n_cols_map} != values columns {n_cols_arr}"
            )
        idxs = sorted(self.columns.values())
        if idxs != list(range(n_cols_arr)):
            raise ValueError("columns indices must be a contiguous 0..K-1 set")

    @property
    def n_bars(self) -> int:
        return int(self.values.shape[0])

    @property
    def n_columns(self) -> int:
        return int(self.values.shape[1])

    def column(self, name: str) -> np.ndarray:
        if name not in self.columns:
            raise KeyError(f"unknown feature column: {name!r}")
        return self.values[:, self.columns[name]]


@dataclass(frozen=True)
class SignalMatrix:
    """Per-bar strategy signal arrays. All arrays share length N (bars).

    ``entry`` is bool/int8 (1 = signal fired on this bar). ``side`` is +1/-1/0.
    ``stop`` is the raw stop price (execution materializes the final stop).
    ``target_r`` is the desired R-multiple for the target.
    """

    entry: np.ndarray
    side: np.ndarray
    stop: np.ndarray
    target_r: np.ndarray
    score: np.ndarray
    setup_code: np.ndarray
    signal_hash: str

    def __post_init__(self) -> None:
        n = self.entry.shape[0]
        for name in ("entry", "side", "stop", "target_r", "score", "setup_code"):
            arr = getattr(self, name)
            _ensure_1d(name, arr)
            if arr.shape[0] != n:
                raise ValueError(
                    f"SignalMatrix length mismatch: entry={n} {name}={arr.shape[0]}"
                )

    @property
    def n_bars(self) -> int:
        return int(self.entry.shape[0])


@dataclass(frozen=True)
class TradeRecordArray:
    """Compact per-trade record arrays. All arrays share length M (trades)."""

    entry_bar: np.ndarray
    exit_bar: np.ndarray
    side: np.ndarray
    qty: np.ndarray
    entry_price: np.ndarray
    exit_price: np.ndarray
    stop_price: np.ndarray
    target_price: np.ndarray
    pnl: np.ndarray
    r_multiple: np.ndarray
    exit_reason: np.ndarray
    candidate_id: np.ndarray

    def __post_init__(self) -> None:
        m = self.entry_bar.shape[0]
        for name in (
            "entry_bar", "exit_bar", "side", "qty",
            "entry_price", "exit_price", "stop_price", "target_price",
            "pnl", "r_multiple", "exit_reason", "candidate_id",
        ):
            arr = getattr(self, name)
            _ensure_1d(name, arr)
            if arr.shape[0] != m:
                raise ValueError(
                    f"TradeRecordArray length mismatch: entry_bar={m} {name}={arr.shape[0]}"
                )

    @property
    def n_trades(self) -> int:
        return int(self.entry_bar.shape[0])
