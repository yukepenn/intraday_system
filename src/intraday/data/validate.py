"""Data validation helpers.

Light layout/tracking checks live here. Heavier BarMatrix validation
(missing minutes, duplicate bars) lands in Phase 1.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from intraday.core.arrays import BarMatrix
from intraday.core.errors import DataContractError
from intraday.data.catalog import build_raw_data_inventory


def validate_raw_data_layout(
    root: Path | str,
    *,
    require_all_canonical: bool = False,
    base: Path | str | None = None,
) -> dict:
    """Inspect raw data layout and return a summary.

    Raises DataContractError when require_all_canonical=True and any
    non-canonical file is present, or when any file is classified as 'unknown'.

    ``base`` should be the repo root when paths should resolve consistently with
    the inventory CLI (defaults internally to repo detection when omitted).
    """
    rows = build_raw_data_inventory(root, base=base)
    summary = {
        "total_files": len(rows),
        "canonical": sum(1 for r in rows if r["layout_type"] == "canonical"),
        "legacy_qt_like": sum(1 for r in rows if r["layout_type"] == "legacy_qt_like"),
        "unknown": sum(1 for r in rows if r["layout_type"] == "unknown"),
    }
    if summary["unknown"]:
        raise DataContractError(
            f"raw data contains {summary['unknown']} file(s) with unknown layout"
        )
    if require_all_canonical and summary["legacy_qt_like"]:
        raise DataContractError(
            f"raw data contains {summary['legacy_qt_like']} non-canonical file(s); "
            "run canonicalization (Phase 1)."
        )
    return summary


_FORBIDDEN_PATTERNS: tuple[str, ...] = (
    "data/cache/",
    "artifacts/local/",
    "artifacts/tmp/",
    "/local/",
    "/tmp/",
    ".npy",
    ".npz",
    ".memmap",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
)


def validate_no_cache_tracked(repo_root: Path | str | None = None) -> list[str]:
    """Return tracked files that match forbidden patterns.

    Uses ``git ls-files`` under the hood. Empty list = clean.
    """
    cwd = Path(repo_root) if repo_root is not None else None
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise DataContractError("git executable not found on PATH") from exc
    if result.returncode != 0:
        return []
    paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    violators = [p for p in paths if any(pat in p for pat in _FORBIDDEN_PATTERNS)]
    return violators


@dataclass(frozen=True)
class DataValidationReport:
    """Structured output from curated / BarMatrix validation."""

    symbol: str
    start: str
    end: str
    row_count: int
    session_count: int
    duplicate_timestamp_count: int
    missing_minute_count: int
    full_session_count: int
    short_session_count: int
    zero_volume_count: int
    negative_volume_count: int
    ohlc_error_count: int
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def validate_bar_matrix(
    bars: BarMatrix,
    *,
    symbol: str = "?",
    start: str = "",
    end: str = "",
    strict: bool = False,
) -> DataValidationReport:
    """Validate ``BarMatrix`` invariants and RTH minute/session heuristics."""
    errors: list[str] = []
    warnings: list[str] = []
    n = bars.n_bars
    if n == 0:
        return DataValidationReport(
            symbol=symbol,
            start=start,
            end=end,
            row_count=0,
            session_count=0,
            duplicate_timestamp_count=0,
            missing_minute_count=0,
            full_session_count=0,
            short_session_count=0,
            zero_volume_count=0,
            negative_volume_count=0,
            ohlc_error_count=0,
            errors=tuple(),
            warnings=("empty_bars",),
        )

    dup_ts = int(np.sum(np.diff(bars.ts_ns) == 0))
    if dup_ts:
        errors.append(f"duplicate_ts_ns_count={dup_ts}")

    if not (np.diff(bars.ts_ns) > 0).all():
        errors.append("ts_ns_not_strictly_increasing")

    if not (bars.session_id[1:] >= bars.session_id[:-1]).all():
        errors.append("session_id_not_monotone")

    bad_minute = (bars.minute < 0) | (bars.minute > 389)
    bad_minute_n = int(np.sum(bad_minute))
    if bad_minute_n:
        msg = f"minute_outside_0_389_count={bad_minute_n}"
        (errors if strict else warnings).append(msg)

    ohlc_bad = (
        (bars.high < np.maximum.reduce([bars.open, bars.close, bars.low]))
        | (bars.low > np.minimum.reduce([bars.open, bars.close, bars.high]))
    )
    ohlc_nan = (
        np.isnan(bars.open)
        | np.isnan(bars.high)
        | np.isnan(bars.low)
        | np.isnan(bars.close)
    )
    ohlc_err = int(np.sum(ohlc_bad | ohlc_nan))
    if ohlc_err:
        errors.append(f"ohlc_violations={ohlc_err}")

    neg_v = int(np.sum(bars.volume < 0))
    if neg_v:
        errors.append(f"negative_volume_count={neg_v}")

    zero_v = int(np.sum(bars.volume == 0))

    sid_unique, sid_start = np.unique(bars.session_id, return_index=True)
    session_count = int(len(sid_unique))
    full_sessions = 0
    short_sessions = 0
    missing_minutes = 0
    for i, _sid in enumerate(sid_unique):
        start_i = int(sid_start[i])
        end_i = int(sid_start[i + 1]) if i + 1 < len(sid_start) else n
        mins = bars.minute[start_i:end_i]
        u = np.unique(mins)
        n_unique = int(len(u))
        if n_unique == 390 and u[0] == 0 and u[-1] == 389:
            full_sessions += 1
        else:
            short_sessions += 1
            present = np.zeros(390, dtype=np.bool_)
            present[u.astype(int)] = True
            missing_minutes += int(390 - int(present.sum()))

    if missing_minutes and strict:
        errors.append(f"missing_minute_slots_total={missing_minutes}")
    elif missing_minutes:
        warnings.append(f"missing_minute_slots_total={missing_minutes}")

    return DataValidationReport(
        symbol=symbol,
        start=start,
        end=end,
        row_count=n,
        session_count=session_count,
        duplicate_timestamp_count=dup_ts,
        missing_minute_count=missing_minutes,
        full_session_count=full_sessions,
        short_session_count=short_sessions,
        zero_volume_count=zero_v,
        negative_volume_count=neg_v,
        ohlc_error_count=ohlc_err,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def validate_curated_dataset(
    symbol: str,
    start: str,
    end: str,
    *,
    data_root: Path | str,
    strict: bool = False,
    base: Path | str | None = None,
) -> DataValidationReport:
    """Load curated data for ``[start, end]`` and validate as a ``BarMatrix``."""
    from intraday.data.loader import load_bars_from_curated

    bars = load_bars_from_curated(
        symbol,
        start,
        end,
        data_root=data_root,
        base=base,
    )
    return validate_bar_matrix(
        bars,
        symbol=symbol,
        start=start,
        end=end,
        strict=strict,
    )
