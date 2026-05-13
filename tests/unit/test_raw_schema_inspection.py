"""Raw parquet schema inspection tests (synthetic files)."""

from __future__ import annotations

from pathlib import Path

import polars as pl
from intraday.data.inspect import inspect_raw_dataset_schema, inspect_raw_parquet_schema


def test_inspect_raw_parquet_schema_smoke(tmp_path: Path) -> None:
    fp = tmp_path / "x.parquet"
    pl.DataFrame(
        {
            "timestamp": [1, 2],
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


def test_inspect_raw_dataset_schema_filters_symbol(tmp_path: Path) -> None:
    root = tmp_path / "data" / "raw" / "ibkr" / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / "month=01"
    root.mkdir(parents=True)
    fp = root / "data.parquet"
    pl.DataFrame(
        {
            "timestamp": [1],
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [1.0],
        }
    ).write_parquet(fp)
    rows = inspect_raw_dataset_schema(tmp_path / "data" / "raw" / "ibkr", symbol="QQQ", base=tmp_path)
    assert len(rows) == 1
    assert rows[0]["schema_status"] == "usable"
