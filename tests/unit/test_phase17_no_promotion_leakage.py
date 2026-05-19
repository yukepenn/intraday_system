"""Phase17 guardrails: review-only artifacts, no promotion leakage."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE17 = ROOT / "artifacts" / "layer1_10_strategy_expanded_grid_region_review_phase17"


def test_phase17_guardrails_forbid_runtime_promotion_paths() -> None:
    text = (PHASE17 / "non_promotion_guardrails.md").read_text(encoding="utf-8")
    required = [
        "No new Layer1 grids were run.",
        "No Layer1 select-dry-run was run.",
        "No candidate YAML was created.",
        "No promotion was performed.",
        "No Layer2 work was created or run.",
        "No Layer3 work was created or run.",
        "No WFO or mini-WFO was run.",
        "No live/paper config or run was created.",
        "No strategy retuning was performed.",
        "No feature semantic changes were made.",
        "No execution truth changes were made.",
        "Top rows are not candidates.",
        "H2 is not confirmation.",
        "Phase17 classifications are diagnostic only.",
    ]
    for phrase in required:
        assert phrase in text


def test_phase17_did_not_create_candidate_or_layer_runtime_yaml() -> None:
    candidate_yamls = [
        p
        for p in (ROOT / "configs" / "candidates").rglob("*")
        if p.suffix.lower() in {".yaml", ".yml"}
    ]
    assert candidate_yamls == []

    forbidden_parts = {"layer2", "layer3", "wfo", "live", "paper"}
    phase17_yamls = [
        p for p in (ROOT / "configs").rglob("*phase17*") if p.suffix.lower() in {".yaml", ".yml"}
    ]
    assert phase17_yamls == []

    leaked_runtime_configs = [
        p
        for p in (ROOT / "configs").rglob("*")
        if p.suffix.lower() in {".yaml", ".yml"}
        and any(part.lower() in forbidden_parts for part in p.parts)
        and "README" not in p.name.upper()
    ]
    assert leaked_runtime_configs == []


def test_phase17_artifacts_exclude_heavy_or_row_level_outputs() -> None:
    forbidden_suffixes = {".parquet", ".npy", ".npz", ".memmap"}
    forbidden_name_fragments = {
        "row_level_trades",
        "row_level_equity",
        "equity_curve",
        "top_runs",
        "memmap",
    }
    bad = []
    for path in PHASE17.rglob("*"):
        if not path.is_file():
            continue
        lowered = path.name.lower()
        if path.suffix.lower() in forbidden_suffixes:
            bad.append(path)
        elif any(fragment in lowered for fragment in forbidden_name_fragments):
            bad.append(path)
    assert bad == []


def test_phase17_source_map_keeps_codex_review_untouched() -> None:
    source_map = (PHASE17 / "SOURCE_MAP.csv").read_text(encoding="utf-8")
    assert "CODEX_REVIEW.md" not in source_map

    status = subprocess.run(
        ["git", "status", "--short", "--", "CODEX_REVIEW.md"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert status.stdout.strip() == ""
