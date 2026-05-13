"""Curated loader → BarMatrix tests."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import polars as pl
from intraday.data.loader import load_bars_from_curated
from intraday.data.normalize import normalize_raw_ibkr_to_curated


def _fixture_curated(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "ibkr" / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / "month=01"
    raw.mkdir(parents=True)
    start = datetime(2024, 1, 2, 9, 30)
    ts = [start + timedelta(minutes=i) for i in range(3)]
    n = len(ts)
    pl.DataFrame(
        {
            "timestamp": ts,
            "open": [1.0] * n,
            "high": [1.1] * n,
            "low": [0.9] * n,
            "close": [1.05] * n,
            "volume": [100.0] * n,
        }
    ).write_parquet(raw / "data.parquet")
    curated = tmp_path / "data" / "curated" / "bars_1m_rth"
    normalize_raw_ibkr_to_curated(
        tmp_path / "data" / "raw" / "ibkr",
        curated,
        "QQQ",
        "2024-01-01",
        "2024-01-31",
        timestamp_column="timestamp",
        timestamp_timezone_if_naive="America/New_York",
        timestamp_semantics="bar_start",
        write=True,
        base=tmp_path,
    )


def test_load_bars_from_curated_shapes_and_hash_stable(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _fixture_curated(tmp_path)
    bm1 = load_bars_from_curated(
        "QQQ",
        "2024-01-01",
        "2024-01-31",
        data_root=tmp_path / "data" / "curated" / "bars_1m_rth",
        base=tmp_path,
    )
    bm2 = load_bars_from_curated(
        "QQQ",
        "2024-01-01",
        "2024-01-31",
        data_root=tmp_path / "data" / "curated" / "bars_1m_rth",
        base=tmp_path,
    )
    assert bm1.n_bars == bm2.n_bars
    assert bm1.data_hash == bm2.data_hash
    assert bm1.ts_ns.shape == bm1.open.shape
    assert np.issubdtype(bm1.session_id.dtype, np.integer)
