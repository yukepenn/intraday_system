# Phase17 Review Bundle

## Phase

`PHASE17_REVIEW_10_STRATEGY_EXPANDED_GRID_RESULTS_BY_REGION`

## Task Type

diagnostic + strategy-family review + artifact/reporting analysis. This was a review/diagnostic phase only.

## Git Baseline

Branch `main`; pre-task HEAD `1fba694`. Final commit is recorded in the Cursor final response because the final commit hash is self-referential before commit.

## Why Phase17 Was Needed

Phase16B completed all 20 expanded grids after runtime/reporting repairs. Phase17 was needed to review all-current-10 results by parameter regions and top-neighborhood support, not by single top-row sorting.

## Phase16B Acceptance Summary

Phase16B accepted decision `PHASE16_EXPANDED_GRID_RUN_RESUMED_COMPLETE`: ORB retest and failed ORB prior-state runtime blockers were repaired, drawdown/risk/cost reporting was repaired, and all 20 grids completed with full combo coverage. H2 carries `missing_minute_slots_total=540` and remains diagnostic-only.

## Files And Artifacts Read

Status docs, architecture/contracts, Phase16/16B curated artifacts, 10 Phase16 expanded grid specs, 20 Layer1 configs, and the local-only Phase16 `runs/` sweep summaries were read. `CODEX_REVIEW.md` was read earlier in the task and intentionally not edited.

## Input Artifact Validation Summary

See `phase17_input_artifact_validation.csv`. Required curated Phase16B and Phase16 inputs were available. Local sweep CSVs under `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` were used as local-only inputs and are not copied or staged.

## Review Methodology

The review compares region medians, p25/p75 dispersion, best/worst total R, drawdown distribution, accepted-trade sample size, zero-trade counts, risk-per-share, cost-to-risk, H1/H2 behavior, and neighborhood support around top total-R rows. Top rows are warning inputs only, not candidates.

## Strategy Surface Status Summary

Status counts: {'WATCH_HIGH_DRAWDOWN': 3, 'ROBUST_REGION_CANDIDATE_FOR_FURTHER_REVIEW': 1, 'WATCH_REGIME_DEPENDENT': 1, 'WATCH_PROMISING_REGION': 2, 'WATCH_LOW_SAMPLE': 3}

Robust-for-further-review diagnostics: orb_continuation.

Watch diagnostics: pa_buy_sell_close_trend, orb_retest_continuation, failed_orb, gap_acceptance_failure, vwap_trend_pullback, vwap_reclaim_reject, prior_day_level_trap, cci_extreme_snapback, stochastic_oversold_cross.

Hold diagnostics: none.

## H1/H2 Interpretation

H1 is the cleaner design diagnostic. H2 contributes only diagnostic stress information because `missing_minute_slots_total=540` remains attached. H2-only strength is not confirmation and cannot unlock selection, candidate YAML, or Layer2.

## Region And Neighborhood Findings

`parameter_region_summary.csv`, `axis_marginal_summary.csv`, `pairwise_interaction_summary.csv`, and `h1_h2_cross_window_region_matrix.csv` provide the region-first review. `top_neighborhood_summary.csv` and `isolated_top_row_warning.csv` explicitly check whether top rows sit inside supportive neighborhoods.

## Isolated Top-Row Warnings

Warnings are anti-argmax diagnostics. Any `MEDIUM` or `HIGH` warning means a top row should be treated as isolated or insufficiently supported until a future region review proves otherwise.

## Drawdown / Sample / Risk / Cost Diagnostics

Drawdown uses positive drawdown magnitude ordering. Risk-per-share and cost-to-risk are aggregate-only summaries derived from execution-produced trade fields in existing sweep results; no fills, stops, targets, PnL, or R are recomputed.

## Phase18 Improvement Backlog Summary

`strategy_improvement_backlog.csv` contains 16 evidence-backed, non-promotional improvement items. The backlog is for design/implementation review only, not candidate promotion.

## Validation Results

See `validation_results.csv`. Phase17 added schema/no-promotion tests and records command outcomes there.

## Artifact Hygiene

Only curated Phase17 CSV/MD artifacts are generated under `artifacts/layer1_10_strategy_expanded_grid_region_review_phase17`. Local Phase16 run outputs remain local-only. No raw/curated/cache/parquet/npy/npz/memmap, row-level trades, row-level equity, top_runs, candidates, Layer2, Layer3, WFO, live, or paper artifacts are included.

## Explicit Non-Runs

No new Layer1 grids, no select-dry-run, no candidate YAML, no promotion, no Layer2, no Layer3, no WFO, no live/paper, no strategy retuning, no feature semantic changes, and no execution truth changes.

## Risks / Blockers

H2 warning remains the main data-quality risk. Failed ORB helper coverage remains thinner than ORB retest coverage from Phase16B. Validation of Phase16 full-grid completion is artifact-reported and this phase did not rerun grids.

## Decision

`PHASE17_EXPANDED_GRID_REGION_REVIEW_COMPLETE`

## Cursor Provisional Recommended Next Step

`DESIGN_PHASE18_EXISTING_10_STRATEGY_IMPROVEMENTS`

Final roadmap decision belongs to ChatGPT Pro + user after Codex review.
