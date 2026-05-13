"""catalog.py unit tests."""

from __future__ import annotations

from pathlib import Path

from intraday.data.catalog import build_raw_data_inventory, infer_raw_layout


def test_infer_canonical_layout() -> None:
    rel = "data/raw/ibkr/asset=equity/symbol=QQQ/timeframe=1m/year=2024/month=06/bars.parquet"
    info = infer_raw_layout(rel)
    assert info.layout_type == "canonical"
    assert info.asset == "equity"
    assert info.symbol == "QQQ"
    assert info.timeframe == "1m"
    assert info.year == 2024
    assert info.month == 6
    assert info.proposed_canonical_path == rel


def test_infer_legacy_qt_like_layout() -> None:
    rel = "data/raw/ibkr/equity/bars_1min/symbol=QQQ/year=2020/month=01/data.parquet"
    info = infer_raw_layout(rel)
    assert info.layout_type == "legacy_qt_like"
    assert info.asset == "equity"
    assert info.symbol == "QQQ"
    assert info.timeframe == "1m"
    assert info.year == 2020
    assert info.month == 1
    assert info.proposed_canonical_path == (
        "data/raw/ibkr/asset=equity/symbol=QQQ/timeframe=1m/year=2020/month=01/bars.parquet"
    )


def test_infer_unknown_layout() -> None:
    info = infer_raw_layout("some/random/path/data.parquet")
    assert info.layout_type == "unknown"
    assert info.proposed_canonical_path is None


def test_build_raw_data_inventory_empty(tmp_path: Path) -> None:
    rows = build_raw_data_inventory(tmp_path)
    assert rows == []


def test_build_raw_data_inventory_with_files(tmp_path: Path) -> None:
    fpath = (
        tmp_path
        / "data" / "raw" / "ibkr" / "equity" / "bars_1min"
        / "symbol=QQQ" / "year=2020" / "month=01"
    )
    fpath.mkdir(parents=True)
    f = fpath / "data.parquet"
    f.write_bytes(b"PAR1" + b"\x00" * 1024)

    rows = build_raw_data_inventory(tmp_path / "data" / "raw" / "ibkr", base=tmp_path)
    assert len(rows) == 1
    row = rows[0]
    assert row["layout_type"] == "legacy_qt_like"
    assert row["symbol"] == "QQQ"
    assert row["year"] == 2020
    assert row["month"] == 1
    assert row["file_size_bytes"] > 0
    assert row["commit_safety"] == "safe_normal_git"
    assert row["proposed_canonical_path"].endswith(
        "asset=equity/symbol=QQQ/timeframe=1m/year=2020/month=01/bars.parquet"
    )
