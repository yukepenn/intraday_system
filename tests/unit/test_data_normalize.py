"""Normalization tests (synthetic parquet, no real QQQ dependency)."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import polars as pl
import pytest
from intraday.core.errors import ConfigError, DataContractError
from intraday.data.normalize import normalize_raw_ibkr_to_curated


def _write_legacy_month(tmp_path: Path) -> Path:
    raw = tmp_path / "data" / "raw" / "ibkr"
    month = raw / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / "month=01"
    month.mkdir(parents=True)
    start = datetime(2024, 1, 2, 9, 30)
    ts = [start + timedelta(minutes=i) for i in range(6)]
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
    ).write_parquet(month / "data.parquet")
    return raw


def test_normalize_writes_curated_schema(tmp_path: Path) -> None:
    raw_root = _write_legacy_month(tmp_path)
    curated = tmp_path / "data" / "curated" / "bars_1m_rth"
    res = normalize_raw_ibkr_to_curated(
        raw_root,
        curated,
        "QQQ",
        "2024-01-01",
        "2024-01-31",
        asset="equity",
        timeframe="1m",
        timestamp_column="timestamp",
        timestamp_timezone_if_naive="America/New_York",
        timestamp_semantics="bar_start",
        write=True,
        base=tmp_path,
    )
    assert res.rows_out > 0
    out_fp = curated / "asset=equity" / "symbol=QQQ" / "year=2024" / "month=01" / "bars.parquet"
    assert out_fp.exists()
    df = pl.read_parquet(out_fp)
    for col in (
        "ts_utc",
        "ts_utc_ns",
        "ts_local",
        "session_date",
        "session_id",
        "bar_index",
        "minute_of_session",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "source",
        "is_rth",
    ):
        assert col in df.columns


def test_normalize_rejects_non_accepted_timestamp_column(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "ibkr"
    month = raw / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / "month=01"
    month.mkdir(parents=True)
    pl.DataFrame(
        {
            "timestamp": [datetime(2024, 1, 2, 9, 30)],
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [1.0],
        }
    ).write_parquet(month / "data.parquet")
    with pytest.raises(DataContractError):
        normalize_raw_ibkr_to_curated(
            raw,
            tmp_path / "curated",
            "QQQ",
            "2024-01-01",
            "2024-01-31",
            timestamp_column="bad_ts_name",
            timestamp_timezone_if_naive="America/New_York",
            timestamp_semantics="bar_start",
            base=tmp_path,
        )


def test_normalize_uses_ts_ny_when_configured(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "ibkr"
    month = raw / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / "month=01"
    month.mkdir(parents=True)
    start = datetime(2024, 1, 2, 9, 30)
    ts = [start + timedelta(minutes=i) for i in range(3)]
    pl.DataFrame(
        {
            "ts_ny": ts,
            "open": [1.0] * 3,
            "high": [1.1] * 3,
            "low": [0.9] * 3,
            "close": [1.05] * 3,
            "volume": [1.0] * 3,
        }
    ).write_parquet(month / "data.parquet")
    res = normalize_raw_ibkr_to_curated(
        raw,
        tmp_path / "curated",
        "QQQ",
        "2024-01-01",
        "2024-01-31",
        timestamp_column="ts_ny",
        timestamp_timezone_if_naive="America/New_York",
        timestamp_semantics="bar_start",
        base=tmp_path,
    )
    assert res.rows_out == 3


def test_normalize_partial_month_write_blocked(tmp_path: Path) -> None:
    raw_root = _write_legacy_month(tmp_path)
    curated = tmp_path / "data" / "curated" / "bars_1m_rth"
    with pytest.raises(ConfigError):
        normalize_raw_ibkr_to_curated(
            raw_root,
            curated,
            "QQQ",
            "2024-01-02",
            "2024-01-31",
            timestamp_column="timestamp",
            timestamp_timezone_if_naive="America/New_York",
            timestamp_semantics="bar_start",
            write=True,
            base=tmp_path,
        )


def test_normalize_exact_session_date_filter_dry_run(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "ibkr"
    month = raw / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / "month=01"
    month.mkdir(parents=True)
    rows: list[datetime] = []
    for day in (2, 3):
        start = datetime(2024, 1, day, 9, 30)
        rows.extend([start + timedelta(minutes=i) for i in range(4)])
    n = len(rows)
    pl.DataFrame(
        {
            "timestamp": rows,
            "open": [1.0] * n,
            "high": [1.1] * n,
            "low": [0.9] * n,
            "close": [1.05] * n,
            "volume": [1.0] * n,
        }
    ).write_parquet(month / "data.parquet")
    res = normalize_raw_ibkr_to_curated(
        raw,
        tmp_path / "curated",
        "QQQ",
        "2024-01-02",
        "2024-01-02",
        timestamp_column="timestamp",
        timestamp_timezone_if_naive="America/New_York",
        timestamp_semantics="bar_start",
        write=False,
        base=tmp_path,
    )
    assert res.rows_out == 4
    assert any("session_date_filter_dropped_rows=4" in w for w in res.warnings)


def test_normalize_bar_end_minute_mapping(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "ibkr"
    month = raw / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / "month=01"
    month.mkdir(parents=True)
    pl.DataFrame(
        {
            "timestamp": [
                datetime(2024, 1, 2, 9, 31),
                datetime(2024, 1, 2, 9, 32),
            ],
            "open": [1.0, 1.0],
            "high": [1.1, 1.1],
            "low": [0.9, 0.9],
            "close": [1.05, 1.05],
            "volume": [1.0, 1.0],
        }
    ).write_parquet(month / "data.parquet")
    res = normalize_raw_ibkr_to_curated(
        raw,
        tmp_path / "curated",
        "QQQ",
        "2024-01-01",
        "2024-01-31",
        timestamp_column="timestamp",
        timestamp_timezone_if_naive="America/New_York",
        timestamp_semantics="bar_end",
        write=False,
        base=tmp_path,
    )
    assert res.rows_out == 2


def test_normalize_rth_filter_excludes_before_0930(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "ibkr"
    month = raw / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / "month=01"
    month.mkdir(parents=True)
    pl.DataFrame(
        {
            "timestamp": [
                datetime(2024, 1, 2, 9, 29),
                datetime(2024, 1, 2, 9, 30),
                datetime(2024, 1, 2, 15, 59),
            ],
            "open": [1.0, 1.0, 1.0],
            "high": [1.1, 1.1, 1.1],
            "low": [0.9, 0.9, 0.9],
            "close": [1.05, 1.05, 1.05],
            "volume": [1.0, 1.0, 1.0],
        }
    ).write_parquet(month / "data.parquet")
    res = normalize_raw_ibkr_to_curated(
        raw,
        tmp_path / "curated",
        "QQQ",
        "2024-01-01",
        "2024-01-31",
        timestamp_column="timestamp",
        timestamp_timezone_if_naive="America/New_York",
        timestamp_semantics="bar_start",
        write=False,
        base=tmp_path,
    )
    assert res.rows_out == 2


def test_normalize_invalid_ohlc_raises(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "ibkr"
    month = raw / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / "month=01"
    month.mkdir(parents=True)
    pl.DataFrame(
        {
            "timestamp": [datetime(2024, 1, 2, 9, 30)],
            "open": [1.0],
            "high": [0.5],
            "low": [0.9],
            "close": [1.05],
            "volume": [1.0],
        }
    ).write_parquet(month / "data.parquet")
    with pytest.raises(DataContractError):
        normalize_raw_ibkr_to_curated(
            raw,
            tmp_path / "curated",
            "QQQ",
            "2024-01-01",
            "2024-01-31",
            timestamp_column="timestamp",
            timestamp_timezone_if_naive="America/New_York",
            timestamp_semantics="bar_start",
            base=tmp_path,
        )


def test_normalize_conflicting_duplicate_timestamps_raise(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "ibkr"
    month = raw / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / "month=01"
    month.mkdir(parents=True)
    t0 = datetime(2024, 1, 2, 9, 30)
    pl.DataFrame(
        {
            "timestamp": [t0, t0],
            "open": [1.0, 2.0],
            "high": [1.1, 2.1],
            "low": [0.9, 1.9],
            "close": [1.05, 2.05],
            "volume": [1.0, 1.0],
        }
    ).write_parquet(month / "data.parquet")
    with pytest.raises(DataContractError):
        normalize_raw_ibkr_to_curated(
            raw,
            tmp_path / "curated",
            "QQQ",
            "2024-01-01",
            "2024-01-31",
            timestamp_column="timestamp",
            timestamp_timezone_if_naive="America/New_York",
            timestamp_semantics="bar_start",
            base=tmp_path,
        )
