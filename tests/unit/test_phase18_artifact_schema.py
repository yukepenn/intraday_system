"""Phase18 improvement-design artifact schema checks."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE18 = ROOT / "artifacts" / "existing_10_strategy_improvement_design_phase18"

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
    "phase18_input_artifact_validation.csv": {
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
    "per_strategy_improvement_design_matrix.csv": {
        "strategy",
        "current_surface_status",
        "primary_issue_category",
        "evidence_source",
        "proposed_phase18_action",
        "allowed_change_type",
        "forbidden_change_type",
        "implementation_allowed_next_phase",
        "requires_feature_work",
        "requires_strategy_logic_work",
        "requires_short_side_design",
        "requires_reporting_work",
        "requires_new_grid_later",
        "h2_warning_attached",
        "overfit_risk",
        "proposed_tests",
        "rationale",
        "next_handling",
    },
    "feature_gap_design_matrix.csv": {
        "strategy",
        "feature_gap_or_context_need",
        "existing_feature_available",
        "current_feature_config",
        "proposed_feature_or_context",
        "generic_market_fact",
        "no_lookahead_risk",
        "session_boundary_risk",
        "required_tests",
        "allowed_next_phase",
        "rationale",
        "notes",
    },
    "short_side_feasibility_matrix.csv": {
        "strategy",
        "short_side_feasible",
        "symmetry_type",
        "rationale",
        "required_context",
        "existing_features_sufficient",
        "new_features_needed",
        "risk_of_naive_mirroring",
        "recommended_next_action",
        "required_tests",
        "notes",
    },
    "implementation_priority_matrix.csv": {
        "priority_rank",
        "strategy",
        "improvement_theme",
        "reason",
        "expected_scope",
        "implementation_complexity",
        "overfit_risk",
        "dependency",
        "recommended_next_phase",
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


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_phase18_required_csv_artifacts_parse_and_have_expected_columns() -> None:
    for name, expected in EXPECTED_COLUMNS.items():
        path = PHASE18 / name
        assert path.is_file(), name
        rows = _read_csv(path)
        assert rows, name
        assert expected.issubset(rows[0]), name


def test_phase18_design_matrices_cover_exactly_current_10_strategies() -> None:
    for name in [
        "per_strategy_improvement_design_matrix.csv",
        "feature_gap_design_matrix.csv",
        "short_side_feasibility_matrix.csv",
    ]:
        rows = _read_csv(PHASE18 / name)
        assert {row["strategy"] for row in rows} == STRATEGIES


def test_phase18_per_strategy_matrix_preserves_non_promotion_guardrails() -> None:
    rows = _read_csv(PHASE18 / "per_strategy_improvement_design_matrix.csv")
    assert {row["h2_warning_attached"] for row in rows} == {"true"}
    for row in rows:
        forbidden = row["forbidden_change_type"]
        assert "candidate_promotion" in forbidden
        assert "H2_confirmation" in forbidden
        assert "top_row_retuning" in forbidden


def test_phase18_h2_warning_is_preserved_in_review_artifacts() -> None:
    warning = "missing_minute_slots_total=540"
    for name in [
        "CHATGPT_REVIEW_BUNDLE.md",
        "h2_warning_carryforward.md",
        "phase18_decision.md",
        "candidate_promotion_still_blocked.md",
    ]:
        assert warning in (PHASE18 / name).read_text(encoding="utf-8")

    key_rows = _read_csv(PHASE18 / "chatgpt_key_tables.csv")
    assert any(row["item"] == "H2_warning" and row["value"] == warning for row in key_rows)
