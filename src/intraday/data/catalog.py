"""Raw data catalog and inventory.

Discovers parquet files under a raw root, classifies each as canonical,
legacy_qt_like, or unknown, and writes a curated inventory.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Literal

LayoutType = Literal["canonical", "legacy_qt_like", "unknown"]
CommitSafety = Literal[
    "safe_normal_git",
    "large_warn",
    "too_large_requires_lfs",
    "local_only_recommended",
]

LARGE_WARN_BYTES: int = 50 * 1024 * 1024
TOO_LARGE_BYTES: int = 100 * 1024 * 1024

_CANONICAL_RE = re.compile(
    r"data/raw/ibkr/asset=(?P<asset>[^/]+)/symbol=(?P<symbol>[^/]+)/"
    r"timeframe=(?P<timeframe>[^/]+)/year=(?P<year>\d{4})/month=(?P<month>\d{2})/"
    r"(?P<filename>[^/]+\.parquet)$"
)

_LEGACY_QT_LIKE_RE = re.compile(
    r"data/raw/ibkr/(?P<asset>[^/]+)/(?P<timeframe_dir>bars_1min|bars_1m)/"
    r"symbol=(?P<symbol>[^/]+)/year=(?P<year>\d{4})/month=(?P<month>\d{2})/"
    r"(?P<filename>[^/]+\.parquet)$"
)


@dataclass(frozen=True)
class RawLayoutInfo:
    """Layout-inference result for one parquet file."""

    relative_path: str
    file_name: str
    asset: str | None
    symbol: str | None
    timeframe: str | None
    year: int | None
    month: int | None
    layout_type: LayoutType
    proposed_canonical_path: str | None


def find_parquet_files(root: Path | str) -> list[Path]:
    """Return every ``*.parquet`` under ``root`` sorted lexicographically."""
    root_path = Path(root)
    if not root_path.exists():
        return []
    return sorted(root_path.rglob("*.parquet"))


def _normalize_rel(rel: Path | str) -> str:
    return Path(rel).as_posix()


def infer_raw_layout(path: Path | str, *, base: Path | str | None = None) -> RawLayoutInfo:
    """Classify a parquet path. ``base`` is the repo root for relpath computation."""
    p = Path(path)
    if base is None:
        rel = _normalize_rel(p)
    else:
        try:
            rel = _normalize_rel(p.resolve().relative_to(Path(base).resolve()))
        except ValueError:
            rel = _normalize_rel(p)

    rel_norm = rel.replace("\\", "/")

    m = _CANONICAL_RE.search(rel_norm)
    if m:
        year = int(m.group("year"))
        month = int(m.group("month"))
        proposed = (
            f"data/raw/ibkr/asset={m.group('asset')}/symbol={m.group('symbol')}/"
            f"timeframe={m.group('timeframe')}/year={year}/month={month:02d}/bars.parquet"
        )
        return RawLayoutInfo(
            relative_path=rel_norm,
            file_name=p.name,
            asset=m.group("asset"),
            symbol=m.group("symbol"),
            timeframe=m.group("timeframe"),
            year=year,
            month=month,
            layout_type="canonical",
            proposed_canonical_path=proposed,
        )

    m = _LEGACY_QT_LIKE_RE.search(rel_norm)
    if m:
        asset = m.group("asset")
        timeframe_dir = m.group("timeframe_dir")
        timeframe = "1m" if timeframe_dir in ("bars_1min", "bars_1m") else timeframe_dir
        year = int(m.group("year"))
        month = int(m.group("month"))
        proposed = (
            f"data/raw/ibkr/asset={asset}/symbol={m.group('symbol')}/"
            f"timeframe={timeframe}/year={year}/month={month:02d}/bars.parquet"
        )
        return RawLayoutInfo(
            relative_path=rel_norm,
            file_name=p.name,
            asset=asset,
            symbol=m.group("symbol"),
            timeframe=timeframe,
            year=year,
            month=month,
            layout_type="legacy_qt_like",
            proposed_canonical_path=proposed,
        )

    return RawLayoutInfo(
        relative_path=rel_norm,
        file_name=p.name,
        asset=None,
        symbol=None,
        timeframe=None,
        year=None,
        month=None,
        layout_type="unknown",
        proposed_canonical_path=None,
    )


def _commit_safety(size_bytes: int) -> CommitSafety:
    if size_bytes >= TOO_LARGE_BYTES:
        return "too_large_requires_lfs"
    if size_bytes >= LARGE_WARN_BYTES:
        return "large_warn"
    return "safe_normal_git"


def build_raw_data_inventory(
    root: Path | str,
    *,
    base: Path | str | None = None,
) -> list[dict]:
    """Build an inventory list of dicts (one per parquet file) under ``root``."""
    base_path = Path(base).resolve() if base is not None else Path(root).resolve().parents[1]
    files = find_parquet_files(root)
    rows: list[dict] = []
    for p in files:
        stat = p.stat()
        info = infer_raw_layout(p, base=base_path)
        size_b = int(stat.st_size)
        size_mib = round(size_b / (1024 * 1024), 4)
        mtime_iso = (
            datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        )
        rows.append(
            {
                **asdict(info),
                "file_size_bytes": size_b,
                "file_size_mib": size_mib,
                "modified_time_utc": mtime_iso,
                "commit_safety": _commit_safety(size_b),
            }
        )
    rows.sort(key=lambda r: r["relative_path"])
    return rows


_CSV_FIELDS: tuple[str, ...] = (
    "relative_path",
    "file_name",
    "asset",
    "symbol",
    "timeframe",
    "year",
    "month",
    "layout_type",
    "proposed_canonical_path",
    "file_size_bytes",
    "file_size_mib",
    "modified_time_utc",
    "commit_safety",
)


def _write_csv(rows: Iterable[dict], output_csv: Path | str) -> Path:
    out = Path(output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(_CSV_FIELDS))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in _CSV_FIELDS})
    return out


def _write_md(rows: list[dict], root: Path | str, output_md: Path | str) -> Path:
    out = Path(output_md)
    out.parent.mkdir(parents=True, exist_ok=True)
    total = len(rows)
    total_bytes = sum(int(r["file_size_bytes"]) for r in rows)
    total_mib = round(total_bytes / (1024 * 1024), 3)
    max_bytes = max((int(r["file_size_bytes"]) for r in rows), default=0)
    max_mib = round(max_bytes / (1024 * 1024), 3)

    layout_counts: dict[str, int] = {"canonical": 0, "legacy_qt_like": 0, "unknown": 0}
    safety_counts: dict[str, int] = {
        "safe_normal_git": 0,
        "large_warn": 0,
        "too_large_requires_lfs": 0,
        "local_only_recommended": 0,
    }
    symbol_year_counts: dict[tuple[str, int], int] = {}
    for r in rows:
        layout_counts[r["layout_type"]] = layout_counts.get(r["layout_type"], 0) + 1
        safety_counts[r["commit_safety"]] = safety_counts.get(r["commit_safety"], 0) + 1
        sym = r.get("symbol") or "?"
        yr = r.get("year") or 0
        symbol_year_counts[(sym, int(yr))] = symbol_year_counts.get((sym, int(yr)), 0) + 1

    lines: list[str] = []
    lines.append("# Raw data inventory")
    lines.append("")
    lines.append(f"- root: `{Path(root).as_posix()}`")
    lines.append(f"- total files: {total}")
    lines.append(f"- total size: {total_mib} MiB ({total_bytes} bytes)")
    lines.append(f"- largest file: {max_mib} MiB")
    lines.append("")
    lines.append("## Layout classification")
    for k in ("canonical", "legacy_qt_like", "unknown"):
        lines.append(f"- {k}: {layout_counts.get(k, 0)}")
    lines.append("")
    lines.append("## Commit-safety distribution")
    for k in (
        "safe_normal_git",
        "large_warn",
        "too_large_requires_lfs",
        "local_only_recommended",
    ):
        lines.append(f"- {k}: {safety_counts.get(k, 0)}")
    lines.append("")
    if symbol_year_counts:
        lines.append("## Coverage by (symbol, year)")
        for (sym, yr), count in sorted(symbol_year_counts.items()):
            lines.append(f"- {sym} {yr}: {count} month(s)")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_raw_data_inventory(
    root: Path | str,
    *,
    output_csv: Path | str,
    output_md: Path | str | None = None,
    base: Path | str | None = None,
) -> tuple[Path, Path | None]:
    """Build and write the raw data inventory to ``output_csv`` (and optional MD)."""
    rows = build_raw_data_inventory(root, base=base)
    csv_path = _write_csv(rows, output_csv)
    md_path = _write_md(rows, root, output_md) if output_md is not None else None
    return csv_path, md_path
