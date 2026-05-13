"""Timestamp semantics inspection (sample-based, evidence-first)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import polars as pl

from intraday.data.catalog import build_raw_data_inventory

Guess = Literal["bar_start", "bar_end", "unknown"]
RthGuess = Literal["likely_rth_only", "likely_mixed_hours", "unknown"]


@dataclass(frozen=True)
class TimestampSemanticsRow:
    relative_path: str
    sample_rows: int
    first_ts_local: str | None
    last_ts_local: str | None
    median_delta_seconds: float | None
    first_regular_near_0930: bool | None
    last_regular_near_1600: bool | None
    premarket_rows: int
    afterhours_rows: int
    raw_timezone_guess: str
    timestamp_semantics_guess: Guess
    rth_status_guess: RthGuess
    notes: str


def format_repo_relative(path: Path, *, repo_base: Path | None) -> str:
    if repo_base is not None:
        try:
            rel = path.resolve().relative_to(repo_base.resolve()).as_posix()
            return f"<repo-root>/{rel}"
        except ValueError:
            pass
    return path.resolve().as_posix()


def select_timestamp_audit_paths(
    root: Path,
    *,
    symbol: str,
    base: Path | None,
) -> list[Path]:
    """Pick earliest, latest, one March-like, one November-like, and one 2024 month (if present)."""
    rows = [r for r in build_raw_data_inventory(root, base=base) if r.get("symbol") == symbol]
    rows.sort(key=lambda r: (int(r.get("year") or 0), int(r.get("month") or 0)))
    if not rows:
        return []

    def idx_path(i: int) -> Path | None:
        if 0 <= i < len(rows):
            return Path(rows[i]["resolved_path"])
        return None

    picks: list[Path | None] = [
        idx_path(0),
        idx_path(len(rows) - 1),
    ]
    for r in rows:
        if int(r.get("month") or 0) == 3:
            picks.append(Path(r["resolved_path"]))
            break
    for r in rows:
        if int(r.get("month") or 0) == 11:
            picks.append(Path(r["resolved_path"]))
            break
    for r in rows:
        if int(r.get("year") or 0) == 2024:
            picks.append(Path(r["resolved_path"]))
            break

    seen: set[str] = set()
    uniq: list[Path] = []
    for p in picks:
        if p is None:
            continue
        k = p.resolve().as_posix()
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    return uniq


def _ny_series_from_raw(
    s: pl.Series,
    *,
    timezone_if_naive: str,
) -> pl.Series:
    dtype = s.dtype
    if dtype == pl.Date:
        s = s.cast(pl.Datetime("ns"))
        dtype = s.dtype
    if isinstance(dtype, pl.Datetime) and dtype.time_zone is None:
        return s.cast(pl.Datetime("ns")).dt.replace_time_zone(timezone_if_naive)
    if isinstance(dtype, pl.Datetime):
        return s.dt.convert_time_zone("America/New_York")
    raise ValueError(f"unsupported timestamp dtype {dtype}")


def audit_timestamp_semantics_sample(
    root: Path | str,
    *,
    symbol: str,
    timestamp_column: str,
    timezone_if_naive: str,
    base: Path | str | None = None,
    max_rows: int = 5000,
) -> list[dict[str, Any]]:
    """Read small samples from selected monthly files and emit evidence rows."""
    root_p = Path(root).resolve()
    base_p = Path(base).resolve() if base is not None else None
    files = select_timestamp_audit_paths(root_p, symbol=symbol, base=base_p)
    out: list[dict[str, Any]] = []
    for fp in files:
        df = pl.read_parquet(fp, columns=[timestamp_column]).head(max_rows)
        s = df[timestamp_column]
        dtype = s.dtype
        tz_note = str(dtype)
        ts = _ny_series_from_raw(s, timezone_if_naive=timezone_if_naive)
        tsn = ts.dt.hour().cast(pl.Int32) * 60 + ts.dt.minute().cast(pl.Int32)
        pre = int(((tsn < (9 * 60 + 30)) & (tsn > 0)).sum())
        ah = int((tsn >= 16 * 60).sum())
        dts = ts.diff().dt.total_seconds().drop_nulls()
        med = float(dts.median()) if len(dts) else None
        first = ts[0] if len(ts) else None
        last = ts[-1] if len(ts) else None
        first_m = int((ts.dt.hour().cast(pl.Int32) * 60 + ts.dt.minute().cast(pl.Int32))[0])
        last_m = int((ts.dt.hour().cast(pl.Int32) * 60 + ts.dt.minute().cast(pl.Int32))[-1])
        near_open = first_m in (9 * 60 + 30, 9 * 60 + 31)
        sem: Guess = "unknown"
        if near_open and med == 60.0:
            sem = "bar_start"
        if (first_m == 9 * 60 + 31) and med == 60.0:
            sem = "bar_end"
        rth: RthGuess = "unknown"
        if pre == 0 and ah == 0:
            rth = "likely_rth_only"
        elif pre > 0 or ah > 0:
            rth = "likely_mixed_hours"
        out.append(
            {
                "file": fp.as_posix(),
                "timezone_note": tz_note,
                "median_delta_s": med,
                "first_local": str(first) if first is not None else "",
                "last_local": str(last) if last is not None else "",
                "premarket_rows": pre,
                "afterhours_rows": ah,
                "raw_timezone_guess": timezone_if_naive
                if isinstance(dtype, pl.Datetime) and dtype.time_zone is None
                else (getattr(dtype, "time_zone", None) or "unknown"),
                "timestamp_semantics_guess": sem,
                "rth_status_guess": rth,
                "notes": "sample_only_not_proof",
            }
        )
    return out


def build_timestamp_semantics_audit_rows(
    root: Path | str,
    *,
    symbol: str,
    timestamp_column: str,
    timezone_if_naive: str,
    base: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Per sampled month file: row counts, dtype, first/last timestamps, RTH anchors, pre/after counts."""
    root_p = Path(root).resolve()
    base_p = Path(base).resolve() if base is not None else None
    files = select_timestamp_audit_paths(root_p, symbol=symbol, base=base_p)
    rows_out: list[dict[str, Any]] = []
    for fp in files:
        df = pl.read_parquet(fp, columns=[timestamp_column])
        n = len(df)
        s = df[timestamp_column]
        dtype = s.dtype
        dtype_s = str(dtype)
        try:
            ts = _ny_series_from_raw(s, timezone_if_naive=timezone_if_naive)
        except ValueError as exc:
            rows_out.append(
                {
                    "raw_path": format_repo_relative(fp, repo_base=base_p),
                    "row_count": n,
                    "timestamp_column": timestamp_column,
                    "dtype": dtype_s,
                    "timezone_evidence": "",
                    "first_raw_timestamp": "",
                    "last_raw_timestamp": "",
                    "first_local_date": "",
                    "last_local_date": "",
                    "first_rth_local_timestamp": "",
                    "last_rth_local_timestamp": "",
                    "first_minute_of_session": "",
                    "last_minute_of_session": "",
                    "premarket_row_count": "",
                    "afterhours_row_count": "",
                    "inferred_rth_only_status": "",
                    "inferred_timestamp_semantics": "",
                    "evidence_notes": f"timestamp_convert_error:{exc}",
                }
            )
            continue

        tsn = ts.dt.hour().cast(pl.Int32) * 60 + ts.dt.minute().cast(pl.Int32)
        pre = int(((tsn < (9 * 60 + 30)) & (tsn > 0)).sum())
        ah = int((tsn >= 16 * 60).sum())
        rth_mask = (tsn >= (9 * 60 + 30)) & (tsn < (16 * 60))
        rth_ts = ts.filter(rth_mask)
        dts = ts.diff().dt.total_seconds().drop_nulls()
        med = float(dts.median()) if len(dts) else None
        first_raw = s[0] if n else None
        last_raw = s[-1] if n else None
        first_m = (
            int((ts.dt.hour().cast(pl.Int32) * 60 + ts.dt.minute().cast(pl.Int32))[0]) if n else -1
        )
        sem: Guess = "unknown"
        if first_m in (9 * 60 + 30, 9 * 60 + 31) and med == 60.0:
            sem = "bar_start"
        elif first_m == 9 * 60 + 31 and med == 60.0:
            sem = "bar_end"
        rth_guess: RthGuess = "unknown"
        if pre == 0 and ah == 0:
            rth_guess = "likely_rth_only"
        elif pre > 0 or ah > 0:
            rth_guess = "likely_mixed_hours"

        tz_ev = (
            timezone_if_naive
            if isinstance(dtype, pl.Datetime) and dtype.time_zone is None
            else (getattr(dtype, "time_zone", None) or "unknown")
        )

        first_rth = str(rth_ts[0]) if len(rth_ts) else ""
        last_rth = str(rth_ts[-1]) if len(rth_ts) else ""
        mos = (tsn - (9 * 60 + 30)).filter(rth_mask)
        first_mos = int(mos[0]) if len(mos) else None
        last_mos = int(mos[-1]) if len(mos) else None

        rows_out.append(
            {
                "raw_path": format_repo_relative(fp, repo_base=base_p),
                "row_count": n,
                "timestamp_column": timestamp_column,
                "dtype": dtype_s,
                "timezone_evidence": str(tz_ev),
                "first_raw_timestamp": str(first_raw) if first_raw is not None else "",
                "last_raw_timestamp": str(last_raw) if last_raw is not None else "",
                "first_local_date": str(ts.dt.strftime("%Y-%m-%d")[0]) if n else "",
                "last_local_date": str(ts.dt.strftime("%Y-%m-%d")[-1]) if n else "",
                "first_rth_local_timestamp": first_rth,
                "last_rth_local_timestamp": last_rth,
                "first_minute_of_session": first_mos if first_mos is not None else "",
                "last_minute_of_session": last_mos if last_mos is not None else "",
                "premarket_row_count": pre,
                "afterhours_row_count": ah,
                "inferred_rth_only_status": rth_guess,
                "inferred_timestamp_semantics": sem,
                "evidence_notes": "sample_full_month_file_polars_read",
            }
        )
    return rows_out
