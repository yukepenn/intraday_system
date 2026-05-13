"""Smoke tests for data CLI commands."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import polars as pl
import yaml


def _run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "intraday.cli.main", *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd is not None else None,
    )


def test_data_inventory_smoke(tmp_path: Path) -> None:
    out = tmp_path / "inv.csv"
    res = _run(["data", "inventory", "--root", str(tmp_path / "missing"), "--output", str(out)])
    assert res.returncode == 0, (res.stdout, res.stderr)
    assert out.exists()


def test_data_normalize_dry_run_smoke(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    raw = tmp_path / "data" / "raw" / "ibkr" / "equity" / "bars_1min" / "symbol=QQQ" / "year=2024" / "month=01"
    raw.mkdir(parents=True)
    from datetime import datetime, timedelta

    start = datetime(2024, 1, 2, 9, 30)
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
    ).write_parquet(raw / "data.parquet")

    ds = {
        "dataset_id": "synth",
        "asset": "equity",
        "symbol": "QQQ",
        "timeframe": "1m",
        "raw_root": (tmp_path / "data" / "raw" / "ibkr").as_posix(),
        "curated_root": (tmp_path / "data" / "curated" / "bars_1m_rth").as_posix(),
        "rth_only_default": True,
        "timezone": "America/New_York",
        "source": "test",
        "raw_timestamp": {
            "column": "timestamp",
            "timezone_if_naive": "America/New_York",
            "semantics": "bar_start",
            "curated_semantics": "bar_start",
        },
        "ohlcv": {"open": "open", "high": "high", "low": "low", "close": "close", "volume": "volume"},
    }
    ds_path = tmp_path / "ds.yaml"
    ds_path.write_text(yaml.safe_dump(ds), encoding="utf-8")

    res = _run(
        [
            "data",
            "normalize",
            "--dataset",
            str(ds_path),
            "--symbol",
            "QQQ",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-31",
        ],
        cwd=tmp_path,
    )
    assert res.returncode == 0, (res.stdout, res.stderr)
    payload = json.loads(res.stdout)
    assert payload["rows_out"] > 0
