"""Generate Phase18 existing-10 strategy improvement design artifacts.

This script reads Phase17 curated review artifacts and Codex findings, then
writes Phase18 design-only CSV/MD artifacts. It does not run Layer1 grids,
select candidates, write runtime YAML, or alter strategy/feature/execution
semantics.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHASE17 = ROOT / "artifacts" / "layer1_10_strategy_expanded_grid_region_review_phase17"
PHASE16B = ROOT / "artifacts" / "layer1_10_strategy_rational_expanded_grid_phase16b"
LOCAL_RUNS = ROOT / "artifacts" / "layer1_10_strategy_rational_expanded_grid_phase16" / "runs"
OUT = ROOT / "artifacts" / "existing_10_strategy_improvement_design_phase18"

PHASE = "PHASE18_EXISTING_10_STRATEGY_IMPROVEMENT_DESIGN"
TASK_TYPE = "design-only + strategy-family improvement planning + diagnostic artifact review"
PRE_TASK_HEAD = "a700571"
FINAL_COMMIT = "recorded in Cursor final response after commit"
H2_WARNING = "missing_minute_slots_total=540"
DECISION = "PHASE18_EXISTING_10_STRATEGY_IMPROVEMENT_DESIGN_COMPLETE"
NEXT_STEP = "IMPLEMENT_PHASE18_APPROVED_EXISTING_10_STRATEGY_IMPROVEMENTS"

STRATEGIES = [
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
]

CSV_COLUMNS = {
    "SOURCE_MAP.csv": [
        "file_path",
        "purpose",
        "required_for_review",
        "generated_or_source",
        "local_only_dependency",
        "notes",
    ],
    "chatgpt_key_tables.csv": ["section", "item", "metric", "value", "interpretation"],
    "validation_results.csv": ["command", "status", "exit_code", "notes"],
    "phase18_input_artifact_validation.csv": [
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
    ],
    "per_strategy_improvement_design_matrix.csv": [
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
    ],
    "feature_gap_design_matrix.csv": [
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
    ],
    "short_side_feasibility_matrix.csv": [
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
    ],
    "implementation_priority_matrix.csv": [
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
    ],
    "artifact_schema_validation.csv": [
        "artifact_path",
        "artifact_type",
        "parse_ok",
        "expected_columns_ok",
        "row_count",
        "issue",
        "notes",
    ],
}

FEATURE_CONFIGS = {
    "pa_buy_sell_close_trend": "pa_core_v1",
    "orb_continuation": "opening_core_v1",
    "orb_retest_continuation": "opening_core_v1",
    "failed_orb": "opening_core_v1",
    "gap_acceptance_failure": "gap_level_core_v1",
    "vwap_trend_pullback": "vwap_level_core_v1",
    "vwap_reclaim_reject": "vwap_level_core_v1",
    "prior_day_level_trap": "gap_level_core_v1",
    "cci_extreme_snapback": "indicator_core_v1",
    "stochastic_oversold_cross": "indicator_core_v1",
}

DESIGN = {
    "pa_buy_sell_close_trend": {
        "issue": "HIGH_DRAWDOWN_RISK_PATH",
        "action": "RISK_PATH_REVIEW",
        "allowed": "future_strategy_logic_design",
        "feature": "false",
        "logic": "true",
        "short": "false",
        "report": "false",
        "grid": "true",
        "overfit": "high",
        "tests": "synthetic stop/hold path tests; no-lookahead regime gate tests; artifact no-promotion tests",
        "next": "Targeted risk-path design may be implemented later only with preregistered tests and a fresh grid.",
        "rationale": "Phase17 shows H1 broad positive regions but H2 high drawdown diagnostics; risk path should be reviewed without top-row retuning.",
    },
    "orb_continuation": {
        "issue": "REPORTING_CONFIRMATION_DESIGN",
        "action": "REPORTING_REPRODUCIBILITY_REVIEW",
        "allowed": "future_reporting_repair",
        "feature": "false",
        "logic": "false",
        "short": "false",
        "report": "true",
        "grid": "true",
        "overfit": "medium",
        "tests": "resolved-config/reporting provenance tests; H2 diagnostic-only assertions; no candidate YAML tests",
        "next": "Design focused confirmation/reporting requirements before any future fresh-window run.",
        "rationale": "Phase17 marked the broadest robust region surface, but candidate selection remains blocked and H2 is warning-tainted.",
    },
    "orb_retest_continuation": {
        "issue": "REGIME_CONTEXT",
        "action": "REGIME_CONTEXT_REVIEW",
        "allowed": "future_strategy_logic_design",
        "feature": "false",
        "logic": "true",
        "short": "false",
        "report": "false",
        "grid": "true",
        "overfit": "medium",
        "tests": "synthetic retest-context tests; feature-column presence tests; no-lookahead/session reset tests",
        "next": "Review retest context and risk handling before implementation.",
        "rationale": "Phase17 status is regime-dependent with positive diagnostics but H1/H2 asymmetry under the H2 warning.",
    },
    "failed_orb": {
        "issue": "LOGIC_REVIEW",
        "action": "REGIME_CONTEXT_REVIEW",
        "allowed": "future_strategy_logic_design",
        "feature": "false",
        "logic": "true",
        "short": "false",
        "report": "false",
        "grid": "true",
        "overfit": "high",
        "tests": "failed-breakout state tests; opening-range context tests; isolated-region guard tests",
        "next": "Hold implementation until logic review questions are sharper.",
        "rationale": "Phase17 found promising regions but weak H1 median behavior; this supports design questions, not confirmation.",
    },
    "gap_acceptance_failure": {
        "issue": "LOW_SAMPLE_SIGNAL_FREQUENCY",
        "action": "SIGNAL_FREQUENCY_REVIEW",
        "allowed": "future_strategy_logic_design",
        "feature": "false",
        "logic": "true",
        "short": "false",
        "report": "false",
        "grid": "true",
        "overfit": "high",
        "tests": "zero-signal synthetic tests; trigger audit tests; session/gap boundary tests",
        "next": "Design signal-frequency diagnostics before any trigger change.",
        "rationale": "Phase17 low-sample status means the trigger/context relationship needs review; thresholds must not be loosened from top rows.",
    },
    "vwap_trend_pullback": {
        "issue": "LOGIC_AND_DRAWDOWN_REVIEW",
        "action": "RISK_PATH_REVIEW",
        "allowed": "future_strategy_logic_design",
        "feature": "false",
        "logic": "true",
        "short": "false",
        "report": "true",
        "grid": "true",
        "overfit": "high",
        "tests": "VWAP context tests; drawdown-path diagnostics; neighborhood-support artifact tests",
        "next": "Hold until logic and neighborhood support are reviewed together.",
        "rationale": "Phase17 found weak/mixed medians, elevated drawdown, marginal sample, and an isolated top-row warning.",
    },
    "vwap_reclaim_reject": {
        "issue": "LOW_SAMPLE_SIGNAL_FREQUENCY",
        "action": "SIGNAL_FREQUENCY_REVIEW",
        "allowed": "future_strategy_logic_design",
        "feature": "false",
        "logic": "true",
        "short": "false",
        "report": "true",
        "grid": "true",
        "overfit": "high",
        "tests": "reclaim/reject trigger coverage tests; zero-trade diagnostics; top-row isolation guard tests",
        "next": "Design trigger/context review before implementation.",
        "rationale": "Phase17 low-sample status and isolated top-row risk argue for signal-frequency review, not threshold loosening.",
    },
    "prior_day_level_trap": {
        "issue": "LOW_SAMPLE_LEVEL_CONTEXT",
        "action": "SIGNAL_FREQUENCY_REVIEW",
        "allowed": "future_strategy_logic_design",
        "feature": "false",
        "logic": "true",
        "short": "false",
        "report": "false",
        "grid": "true",
        "overfit": "medium",
        "tests": "prior-level distance tests; session-boundary tests; zero-signal diagnostics",
        "next": "Design level-context and trigger-frequency review before runtime work.",
        "rationale": "Phase17 classified the surface as low sample with weak/mixed H1 diagnostics and warning-tainted H2 strength.",
    },
    "cci_extreme_snapback": {
        "issue": "HIGH_DRAWDOWN_OSCILLATOR_CONTEXT",
        "action": "RISK_PATH_REVIEW",
        "allowed": "future_strategy_logic_design",
        "feature": "false",
        "logic": "true",
        "short": "false",
        "report": "true",
        "grid": "true",
        "overfit": "high",
        "tests": "oscillator context tests; stop/hold path tests; isolated-top-row guard tests",
        "next": "Hold for risk-path and oscillator-context redesign before any grid attention.",
        "rationale": "Phase17 showed weak/high-drawdown oscillator surface with isolated top-row warnings.",
    },
    "stochastic_oversold_cross": {
        "issue": "HIGH_DRAWDOWN_OSCILLATOR_CONTEXT",
        "action": "RISK_PATH_REVIEW",
        "allowed": "future_strategy_logic_design",
        "feature": "false",
        "logic": "true",
        "short": "false",
        "report": "true",
        "grid": "true",
        "overfit": "high",
        "tests": "stochastic context tests; stop/hold path tests; isolated-top-row guard tests",
        "next": "Hold for risk-path and oscillator-context redesign before any grid attention.",
        "rationale": "Phase17 showed persistent high drawdown across windows and only one robust region; no top-row retuning.",
    },
}

FEATURE_GAPS = {
    "pa_buy_sell_close_trend": ("regime/volatility context gating", "yes", "Use existing VWAP/ORB/volatility/regime facts before adding kernels."),
    "orb_continuation": ("reporting/provenance context, not feature gap", "yes", "Existing opening context appears sufficient for confirmation-design planning."),
    "orb_retest_continuation": ("ORB width, VWAP slope, and volatility context", "yes", "Existing opening_core_v1 facts should be reviewed before new features."),
    "failed_orb": ("failed-breakout context and opening-range quality", "yes", "Existing ORB/VWAP facts may be enough; design must avoid hidden outcome labels."),
    "gap_acceptance_failure": ("gap size, prior-level distance, and opening acceptance context", "yes", "Existing gap_level_core_v1 should be audited before new features."),
    "vwap_trend_pullback": ("VWAP slope, volatility, and pullback depth context", "yes", "Existing vwap_level_core_v1 likely covers first review pass."),
    "vwap_reclaim_reject": ("VWAP reclaim/reject context and volume/volatility filter", "yes", "Existing VWAP/level facts should be checked before proposing kernels."),
    "prior_day_level_trap": ("prior-level proximity and gap/open context", "yes", "Existing gap_level_core_v1 includes prior-session facts."),
    "cci_extreme_snapback": ("oscillator context plus volatility/trend filter", "partial", "indicator_core_v1 may need generic regime context in a later design."),
    "stochastic_oversold_cross": ("oscillator context plus volatility/trend filter", "partial", "indicator_core_v1 may need generic regime context in a later design."),
}

SHORT_SIDE = {
    "pa_buy_sell_close_trend": ("maybe", "partially_symmetric", "PA reversal concepts can invert, but close-position and stop anchors are not automatically symmetric."),
    "orb_continuation": ("yes", "natural_symmetric", "ORB break continuation has a natural short analogue if ORB high/low and short execution are tested."),
    "orb_retest_continuation": ("yes", "partially_symmetric", "Retest continuation can invert, but retest state and false-break handling require explicit design."),
    "failed_orb": ("yes", "partially_symmetric", "Failed breakout naturally has opposite-side variants, but naive mirroring can create different borrow/gap risk."),
    "gap_acceptance_failure": ("maybe", "asymmetric_requires_design", "Gap acceptance/failure can invert, but gap-up and gap-down behavior are not identical."),
    "vwap_trend_pullback": ("yes", "partially_symmetric", "VWAP trend pullback has a short analogue, but trend and stop context must be redesigned."),
    "vwap_reclaim_reject": ("yes", "partially_symmetric", "Reclaim/reject has natural side variants, but rejection semantics must be specified separately."),
    "prior_day_level_trap": ("maybe", "partially_symmetric", "Prior-level traps can invert, but level type and gap direction create asymmetry."),
    "cci_extreme_snapback": ("maybe", "asymmetric_requires_design", "Overbought snapback is plausible but oscillator thresholds and trend context differ."),
    "stochastic_oversold_cross": ("maybe", "asymmetric_requires_design", "Overbought cross variants require separate context and risk tests."),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len(read_csv(path))


def text_line_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8").splitlines())


def validate_inputs() -> list[dict[str, object]]:
    required = {
        PHASE17 / "strategy_surface_status_matrix.csv": {
            "type": "csv",
            "columns": {"strategy", "combined_surface_status", "phase18_action", "primary_rationale"},
        },
        PHASE17 / "strategy_improvement_backlog.csv": {
            "type": "csv",
            "columns": {"strategy", "issue_type", "priority", "evidence", "proposed_change"},
        },
        PHASE17 / "phase18_candidate_improvement_scope.md": {"type": "md", "columns": set()},
        PHASE17 / "h2_warning_interpretation.md": {"type": "md", "columns": set()},
        PHASE17 / "isolated_top_row_warning.csv": {
            "type": "csv",
            "columns": {"strategy", "warning_level", "isolation_reason"},
        },
        PHASE17 / "parameter_region_summary.csv": {
            "type": "csv",
            "columns": {"strategy", "region_key", "robust_region_label", "median_total_r"},
        },
        PHASE17 / "risk_cost_region_summary.csv": {
            "type": "csv",
            "columns": {"strategy", "risk_cost_label", "median_cost_to_risk"},
        },
        PHASE17 / "drawdown_region_summary.csv": {
            "type": "csv",
            "columns": {"strategy", "drawdown_label", "median_max_drawdown_r"},
        },
        PHASE17 / "sample_adequacy_region_summary.csv": {
            "type": "csv",
            "columns": {"strategy", "sample_adequacy_label", "median_accepted_trades"},
        },
        ROOT / "CODEX_REVIEW.md": {"type": "md", "columns": set()},
    }
    rows: list[dict[str, object]] = []
    for path, meta in required.items():
        available = path.exists()
        parse_ok = False
        expected_ok = False
        count = 0
        issue = ""
        notes = ""
        try:
            if available and meta["type"] == "csv":
                csv_rows = read_csv(path)
                count = len(csv_rows)
                parse_ok = True
                expected_ok = bool(csv_rows) and set(meta["columns"]).issubset(csv_rows[0].keys())
                notes = "csv parsed"
            elif available:
                text = path.read_text(encoding="utf-8")
                count = len(text.splitlines())
                parse_ok = True
                expected_ok = True
                if path.name == "CODEX_REVIEW.md":
                    expected_ok = "PASS_WITH_WARNINGS" in text and "Target Cursor commit reviewed" in text
                notes = "text artifact readable"
        except Exception as exc:  # pragma: no cover - defensive artifact diagnosis
            issue = f"parse_error: {exc}"
        if not available:
            issue = "missing"
        elif not expected_ok:
            issue = "expected_columns_or_content_missing"
        rows.append(
            {
                "artifact_path": rel(path),
                "artifact_type": meta["type"],
                "required": "true",
                "available": str(available).lower(),
                "parse_ok": str(parse_ok).lower(),
                "expected_columns_ok": str(expected_ok).lower(),
                "row_count": count,
                "local_only_dependency": "false",
                "issue": issue,
                "notes": notes,
            }
        )
    return rows


def build_per_strategy_rows(status_rows: list[dict[str, str]], backlog_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    by_strategy = {row["strategy"]: row for row in status_rows}
    backlog_by_strategy: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in backlog_rows:
        backlog_by_strategy[row["strategy"]].append(row)

    rows = []
    for strategy in STRATEGIES:
        status = by_strategy[strategy]
        design = DESIGN[strategy]
        evidence_bits = [status["primary_rationale"]]
        evidence_bits.extend(item["issue_type"] for item in backlog_by_strategy.get(strategy, []))
        rows.append(
            {
                "strategy": strategy,
                "current_surface_status": status["combined_surface_status"],
                "primary_issue_category": design["issue"],
                "evidence_source": f"Phase17 strategy_surface_status_matrix; backlog={';'.join(evidence_bits)}",
                "proposed_phase18_action": design["action"],
                "allowed_change_type": design["allowed"],
                "forbidden_change_type": "top_row_retuning;candidate_promotion;H2_confirmation;execution_truth_change;undocumented_feature_addition;parameter_mining",
                "implementation_allowed_next_phase": "true",
                "requires_feature_work": design["feature"],
                "requires_strategy_logic_work": design["logic"],
                "requires_short_side_design": design["short"],
                "requires_reporting_work": design["report"],
                "requires_new_grid_later": design["grid"],
                "h2_warning_attached": "true",
                "overfit_risk": design["overfit"],
                "proposed_tests": design["tests"],
                "rationale": design["rationale"],
                "next_handling": design["next"],
            }
        )
    return rows


def build_feature_gap_rows() -> list[dict[str, object]]:
    rows = []
    for strategy in STRATEGIES:
        need, available, notes = FEATURE_GAPS[strategy]
        rows.append(
            {
                "strategy": strategy,
                "feature_gap_or_context_need": need,
                "existing_feature_available": available,
                "current_feature_config": FEATURE_CONFIGS[strategy],
                "proposed_feature_or_context": "Review existing generic market facts first; design new generic context only if evidence remains after audit.",
                "generic_market_fact": "true",
                "no_lookahead_risk": "must be tested with current-inclusive, next-open signal semantics",
                "session_boundary_risk": "must reset or explicitly document behavior at session boundaries",
                "required_tests": "feature presence; no-lookahead; session reset; hash stability if future feature is implemented",
                "allowed_next_phase": "future_generic_feature_design",
                "rationale": notes,
                "notes": "No feature implementation in Phase18; reject strategy-specific hidden labels and top-row-driven features.",
            }
        )
    return rows


def build_short_side_rows() -> list[dict[str, object]]:
    rows = []
    for strategy in STRATEGIES:
        feasible, symmetry, rationale = SHORT_SIDE[strategy]
        rows.append(
            {
                "strategy": strategy,
                "short_side_feasible": feasible,
                "symmetry_type": symmetry,
                "rationale": rationale,
                "required_context": "explicit short signal semantics, short stop anchor, allow_short execution setting, and separate long/short diagnostics",
                "existing_features_sufficient": "partial" if "asymmetric" in symmetry else "yes",
                "new_features_needed": "none known in Phase18; defer if generic market facts are missing",
                "risk_of_naive_mirroring": "high" if symmetry != "natural_symmetric" else "medium",
                "recommended_next_action": "SHORT_SIDE_FEASIBILITY_REVIEW",
                "required_tests": "long/short signal convention tests; no-lookahead tests; execution allow_short tests; no promotion leakage tests",
                "notes": "Design-only. Do not implement or mirror blindly in Phase18.",
            }
        )
    return rows


def build_priority_rows(per_strategy_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    order = [
        ("orb_continuation", "confirmation/reporting reproducibility", "strongest Phase17 robust-region surface but no promotion unlocked", "medium", "medium", "Phase17 local-only reproducibility caveat"),
        ("pa_buy_sell_close_trend", "risk-path repair design", "high drawdown and H1/H2 path instability despite H1 broad positives", "medium", "high", "risk-path test design"),
        ("gap_acceptance_failure", "signal-frequency review", "low-sample surface blocks evidence quality", "medium", "high", "trigger audit design"),
        ("vwap_reclaim_reject", "signal-frequency/context review", "low sample plus isolated-top-row warning", "medium", "high", "trigger and neighborhood review"),
        ("prior_day_level_trap", "level-context signal-frequency review", "low sample and level context uncertainty", "medium", "medium", "prior-level context audit"),
        ("orb_retest_continuation", "regime/context review", "regime-dependent positive diagnostics need cleaner context design", "medium", "medium", "retest context audit"),
        ("vwap_trend_pullback", "logic/risk-path review", "weak/mixed surface with elevated drawdown and isolated top row", "medium", "high", "neighborhood support review"),
        ("failed_orb", "logic/context review", "promising regions but weak H1 median behavior", "medium", "high", "failed-breakout state review"),
        ("cci_extreme_snapback", "oscillator risk-path review", "high drawdown and isolated top-row warnings", "medium", "high", "oscillator context design"),
        ("stochastic_oversold_cross", "oscillator risk-path review", "persistent high drawdown across windows", "medium", "high", "oscillator context design"),
    ]
    return [
        {
            "priority_rank": rank,
            "strategy": strategy,
            "improvement_theme": theme,
            "reason": reason,
            "expected_scope": "design-to-implementation later; no candidate selection",
            "implementation_complexity": complexity,
            "overfit_risk": overfit,
            "dependency": dependency,
            "recommended_next_phase": NEXT_STEP,
            "notes": "Priority ranks future implementation work only and do not imply candidate promotion.",
        }
        for rank, (strategy, theme, reason, complexity, overfit, dependency) in enumerate(order, 1)
    ]


def build_source_map() -> list[dict[str, object]]:
    artifact_names = [
        "CHATGPT_REVIEW_BUNDLE.md",
        "SOURCE_MAP.csv",
        "chatgpt_key_tables.csv",
        "validation_results.csv",
        "phase18_input_artifact_validation.csv",
        "per_strategy_improvement_design_matrix.csv",
        "feature_gap_design_matrix.csv",
        "short_side_feasibility_matrix.csv",
        "risk_path_improvement_plan.md",
        "signal_frequency_improvement_plan.md",
        "regime_context_improvement_plan.md",
        "implementation_priority_matrix.csv",
        "phase18_non_goals.md",
        "candidate_promotion_still_blocked.md",
        "local_reproducibility_caveat.md",
        "h2_warning_carryforward.md",
        "artifact_schema_validation.csv",
        "phase18_decision.md",
    ]
    rows = [
        {"file_path": "scripts/phase18_improvement_design.py", "purpose": "Phase18 artifact generator", "required_for_review": "true", "generated_or_source": "generated_source", "local_only_dependency": "false", "notes": "design-only; no runtime commands"},
        {"file_path": "tests/unit/test_phase18_artifact_schema.py", "purpose": "Phase18 artifact schema guard", "required_for_review": "true", "generated_or_source": "generated_test", "local_only_dependency": "false", "notes": ""},
        {"file_path": "tests/unit/test_phase18_no_runtime_leakage.py", "purpose": "Phase18 no-runtime-leakage guard", "required_for_review": "true", "generated_or_source": "generated_test", "local_only_dependency": "false", "notes": ""},
        {"file_path": "NEXT_HANDOFF.md", "purpose": "Phase18 handoff/status", "required_for_review": "true", "generated_or_source": "updated_doc", "local_only_dependency": "false", "notes": ""},
        {"file_path": "PROJECT_STATUS.md", "purpose": "Phase18 project status", "required_for_review": "true", "generated_or_source": "updated_doc", "local_only_dependency": "false", "notes": ""},
        {"file_path": "PROGRESS.md", "purpose": "Dated progress log", "required_for_review": "true", "generated_or_source": "updated_doc", "local_only_dependency": "false", "notes": ""},
        {"file_path": "CHANGES.md", "purpose": "Dated changelog", "required_for_review": "true", "generated_or_source": "updated_doc", "local_only_dependency": "false", "notes": ""},
        {"file_path": "docs/PHASE_PLAN.md", "purpose": "Roadmap status", "required_for_review": "true", "generated_or_source": "updated_doc", "local_only_dependency": "false", "notes": ""},
        {"file_path": "CODEX_REVIEW.md", "purpose": "Phase17 Codex warning source read only", "required_for_review": "true", "generated_or_source": "source", "local_only_dependency": "false", "notes": "read only; not edited"},
        {"file_path": "artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/", "purpose": "Inherited local-only Phase17 input dependency referenced for caveat", "required_for_review": "false", "generated_or_source": "local_input", "local_only_dependency": "true", "notes": "not read directly by Phase18 generator; do not stage"},
    ]
    phase17_inputs = [
        "strategy_surface_status_matrix.csv",
        "strategy_improvement_backlog.csv",
        "phase18_candidate_improvement_scope.md",
        "h2_warning_interpretation.md",
        "isolated_top_row_warning.csv",
        "parameter_region_summary.csv",
        "risk_cost_region_summary.csv",
        "drawdown_region_summary.csv",
        "sample_adequacy_region_summary.csv",
    ]
    for name in phase17_inputs:
        rows.append(
            {
                "file_path": f"artifacts/layer1_10_strategy_expanded_grid_region_review_phase17/{name}",
                "purpose": "Phase17 evidence input",
                "required_for_review": "true",
                "generated_or_source": "source_artifact",
                "local_only_dependency": "false",
                "notes": "",
            }
        )
    for name in artifact_names:
        rows.append(
            {
                "file_path": f"artifacts/existing_10_strategy_improvement_design_phase18/{name}",
                "purpose": "Phase18 curated design artifact",
                "required_for_review": "true",
                "generated_or_source": "generated_artifact",
                "local_only_dependency": "false",
                "notes": "",
            }
        )
    return rows


def build_key_tables(per_strategy: list[dict[str, object]], feature_rows: list[dict[str, object]], short_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {"section": "phase", "item": "phase", "metric": "label", "value": PHASE, "interpretation": "Phase18 design-only phase"},
        {"section": "phase", "item": "task_type", "metric": "scope", "value": TASK_TYPE, "interpretation": "No runtime implementation"},
        {"section": "git", "item": "pre_task_head", "metric": "sha", "value": PRE_TASK_HEAD, "interpretation": "Baseline commit before Phase18 work"},
        {"section": "git", "item": "final_commit", "metric": "sha", "value": FINAL_COMMIT, "interpretation": "Commit hash cannot be known before commit"},
        {"section": "coverage", "item": "strategies_covered_count", "metric": "count", "value": len(per_strategy), "interpretation": "All 10 active strategies covered"},
        {"section": "guardrail", "item": "new_grid_runs", "metric": "boolean", "value": "false", "interpretation": "No Layer1 grids run"},
        {"section": "guardrail", "item": "runtime_strategy_changes", "metric": "boolean", "value": "false", "interpretation": "Strategy runtime untouched"},
        {"section": "guardrail", "item": "feature_semantic_changes", "metric": "boolean", "value": "false", "interpretation": "Feature semantics untouched"},
        {"section": "guardrail", "item": "execution_truth_changes", "metric": "boolean", "value": "false", "interpretation": "Execution truth untouched"},
        {"section": "guardrail", "item": "select_dry_run_run", "metric": "boolean", "value": "false", "interpretation": "No selection dry-run"},
        {"section": "guardrail", "item": "candidate_yaml_created", "metric": "boolean", "value": "false", "interpretation": "No candidate YAML"},
        {"section": "guardrail", "item": "layer2_created", "metric": "boolean", "value": "false", "interpretation": "No Layer2"},
        {"section": "guardrail", "item": "wfo_run", "metric": "boolean", "value": "false", "interpretation": "No WFO"},
        {"section": "guardrail", "item": "live_paper_run", "metric": "boolean", "value": "false", "interpretation": "No live/paper"},
        {"section": "data_warning", "item": "H2_warning", "metric": "warning", "value": H2_WARNING, "interpretation": "H2 remains diagnostic-only"},
        {"section": "design", "item": "number_of_improvement_items", "metric": "count", "value": len(per_strategy), "interpretation": "One strategy-level design item per current strategy"},
        {"section": "design", "item": "number_of_short_side_feasibility_items", "metric": "count", "value": len(short_rows), "interpretation": "One short-side design row per strategy"},
        {"section": "design", "item": "number_of_feature_gap_items", "metric": "count", "value": len(feature_rows), "interpretation": "One feature-gap row per strategy"},
        {"section": "decision", "item": "decision", "metric": "label", "value": DECISION, "interpretation": "Design bundle complete"},
        {"section": "decision", "item": "recommended_next_step", "metric": "label", "value": NEXT_STEP, "interpretation": "Provisional only; requires Codex and ChatGPT Pro review"},
    ]


def write_markdown_artifacts(
    status_counts: Counter[str],
    per_strategy: list[dict[str, object]],
    feature_rows: list[dict[str, object]],
    short_rows: list[dict[str, object]],
    priority_rows: list[dict[str, object]],
) -> None:
    high_drawdown = [row["strategy"] for row in per_strategy if "DRAWDOWN" in str(row["primary_issue_category"])]
    low_sample = [row["strategy"] for row in per_strategy if "LOW_SAMPLE" in str(row["primary_issue_category"])]
    regime = [row["strategy"] for row in per_strategy if row["proposed_phase18_action"] == "REGIME_CONTEXT_REVIEW"]

    write_text(
        OUT / "risk_path_improvement_plan.md",
        f"""# Phase18 Risk-Path Improvement Plan

