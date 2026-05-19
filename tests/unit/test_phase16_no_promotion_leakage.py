"""Phase16 guardrails against promotion/runtime leakage."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE16 = ROOT / "artifacts" / "layer1_10_strategy_rational_expanded_grid_phase16"


def test_phase16_did_not_create_candidate_yaml_or_layer2_runtime_configs() -> None:
    candidate_root = ROOT / "configs" / "candidates"
    candidate_yamls = (
        [p for p in candidate_root.rglob("*") if p.suffix.lower() in {".yaml", ".yml"}]
        if candidate_root.exists()
        else []
    )
    assert candidate_yamls == []

    forbidden_config_parts = {"layer2", "layer3", "wfo", "live", "paper"}
    phase16_configs = list((ROOT / "configs").rglob("*phase16*"))
    leaked = [
        p
        for p in phase16_configs
        if p.suffix.lower() in {".yaml", ".yml"}
        and any(part.lower() in forbidden_config_parts for part in p.parts)
    ]
    assert leaked == []


def test_phase16_artifacts_exclude_heavy_runtime_outputs() -> None:
    forbidden_suffixes = {".parquet", ".npy", ".npz"}
    forbidden_name_fragments = {
        "row_level_trades",
        "equity_curve",
        "top_runs",
        "memmap",
    }
    bad = []
    for path in PHASE16.rglob("*"):
        if not path.is_file():
            continue
        lowered = path.name.lower()
        if path.suffix.lower() in forbidden_suffixes:
            bad.append(path)
        elif any(fragment in lowered for fragment in forbidden_name_fragments):
            bad.append(path)
    assert bad == []


def test_phase16_guardrail_docs_record_non_runs_and_codex_review_untouched() -> None:
    guardrails = (PHASE16 / "non_promotion_guardrails.md").read_text(encoding="utf-8")
    assert "No candidate YAML was created." in guardrails
    assert "No Layer1 select-dry-run was run." in guardrails
    assert "No Layer2 work was created or run." in guardrails
    assert "No WFO or mini-WFO was run." in guardrails

    source_map = (PHASE16 / "SOURCE_MAP.csv").read_text(encoding="utf-8")
    assert "CODEX_REVIEW.md" not in source_map
