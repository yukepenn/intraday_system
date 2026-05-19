# Phase15 Review Bundle

## Summary

- Phase name: `PHASE15_LAYER1_STRATEGY_LIBRARY_RESULT_REVIEW_AND_FOCUSED_GRID_DESIGN`
- Branch: `main`
- Pre-task HEAD: `9df439e8602d8366dfc21778e2dc640620e56b0e`
- Phase14 Cursor commit reviewed by Codex: `407ee3827c7dc761498633bf2c001825fb4591f5`
- Phase14 target parent: `dbaeb3d96f32585d04ed9450affa0751b1a974e9`
- Latest Codex review commit: `9df439e8602d8366dfc21778e2dc640620e56b0e`
- HEAD is Codex review commit: `true`
- Codex changed only `CODEX_REVIEW.md`: `true`
- Working tree before edits: clean
- Decision label: `LAYER1_STRATEGY_LIBRARY_RESULT_REVIEW_COMPLETE`
- Recommended next step: `RUN_LAYER1_STRATEGY_LIBRARY_FOCUSED_DIAGNOSTIC_GRID`

## Files Read

Read root roadmap/status docs, architecture/contracts, Phase14 review artifacts, Phase14 configs/inventories, representative H1/H2 sweep results, feature configs, strategy grids, candidate/Layer2 placeholders, and Layer1 config/grid/runner/report/result code. `CODEX_REVIEW.md` was read and left untouched.

## Phase14 Evidence Reviewed

- `per_strategy_grid_summary.csv`, `per_strategy_health_summary.csv`, `skip_reject_summary.csv`, `feature_signal_hash_summary.csv`, `data_availability_summary.csv`, `phase14_run_manifest.csv`, `layer1_config_inventory.csv`.
- All 20 representative H1/H2 `sweep_results.csv` files were parsed for schema and row counts.
- H1 and H2 runs report `CLEAN_PLUMBING` for all 10 active strategies.

## Strategy Status Summary

- `pa_buy_sell_close_trend`: `LEGACY_HOLD` - Phase10 held PA; Phase14 has positive best rows but negative medians in both windows and high drawdown, so this does not revive PA tuning.
- `orb_continuation`: `FOCUSED_DIAGNOSTIC_CANDIDATE` - Only family with positive best and positive median total_r in both observed windows, with clean plumbing and enough sample for a bounded future diagnostic design.
- `orb_retest_continuation`: `WATCH_REGIME_FLIP` - H1 median is positive but H2 median turns negative; best rows alone are not enough for focused status.
- `failed_orb`: `HOLD_WEAK_OR_NEGATIVE` - H1 best row is negative and both window medians are negative; H2 best row is not confirmation evidence.
- `gap_acceptance_failure`: `WATCH_LOW_SAMPLE` - Small-N and infinite profit-factor artifacts dominate; positive best rows are not stable evidence.
- `vwap_trend_pullback`: `WATCH_HIGH_DRAWDOWN` - Best rows are positive, but medians are negative and drawdown is too high for focused status.
- `vwap_reclaim_reject`: `WATCH_REGIME_FLIP` - H1 is weak across best and median while H2 is positive; H2 cannot be confirmation due phase scope and data warning.
- `prior_day_level_trap`: `WATCH_REGIME_FLIP` - H2 median is positive but H1 median is negative; this is a watch item, not a focused candidate.
- `cci_extreme_snapback`: `WATCH_HIGH_DRAWDOWN` - Positive best rows coexist with strongly negative medians and severe drawdown, so top-row interpretation is unsafe.
- `stochastic_oversold_cross`: `WATCH_HIGH_DRAWDOWN` - Both medians are near -10R despite positive best rows; drawdown risk dominates.

## H1/H2 Interpretation

Only `orb_continuation` has positive median total_r in both observed windows with adequate sample. Several families have positive best rows, but negative medians, high drawdown, H1/H2 asymmetry, low sample, or zero-signal combos. H1/H2 are design diagnostics only and are not candidate evidence.

## H2 Data Warning

H2 carries `missing_minute_slots_total=540`. H2 was allowed as an exact-repeat sanity/plumbing diagnostic only. It is not confirmation evidence and must not be used alone to promote, tune, or rank strategies.

## Focused-Grid Design Summary

A future bounded Phase16 focused diagnostic grid is reasonable for `orb_continuation` only, capped at 36 combos. The scope remains non-promotional, pre-registered, and diagnostic. Watch/hold families should not enter the first focused grid unless a later prompt defines a separate bounded shadow diagnostic.

## Promotion Prerequisite Gaps

Promotion remains blocked by fresh-holdout, multi-window, data-quality, selection-gate, drawdown/sample/stability, artifact-schema, candidate-YAML-schema, full resolved config reconstruction, Codex review, and ChatGPT strategic approval requirements.

## Ruff / Hygiene Triage

Full-repo Ruff remains red due known pre-existing script files: `scripts/generate_phase7_dry_run.py` and `scripts/validate_repo.py`. This does not block Phase15 unless tests fail, but should be repaired before heavier research or tracked as `REPAIR_PREEXISTING_RUFF_SCRIPT_BASELINE`.

## Explicit Non-Goals Preserved

No new Layer1 grid, no select-dry-run, no candidate YAML, no promotion, no Layer2, no Layer3, no WFO, no live/paper, no strategy retuning, no feature semantics changes, no execution truth changes, no QT runtime dependency, and no heavy/local artifacts.

## Validation Commands Run

See `validation_results.csv`.

## Known Limitations

- Phase15 uses existing Phase14 artifacts only and does not regenerate research results.
- H2 remains caveated by the missing-minute warning.
- Classification is review/design only, not a ranking for live/paper or promotion.
- `final_commit` is recorded in the final Cursor response after commit.
