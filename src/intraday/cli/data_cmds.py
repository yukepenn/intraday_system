"""CLI implementations for data subcommands."""

from __future__ import annotations

import calendar
import csv
import json
from pathlib import Path

import polars as pl

from intraday.core.config import load_yaml, resolve_path
from intraday.core.errors import ConfigError, DataContractError, IntradaySystemError
from intraday.core.paths import repo_root
from intraday.data.canonicalize import (
    apply_raw_layout_canonicalization,
    plan_raw_layout_canonicalization,
)
from intraday.data.catalog import build_raw_data_inventory
from intraday.data.inspect import inspect_raw_dataset_schema
from intraday.data.loader import curated_parquet_paths_for_window, load_bars_from_curated
from intraday.data.normalize import normalize_raw_ibkr_to_curated
from intraday.data.timestamp_audit import build_timestamp_semantics_audit_rows
from intraday.data.validate import validate_curated_dataset


def _path_repo_rel(path: Path, repo_base: Path) -> str:
    try:
        return path.resolve().relative_to(repo_base.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _load_dataset(path: str) -> dict:
    root = repo_root()
    p = Path(path)
    if not p.is_absolute():
        p = root / p
    return load_yaml(p)


def _write_csv_dicts(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in headers})


def cmd_data_inspect(dataset: str, symbol: str) -> int:
    cfg = _load_dataset(dataset)
    base = repo_root()
    raw_root = resolve_path(str(cfg.get("raw_root", "data/raw/ibkr")), base=base)
    rt = cfg.get("raw_timestamp") or {}
    ts_raw = rt.get("column")
    ts_arg = str(ts_raw) if ts_raw is not None else None
    rows = inspect_raw_dataset_schema(
        raw_root,
        symbol=symbol,
        base=base,
        raw_timestamp_column=ts_arg,
    )
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

    def _repo_rel(p: str) -> str:
        try:
            rel = Path(p).resolve().relative_to(base.resolve())
            return f"<repo-root>/{rel.as_posix()}"
        except ValueError:
            return p

    out_paths = [_repo_rel(x) for x in res.output_paths]
    print(
        json.dumps(
            {
                "rows_in": res.rows_in,
                "rows_out": res.rows_out,
                "rows_rth": res.rows_rth,
                "duplicate_identical_count": res.duplicate_identical_count,
                "months_touched": res.months_touched,
                "output_paths": out_paths,
                "warnings": res.warnings,
                "errors": res.errors,
                "dry_run": not write,
            },
            indent=2,
        )
    )
    return 0


def cmd_data_timestamp_audit(dataset: str, symbol: str, *, output_dir: str) -> int:
    cfg = _load_dataset(dataset)
    base = repo_root()
    raw_root = resolve_path(str(cfg.get("raw_root", "data/raw/ibkr")), base=base)
    rt = cfg.get("raw_timestamp") or {}
    ts_col = str(rt.get("column", "timestamp"))
    tz_naive = str(rt.get("timezone_if_naive", cfg.get("timezone", "America/New_York")))
    out_dir = Path(output_dir)
    if not out_dir.is_absolute():
        out_dir = base / out_dir
    rows = build_timestamp_semantics_audit_rows(
        raw_root,
        symbol=symbol,
        timestamp_column=ts_col,
        timezone_if_naive=tz_naive,
        base=base,
    )
    csv_p = out_dir / "timestamp_semantics_audit.csv"
    md_p = out_dir / "timestamp_semantics_audit.md"
    _write_csv_dicts(csv_p, rows)
    lines = [
        "# Timestamp semantics audit",
        "",
        f"Dataset: `{dataset}`",
        f"Symbol: `{symbol}`",
        f"Timestamp column: `{ts_col}`",
        "",
        "| " + " | ".join(rows[0].keys()) + " |" if rows else "| (no rows) |",
        "| " + " | ".join(["---"] * len(rows[0])) + " |" if rows else "",
    ]
    if rows:
        for r in rows:
            lines.append("| " + " | ".join(str(r.get(k, "")) for k in rows[0].keys()) + " |")
    md_p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote_csv": _path_repo_rel(csv_p, base),
                "wrote_md": _path_repo_rel(md_p, base),
                "rows": len(rows),
            },
            indent=2,
        )
    )
    return 0


