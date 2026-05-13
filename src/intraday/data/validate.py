"""Data validation helpers.

Light layout/tracking checks live here. Heavier BarMatrix validation
(missing minutes, duplicate bars) lands in Phase 1.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from intraday.core.errors import DataContractError
from intraday.data.catalog import build_raw_data_inventory


def validate_raw_data_layout(
    root: Path | str,
    *,
    require_all_canonical: bool = False,
) -> dict:
    """Inspect raw data layout and return a summary.

    Raises DataContractError when require_all_canonical=True and any
    non-canonical file is present, or when any file is classified as 'unknown'.
    """
    rows = build_raw_data_inventory(root)
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
