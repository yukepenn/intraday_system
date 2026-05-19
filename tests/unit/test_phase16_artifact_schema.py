"""Phase16 review artifact schema tests."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE16 = ROOT / "artifacts" / "layer1_10_strategy_rational_expanded_grid_phase16"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_phase16_required_csv_artifacts_parse_and_have_expected_columns() -> None:
    required = {
        "SOURCE_MAP.csv": {
            "file_path",
            "purpose",
            "required_for_review",
            "generated_or_source",
            "local_only_dependency",
            "notes",
        },
        "chatgpt_key_tables.csv": {"section", "item", "metric", "value", "interpretation"},
        "validation_results.csv": {"command", "status", "exit_code", "notes"},
        "expanded_grid_axis_rationale.csv": {
            "strategy",
            "axis",
            "values",
            "combo_multiplier",
            "trader_logic_rationale",
            "supported_by_config",
            "supported_by_strategy_validation",
            "risk_of_overfit",
            "notes",
        },
        "expanded_grid_inventory.csv": {
            "strategy",
            "grid_config_path",
            "base_strategy_config",
            "feature_config",
            "combo_count",
            "combo_budget_tier",
            "combo_budget_status",
            "axes_count",
            "supported_fields_ok",
            "max_combo_cap_ok",
            "notes",
        },
        "per_strategy_combo_count.csv": {
            "strategy",
            "combo_count",
            "target_range",
            "within_target_range",
            "exceeds_1500",
            "exceeds_5000",
            "justification_if_large",
            "notes",
        },
        "phase16_run_manifest.csv": {
            "run_id",
            "strategy",
            "symbol",
            "window",
            "start",
            "end",
            "layer1_config",
            "strategy_grid_config",
            "feature_config",
            "execution_mode",
            "artifact_root",
            "run_status",
            "notes",
        },
        "layer1_config_inventory.csv": {
            "strategy",
            "symbol",
            "window",
            "config_path",
            "grid_path",
            "feature_config",
            "artifact_root",
            "combo_count",
            "grid_inspect_status",
            "issue",
            "notes",
        },
        "data_window_quality_summary.csv": {
            "symbol",
            "window",
            "start",
            "end",
            "rows_loaded",
            "full_sessions",
            "data_validation_status",
            "missing_minute_slots_total",
            "warning",
            "interpretation",
        },
        "per_strategy_metric_summary.csv": {
            "strategy",
            "window",
            "combo_count",
            "combos_ran",
            "combos_failed",
            "total_signal_entries",
            "total_valid_intents",
            "total_accepted_trades",
            "total_rejected_trades",
            "combos_with_zero_signals",
            "combos_with_zero_accepted_trades",
            "best_total_r",
            "median_total_r",
            "p25_total_r",
            "p75_total_r",
            "best_profit_factor_r",
            "median_profit_factor_r",
            "worst_max_drawdown_r",
            "median_max_drawdown_r",
            "notes",
        },
        "risk_per_share_distribution.csv": {
            "strategy",
            "window",
            "risk_bucket",
            "trade_count",
            "avg_risk_per_share",
            "median_risk_per_share",
            "p10_risk_per_share",
            "p90_risk_per_share",
            "avg_realized_r",
            "median_realized_r",
            "notes",
        },
        "cost_to_risk_summary.csv": {
            "strategy",
            "window",
            "cost_to_risk_bucket",
            "trade_count",
            "avg_cost_to_risk",
            "median_cost_to_risk",
            "avg_realized_r",
            "median_realized_r",
            "warning",
            "notes",
        },
        "drawdown_summary.csv": {
            "strategy",
            "window",
            "combo_count",
            "median_max_drawdown_r",
            "p75_max_drawdown_r",
            "worst_max_drawdown_r",
            "drawdown_warning_count",
            "notes",
        },
        "sample_adequacy_summary.csv": {
            "strategy",
            "window",
            "combo_count",
            "median_accepted_trades",
            "p25_accepted_trades",
            "combos_below_min_sample",
            "zero_trade_combos",
            "sample_adequacy_label",
            "notes",
        },
        "zero_trade_zero_signal_summary.csv": {
            "strategy",
            "window",
            "combo_count",
            "zero_signal_combos",
            "zero_valid_intent_combos",
            "zero_accepted_trade_combos",
            "notes",
        },
        "rejection_skip_reason_summary.csv": {
            "strategy",
            "window",
            "reject_reason",
            "count",
            "notes",
        },
        "feature_signal_hash_summary.csv": {
            "strategy",
            "window",
            "feature_hash_count",
            "primary_feature_hash",
            "signal_hash_count",
            "primary_signal_hash",
            "notes",
        },
        "preliminary_region_summary.csv": {
            "strategy",
            "window",
            "region_key",
            "region_definition",
            "combo_count",
            "median_total_r",
            "p25_total_r",
            "p75_total_r",
            "median_max_drawdown_r",
            "median_accepted_trades",
            "preliminary_observation",
            "phase17_review_required",
        },
        "future_strategy_logic_improvement_backlog.csv": {
            "strategy",
            "desired_axis_or_feature",
            "reason",
            "current_blocker",
            "suggested_future_phase",
            "notes",
        },
        "artifact_schema_validation.csv": {
            "artifact_path",
            "artifact_type",
            "parse_ok",
            "expected_columns_ok",
            "row_count",
            "issue",
            "notes",
        },
    }
    for name, expected in required.items():
        rows = _read_csv(PHASE16 / name)
        assert rows, name
        assert expected.issubset(rows[0]), name


def test_phase16_h2_warning_and_runtime_blocker_are_recorded() -> None:
    quality_rows = {
        row["window"]: row for row in _read_csv(PHASE16 / "data_window_quality_summary.csv")
    }
    assert quality_rows["qqq_2024h2"]["missing_minute_slots_total"] == "540"
    assert "not clean confirmation" in quality_rows["qqq_2024h2"]["interpretation"]

    manifest = _read_csv(PHASE16 / "phase16_run_manifest.csv")
    statuses = {row["run_status"] for row in manifest}
    assert "blocked_runtime" in statuses
    assert "not_run_due_runtime_blocker" in statuses