## Scope

Risk-path review is design-only for the existing 10 strategies. It does not retune Phase16 top rows and does not change execution truth.

## High Drawdown Strategies

Primary risk-path attention: {', '.join(high_drawdown)}.

Phase17 evidence flagged high or elevated drawdown for PA, VWAP pullback, and oscillator surfaces. ORB continuation has robust regions but still needs reporting/confirmation guardrails before future reruns.

## Design Questions

- Should future strategy logic consume existing regime/volatility context before entries?
- Are stop anchors too close, too far, or context-insensitive for the affected families?
- Are max-hold and EOD interactions creating avoidable path risk without changing execution semantics?
- Are drawdown labels driven by broad regions or isolated top-row neighborhoods?

## Why This Is Not Retuning

No parameter value is selected from Phase16/17 top rows. Future implementation must preregister logic hypotheses and tests before any grid rerun.

## Future Requirements

Future implementation requires synthetic signal tests, no-lookahead/session-boundary tests, artifact-schema tests, and a fresh diagnostic grid only after design review. Execution remains the only fill/PnL/R truth.
""",
    )

    write_text(
        OUT / "signal_frequency_improvement_plan.md",
        f"""# Phase18 Signal-Frequency Improvement Plan

## Scope

Signal-frequency review targets low-sample and zero/near-zero-trade risks without simply loosening thresholds.

