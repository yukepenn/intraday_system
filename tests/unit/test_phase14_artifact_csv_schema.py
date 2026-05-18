"""Phase 14 artifact CSV parse/schema sanity checks."""

from __future__ import annotations

import csv
from pathlib import Path

from intraday.core.paths import repo_root

PHASE14_ROOT = Path("artifacts/layer1_strategy_library_small_grid_phase14")

EXPECTED_COLUMNS = {
    PHASE14_ROOT / "SOURCE_MAP.csv": [
        "file",
        "category",
        "purpose",
        "changed",
        "must_review",
        "notes",
    ],
    PHASE14_ROOT / "chatgpt_key_tables.csv": ["key", "value", "notes"],
    PHASE14_ROOT / "validation_results.csv": ["command", "status", "exit_code", "notes"],
    PHASE14_ROOT / "artifact_schema_validation.csv": [
        "artifact_path",
        "artifact_type",
        "parse_ok",
        "expected_columns_ok",
        "row_count",
        "issue",
        "notes",
    ],
    PHASE14_ROOT / "phase14_run_manifest.csv": [
        "run_id",
        "strategy",
        "family",
        "symbol",
        "window",
        "start",
        "end",
        "layer1_config",
        "feature_config",
        "strategy_grid_config",
        "artifact_root",
        "run_status",
        "notes",
    ],
    PHASE14_ROOT / "layer1_config_inventory.csv": [
        "strategy",
        "symbol",
        "window",
        "config_path",
        "strategy_grid_path",
        "feature_config",
        "artifact_root",
        "combo_count",
        "inspect_status",
        "issue",
        "notes",
    ],
    PHASE14_ROOT / "per_strategy_grid_summary.csv": [
        "strategy",
        "family",
        "symbol",
        "window",
        "combo_count",
        "combos_ran",
        "combos_failed",
        "total_signal_entries",
        "total_valid_intents",
        "total_executed_results",
        "total_accepted_trades",
        "total_rejected_trades",
        "combos_with_zero_signals",
        "combos_with_zero_valid_intents",
        "combos_with_zero_accepted_trades",
        "best_total_r_combo_id",
        "best_total_r",
        "best_profit_factor_combo_id",
        "best_profit_factor_r",
        "median_total_r",
        "min_total_r",
        "max_drawdown_r_worst",
        "notes",
    ],
    PHASE14_ROOT / "per_strategy_health_summary.csv": [
        "strategy",
        "window",
        "loader_ok",
        "feature_build_ok",
        "signal_generation_ok",
        "intent_adapter_ok",
        "execution_ok",
        "artifact_write_ok",
        "grid_inspect_ok",
        "run_status",
        "primary_blocker",
        "diagnostic_health_label",
        "notes",
    ],
    PHASE14_ROOT / "skip_reject_summary.csv": [
        "strategy",
        "window",
        "combo_id",
        "signal_entries",
        "valid_intents",
        "executed_results",
        "accepted_trades",
        "rejected_trades",
        "skip_reason_counts_json",
        "adapter_skip_reasons_json",
        "exit_reason_counts_json",
        "reject_reason_counts_json",
    ],
    PHASE14_ROOT / "feature_signal_hash_summary.csv": [
        "strategy",
        "window",
        "combo_id",
        "feature_config",
        "feature_hash",
        "signal_hash",
        "config_hash",
        "params_json",
        "notes",
    ],
    PHASE14_ROOT / "repaired_phase13_artifacts_summary.csv": [
        "artifact_path",
        "issue_before",
        "repair_action",
        "parse_ok_after",
        "notes",
    ],
    PHASE14_ROOT / "data_availability_summary.csv": [
        "symbol",
        "window",
        "start",
        "end",
        "data_root",
        "validate_curated_status",
        "load_bars_status",
        "rows_loaded",
        "issue",
        "notes",
    ],
    Path("artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/SOURCE_MAP.csv"): [
        "file",
        "category",
        "purpose",
        "changed",
        "must_review",
        "notes",
    ],
    Path("artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/chatgpt_key_tables.csv"): [
        "key",
        "value",
        "notes",
    ],
    Path("artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/validation_results.csv"): [
        "command",
        "status",
        "notes",
    ],
    Path("artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/strategy_inventory.csv"): [
        "strategy",
        "family",
        "version",
        "required_feature_set",
        "feature_config",
        "setup_code",
        "long_only_mvp",
        "base_yaml",
        "grid_yaml",
        "metadata_yaml",
        "tests",
        "status",
    ],
    Path(
        "artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/feature_requirements_matrix.csv"
    ): [
        "strategy",
        "required_feature_set",
        "feature_column",
        "source_group",
        "available_now",
        "added_in_phase13",
        "no_lookahead_risk",
        "notes",
    ],
    Path("artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/config_inventory.csv"): [
        "config_path",
        "config_type",
        "strategy_or_feature_set",
        "combo_count_if_grid",
        "runtime_truth",
        "notes",
    ],
    Path(
        "artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/phase14_readiness_matrix.csv"
    ): [
        "strategy",
        "loader_ok",
        "base_yaml_ok",
        "grid_yaml_ok",
        "feature_config_ok",
        "synthetic_signal_test_ok",
        "no_lookahead_test_ok",
        "ready_for_phase14_small_grid",
        "blockers",
    ],
}


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), list(reader)


def test_phase14_and_repaired_phase13_csv_artifacts_parse() -> None:
    root = repo_root()
    for rel_path, expected in EXPECTED_COLUMNS.items():
        path = root / rel_path
        assert path.is_file(), rel_path
        header, rows = _read_csv(path)
        assert header == expected, rel_path
        assert len(rows) >= 1, rel_path
        assert header != list(",".join(expected)), rel_path
        assert all(len(col) > 1 or col in {"R"} for col in header), rel_path
