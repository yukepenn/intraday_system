"""Guarded legacy → canonical raw layout moves (bytes preserved, dry-run default)."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from intraday.core.errors import DataContractError
from intraday.core.hashing import hash_file
from intraday.data.catalog import build_raw_data_inventory

MoveStatus = Literal["planned", "moved", "skipped_duplicate", "blocked", "error"]


@dataclass(frozen=True)
class LayoutMovePlan:
    """One legacy parquet → canonical parquet path (no bytes rewrite)."""

    source_path: Path
    target_path: Path
    source_size_bytes: int
    source_sha256: str
    symbol: str | None
    year: int | None
    month: int | None
    status_note: str = ""


@dataclass
class LayoutMoveResult:
    """Outcome of applying a canonicalization plan."""

    moves_attempted: int = 0
    moves_completed: int = 0
    skipped_duplicates: int = 0
    blocked: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _canonical_target_for_legacy(ibkr_root: Path, inv_row: dict[str, Any]) -> Path | None:
    if inv_row.get("layout_type") != "legacy_qt_like":
        return None
    asset = inv_row.get("asset")
    sym = inv_row.get("symbol")
    tf = inv_row.get("timeframe")
    year = inv_row.get("year")
    month = inv_row.get("month")
    if asset is None or sym is None or tf is None or year is None or month is None:
        return None
    return (
        ibkr_root
        / f"asset={asset}"
        / f"symbol={sym}"
        / f"timeframe={tf}"
        / f"year={int(year)}"
        / f"month={int(month):02d}"
        / "bars.parquet"
    )


def plan_raw_layout_canonicalization(
    root: Path | str,
    *,
    symbol: str | None = None,
    base: Path | str | None = None,
) -> list[LayoutMovePlan]:
    """Build a move plan for legacy_qt_like parquet files under ``root``."""
    ibkr_root = Path(root).resolve()
    rows = build_raw_data_inventory(ibkr_root, base=base)
    plans: list[LayoutMovePlan] = []
    for inv in rows:
        if inv.get("layout_type") != "legacy_qt_like":
            continue
        if symbol is not None and inv.get("symbol") != symbol:
            continue
        src = Path(inv["resolved_path"])
        if src.suffix.lower() != ".parquet":
            continue
        tgt = _canonical_target_for_legacy(ibkr_root, inv)
        if tgt is None:
            continue
        if not src.exists():
            continue
        st = src.stat()
        sha = hash_file(src)
        plans.append(
            LayoutMovePlan(
                source_path=src,
                target_path=tgt,
                source_size_bytes=int(st.st_size),
                source_sha256=sha,
                symbol=inv.get("symbol"),
                year=inv.get("year"),
                month=inv.get("month"),
            )
        )
    plans.sort(key=lambda p: p.source_path.as_posix())
    return plans


def apply_raw_layout_canonicalization(
    plan: list[LayoutMovePlan],
    *,
    write: bool = False,
) -> LayoutMoveResult:
    """Execute ``plan``. When ``write`` is False, only validates and reports blockers."""
    result = LayoutMoveResult()
    for step in plan:
        result.moves_attempted += 1
        src, tgt = step.source_path, step.target_path
        if not src.exists():
            result.errors.append(f"missing_source: {src}")
            continue
        if tgt.exists():
            if int(tgt.stat().st_size) == step.source_size_bytes:
                if hash_file(tgt) == step.source_sha256:
                    result.skipped_duplicates += 1
                    continue
            msg = f"target_exists_different_bytes: {tgt}"
            result.blocked.append(msg)
            raise DataContractError(msg)
        if not write:
            continue
        tgt.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(src), str(tgt))
        except OSError as exc:
            result.errors.append(f"move_failed {src} -> {tgt}: {exc}")
            raise DataContractError(str(exc)) from exc
        result.moves_completed += 1
    return result


def plan_to_records(plan: list[LayoutMovePlan]) -> list[dict[str, Any]]:
    return [
        {
            "source_path": p.source_path.as_posix(),
            "target_path": p.target_path.as_posix(),
            "source_size_bytes": p.source_size_bytes,
            "source_sha256": p.source_sha256,
            "symbol": p.symbol,
            "year": p.year,
            "month": p.month,
        }
        for p in plan
    ]
