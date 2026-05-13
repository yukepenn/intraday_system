"""Curated loader → BarMatrix tests."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import polars as pl
from intraday.data.loader import load_bars_from_curated
from intraday.data.normalize import normalize_raw_ibkr_to_curated


def _fixture_curated(tmp_path: Path) -> None:
    raw = (
        tmp_path
        / "data"
        / "raw"
        / "ibkr"
        / "equity"
        / "bars_1min"
        / "symbol=QQQ"
        / "year=2024"
        / "month=01"
    )
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


def test_load_bars_recomputes_session_id_across_months(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    raw = tmp_path / "data" / "raw" / "ibkr"
    for month, day in ((1, 2), (2, 1)):
        mdir = raw / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / f"month={month:02d}"
        mdir.mkdir(parents=True)
        start = datetime(2024, month, day, 9, 30)
        ts = [start + timedelta(minutes=i) for i in range(3)]
        pl.DataFrame(
            {
                "timestamp": ts,
                "open": [1.0] * 3,
                "high": [1.1] * 3,
                "low": [0.9] * 3,
                "close": [1.05] * 3,
                "volume": [1.0] * 3,
            }
        ).write_parquet(mdir / "data.parquet")

    curated = tmp_path / "data" / "curated" / "bars_1m_rth"
    normalize_raw_ibkr_to_curated(
        raw,
        curated,
        "QQQ",
        "2024-01-01",
        "2024-02-29",
        timestamp_column="timestamp",
        timestamp_timezone_if_naive="America/New_York",
        timestamp_semantics="bar_start",
        write=True,
        base=tmp_path,
    )
    sym_base = curated / "asset=equity" / "symbol=QQQ"
    for sub in sym_base.glob("year=*/month=*/bars.parquet"):
        df = pl.read_parquet(sub)
        df = df.with_columns(pl.lit(0).cast(pl.Int32).alias("session_id"))
        df.write_parquet(sub)

    bm = load_bars_from_curated(
        "QQQ",
        "2024-01-01",
        "2024-02-29",
        data_root=curated,
        base=tmp_path,
    )
    assert bm.n_bars == 6
    assert list(np.unique(bm.session_id)) == [0, 1]
    assert np.all(bm.session_id[1:] >= bm.session_id[:-1])
    assert bm.minute[0] == 0
    assert bm.minute[3] == 0


def test_load_bars_data_hash_changes_when_volume_changes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _fixture_curated(tmp_path)
    bm1 = load_bars_from_curated(
        "QQQ",
        "2024-01-01",
        "2024-01-31",
        data_root=tmp_path / "data" / "curated" / "bars_1m_rth",
        base=tmp_path,
    )
    fp = (
        tmp_path
        / "data"
        / "curated"
        / "bars_1m_rth"
        / "asset=equity"
        / "symbol=QQQ"
        / "year=2024"
        / "month=01"
        / "bars.parquet"
    )
    df = pl.read_parquet(fp)
    df = df.with_columns((pl.col("volume") * 2).alias("volume"))
    df.write_parquet(fp)
    bm2 = load_bars_from_curated(
        "QQQ",
        "2024-01-01",
        "2024-01-31",
        data_root=tmp_path / "data" / "curated" / "bars_1m_rth",
        base=tmp_path,
    )
    assert bm1.data_hash != bm2.data_hash
