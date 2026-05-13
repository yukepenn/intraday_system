"""Timestamp semantics helpers (synthetic)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import polars as pl
from intraday.data.normalize import _to_ny_bar_start


def test_bar_start_naive_wall_clock_minute_mapping() -> None:
    df = pl.DataFrame(
        {
            "ts": [
                datetime(2024, 1, 2, 9, 30),
                datetime(2024, 1, 2, 9, 31),
                datetime(2024, 1, 2, 9, 32),
            ],
        }
    )
    ny = _to_ny_bar_start(df["ts"], "America/New_York", "bar_start")
    h = ny.dt.hour().cast(pl.Int32)
    mi = ny.dt.minute().cast(pl.Int32)
    mins = h * 60 + mi - (9 * 60 + 30)
    assert mins.to_list() == [0, 1, 2]


def test_bar_end_shifts_back_one_minute() -> None:
    df = pl.DataFrame(
        {
            "ts": [
                datetime(2024, 1, 2, 9, 31),
                datetime(2024, 1, 2, 9, 32),
                datetime(2024, 1, 2, 9, 33),
            ],
        }
    )
    ny = _to_ny_bar_start(df["ts"], "America/New_York", "bar_end")
    h = ny.dt.hour().cast(pl.Int32)
    mi = ny.dt.minute().cast(pl.Int32)
    mins = h * 60 + mi - (9 * 60 + 30)
    assert mins.to_list() == [0, 1, 2]


def test_audit_timestamp_semantics_sample_runs(tmp_path: Path) -> None:
    from intraday.data.timestamp_audit import audit_timestamp_semantics_sample

    root = (
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
    root.mkdir(parents=True)
    pl.DataFrame(
        {
            "timestamp": [
                datetime(2024, 1, 2, 9, 30),
                datetime(2024, 1, 2, 9, 31),
            ],
        }
    ).write_parquet(root / "data.parquet")
    rows = audit_timestamp_semantics_sample(
        tmp_path / "data" / "raw" / "ibkr",
        symbol="QQQ",
        timestamp_column="timestamp",
        timezone_if_naive="America/New_York",
        base=tmp_path,
        max_rows=100,
    )
    assert len(rows) >= 1
