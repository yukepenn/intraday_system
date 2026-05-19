"""Phase18B artifact schema checks."""

from __future__ import annotations

import csv

from intraday.core.paths import repo_root

ARTIFACT_DIR = repo_root() / "artifacts/existing_10_strategy_refinement_phase18b"

REQUIRED_SCHEMAS = {
    "SOURCE_MAP.csv": [
        "file_path",
        "purpose",
        "required_for_review",
        "generated_or_source",
        "local_only_dependency",
        "notes",
    ],
    "chatgpt_key_tables.csv": ["section", "item", "metric", "value", "interpretation"],
    "validation_results.csv": ["command", "status", "notes"],
    "approved_refinement_scope.csv": [
        "strategy",
        "approved_refinement",
        "source_phase18_evidence",
        "implemented",
        "deferred",
        "reason_if_deferred",
        "overfit_risk",
        "tests_required",
        "notes",
    ],
    "v2_feature_config_inventory.csv": [
        "feature_config",
        "purpose",
        "feature_groups_enabled",
        "new_feature_columns",
        "existing_feature_columns",
        "no_lookahead_tests",
        "session_tests",
        "notes",
    ],
    "v2_strategy_config_inventory.csv": [
        "strategy",
        "base_config_v2",
        "grid_config_v2",
        "metadata_updated",
        "required_feature_config",
        "new_optional_parameters",
        "default_backward_compatible",
        "notes",
    ],
    "v2_grid_skeleton_inventory.csv": [
        "strategy",
        "grid_config",
        "combo_count",
        "intended_use",
        "broad_sweep_allowed",
        "grid_inspect_status",
        "notes",
    ],
    "no_lookahead_test_summary.csv": [
        "strategy",
        "test_name",
        "logic_branch",
        "session_reset_tested",
        "future_perturbation_tested",
        "current_bar_self_count_prevented",
        "status",
        "notes",
    ],
    "grid_inspect_summary.csv": [
        "config_path",
        "strategy",
        "grid_path",
        "feature_config",
        "combo_count",
        "inspect_status",
        "notes",
    ],
    "backward_compatibility_report.csv": [
        "strategy",
        "v1_config_still_valid",
        "v1_default_behavior_preserved",
        "compatibility_notes",
        "tests",
        "status",
    ],
    "artifact_schema_validation.csv": ["artifact", "required_columns", "parse_status", "notes"],
}

REQUIRED_MARKDOWN = (
    "CHATGPT_REVIEW_BUNDLE.md",
    "feature_config_change_log.md",
    "strategy_logic_change_log.md",
    "config_validation_change_log.md",
    "short_side_deferred_plan.md",
    "non_promotion_guardrails.md",
    "phase18b_decision.md",
)


def test_phase18b_required_csv_artifacts_are_parseable() -> None:
    for name, expected_header in REQUIRED_SCHEMAS.items():
        path = ARTIFACT_DIR / name
        assert path.is_file(), name
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == expected_header
            rows = list(reader)
        assert rows, name


def test_phase18b_required_markdown_artifacts_exist() -> None:
    for name in REQUIRED_MARKDOWN:
        path = ARTIFACT_DIR / name
        assert path.is_file(), name
        assert path.read_text(encoding="utf-8").strip()


def test_phase18b_key_guardrail_metrics() -> None:
    with (ARTIFACT_DIR / "chatgpt_key_tables.csv").open(newline="", encoding="utf-8") as f:
        rows = {row["metric"]: row["value"] for row in csv.DictReader(f)}
    assert rows["strategies_covered_count"] == "10"
    assert rows["new_grid_runs"] == "false"
    assert rows["candidate_yaml_created"] == "false"
    assert rows["select_dry_run_run"] == "false"
    assert rows["layer2_created"] == "false"
    assert rows["execution_truth_changed"] == "false"
