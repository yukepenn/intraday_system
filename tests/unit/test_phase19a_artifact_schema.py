"""Phase19A artifact schema tests."""

from __future__ import annotations

import csv
from pathlib import Path

ARTIFACT_DIR = Path("artifacts/phase19a_side_support_brooks_feature_foundation")

REQUIRED_ARTIFACTS = {
    "CHATGPT_REVIEW_BUNDLE.md",
    "SOURCE_MAP.csv",
    "chatgpt_key_tables.csv",
    "validation_results.csv",
    "swing_core_packaging_decision.md",
    "side_support_implementation_summary.md",
    "side_support_test_matrix.csv",
    "brooks_feature_slice_decision.md",
    "brooks_feature_config_inventory.csv",
    "brooks_feature_test_matrix.csv",
    "current10_backward_compatibility_summary.csv",
    "implementation_scope_deferred_items.md",
    "non_promotion_guardrails.md",
    "artifact_schema_validation.csv",
    "phase19a_decision.md",
}


def _read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_phase19a_required_artifacts_exist() -> None:
    missing = [name for name in sorted(REQUIRED_ARTIFACTS) if not (ARTIFACT_DIR / name).exists()]
    assert missing == []


def test_phase19a_artifacts_are_csv_or_md_only() -> None:
    files = [path for path in ARTIFACT_DIR.rglob("*") if path.is_file()]
    assert files
    assert {path.suffix for path in files} <= {".csv", ".md"}


def test_phase19a_source_map_schema() -> None:
    rows = _read_csv("SOURCE_MAP.csv")
    assert rows
    assert set(rows[0]) == {
        "file_path",
        "purpose",
        "required_for_review",
        "generated_or_source",
        "local_only_dependency",
        "notes",
    }


def test_phase19a_key_tables_required_metrics() -> None:
    rows = _read_csv("chatgpt_key_tables.csv")
    metrics = {row["metric"]: row["value"] for row in rows}
    assert metrics["phase"] == "PHASE19A_IMPLEMENT_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION_SLICE"
    assert metrics["side_support_implemented"] == "true"
    assert metrics["current_default_long_only_preserved"] == "true"
    assert metrics["brooks_feature_configs_created_count"] == "2"
    assert metrics["strategies_11_to_20_created"] == "false"
    assert metrics["actual_layer1_grid_runs"] == "0"
    assert metrics["candidate_yaml_created"] == "false"
    assert metrics["select_dry_run_run"] == "false"
    assert metrics["layer2_created"] == "false"
    assert metrics["wfo_run"] == "false"
    assert metrics["live_paper_run"] == "false"
    assert metrics["economic_claims_made"] == "false"


def test_phase19a_guardrails_include_required_non_runs() -> None:
    text = (ARTIFACT_DIR / "non_promotion_guardrails.md").read_text(encoding="utf-8")
    for needle in (
        "no candidate YAML",
        "no promotion",
        "no select-dry-run",
        "no Layer2/3",
        "no WFO/live/paper",
        "no strategies 11-20 implementation",
        "no actual Layer1 grid",
        "no economic claims",
        "no H2 confirmation",
        "no top-row retuning",
    ):
        assert needle in text
