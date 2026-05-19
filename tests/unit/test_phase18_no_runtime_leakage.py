"""Phase18 guardrails: design-only artifacts, no runtime leakage."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE18 = ROOT / "artifacts" / "existing_10_strategy_improvement_design_phase18"


def test_phase18_non_goals_forbid_runtime_paths() -> None:
    text = (PHASE18 / "phase18_non_goals.md").read_text(encoding="utf-8")
    required = [
        "no runtime strategy changes",
        "no feature implementation",
        "no new grids",
        "no select-dry-run",
        "no candidate YAML",
        "no promotion",
        "no Layer2/3",
        "no WFO/live/paper",
        "no H2 confirmation",
        "no top-row retuning",
    ]
    for phrase in required:
        assert phrase in text


def test_phase18_did_not_create_candidate_or_layer_runtime_yaml() -> None:
    candidate_yamls = [
        p
        for p in (ROOT / "configs" / "candidates").rglob("*")
        if p.suffix.lower() in {".yaml", ".yml"}
    ]
    assert candidate_yamls == []

    phase18_yamls = [
        p for p in (ROOT / "configs").rglob("*phase18*") if p.suffix.lower() in {".yaml", ".yml"}
    ]
    assert phase18_yamls == []

    forbidden_parts = {"layer2", "layer3", "wfo", "live", "paper"}
    leaked_runtime_configs = [
        p
        for p in (ROOT / "configs").rglob("*")
        if p.suffix.lower() in {".yaml", ".yml"}
        and any(part.lower() in forbidden_parts for part in p.parts)
        and "README" not in p.name.upper()
    ]
    assert leaked_runtime_configs == []


def test_phase18_artifacts_exclude_heavy_or_row_level_outputs() -> None:
    forbidden_suffixes = {".parquet", ".npy", ".npz", ".memmap"}
    forbidden_name_fragments = {
        "row_level_trades",
        "row_level_equity",
        "equity_curve",
        "top_runs",
        "memmap",
        "sweep_results",
    }
    bad = []
    for path in PHASE18.rglob("*"):
        if not path.is_file():
            continue
        lowered = path.name.lower()
        if path.suffix.lower() in forbidden_suffixes:
            bad.append(path)
        elif any(fragment in lowered for fragment in forbidden_name_fragments):
            bad.append(path)
    assert bad == []


def test_phase18_source_map_marks_local_runs_local_only_and_codex_untouched() -> None:
    source_map = (PHASE18 / "SOURCE_MAP.csv").read_text(encoding="utf-8")
    assert "artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/" in source_map
    assert "true,do not stage" in source_map or "true,not read directly" in source_map
    assert "CODEX_REVIEW.md" in source_map
    assert "read only; not edited" in source_map

    status = subprocess.run(
        ["git", "status", "--short", "--", "CODEX_REVIEW.md"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert status.stdout.strip() == ""
