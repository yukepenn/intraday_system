from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE15 = ROOT / "artifacts" / "layer1_strategy_library_result_review_phase15"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_phase15_required_csv_artifacts_parse() -> None:
    required = {
        "phase15_input_artifact_parse_validation.csv": {
            "artifact_path",
            "artifact_type",
            "parse_status",
            "expected_columns_status",
            "row_count",
            "issue",
            "notes",
        },
        "cross_window_metric_matrix.csv": {
            "strategy",
            "family",
            "h1_total_accepted_trades",
            "h2_total_accepted_trades",
            "h1_median_total_r",
            "h2_median_total_r",
            "cross_window_pattern",
            "h2_warning_attached",
        },
        "strategy_family_status_matrix.csv": {
            "strategy",
            "family",
            "primary_status",
            "secondary_tags",
            "promotion_ready",
            "focused_grid_ready",
            "rationale",
            "next_action",
        },
        "hold_watch_rationale.csv": {
            "strategy",
            "primary_status",
            "reason_category",
            "evidence_fields",
            "rationale",
            "recommended_handling",
        },
        "focused_grid_candidate_scope.csv": {
            "strategy",
            "family",
            "include_in_future_focused_grid",
            "allowed_axes",
            "forbidden_axes",
            "non_promotion_notes",
        },
        "next_phase_decision_matrix.csv": {
            "possible_next_step",
            "condition_required",
            "recommendation",
            "rationale",
            "allowed",
            "forbidden_followups",
        },
        "chatgpt_key_tables.csv": {"key", "value", "notes"},
        "SOURCE_MAP.csv": {"file", "category", "purpose", "changed", "must_review", "notes"},
        "validation_results.csv": {"command", "status", "exit_code", "notes"},
    }
    for name, expected in required.items():
        rows = _read_csv(PHASE15 / name)
        assert rows, name
        assert expected.issubset(rows[0]), name


def test_phase15_strategy_status_covers_active_universe() -> None:
    expected = {
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
    rows = _read_csv(PHASE15 / "strategy_family_status_matrix.csv")

    assert {row["strategy"] for row in rows} == expected
    assert len(rows) == len(expected)
    assert all(row["primary_status"] for row in rows)
    assert all(row["promotion_ready"] == "false" for row in rows)


def test_phase15_h2_warning_and_non_promotion_are_recorded() -> None:
    key_rows = {row["key"]: row["value"] for row in _read_csv(PHASE15 / "chatgpt_key_tables.csv")}
    assert key_rows["phase14_h2_warning"] == "missing_minute_slots_total=540"
    assert key_rows["new_grid_runs"] == "false"
    assert key_rows["select_dry_run_run"] == "false"
    assert key_rows["candidate_yaml_added"] == "false"
    assert key_rows["layer2_added"] == "false"

    guardrails = (PHASE15 / "non_promotion_guardrails.md").read_text(encoding="utf-8")
    assert "No new Layer1 grids were run." in guardrails
    assert "Phase14 top rows are not candidates." in guardrails
