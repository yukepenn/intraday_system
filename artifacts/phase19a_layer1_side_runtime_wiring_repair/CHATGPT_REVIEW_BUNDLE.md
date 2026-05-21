# Phase19A Layer1 Side Runtime Wiring Repair Review Bundle

Phase name: `PHASE19A_REPAIR_LAYER1_SIDE_RUNTIME_WIRING`.

Task type: repair + validation + Layer1 side-runtime integration.

Git baseline: branch `main`, pre-task HEAD `202faea`.

## Why This Repair Was Needed

Codex Phase19A review passed with warnings because side support existed at the helper, adapter, and execution-boundary levels, but Layer1 orchestration was not yet passing close prices into signal validation or side-mode-derived allowed sides into the adapter.

## Codex Phase19A Warning Summary

`run_layer1_smoke(...)` and `run_layer1_controlled_grid(...)` still called `validate_signal_matrix(signals, bars.n_bars)` without `reference_close=bars.close`, and called `build_trade_intents_from_signals(...)` without `allowed_sides`. That left Layer1 effectively long-only at the adapter boundary and did not enforce short stop geometry at runtime.

## Exact Files Changed

- `src/intraday/layer1/runner.py`
- `tests/unit/test_phase19a_layer1_side_runtime_wiring.py`
- `README.md`
- `NEXT_HANDOFF.md`
- `PROJECT_STATUS.md`
- `PROGRESS.md`
- `CHANGES.md`
- `docs/PHASE_PLAN.md`
- `artifacts/phase19a_layer1_side_runtime_wiring_repair/*`

`CODEX_REVIEW.md` was not edited.

## Runner Wiring Summary

Layer1 now derives `allowed_sides` from strategy config `signal.side_mode` through `normalize_side_mode(...)` and `allowed_sides_for_mode(...)`. Both smoke and controlled-grid paths pass `reference_close=bars.close` to `validate_signal_matrix(...)` and pass `allowed_sides` to `build_trade_intents_from_signals(...)`.

## Side-Mode / Allowed-Sides Summary

- `long_only` maps to LONG only and remains the default when `signal.side_mode` is missing.
- `short_only` maps to SHORT only.
- `both` maps to LONG and SHORT.

Layer1 does not let strategy YAML override `ExecutionSpec.allow_short`.

## Reference-Close Validation Summary

Signal validation in Layer1 now receives `bars.close`, so long stops are checked below the signal close and short stops are checked above the signal close in the runtime runner paths.

## Current-10 Regression Summary

Current-10 default behavior remains behaviorally equivalent: missing `signal.side_mode` still normalizes to `long_only`, default execution remains `allow_short=false`, and existing long-only adapter behavior is preserved.

## Validation Results

See `validation_results.csv`. Final required validation passed after a minor Ruff import/format cleanup in the new test file.

## Explicit Non-Runs

- no actual Layer1 grids
- no expanded/full grids
- no select-dry-run
- no candidate YAML
- no promotion
- no Layer2/Layer3
- no WFO/live/paper
- no economic ranking or claims

## Risks / Blockers

No Layer1 side-runtime blocker remains for the repaired smoke and controlled-grid paths. Candidate/promotion/Layer2 remain blocked because no Phase19 strategy runtime, candidate pool, economic grid, or selection evidence was created in this repair.

## Decision

`PHASE19A_LAYER1_SIDE_RUNTIME_WIRING_REPAIR_COMPLETE`

## Cursor Provisional Recommended Next Step

`IMPLEMENT_PHASE19B_CORE_BROOKS_PA_STRATEGIES_11_TO_17`

Final roadmap decision belongs to ChatGPT Pro + the user after Codex review.
