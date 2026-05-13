"""Raw data catalog and inventory.

Discovers parquet files under a raw root, classifies each as canonical,
legacy_qt_like, or unknown, and writes a curated inventory.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from intraday.core.paths import repo_root

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

# When inventory root is ``data/raw/ibkr`` (or a temp mirror), paths are often
# ``equity/bars_1min/...`` without the ``data/raw/ibkr`` prefix.
_CANONICAL_SUFFIX_RE = re.compile(
    r"^(.*/)?asset=(?P<asset>[^/]+)/symbol=(?P<symbol>[^/]+)/"
    r"timeframe=(?P<timeframe>[^/]+)/year=(?P<year>\d{4})/month=(?P<month>\d{2})/"
    r"(?P<filename>[^/]+\.parquet)$"
)

_LEGACY_SUFFIX_RE = re.compile(
    r"^(.*/)?(?P<asset>[^/]+)/(?P<timeframe_dir>bars_1min|bars_1m)/"
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


def _match_canonical(rel_norm: str) -> re.Match[str] | None:
    m = _CANONICAL_RE.search(rel_norm)
    if m:
        return m
    return _CANONICAL_SUFFIX_RE.match(rel_norm)


def _match_legacy(rel_norm: str) -> re.Match[str] | None:
    m = _LEGACY_QT_LIKE_RE.search(rel_norm)
    if m:
        return m
    return _LEGACY_SUFFIX_RE.match(rel_norm)


def _info_from_canonical_match(
    rel_norm: str,
    file_name: str,
    m: re.Match[str],
) -> RawLayoutInfo:
    year = int(m.group("year"))
    month = int(m.group("month"))
    proposed = (
        f"data/raw/ibkr/asset={m.group('asset')}/symbol={m.group('symbol')}/"
        f"timeframe={m.group('timeframe')}/year={year}/month={month:02d}/bars.parquet"
    )
    return RawLayoutInfo(
        relative_path=rel_norm,
        file_name=file_name,
        asset=m.group("asset"),
        symbol=m.group("symbol"),
        timeframe=m.group("timeframe"),
        year=year,
        month=month,
        layout_type="canonical",
        proposed_canonical_path=proposed,
    )


def _info_from_legacy_match(
    rel_norm: str,
    file_name: str,
    m: re.Match[str],
) -> RawLayoutInfo:
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
        file_name=file_name,
        asset=asset,
        symbol=m.group("symbol"),
        timeframe=timeframe,
        year=year,
        month=month,
        layout_type="legacy_qt_like",
        proposed_canonical_path=proposed,
    )


def infer_raw_layout(
    path: Path | str,
    *,
    base: Path | str | None = None,
    layout_root: Path | str | None = None,
) -> RawLayoutInfo:
    """Classify a parquet path.

    ``base`` is the repo root (or any anchor) for stable relative_path output
    when the file resolves under ``base``.

    ``layout_root`` is the directory passed to inventory (e.g. ``data/raw/ibkr``).
    When the resolved path is under ``layout_root``, a virtual path
    ``data/raw/ibkr/<suffix>`` is used for layout matching if the repo-relative
    form is not already recognized.
    """
    p = Path(path)
    try:
        pabs = p.resolve()
    except OSError:
        pabs = p

    rel_norm: str
    if base is not None:
        base_res = Path(base).resolve()
        try:
            rel_norm = _normalize_rel(pabs.relative_to(base_res)).replace("\\", "/")
        except ValueError:
            rel_norm = _normalize_rel(pabs).replace("\\", "/")
    else:
        rel_norm = _normalize_rel(pabs).replace("\\", "/")

    match_candidates: list[str] = [rel_norm]
    if layout_root is not None:
        try:
            lr = Path(layout_root).resolve()
            suffix = pabs.relative_to(lr).as_posix().replace("\\", "/")
            virt = f"data/raw/ibkr/{suffix}"
            if virt not in match_candidates:
                match_candidates.insert(0, virt)
        except ValueError:
            pass

    if not rel_norm.startswith("data/raw/ibkr/"):
        idx = rel_norm.find("data/raw/ibkr/")
        if idx >= 0:
            tail = rel_norm[idx:]
            if tail not in match_candidates:
                match_candidates.insert(0, tail)

    file_name = p.name
    for cand in match_candidates:
        m = _match_canonical(cand)
        if m:
            return _info_from_canonical_match(rel_norm, file_name, m)
        m = _match_legacy(cand)
        if m:
            return _info_from_legacy_match(rel_norm, file_name, m)

    return RawLayoutInfo(
        relative_path=rel_norm,
        file_name=file_name,
        asset=None,
        symbol=None,
        timeframe=None,
        year=None,
        month=None,
        layout_type="unknown",
        proposed_canonical_path=None,
    )


def _resolve_inventory_base(
    root: Path,
    base: Path | str | None,
) -> Path:
    if base is not None:
        return Path(base).resolve()
    try:
        return repo_root()
    except RuntimeError:
        return root.resolve()


def build_raw_data_inventory(
    root: Path | str,
    *,
    base: Path | str | None = None,
) -> list[dict]:
    """Build an inventory list of dicts (one per parquet file) under ``root``."""
    root_path = Path(root).resolve()
    base_path = _resolve_inventory_base(root_path, base)
    files = find_parquet_files(root_path)
    rows: list[dict] = []
    for fp in files:
        stat = fp.stat()
        info = infer_raw_layout(fp, base=base_path, layout_root=root_path)
        size_b = int(stat.st_size)
        size_mib = round(size_b / (1024 * 1024), 4)
        mtime_iso = (
            datetime.fromtimestamp(stat.st_mtime, tz=UTC)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        )
        rows.append(
            {
                **asdict(info),
                "resolved_path": str(fp.resolve()),
                "file_size_bytes": size_b,
                "file_size_mib": size_mib,
                "modified_time_utc": mtime_iso,
                "commit_safety": _commit_safety(size_b),
            }
        )
    rows.sort(key=lambda r: r["relative_path"])
    return rows


def _commit_safety(size_bytes: int) -> CommitSafety:
    if size_bytes >= TOO_LARGE_BYTES:
        return "too_large_requires_lfs"
    if size_bytes >= LARGE_WARN_BYTES:
        return "large_warn"
    return "safe_normal_git"


_CSV_FIELDS: tuple[str, ...] = (
    "relative_path",
    "resolved_path",
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
