# Phase19A Review Bundle

Phase name: `PHASE19A_IMPLEMENT_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION_SLICE`.

Task type: infrastructure + limited feature implementation + validation.

Git baseline: branch `main`, pre-task HEAD `5eb067b`.

## Why This Phase Was Needed

Phase19 design completed Brooks PA strategy specs and side-support architecture, but Codex review warned that README/status were stale and `pa_brooks_swing_core` packaging was ambiguous. Phase19A implements only the shared side-support foundation and Brooks PA Slice F1 feature foundation before any strategy 11-20 code is allowed.

## Phase19 Design + Codex Warning Summary

Codex verdict was `PASS_WITH_WARNINGS`: side support was system-wide and strong, current defaults needed preservation, README was stale, swing-core packaging needed a concrete choice, Brooks features were broad, and implementation should be split. Phase19A follows that split.

## README / Status Cleanup Summary

README, status docs, progress/changelog, phase plan, and handoff are updated to show Phase19A completion scope and explicitly preserve non-promotion boundaries.

## Swing-Core Packaging Decision

Option A: lightweight `pa_brooks_swing_core` lives inside `pa_brooks_core_v1.yaml`. No separate `pa_brooks_swing_v1.yaml` is created. Advanced swing/reversal classifiers remain deferred.

## Side-Support Implementation Summary

The shared SignalMatrix contract now accepts `side=+1` and `side=-1`, with optional side-specific stop geometry checks against reference close. The signal adapter now supports explicit `allowed_sides`, defaults to long-only, rejects short by default with `side_not_allowed`, and accepts short only when the caller opts in. Execution remains the final `SHORT_NOT_ALLOWED` authority.

## Brooks Feature Slice F1 Summary

Created:

- `configs/features/pa_brooks_core_v1.yaml`
- `configs/features/pa_brooks_range_v1.yaml`

Implemented market-fact groups:

- `pa_brooks_bar_core`
- `pa_brooks_regime_core`
- `pa_brooks_swing_core`
- `pa_brooks_range_core`

Total Slice F1 columns: 61. No strategy decision labels, outcome labels, PnL/R labels, fill/target labels, or target prices are created.

## Validation Summary

Targeted Phase19A side-support and Brooks feature tests passed before artifact finalization. Full validation status is recorded in `validation_results.csv`.

## Current-10 Backward Compatibility Summary

Default execution remains `allow_short=false`. Current-10 base and Phase18B configs still normalize to `long_only`. No current-10 strategy source files were retrofitted to short.

## Explicit Non-Runs

- no strategies 11-20 source files
- no Phase19 strategy runtime YAMLs
- no Layer1 grid runs
- no select-dry-run
- no candidate YAML
- no promotion
- no Layer2/3
- no WFO/live/paper
- no economic claims

## Risks / Blockers

No Phase19A blocker remains. Deferred risk is feature breadth for opening/reversal slices and eventual strategies 18-20; those require later review.

## Decision

`PHASE19A_SIDE_SUPPORT_AND_FEATURE_SLICE_COMPLETE`

## Cursor Provisional Next Step

`IMPLEMENT_PHASE19B_CORE_BROOKS_PA_STRATEGIES_11_TO_17`

Final roadmap decision belongs to ChatGPT Pro + user after Codex review.
