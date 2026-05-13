"""Load curated parquet into ``BarMatrix`` (hot arrays)."""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from intraday.core.arrays import BarMatrix
from intraday.core.config import load_yaml
from intraday.core.errors import DataContractError
from intraday.core.hashing import hash_config, hash_paths_manifest
from intraday.core.paths import repo_root

CURATED_SCHEMA_VERSION = "bars_1m_rth_v1"

_DEFAULT_CURATED_COLS: tuple[str, ...] = (
    "open",
    "high",
    "low",
    "close",
    "volume",
    "session_id",
    "session_date",
    "minute_of_session",
    "ts_utc_ns",
)


def _symbol_id_from_config(symbol: str, *, config_path: Path | None = None) -> int:
    root = repo_root()
    path = config_path or (root / "configs/data/symbols.yaml")
    data = load_yaml(path)
    symbols = data.get("symbols", [])
    for row in symbols:
        if str(row.get("symbol", "")).upper() == symbol.upper():
            return int(row["symbol_id"])
    h = hashlib.sha256(f"symbol_id::{symbol}".encode()).hexdigest()
    return int(h[:8], 16) % (2**31)


def _month_iter(start_d: date, end_d: date) -> list[tuple[int, int]]:
    y, m = start_d.year, start_d.month
    out: list[tuple[int, int]] = []
    cur = date(y, m, 1)
    end_m = date(end_d.year, end_d.month, 1)
    while cur <= end_m:
        out.append((cur.year, cur.month))
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)
    return out


def _curated_paths_for_range(
    data_root: Path,
    *,
    asset: str,
    symbol: str,
    start: str,
    end: str,
) -> list[Path]:
    start_d = date.fromisoformat(start[:10])
    end_d = date.fromisoformat(end[:10])
    base = data_root / f"asset={asset}" / f"symbol={symbol}"
    if not base.exists():
        return []
    paths: list[Path] = []
    for y, m in _month_iter(start_d, end_d):
        month_dir = base / f"year={y}" / f"month={m:02d}"
        if not month_dir.is_dir():
            continue
        if m < 12:
            last_day = date(y, m + 1, 1) - timedelta(days=1)
        else:
            last_day = date(y, 12, 31)
        # include month if it overlaps requested calendar window
        month_start = date(y, m, 1)
        if month_start > end_d or last_day < start_d:
            continue
        for f in sorted(month_dir.glob("*.parquet")):
            paths.append(f)
    paths.sort(key=lambda p: p.as_posix())
    return paths


def load_bars_from_curated(
    symbol: str,
    start: str,
    end: str,
    *,
    data_root: Path | str = Path("data/curated/bars_1m_rth"),
    asset: str = "equity",
    columns: list[str] | None = None,
    base: Path | str | None = None,
    symbols_config: Path | str | None = None,
) -> BarMatrix:
    """Scan curated monthly parquet for ``symbol`` and build a ``BarMatrix``."""
    root = Path(base).resolve() if base is not None else repo_root()
    dr = Path(data_root)
    if not dr.is_absolute():
        dr = (root / dr).resolve()
    paths = _curated_paths_for_range(dr, asset=asset, symbol=symbol, start=start, end=end)
    if not paths:
        raise DataContractError(
            f"no curated parquet under {dr} for {symbol} in [{start}, {end}]"
        )
    start_key = int(start[:4]) * 10000 + int(start[5:7]) * 100 + int(start[8:10])
    end_key = int(end[:4]) * 10000 + int(end[5:7]) * 100 + int(end[8:10])

    use_cols = tuple(columns) if columns is not None else _DEFAULT_CURATED_COLS
    scans = [pl.scan_parquet(p).select([pl.col(c) for c in use_cols]) for p in paths]
    lf = pl.concat(scans, how="vertical")
    if "minute_of_session" in use_cols:
        lf = lf.rename({"minute_of_session": "minute"})
    lf = lf.filter(
        (pl.col("session_date") >= pl.lit(start_key)) & (pl.col("session_date") <= pl.lit(end_key))
    )
    lf = lf.sort("ts_utc_ns")
    df = lf.collect()

    o = df["open"].to_numpy().astype(np.float64, copy=False)
    h = df["high"].to_numpy().astype(np.float64, copy=False)
    lo = df["low"].to_numpy().astype(np.float64, copy=False)
    c = df["close"].to_numpy().astype(np.float64, copy=False)
    v = df["volume"].to_numpy().astype(np.float64, copy=False)
    sid = df["session_id"].to_numpy().astype(np.int32, copy=False)
    sdt = df["session_date"].to_numpy().astype(np.int32, copy=False)
    minute = df["minute"].to_numpy().astype(np.int16, copy=False)
    ts_ns = df["ts_utc_ns"].to_numpy().astype(np.int64, copy=False)

    sym_cfg = Path(symbols_config) if symbols_config is not None else None
    symbol_id = _symbol_id_from_config(symbol, config_path=sym_cfg)

    manifest_hash = hash_paths_manifest(paths, base=dr, include_mtime=True)
    meta: dict[str, Any] = {
        "symbol": symbol,
        "asset": asset,
        "start": start,
        "end": end,
        "schema_version": CURATED_SCHEMA_VERSION,
        "n_rows": int(len(df)),
        "first_ts_ns": int(ts_ns[0]) if len(ts_ns) else None,
        "last_ts_ns": int(ts_ns[-1]) if len(ts_ns) else None,
        "manifest_hash": manifest_hash,
    }
    data_hash = hash_config(meta)

    bm = BarMatrix(
        open=o,
        high=h,
        low=lo,
        close=c,
        volume=v,
        session_id=sid,
        session_date=sdt,
        minute=minute,
        ts_ns=ts_ns,
        symbol_id=symbol_id,
        data_hash=data_hash,
    )
    bm.validate()
    return bm