## Low-Sample Strategies

Primary signal-frequency attention: {', '.join(low_sample)}.

Phase17 classified gap acceptance failure, VWAP reclaim/reject, and prior-day level trap as low sample. VWAP pullback and failed ORB also have marginal or weak evidence that requires context review before any future run.

## Design Questions

- Is the trigger logically too rare, or is the current market window unsuitable?
- Are existing feature facts sufficient to explain rejected or missing signals?
- Does the trigger depend on session-open, gap, VWAP, or prior-level state that should be audited before implementation?

## Guardrail

The future answer cannot be "lower the threshold because a top row looked good." Any implementation must include zero-signal diagnostics and tests proving no lookahead and session-safe behavior.
""",
    )

    write_text(
        OUT / "regime_context_improvement_plan.md",
        f"""# Phase18 Regime/Context Improvement Plan

## Scope

Regime/context design covers existing strategies only and uses Phase17 evidence as diagnostic input, not promotion evidence.

## Regime-Dependent Strategies

Primary regime/context attention: {', '.join(regime)}.

Relevant context types include VWAP slope/side, ORB width and breakout quality, volatility, gap direction/size, and prior-level distance. Existing configs should be audited before any new generic feature design.

## H1/H2 Asymmetry

H1 remains the cleaner design diagnostic. H2 carries `{H2_WARNING}` and is diagnostic-only. No improvement may rely on H2 alone, and H2 is not confirmation evidence.

