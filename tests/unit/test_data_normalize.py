"""Normalization tests (synthetic parquet, no real QQQ dependency)."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import polars as pl
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
