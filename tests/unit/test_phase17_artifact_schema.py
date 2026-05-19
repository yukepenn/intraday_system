"""Phase17 region-review artifact schema checks."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE17 = ROOT / "artifacts" / "layer1_10_strategy_expanded_grid_region_review_phase17"

STRATEGIES = {
    "pa_buy_sell_close_trend",
    "orb_continuation",
    "orb_retest_continuation",
    "failed_orb",
    "gap_acceptance_failure",
    "vwap_trend_pullback",
    "vwap_reclaim_reject",
    "prior_day_level_trap",
    "cci_extreme_snapback",
    "stochastic_oversold_cross",
}

EXPECTED_COLUMNS = {
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
    "phase17_input_artifact_validation.csv": {
        "artifact_path",
        "artifact_type",
        "required",
        "available",
        "parse_ok",
        "expected_columns_ok",
        "row_count",
        "local_only_dependency",
        "issue",
        "notes",
    },
    "strategy_surface_status_matrix.csv": {
        "strategy",
        "family",
        "h1_status",
        "h2_status",
        "combined_surface_status",
        "promotion_ready",
        "candidate_yaml_allowed",
        "h2_warning_attached",
    },
    "parameter_region_summary.csv": {
        "strategy",
        "window",
        "region_key",
        "region_definition",
        "axis_group",
        "combo_count",
        "median_total_r",
        "p25_total_r",
        "p75_total_r",
        "median_max_drawdown_r",
        "median_accepted_trades",
        "robust_region_label",
    },
    "top_neighborhood_summary.csv": {
        "strategy",
        "window",
        "top_combo_id",
        "top_metric",
        "top_metric_value",
        "neighborhood_combo_count",
        "neighborhood_median_total_r",
        "neighborhood_robust",
    },
    "isolated_top_row_warning.csv": {
        "strategy",
        "window",
        "combo_id",
        "metric",
        "metric_value",
        "neighborhood_median",
        "warning_level",
    },
    "axis_marginal_summary.csv": {
        "strategy",
        "window",
        "axis",
        "axis_value",
        "combo_count",
        "median_total_r",
        "marginal_interpretation",
    },
    "pairwise_interaction_summary.csv": {
        "strategy",
        "window",
        "axis_a",
        "value_a",
        "axis_b",
        "value_b",
        "combo_count",
        "interaction_interpretation",
    },
    "h1_h2_cross_window_region_matrix.csv": {
        "strategy",
        "region_key",
        "h1_combo_count",
        "h2_combo_count",
        "h1_median_total_r",
        "h2_median_total_r",
        "cross_window_label",
        "h2_warning_attached",
    },
    "drawdown_region_summary.csv": {
        "strategy",
        "window",
        "region_key",
        "combo_count",
        "median_max_drawdown_r",
        "p75_max_drawdown_r",
        "worst_max_drawdown_r",
        "drawdown_label",
    },
    "risk_cost_region_summary.csv": {
        "strategy",
        "window",
        "region_key",
        "combo_count",
        "median_risk_per_share",
        "median_cost_to_risk",
        "risk_cost_label",
    },
    "sample_adequacy_region_summary.csv": {
        "strategy",
        "window",
        "region_key",
        "combo_count",
        "median_accepted_trades",
        "zero_trade_combo_count",
        "sample_adequacy_label",
    },
    "strategy_improvement_backlog.csv": {
        "strategy",
        "issue_type",
        "priority",
        "evidence",
        "proposed_phase",
        "proposed_change",
        "allowed_in_phase18",
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


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_phase17_required_csv_artifacts_parse_and_have_expected_columns() -> None:
    for name, expected in EXPECTED_COLUMNS.items():
        path = PHASE17 / name
        assert path.is_file(), name
        rows = _read_csv(path)
        assert rows, name
        assert expected.issubset(rows[0]), name


def test_phase17_strategy_surface_matrix_covers_all_10_and_forbids_promotion() -> None:
    rows = _read_csv(PHASE17 / "strategy_surface_status_matrix.csv")
    assert {row["strategy"] for row in rows} == STRATEGIES
    assert {row["promotion_ready"] for row in rows} == {"false"}
    assert {row["candidate_yaml_allowed"] for row in rows} == {"false"}
    assert {row["h2_warning_attached"] for row in rows} == {"true"}


def test_phase17_h2_warning_is_preserved_in_review_artifacts() -> None:
    warning = "missing_minute_slots_total=540"
    for name in [
        "CHATGPT_REVIEW_BUNDLE.md",
        "h2_warning_interpretation.md",
        "phase17_decision.md",
    ]:
        assert warning in (PHASE17 / name).read_text(encoding="utf-8")

    key_rows = _read_csv(PHASE17 / "chatgpt_key_tables.csv")
    assert any(row["item"] == "H2_warning" and row["value"] == warning for row in key_rows)