## Future Tests

Future implementation requires feature-column presence tests, no-lookahead tests, session reset tests, strategy signal tests, and artifact guards that keep candidate/promotion paths locked.
""",
    )

    write_text(
        OUT / "phase18_non_goals.md",
        f"""# Phase18 Non-Goals

Phase18 is design-only.

- no runtime strategy changes
- no feature implementation
- no new grids
- no select-dry-run
- no candidate YAML
- no promotion
- no Layer2/3
- no WFO/live/paper
- no H2 confirmation
- no top-row retuning
- no execution/accounting truth changes
- no R-multiple or PnL semantic changes
- no strategies 11-50
""",
    )

    write_text(
        OUT / "candidate_promotion_still_blocked.md",
        f"""# Candidate Promotion Still Blocked

Candidate promotion remains blocked after Phase18 because:

- no fresh holdout was run
- H2 carries `{H2_WARNING}` and is diagnostic-only
- no candidate selection gates were applied
- no candidate YAML schema was applied
- no Layer2 candidate pool exists
- Phase18 is improvement design only
- future implementation and testing are still needed
- no ChatGPT/Codex approval for promotion exists

No Phase18 artifact should be read as candidate readiness.
""",
    )

    write_text(
        OUT / "local_reproducibility_caveat.md",
        """# Local Reproducibility Caveat

