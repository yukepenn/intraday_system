# Phase18 Review Bundle

## Phase

`PHASE18_EXISTING_10_STRATEGY_IMPROVEMENT_DESIGN`

## Task Type

design-only + strategy-family improvement planning + diagnostic artifact review. This is not runtime implementation, research-run, candidate selection, candidate promotion, Layer2, WFO, live, paper, or strategy expansion.

## Git Baseline

Branch `main`; pre-task HEAD `a700571`. Final commit is recorded in the Cursor final response.

## Why Phase18 Was Needed

Phase17 reviewed all-current-10 expanded-grid surfaces and produced a non-promotional backlog. Phase18 converts that review into bounded, evidence-backed improvement design for the existing strategy library.

## Phase17 Acceptance Summary

Phase17 decision: `PHASE17_EXPANDED_GRID_REGION_REVIEW_COMPLETE`. Surface status counts: {'WATCH_HIGH_DRAWDOWN': 3, 'ROBUST_REGION_CANDIDATE_FOR_FURTHER_REVIEW': 1, 'WATCH_REGIME_DEPENDENT': 1, 'WATCH_PROMISING_REGION': 2, 'WATCH_LOW_SAMPLE': 3}. No candidate YAML, promotion, select-dry-run, Layer2/3, WFO, live, paper, runtime retuning, feature semantic change, or execution truth change was unlocked.

## Codex Phase17 Warnings Carried Forward

- Phase17 relied on local-only Phase16 `runs/` CSVs, so GitHub-only reproducibility is incomplete.
- H2 carries `missing_minute_slots_total=540` and is diagnostic-only.
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

`PHASE18_EXISTING_10_STRATEGY_IMPROVEMENT_DESIGN_COMPLETE`

## Cursor Provisional Recommended Next Step

`IMPLEMENT_PHASE18_APPROVED_EXISTING_10_STRATEGY_IMPROVEMENTS`

Final roadmap decision belongs to ChatGPT Pro + user after Codex review.
