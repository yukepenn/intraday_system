# NEXT_HANDOFF

Last updated: **2026-05-21** (Phase **19A repair** Layer1 side-runtime wiring).

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Pre-task HEAD: `202faea`
- Task commit hash: `pending_before_commit`.
- Codex review pending: yes.
- ChatGPT Pro review pending: yes.
- Cursor did not edit `CODEX_REVIEW.md`.

## B. Phase

`PHASE19A_REPAIR_LAYER1_SIDE_RUNTIME_WIRING`

## C. Task Type

Repair + validation + Layer1 side-runtime integration.

## D. What Was Done

- Added runner-local `_allowed_sides_from_strategy_cfg(...)` helper.
- Wired smoke path to pass `reference_close=bars.close` into `validate_signal_matrix(...)`.
- Wired controlled-grid path to pass `reference_close=bars.close` into `validate_signal_matrix(...)`.
- Wired smoke path to pass side-mode-derived `allowed_sides` into `build_trade_intents_from_signals(...)`.
- Wired controlled-grid path to pass side-mode-derived `allowed_sides` into `build_trade_intents_from_signals(...)`.
- Added synthetic Layer1 side-runtime tests for smoke/grid reference-close wiring, allowed-side derivation, short_only/both intent creation, long_only default skip behavior, execution `SHORT_NOT_ALLOWED` authority, short-enabled acceptance, and current-10 default equivalence.
- Added curated Phase19A repair artifacts.

## E. What Was Intentionally Not Done

- No strategies 11-17.
- No strategies 18-20.
- No feature work.
- No actual grids.
- No expanded/full grids.
- No select-dry-run.
- No candidate YAML.
- No promotion.
- No Layer2/3.
- No WFO/live/paper.
- No current-10 short retrofit.
- No execution truth or PnL/R accounting changes.
- No economic claims.

## F. Key Artifacts

Primary bundle:

`artifacts/phase19a_layer1_side_runtime_wiring_repair/`

Key files:

- `CHATGPT_REVIEW_BUNDLE.md`
- `SOURCE_MAP.csv`
- `chatgpt_key_tables.csv`
- `validation_results.csv`
- `side_runtime_wiring_summary.md`
- `side_runtime_test_matrix.csv`
- `current10_regression_summary.csv`
- `non_promotion_guardrails.md`
- `artifact_schema_validation.csv`
- `phase19a_repair_decision.md`

## G. Validation

See `artifacts/phase19a_layer1_side_runtime_wiring_repair/validation_results.csv`.

All required validation passed:

- CLI help / doctor / structure validation.
- `compileall` over `src` and `tests`.
- New Phase19A Layer1 side-runtime repair tests: 10 passed.
- Phase19A side-support regressions.
- Signal adapter, strategy contract, execution reference/cost regressions.
- Brooks Slice F1 regressions.
- Phase19A artifact/no-runtime-leakage regressions.
- Smoke tests.
- Ruff check and Ruff format check after import/format cleanup in the new test file.

## H. Risks / Blockers

- No remaining side-runtime wiring gap found in smoke or controlled-grid paths.
- No current-10 regression issue found.
- Local untracked Phase16 `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` hygiene debt remains and must not be staged.
- Candidate/promotion/Layer2 remain blocked because this repair did not create strategies, candidates, selection evidence, or economic validation.

## I. Decision

### `PHASE19A_LAYER1_SIDE_RUNTIME_WIRING_REPAIR_COMPLETE`

## J. Cursor Provisional Recommended Next Step

### `IMPLEMENT_PHASE19B_CORE_BROOKS_PA_STRATEGIES_11_TO_17`

Forbidden next steps:

- candidate YAML / promotion / select-dry-run
- actual Layer1 economic grids
- Layer2 / Layer3
- WFO / live / paper
- economic ranking or claims

## K. Note

Cursor recommendation is provisional only. Codex review and ChatGPT Pro review are required next. The final roadmap decision belongs to ChatGPT Pro and the user after Codex review.