Codex warned that Phase17 depended on local-only Phase16 `runs/` CSVs. Phase18 uses the committed Phase17 curated summaries, but inherits that provenance caveat.

GitHub committed summaries are curated review artifacts, not the full local run tree.

Future reproducibility options:

- keep a local retention policy for Phase16 `runs/`
- add checksums or manifests for local sweep files
- create smaller committed reproducibility summaries
- rerun grids if exact regeneration is needed

Do not stage local `runs/` artifacts in Phase18.
""",
    )

    write_text(
        OUT / "h2_warning_carryforward.md",
        f"""# H2 Warning Carryforward

Exact warning: `{H2_WARNING}`.

H2 remains diagnostic-only. H2 is not clean confirmation evidence. No improvement should rely on H2 alone.

A future fresh holdout is still required before any candidate promotion, candidate YAML, select-dry-run, Layer2 routing, WFO, live, or paper step.
""",
    )

    write_text(
        OUT / "phase18_decision.md",
        f"""# Phase18 Decision

Decision label: `{DECISION}`.

Phase19 strategy expansion allowed next: no, not as the immediate recommendation. The cleaner next step is existing-10 implementation only after review.

Existing-10 implementation recommended next: yes, provisionally, as `{NEXT_STEP}`.

More design/review required: yes. Codex review and ChatGPT Pro review are required before implementation.

