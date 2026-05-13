"""Raw parquet schema inspection tests (synthetic files)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import polars as pl
from intraday.data.inspect import inspect_raw_dataset_schema, inspect_raw_parquet_schema


def test_inspect_raw_parquet_schema_smoke(tmp_path: Path) -> None:
    fp = tmp_path / "x.parquet"
    pl.DataFrame(
        {
            "timestamp": [datetime(2024, 1, 2, 9, 30), datetime(2024, 1, 2, 9, 31)],
            "open": [1.0, 1.1],
            "high": [1.1, 1.2],
            "low": [0.9, 1.0],
            "close": [1.05, 1.15],
            "volume": [100.0, 110.0],
        }
    ).write_parquet(fp)
    info = inspect_raw_parquet_schema(fp, base=tmp_path)
    assert info.schema_status == "usable"
    assert "timestamp" in info.timestamp_candidate_columns


def test_inspect_accepts_ts_ny_and_ts_utc(tmp_path: Path) -> None:
    for col in ("ts_ny", "ts_utc"):
        fp = tmp_path / f"{col}.parquet"
        pl.DataFrame(
            {
                col: [
                    datetime(2024, 1, 2, 9, 30),
                    datetime(2024, 1, 2, 9, 31),
                ],
                "open": [1.0, 1.0],
                "high": [1.1, 1.1],
                "low": [0.9, 0.9],
                "close": [1.05, 1.05],
                "volume": [1.0, 1.0],
            }
        ).write_parquet(fp)
        info = inspect_raw_parquet_schema(fp, base=tmp_path, configured_timestamp_column=col)
        assert info.schema_status == "usable"
        assert col in info.timestamp_candidate_columns


def test_inspect_missing_accepted_timestamp_fails(tmp_path: Path) -> None:
    fp = tmp_path / "bad.parquet"
    pl.DataFrame(
        {
            "not_a_ts": [datetime(2024, 1, 2, 9, 30)],
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [1.0],
        }
    ).write_parquet(fp)
    info = inspect_raw_parquet_schema(fp, base=tmp_path)
    assert info.schema_status == "missing_timestamp"


def test_inspect_configured_column_must_exist(tmp_path: Path) -> None:
    fp = tmp_path / "x.parquet"
    pl.DataFrame(
        {
            "ts_ny": [datetime(2024, 1, 2, 9, 30)],
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [1.0],
        }
    ).write_parquet(fp)
    info = inspect_raw_parquet_schema(
        fp,
        base=tmp_path,
        configured_timestamp_column="ts_utc",
    )
    assert info.schema_status == "missing_timestamp"
    assert "configured_timestamp_missing" in info.notes


def test_inspect_raw_dataset_schema_filters_symbol(tmp_path: Path) -> None:
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
    fp = root / "data.parquet"
    pl.DataFrame(
        {
            "timestamp": [datetime(2024, 1, 2, 9, 30)],
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [1.0],
        }
    ).write_parquet(fp)
    rows = inspect_raw_dataset_schema(
        tmp_path / "data" / "raw" / "ibkr",
        symbol="QQQ",
        base=tmp_path,
        raw_timestamp_column="timestamp",
    )
    assert len(rows) == 1
    assert rows[0]["schema_status"] == "usable"


def test_inspect_dataset_passes_configured_timestamp(tmp_path: Path) -> None:
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
    fp = root / "data.parquet"
    pl.DataFrame(
        {
            "ts_ny": [datetime(2024, 1, 2, 9, 30)],
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [1.0],
        }
    ).write_parquet(fp)
    rows = inspect_raw_dataset_schema(
        tmp_path / "data" / "raw" / "ibkr",
        symbol="QQQ",
        base=tmp_path,
        raw_timestamp_column="ts_ny",
    )
    assert rows[0]["schema_status"] == "usable"
