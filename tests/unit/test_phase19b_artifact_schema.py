"""Phase19B artifact schema tests."""

from __future__ import annotations

import csv
from pathlib import Path

ARTIFACT_DIR = (
    Path(__file__).resolve().parents[2] / "artifacts" / "phase19b_core_brooks_pa_strategies"
)

REQUIRED_FILES = (
    "CHATGPT_REVIEW_BUNDLE.md",
    "SOURCE_MAP.csv",
    "chatgpt_key_tables.csv",
    "validation_results.csv",
    "side_mode_validation_summary.md",
    "core_brooks_strategy_inventory.csv",
    "strategy_config_inventory.csv",
    "metadata_inventory.csv",
    "grid_skeleton_inventory.csv",
    "layer1_grid_inspect_summary.csv",
    "side_mode_test_matrix.csv",
    "missing_feature_test_matrix.csv",
    "no_lookahead_session_test_matrix.csv",
    "current10_regression_summary.csv",
    "feature_dependency_matrix.csv",
    "deferred_strategy_or_feature_gaps.md",
    "non_promotion_guardrails.md",
    "artifact_schema_validation.csv",
    "phase19b_decision.md",
)


def _header(name: str) -> list[str]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as f:
        return next(csv.reader(f))


def test_phase19b_required_artifacts_exist() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    assert missing == []


def test_phase19b_key_csv_schemas() -> None:
    assert _header("SOURCE_MAP.csv") == [
        "file_path",
        "purpose",
        "required_for_review",
        "generated_or_source",
        "local_only_dependency",
        "notes",
    ]
    assert _header("chatgpt_key_tables.csv") == [
        "section",
        "item",
        "metric",
        "value",
        "interpretation",
    ]
    assert _header("validation_results.csv") == [
        "name",
        "command",
        "exit_code",
        "status",
        "elapsed_seconds",
        "output_excerpt",
    ]


def test_phase19b_guardrails_document_forbidden_non_runs() -> None:
    text = (ARTIFACT_DIR / "non_promotion_guardrails.md").read_text(encoding="utf-8")
    for phrase in (
        "no actual Layer1 grids",
        "no expanded/full grids",
        "no candidate YAML",
        "no select-dry-run",
        "no promotion",
        "no Layer2/3",
        "no WFO/live/paper",
        "no economic claims",
        "no H2 confirmation",
        "no top-row retuning",
        "strategy inspect / grid-inspect only",
    ):
        assert phrase in text