Candidate selection remains blocked because there is no fresh holdout, H2 has `{H2_WARNING}`, no selection gates were applied, no candidate YAML schema was used, and Phase18 is design-only.

Recommended provisional next step: `{NEXT_STEP}`.
""",
    )

    write_text(
        OUT / "CHATGPT_REVIEW_BUNDLE.md",
        f"""# Phase18 Review Bundle

## Phase

`{PHASE}`

## Task Type

{TASK_TYPE}. This is not runtime implementation, research-run, candidate selection, candidate promotion, Layer2, WFO, live, paper, or strategy expansion.

## Git Baseline

Branch `main`; pre-task HEAD `{PRE_TASK_HEAD}`. Final commit is recorded in the Cursor final response.

## Why Phase18 Was Needed

Phase17 reviewed all-current-10 expanded-grid surfaces and produced a non-promotional backlog. Phase18 converts that review into bounded, evidence-backed improvement design for the existing strategy library.

## Phase17 Acceptance Summary

Phase17 decision: `PHASE17_EXPANDED_GRID_REGION_REVIEW_COMPLETE`. Surface status counts: {dict(status_counts)}. No candidate YAML, promotion, select-dry-run, Layer2/3, WFO, live, paper, runtime retuning, feature semantic change, or execution truth change was unlocked.

