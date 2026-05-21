"""Phase19 design-only artifact schema checks.

Design-only test. Asserts that the Phase19 design artifact bundle is
present, contains only CSV/MD audit artifacts, and that key tables /
matrices follow the documented schema. Does not validate any runtime
behavior.
"""

from __future__ import annotations

import csv
from pathlib import Path

ARTIFACT_DIR = Path("artifacts/phase19_brooks_pa_design")

REQUIRED_ARTIFACTS = {
    "CHATGPT_REVIEW_BUNDLE.md",
    "SOURCE_MAP.csv",
    "chatgpt_key_tables.csv",
    "validation_results.csv",
    "side_support_design.md",
    "side_support_test_plan.csv",
    "brooks_pa_feature_foundation_design.md",
    "brooks_pa_feature_audit_matrix.csv",
    "brooks_pa_strategy_design_matrix.csv",
    "brooks_pa_strategy_specs.md",
    "brooks_pa_duplicate_avoidance_matrix.csv",
    "phase19_file_plan.csv",
    "phase19_test_plan.csv",
    "phase19_validation_plan.md",
    "phase19_non_goals.md",
    "non_promotion_guardrails.md",
    "phase19_design_decision.md",
    "artifact_schema_validation.csv",
}

PHASE19_STRATEGIES = {
    "pa_second_entry_pullback",
    "pa_trading_range_bls_hs",
    "pa_failed_breakout_trap",
    "pa_opening_reversal_sr",
    "pa_breakout_pullback_continuation",
    "pa_tight_channel_pullback",
    "pa_broad_channel_zone",
    "pa_mtr_reversal_diagnostic",
    "pa_wedge_reversal_diagnostic",
    "pa_climax_reversal_diagnostic",
}

CURRENT10_DUPLICATES_REJECTED = {
    "pa_opening_breakout_continuation",
    "pa_gap_open_reversal_failure",
    "pa_prior_day_level_trap",
    "pa_vwap_reclaim_reject",
    "pa_orb_retest",
    "pa_orb_continuation",
}


def _read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_phase19_required_artifacts_exist() -> None:
    missing = [name for name in sorted(REQUIRED_ARTIFACTS) if not (ARTIFACT_DIR / name).exists()]
    assert missing == []


def test_phase19_strategy_design_matrix_covers_all_ten() -> None:
    rows = _read_csv("brooks_pa_strategy_design_matrix.csv")
    assert {row["strategy"] for row in rows} == PHASE19_STRATEGIES
    numbers = {int(row["strategy_number"]) for row in rows}
    assert numbers == set(range(11, 21))


def test_phase19_strategy_design_matrix_setup_codes_disjoint_from_current10() -> None:
    rows = _read_csv("brooks_pa_strategy_design_matrix.csv")
    long_codes = {int(row["setup_code_long"]) for row in rows}
    short_codes = {int(row["setup_code_short"]) for row in rows}
    assert long_codes == set(range(7101, 7111))
    assert short_codes == set(range(7201, 7211))
    current10_codes = {1001, 2001, 2002, 2003, 3001, 4001, 4002, 5001, 6001, 6002}
    assert long_codes.isdisjoint(current10_codes)
    assert short_codes.isdisjoint(current10_codes)


def test_phase19_duplicate_avoidance_matrix_rejects_current10_duplicates() -> None:
    rows = _read_csv("brooks_pa_duplicate_avoidance_matrix.csv")
    rejected = {
        row["proposed_strategy"] for row in rows if row["keep_or_reject"].startswith("reject")
    }
    missing = CURRENT10_DUPLICATES_REJECTED - rejected
    assert missing == set(), f"Phase19 duplicate-avoidance matrix must reject: {missing}"


def test_phase19_chatgpt_key_tables_metrics_present() -> None:
    rows = _read_csv("chatgpt_key_tables.csv")
    metrics = {row["metric"]: row["value"] for row in rows}
    assert metrics["name"].startswith("PHASE19_DESIGN_BROOKS_PA_STRATEGIES_11_TO_20")
    assert metrics["strategies_designed_count"] == "10"
    assert metrics["side_support_design_created"] == "true"
    assert metrics["brooks_feature_foundation_designed"] == "true"
    assert metrics["implementation_code_written"] == "false"
    assert metrics["runtime_configs_created"] == "false"
    assert metrics["actual_layer1_grid_runs"] == "0"
    assert metrics["candidate_yaml_created"] == "false"
    assert metrics["select_dry_run_run"] == "false"
    assert metrics["layer2_created"] == "false"
    assert metrics["wfo_run"] == "false"
    assert metrics["live_paper_run"] == "false"
    assert metrics["economic_claims_made"] == "false"
    assert metrics["decision"] == "PHASE19_BROOKS_PA_DESIGN_COMPLETE"


def test_phase19_side_support_test_plan_has_required_columns() -> None:
    rows = _read_csv("side_support_test_plan.csv")
    assert rows
    expected_columns = {
        "test_area",
        "test_name",
        "purpose",
        "expected_behavior",
        "required_before_strategy_short",
        "notes",
    }
    assert set(rows[0].keys()) == expected_columns


def test_phase19_feature_audit_matrix_columns() -> None:
    rows = _read_csv("brooks_pa_feature_audit_matrix.csv")
    assert rows
    expected_columns = {
        "feature_group",
        "feature_name",
        "market_fact",
        "no_lookahead_risk",
        "session_reset_required",
        "requires_new_kernel",
        "can_use_existing_feature",
        "strategy_specific_label_rejected",
        "notes",
    }
    assert set(rows[0].keys()) == expected_columns


def test_phase19_file_plan_columns() -> None:
    rows = _read_csv("phase19_file_plan.csv")
    assert rows
    expected_columns = {
        "future_file_path",
        "file_type",
        "purpose",
        "required_for_phase19_implementation",
        "source_contract",
        "notes",
    }
    assert set(rows[0].keys()) == expected_columns


def test_phase19_test_plan_columns() -> None:
    rows = _read_csv("phase19_test_plan.csv")
    assert rows
    expected_columns = {
        "test_file",
        "test_area",
        "strategies_covered",
        "required_before_phase_complete",
        "notes",
    }
    assert set(rows[0].keys()) == expected_columns


def test_phase19_strategy_specs_md_mentions_each_strategy() -> None:
    text = (ARTIFACT_DIR / "brooks_pa_strategy_specs.md").read_text(encoding="utf-8")
    for name in PHASE19_STRATEGIES:
        assert name in text, f"strategy {name!r} missing from brooks_pa_strategy_specs.md"


def test_phase19_design_decision_is_complete_label() -> None:
    text = (ARTIFACT_DIR / "phase19_design_decision.md").read_text(encoding="utf-8")
    assert "PHASE19_BROOKS_PA_DESIGN_COMPLETE" in text
    assert "IMPLEMENT_PHASE19A_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION" in text


def test_phase19_non_goals_lists_forbidden_items() -> None:
    text = (ARTIFACT_DIR / "phase19_non_goals.md").read_text(encoding="utf-8")
    for needle in (
        "No candidate YAML",
        "No candidate promotion",
        "No `layer1 select-dry-run`",
        "No Layer2 router",
        "No Layer3",
        "No WFO",
        "No live trading",
        "No paper trading",
        "No economic claims",
        "No use of H2",
        "No QT runtime dependency",
        "No execution truth change",
        "No `v2` suffix on any new Phase19 file",
    ):
        assert needle in text, f"phase19_non_goals.md is missing {needle!r}"
