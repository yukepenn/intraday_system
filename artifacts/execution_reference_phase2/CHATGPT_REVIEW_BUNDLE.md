# CHATGPT_REVIEW_BUNDLE — execution_reference_phase2

Readable review bundle for Phase 2 (reference execution). Git baseline: **`7110c1f`** on `main` matched `origin/main` before the Phase 2 patch (see `baseline_inventory.*`).

## Why Phase 2 was needed

Layer 0 (`BarMatrix`) was ready; research truth for fills, stops, targets, session rules, and R-multiples must exist **only** in execution before Layer1/Layer2 consume candidates. This phase implements that Python reference.

## Preflight cleanup

Data README files now state **local-only / gitignored** raw and curated parquet, canonical QQQ expectations, legacy SPY note, relative config paths, and accepted raw timestamp column names. `RAW_REQUIRED_OHLCV_COLUMNS` replaces the misleading `timestamp` tuple entry (alias preserved). **No loader behavior change.**

## ExecutionSpec / TradeIntent / TradeResult

- Spec: validated bounds and enums; YAML load; safe `allow_short`.
- Intent: `validate_shape` for OOB / bad side / qty / `target_r`.
- Result: `rejected` / `accepted_trade`; rejected uses NaN prices and `ExitReason.REJECTED`.
- New reject: `INVALID_INTENT` — see `execution_contract_changes.md`.

## Materialization semantics

Next-open entry, cross-session rejection, entry slippage, stop geometry and `min_risk_per_share`, fixed-R target from **actual** entry, max-hold resolution (`intent` → `spec` default → none). See `materialization_summary.md`.

## Reference path semantics

Intrabar stop/target first; same-bar policy; then EOD (`minute >= eod_exit_minute`); then max-hold (**EOD wins** if both on same bar); session roll and truncated end both exit at **prior/last close** with `ExitReason.EOD`. Non-`None` `management_plan` is an error. See `reference_path_summary.md`.

## Cost / R-multiple

Adverse entry and exit slippage; fixed commission per trade; R from **net** PnL over risk dollars. See `cost_conventions.md`.

## Test matrix

Synthetic `BarMatrix` only — **no QQQ in unit tests**. See `test_matrix.md` / `.csv`.

## Validation results

`compileall`, `pytest` (**127**), Ruff format/check, CLI help/doctor/validate structure, local QQQ `validate-curated` + `load-bars` for 2024H1. See `validation_results.md`.

## Explicit non-implemented items

- Numba `execution.fast` body, parity harness wiring beyond placeholders.
- Feature kernels, strategies, Layer1/2/3, candidate YAML, portfolio sizing, management overlays.

## Risks / blockers

- Windows `safe.directory` git warning.
- SPY legacy raw tree until migrated.
- Exchange early-close calendar still heuristic at Layer 0.

## Decision

`REFERENCE_EXECUTION_ENGINE_COMPLETE`

## Recommended next step

`IMPLEMENT_FAST_EXECUTION_SKELETON_AND_PARITY`