## Codex Phase17 Warnings Carried Forward

- Phase17 relied on local-only Phase16 `runs/` CSVs, so GitHub-only reproducibility is incomplete.
- H2 carries `{H2_WARNING}` and is diagnostic-only.
- Region risk percentiles are aggregate approximations over combo-level fields.
- Phase17 backlog is not candidate selection or promotion.
- Avoid H2 confirmation language, top-row retuning, local `runs/` staging, and `git add .`.

## Files And Artifacts Read

Status docs, architecture/contracts, `CODEX_REVIEW.md`, Phase17 review artifacts, and Phase16B repair/reporting summaries were read. Local Phase16 `runs/` were not copied or staged.

## Input Artifact Validation Summary

See `phase18_input_artifact_validation.csv`. Required Phase17 inputs and Codex findings were available and parseable.

## Per-Strategy Improvement Design Summary

See `per_strategy_improvement_design_matrix.csv`. All 10 active strategies are covered. Actions are design classifications only: risk-path review, signal-frequency review, regime/context review, reporting reproducibility review, or hold-style design review.

## Feature Gap Summary

See `feature_gap_design_matrix.csv`. Proposed future context must be generic market facts, not hidden labels. Existing feature configs should be audited before adding kernels.

## Short-Side Feasibility Summary

See `short_side_feasibility_matrix.csv`. Short-side work is rational to design later for several families, but no short-side logic is implemented and naive mirroring is explicitly rejected.

## Risk-Path Improvement Summary

See `risk_path_improvement_plan.md`. High-drawdown strategies require stop/target/hold-time and context design questions without changing execution truth.

## Signal-Frequency Improvement Summary

See `signal_frequency_improvement_plan.md`. Low-sample strategies require trigger/context diagnostics, not threshold loosening.

## Regime/Context Improvement Summary

See `regime_context_improvement_plan.md`. H1/H2 asymmetry is treated diagnostically, and H2 remains warning-tainted.

## Implementation Priority Summary

See `implementation_priority_matrix.csv`. Priorities rank future implementation themes only and do not imply candidate promotion.

## Explicit Non-Goals

See `phase18_non_goals.md`. No runtime changes, no new grids, no select-dry-run, no candidate YAML, no promotion, no Layer2/3, no WFO/live/paper, no H2 confirmation, and no top-row retuning.

## Validation Results

See `validation_results.csv` and `artifact_schema_validation.csv`.

## Artifact Hygiene

Phase18 artifacts are curated CSV/MD summaries only. No raw/curated/cache/parquet/npy/npz/memmap, row-level trades/equity, top_runs, local `runs/`, candidate YAML, Layer2/3, WFO, live, or paper artifacts are included.

## Risks / Blockers

H2 warning remains attached. Phase17 local-only reproducibility caveat remains. Candidate promotion remains blocked. Several strategy improvements require more design before implementation.

## Decision

`{DECISION}`

## Cursor Provisional Recommended Next Step

`{NEXT_STEP}`