def cmd_data_session_coverage(
    symbol: str,
    start: str,
    end: str,
    *,
    data_root: str,
    output_dir: str,
    asset: str = "equity",
) -> int:
    base = repo_root()
    dr = resolve_path(data_root, base=base)
    out_dir = Path(output_dir)
    if not out_dir.is_absolute():
        out_dir = base / out_dir
    paths = curated_parquet_paths_for_window(
        dr,
        asset=asset,
        symbol=symbol,
        start=start,
        end=end,
    )
    notes: list[str] = []
    if not paths:
        notes.append("no_curated_parquet_for_window")
        rows: list[dict[str, object]] = []
    else:
        start_key = int(start[:4]) * 10000 + int(start[5:7]) * 100 + int(start[8:10])
        end_key = int(end[:4]) * 10000 + int(end[5:7]) * 100 + int(end[8:10])
        lf = pl.concat([pl.scan_parquet(p) for p in paths], how="vertical")
        lf = lf.filter((pl.col("session_date") >= start_key) & (pl.col("session_date") <= end_key))
        m = pl.col("minute_of_session")
        g = lf.group_by("session_date").agg(
            [
                pl.len().alias("row_count"),
                m.min().alias("min_minute"),
                m.max().alias("max_minute"),
                (pl.lit(390) - m.filter((m >= 0) & (m < 390)).n_unique()).alias(
                    "missing_minute_count"
                ),
                (pl.len() - pl.col("ts_utc_ns").n_unique()).alias("duplicate_timestamp_count"),
                (pl.col("volume") == 0).sum().alias("zero_volume_count"),
            ]
        )
        df = g.collect().sort("session_date")
        rows = []
        for r in df.iter_rows(named=True):
            rc = int(r["row_count"])
            dup = int(r["duplicate_timestamp_count"])
            miss = int(r["missing_minute_count"])
            mn = int(r["min_minute"])
            mx = int(r["max_minute"])
            if dup > 0 or miss > 0:
                status = "invalid"
            elif rc == 390 and mn == 0 and mx == 389:
                status = "full_session"
            else:
                status = "short_session"
            note = ""
            if dup > 0:
                note = f"duplicate_ts_rows={dup}"
            if miss > 0:
                note = (note + ";" if note else "") + f"missing_minute_slots={miss}"
            rows.append(
                {
                    "session_date": r["session_date"],
                    "row_count": rc,
                    "min_minute": mn,
                    "max_minute": mx,
                    "missing_minute_count": miss,
                    "duplicate_timestamp_count": dup,
                    "zero_volume_count": int(r["zero_volume_count"]),
                    "status": status,
                    "notes": note,
                }
            )
    csv_p = out_dir / "session_coverage_summary.csv"
    md_p = out_dir / "session_coverage_summary.md"
    _write_csv_dicts(csv_p, rows)
    md_lines = [
        "# Session coverage summary",
        "",
        f"Symbol `{symbol}` window `{start}`..`{end}`",
        "",
    ]
    if notes:
        md_lines.extend([f"Notes: {', '.join(notes)}", ""])
    if rows:
        keys = list(rows[0].keys())
        md_lines.append("| " + " | ".join(keys) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(keys)) + " |")
        for row in rows:
            md_lines.append("| " + " | ".join(str(row[k]) for k in keys) + " |")
    else:
        md_lines.append("_No rows (see notes)._")
    md_p.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote_csv": _path_repo_rel(csv_p, base),
                "wrote_md": _path_repo_rel(md_p, base),
                "sessions": len(rows),
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
