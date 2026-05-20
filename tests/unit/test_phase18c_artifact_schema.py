"""Phase18C artifact schema checks."""

from __future__ import annotations

import csv

from intraday.core.paths import repo_root

ARTIFACT_DIR = repo_root() / "artifacts/existing_10_strategy_refinement_repair_phase18c"

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
    "v2_runtime_field_inventory.csv": [
        "strategy",
        "field",
        "config_section",
        "used_in_strategy_logic",
        "runtime_conversion",
        "validator_function",
        "validated_finite",
        "validated_range",
        "validated_type",
        "branch_test_exists",
        "missing_feature_test_exists",
        "no_lookahead_test_exists",
        "repair_needed",
        "repair_status",
        "notes",
    ],
    "validation_gap_repair_matrix.csv": [
        "strategy",
        "field",
        "gap_type",
        "repair_action",
        "validator_added_or_confirmed",
        "test_name",
        "status",
        "notes",
    ],
    "branch_behavior_test_matrix.csv": [
        "strategy",
        "branch_name",
        "option_fields",
        "test_name",
        "behavior_tested",
        "expected_effect",
        "status",
        "notes",
    ],
    "missing_feature_test_matrix.csv": [
        "strategy",
        "option_field",
        "required_feature_column",
        "test_name",
        "missing_feature_behavior",
        "status",
        "notes",
    ],
    "no_lookahead_branch_test_matrix.csv": [
        "strategy",
        "branch_name",
        "test_name",
        "session_reset_tested",
        "future_perturbation_tested",
        "current_bar_self_count_prevented",
        "helper_level_or_branch_level",
        "status",
        "notes",
    ],
    "deferred_branch_decisions.csv": [
        "strategy",
        "branch_or_field",
        "reason_deferred",
        "risk_if_left_enabled",
        "disabled_or_deferred",
        "future_phase",
        "notes",
    ],
    "backward_compatibility_recheck.csv": [
        "strategy",
        "v1_config_still_valid",
        "v2_config_still_valid",
        "default_behavior_preserved",
        "tests",
        "status",
        "notes",
    ],
    "artifact_schema_validation.csv": ["artifact", "required_columns", "parse_status", "notes"],
}

REQUIRED_MARKDOWN = (
    "CHATGPT_REVIEW_BUNDLE.md",
    "non_promotion_guardrails.md",
    "phase18c_decision.md",
)


def test_phase18c_required_csv_artifacts_are_parseable() -> None:
    for name, expected_header in REQUIRED_SCHEMAS.items():
        path = ARTIFACT_DIR / name
        assert path.is_file(), name
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == expected_header
            rows = list(reader)
        assert rows, name


def test_phase18c_required_markdown_artifacts_exist() -> None:
    for name in REQUIRED_MARKDOWN:
        path = ARTIFACT_DIR / name
        assert path.is_file(), name
        assert path.read_text(encoding="utf-8").strip()


def test_phase18c_key_guardrail_metrics() -> None:
    with (ARTIFACT_DIR / "chatgpt_key_tables.csv").open(newline="", encoding="utf-8") as f:
        rows = {row["metric"]: row["value"] for row in csv.DictReader(f)}
    assert rows["strategies_covered_count"] == "10"
    assert int(rows["runtime_fields_inventoried_count"]) >= 80
    assert rows["new_grid_runs"] == "false"
    assert rows["candidate_yaml_created"] == "false"
    assert rows["select_dry_run_run"] == "false"
    assert rows["layer2_created"] == "false"
    assert rows["execution_truth_changed"] == "false"
