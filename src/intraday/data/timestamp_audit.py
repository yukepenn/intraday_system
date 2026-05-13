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


def _pick_sample_files(
    root: Path,
    *,
    symbol: str,
    base: Path | None,
) -> list[Path]:
    rows = [r for r in build_raw_data_inventory(root, base=base) if r.get("symbol") == symbol]
    rows.sort(key=lambda r: (r.get("year") or 0, r.get("month") or 0))
    if not rows:
        return []
    n = len(rows)
    idxs = {0, n // 2, n - 1}
    # DST-ish months if present
    for i, r in enumerate(rows):
        if int(r.get("month") or 0) in (3, 11):
            idxs.add(i)
            break
    out = [Path(rows[i]["resolved_path"]) for i in sorted(idxs) if i < n]
    # de-dupe
    seen: set[str] = set()
    uniq: list[Path] = []
    for p in out:
        k = p.resolve().as_posix()
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    return uniq


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
    files = _pick_sample_files(root_p, symbol=symbol, base=base_p)
    out: list[dict[str, Any]] = []
    for fp in files:
        df = pl.read_parquet(fp, columns=[timestamp_column]).head(max_rows)
        s = df[timestamp_column]
        dtype = s.dtype
        tz_note = str(dtype)
        if isinstance(dtype, pl.Datetime) and dtype.time_zone is None:
            ts = s.cast(pl.Datetime("ns")).dt.replace_time_zone(timezone_if_naive)
        else:
            ts = s.dt.convert_time_zone("America/New_York")
        tsn = ts.dt.hour().cast(pl.Int32) * 60 + ts.dt.minute().cast(pl.Int32)
        pre = int(((tsn < (9 * 60 + 30)) & (tsn > 0)).sum())
        ah = int((tsn >= 16 * 60).sum())
        dts = ts.diff().dt.total_seconds().drop_nulls()
        med = float(dts.median()) if len(dts) else None
        first = ts[0] if len(ts) else None
        last = ts[-1] if len(ts) else None
        # Heuristic: 60s deltas suggest bar-start labeling; bar-end often still 60s — use anchors
        first_m = int((ts.dt.hour().cast(pl.Int32) * 60 + ts.dt.minute().cast(pl.Int32))[0])
        last_m = int((ts.dt.hour().cast(pl.Int32) * 60 + ts.dt.minute().cast(pl.Int32))[-1])
        near_open = first_m in (9 * 60 + 30, 9 * 60 + 31)
        _near_close = last_m in (15 * 60 + 59, 16 * 60)
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
                else (dtype.time_zone or "unknown"),
                "timestamp_semantics_guess": sem,
                "rth_status_guess": rth,
                "notes": "sample_only_not_proof",
            }
        )
    return out
