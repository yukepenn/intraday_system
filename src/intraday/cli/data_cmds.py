"""CLI implementations for data subcommands."""

from __future__ import annotations

import calendar
import json
from pathlib import Path

from intraday.core.config import load_yaml, resolve_path
from intraday.core.errors import ConfigError, DataContractError, IntradaySystemError
from intraday.core.paths import repo_root
from intraday.data.canonicalize import (
    apply_raw_layout_canonicalization,
    plan_raw_layout_canonicalization,
)
from intraday.data.catalog import build_raw_data_inventory
from intraday.data.inspect import inspect_raw_dataset_schema
from intraday.data.loader import load_bars_from_curated
from intraday.data.normalize import normalize_raw_ibkr_to_curated
from intraday.data.validate import validate_curated_dataset


def _load_dataset(path: str) -> dict:
    root = repo_root()
    p = Path(path)
    if not p.is_absolute():
        p = root / p
    return load_yaml(p)


def cmd_data_inspect(dataset: str, symbol: str) -> int:
    cfg = _load_dataset(dataset)
    raw_root = resolve_path(str(cfg.get("raw_root", "data/raw/ibkr")), base=repo_root())
    rows = inspect_raw_dataset_schema(raw_root, symbol=symbol, base=repo_root())
    print(json.dumps(rows, indent=2, default=str))
    return 0


def cmd_data_canonicalize_raw(root: str, symbol: str, *, write: bool) -> int:
    base = repo_root()
    raw_root = resolve_path(root, base=base)
    plan = plan_raw_layout_canonicalization(raw_root, symbol=symbol, base=base)
    print(f"planned_moves={len(plan)} write={write}")
    for step in plan:
        print(f"{step.source_path} -> {step.target_path}")
    if not plan:
        return 0
    apply_raw_layout_canonicalization(plan, write=write)
    return 0


def cmd_data_normalize(
    dataset: str,
    symbol: str,
    *,
    start: str | None,
    end: str | None,
    write: bool,
    all_available: bool,
) -> int:
    cfg = _load_dataset(dataset)
    base = repo_root()
    raw_root = resolve_path(str(cfg.get("raw_root", "data/raw/ibkr")), base=base)
    curated_root = resolve_path(str(cfg.get("curated_root", "data/curated/bars_1m_rth")), base=base)
    rt = cfg.get("raw_timestamp") or {}
    ts_col = str(rt.get("column", "timestamp"))
    tz_naive = str(rt.get("timezone_if_naive", cfg.get("timezone", "America/New_York")))
    sem = str(rt.get("semantics", "unknown"))
    if sem == "unknown" or sem == "auto_detected_bar_start_or_bar_end":
        raise IntradaySystemError(
            "raw_timestamp.semantics is unknown; run timestamp audit and set "
            "bar_start or bar_end before normalizing."
        )
    if sem not in ("bar_start", "bar_end"):
        raise ConfigError(f"invalid raw_timestamp.semantics: {sem!r}")
    ohlcv = cfg.get("ohlcv") or {}
    asset = str(cfg.get("asset", "equity"))
    timeframe = str(cfg.get("timeframe", "1m"))
    if all_available:
        inv = build_raw_data_inventory(raw_root, base=base)
        months = [
            (int(r["year"]), int(r["month"]))
            for r in inv
            if r.get("symbol") == symbol and r.get("year") and r.get("month")
        ]
        if not months:
            raise DataContractError("no inventory rows to infer date range")
        months.sort()
        y0, m0 = months[0]
        y1, m1 = months[-1]
        start = f"{y0:04d}-{m0:02d}-01"
        last_d = calendar.monthrange(y1, m1)[1]
        end = f"{y1:04d}-{m1:02d}-{last_d:02d}"
    elif start is None or end is None:
        raise ConfigError("start/end are required unless --all-available is set")
    assert start is not None and end is not None
    res = normalize_raw_ibkr_to_curated(
        raw_root,
        curated_root,
        symbol,
        start,
        end,
        asset=asset,
        timeframe=timeframe,
        timestamp_column=ts_col,
        timestamp_timezone_if_naive=tz_naive,
        timestamp_semantics=sem,  # type: ignore[arg-type]
        ohlcv={k: str(v) for k, v in ohlcv.items()} if isinstance(ohlcv, dict) else None,
        rth_only=bool(cfg.get("rth_only_default", True)),
        write=write,
        source_tag=str(cfg.get("source", "ibkr")),
        base=base,
    )
    print(
        json.dumps(
            {
                "rows_in": res.rows_in,
                "rows_out": res.rows_out,
                "rows_rth": res.rows_rth,
                "duplicate_identical_count": res.duplicate_identical_count,
                "months_touched": res.months_touched,
                "output_paths": res.output_paths,
                "warnings": res.warnings,
                "errors": res.errors,
                "dry_run": not write,
            },
            indent=2,
        )
    )
    return 0


def cmd_data_validate_curated(
    symbol: str,
    start: str,
    end: str,
    *,
    data_root: str,
    strict: bool,
) -> int:
    rep = validate_curated_dataset(
        symbol,
        start,
        end,
        data_root=data_root,
        strict=strict,
        base=repo_root(),
    )
    print(json.dumps(rep.__dict__, indent=2, default=str))
    return 1 if rep.errors else 0


def cmd_data_load_bars(symbol: str, start: str, end: str, *, data_root: str) -> int:
    bm = load_bars_from_curated(
        symbol,
        start,
        end,
        data_root=data_root,
        base=repo_root(),
    )
    sdt = bm.session_date
    print(
        json.dumps(
            {
                "rows": bm.n_bars,
                "sessions": int(len(set(sdt.tolist()))) if bm.n_bars else 0,
                "first_ts_ns": int(bm.ts_ns[0]) if bm.n_bars else None,
                "last_ts_ns": int(bm.ts_ns[-1]) if bm.n_bars else None,
                "first_session_date": int(sdt[0]) if bm.n_bars else None,
                "last_session_date": int(sdt[-1]) if bm.n_bars else None,
                "min_minute": int(bm.minute.min()) if bm.n_bars else None,
                "max_minute": int(bm.minute.max()) if bm.n_bars else None,
                "data_hash": bm.data_hash,
                "symbol_id": bm.symbol_id,
            },
            indent=2,
        )
    )
    return 0