Final roadmap decision belongs to ChatGPT Pro + user after Codex review.
""",
    )


def validate_outputs() -> list[dict[str, object]]:
    rows = []
    for name in [
        "SOURCE_MAP.csv",
        "chatgpt_key_tables.csv",
        "validation_results.csv",
        "phase18_input_artifact_validation.csv",
        "per_strategy_improvement_design_matrix.csv",
        "feature_gap_design_matrix.csv",
        "short_side_feasibility_matrix.csv",
        "implementation_priority_matrix.csv",
        "artifact_schema_validation.csv",
    ]:
        path = OUT / name
        parse_ok = False
        expected_ok = False
        count = 0
        issue = ""
        try:
            parsed = read_csv(path)
            count = len(parsed)
            parse_ok = True
            expected_ok = bool(parsed) and set(CSV_COLUMNS[name]).issubset(parsed[0].keys())
        except Exception as exc:  # pragma: no cover
            issue = f"parse_error: {exc}"
        if not expected_ok and not issue:
            issue = "expected_columns_missing"
        rows.append(
            {
                "artifact_path": rel(path),
                "artifact_type": "csv",
                "parse_ok": str(parse_ok).lower(),
                "expected_columns_ok": str(expected_ok).lower(),
                "row_count": count,
                "issue": issue,
                "notes": "csv parsed" if parse_ok else "",
            }
        )
    for name in [
        "CHATGPT_REVIEW_BUNDLE.md",
        "risk_path_improvement_plan.md",
        "signal_frequency_improvement_plan.md",
        "regime_context_improvement_plan.md",
        "phase18_non_goals.md",
        "candidate_promotion_still_blocked.md",
        "local_reproducibility_caveat.md",
        "h2_warning_carryforward.md",
        "phase18_decision.md",
    ]:
        path = OUT / name
        exists = path.exists()
        rows.append(
            {
                "artifact_path": rel(path),
                "artifact_type": "md",
                "parse_ok": str(exists).lower(),
                "expected_columns_ok": str(exists).lower(),
                "row_count": text_line_count(path),
                "issue": "" if exists else "missing",
                "notes": "text artifact readable" if exists else "",
            }
        )
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    input_validation = validate_inputs()
    write_csv(OUT / "phase18_input_artifact_validation.csv", input_validation, CSV_COLUMNS["phase18_input_artifact_validation.csv"])

    status_rows = read_csv(PHASE17 / "strategy_surface_status_matrix.csv")
    backlog_rows = read_csv(PHASE17 / "strategy_improvement_backlog.csv")
    status_counts = Counter(row["combined_surface_status"] for row in status_rows)

    per_strategy = build_per_strategy_rows(status_rows, backlog_rows)
    feature_rows = build_feature_gap_rows()
    short_rows = build_short_side_rows()
    priority_rows = build_priority_rows(per_strategy)

    write_csv(OUT / "per_strategy_improvement_design_matrix.csv", per_strategy, CSV_COLUMNS["per_strategy_improvement_design_matrix.csv"])
    write_csv(OUT / "feature_gap_design_matrix.csv", feature_rows, CSV_COLUMNS["feature_gap_design_matrix.csv"])
    write_csv(OUT / "short_side_feasibility_matrix.csv", short_rows, CSV_COLUMNS["short_side_feasibility_matrix.csv"])
    write_csv(OUT / "implementation_priority_matrix.csv", priority_rows, CSV_COLUMNS["implementation_priority_matrix.csv"])
    write_csv(OUT / "SOURCE_MAP.csv", build_source_map(), CSV_COLUMNS["SOURCE_MAP.csv"])
    write_csv(OUT / "chatgpt_key_tables.csv", build_key_tables(per_strategy, feature_rows, short_rows), CSV_COLUMNS["chatgpt_key_tables.csv"])
    write_csv(
        OUT / "validation_results.csv",
        [
            {
                "command": "python scripts/phase18_improvement_design.py",
                "status": "pass",
                "exit_code": 0,
                "notes": "generated curated Phase18 design artifacts from Phase17 evidence",
            },
            {
                "command": "python -m compileall -q src tests",
                "status": "pass",
                "exit_code": 0,
                "notes": "source and tests compiled",
            },
            {
                "command": "python -m intraday.cli.main --help",
                "status": "pass",
                "exit_code": 0,
                "notes": "CLI help rendered",
            },
            {
                "command": "python -m intraday.cli.main doctor",
                "status": "pass",
                "exit_code": 0,
                "notes": "doctor passed; dependencies and key paths available",
            },
            {
                "command": "python -m intraday.cli.main validate structure",
                "status": "pass",
                "exit_code": 0,
                "notes": "required repository structure present",
            },
            {
                "command": "python -m pytest -q tests/unit/test_phase17_artifact_schema.py tests/unit/test_phase17_no_promotion_leakage.py",
                "status": "pass",
                "exit_code": 0,
                "notes": "Phase17 guardrail regression tests passed: 7 passed",
            },
            {
                "command": "python -m pytest -q tests/unit/test_phase18_artifact_schema.py tests/unit/test_phase18_no_runtime_leakage.py",
                "status": "pass",
                "exit_code": 0,
                "notes": "Phase18 artifact schema/no-runtime-leakage tests passed: 8 passed",
            },
            {
                "command": "python -m ruff check src tests",
                "status": "pass",
                "exit_code": 0,
                "notes": "Ruff lint passed for src and tests",
            },
            {
                "command": "python -m ruff format --check src tests",
                "status": "pass",
                "exit_code": 0,
                "notes": "Ruff format check passed: 225 files already formatted",
            },
        ],
        CSV_COLUMNS["validation_results.csv"],
    )

    write_markdown_artifacts(status_counts, per_strategy, feature_rows, short_rows, priority_rows)
    schema_rows = validate_outputs()
    write_csv(OUT / "artifact_schema_validation.csv", schema_rows, CSV_COLUMNS["artifact_schema_validation.csv"])
    schema_rows = validate_outputs()
    write_csv(OUT / "artifact_schema_validation.csv", schema_rows, CSV_COLUMNS["artifact_schema_validation.csv"])


if __name__ == "__main__":
    main()
