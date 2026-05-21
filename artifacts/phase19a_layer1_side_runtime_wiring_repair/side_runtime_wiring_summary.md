# Phase19A Layer1 Side Runtime Wiring Summary

## Missing After Phase19A

Phase19A had shared side helpers, a side-aware adapter, and execution short-boundary tests, but Layer1 runner paths still used default long-only adapter behavior and did not pass close prices into signal validation.

## Runner Patch

`run_layer1_smoke(...)` and `run_layer1_controlled_grid(...)` now:

- derive `allowed_sides` from the resolved strategy config;
- pass `reference_close=bars.close` into `validate_signal_matrix(...)`;
- pass `allowed_sides` into `build_trade_intents_from_signals(...)`.

## Side Mode Mapping

Layer1 uses the contract helpers rather than duplicating parsing logic:

- `long_only` -> LONG only
- `short_only` -> SHORT only
- `both` -> LONG and SHORT

Missing `signal.side_mode` remains `long_only`, preserving current-10 behavior.

## Adapter / Execution Boundary

The adapter does not inspect `ExecutionSpec.allow_short` and does not pre-filter shorts based on execution policy. It only turns allowed signal sides into `TradeIntent`s. Execution remains the final authority: if `allow_short=false`, a short intent is rejected with `SHORT_NOT_ALLOWED`, preserving the audit trail.

## Current Default Preservation

Default strategy configs without `signal.side_mode` continue to normalize to `long_only`. Default execution remains `allow_short=false`. No current-10 strategy was retrofitted to emit short signals.
