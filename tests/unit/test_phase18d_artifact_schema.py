"""Phase18D artifact schema checks."""

from __future__ import annotations

import csv
from pathlib import Path

ARTIFACT_DIR = Path("artifacts/current10_refined_readiness_phase18d")

CURRENT_10 = {
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

REQUIRED_ARTIFACTS = {
    "CHATGPT_REVIEW_BUNDLE.md",
    "SOURCE_MAP.csv",
    "chatgpt_key_tables.csv",
    "validation_results.csv",
    "current10_v2_readiness_matrix.csv",
    "v2_feature_inspect_summary.csv",
    "v2_strategy_inspect_summary.csv",
    "v2_grid_inspect_summary.csv",
    "v2_layer1_grid_inspect_summary.csv",
    "v2_package_contract_alignment.csv",
    "strategy_onboarding_checklist_v2.md",
    "phase19_strategy_addition_template.md",
    "phase19_to_22_onboarding_gate_matrix.csv",
    "missing_feature_error_shape_assessment.md",
    "local_artifact_hygiene_note.md",
    "non_promotion_guardrails.md",
    "artifact_schema_validation.csv",
    "phase18d_decision.md",
}


def _read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_phase18d_required_artifacts_exist() -> None:
    missing = [name for name in sorted(REQUIRED_ARTIFACTS) if not (ARTIFACT_DIR / name).exists()]
    assert missing == []


def test_phase18d_current10_tables_cover_exact_strategy_universe() -> None:
    for name in (
        "current10_v2_readiness_matrix.csv",
        "v2_strategy_inspect_summary.csv",
        "v2_grid_inspect_summary.csv",
        "v2_layer1_grid_inspect_summary.csv",
    ):
        rows = _read_csv(name)
        assert {row["strategy"] for row in rows} == CURRENT_10


def test_phase18d_csv_schemas_and_decision() -> None:
    feature_rows = _read_csv("v2_feature_inspect_summary.csv")
    assert {row["feature_config"] for row in feature_rows} == {
        "opening_core_v2",
        "vwap_level_core_v2",
        "gap_level_core_v2",
        "indicator_core_v2",
        "pa_core_v2",
    }
    assert all(row["inspect_status"] == "pass" for row in feature_rows)

    key_rows = _read_csv("chatgpt_key_tables.csv")
    metrics = {row["metric"]: row["value"] for row in key_rows}
    assert metrics["current_strategies_checked_count"] == "10"
    assert metrics["v2_feature_configs_checked_count"] == "5"
    assert metrics["v2_strategy_configs_checked_count"] == "10"
    assert metrics["v2_grid_skeletons_checked_count"] == "10"
    assert metrics["layer1_grid_inspect_configs_checked_count"] == "10"
    assert metrics["actual_layer1_grid_runs"] == "0"
    assert metrics["decision"] == "PHASE18D_CURRENT10_REFINED_READINESS_COMPLETE"


def test_phase18d_onboarding_docs_are_contract_operationalization_only() -> None:
    checklist = (ARTIFACT_DIR / "strategy_onboarding_checklist_v2.md").read_text(encoding="utf-8")
    assert "This is not a new runtime contract" in checklist
    assert "If this checklist conflicts with core contract docs, the contract docs win" in checklist
    for contract in (
        "FEATURE_CONTRACT.md",
        "STRATEGY_CONTRACT.md",
        "STRATEGY_FAMILY_ONBOARDING_CONTRACT.md",
        "CONFIG_CONTRACT.md",
        "LAYER1_CONTRACT.md",
        "EXECUTION_CONTRACT.md",
        "BACKTEST_CONTRACT.md",
        "QT_REFERENCE_POLICY.md",
        "LAYER_FLOW.md",
    ):
        assert contract in checklist
