# NEXT_HANDOFF

Last updated: **2026-05-21** (Phase **19 Immediate Fix**: setup codes,
side consistency, and current-10 short retrofit).

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Pre-task HEAD: `ca216cb`
- Task commit hash: `587af5c`
- Push status: pushed to `origin/main`
- Codex review pending: yes (Phase19 immediate fix)
- ChatGPT Pro review pending: yes (after Codex review)
- Cursor did not edit `CODEX_REVIEW.md`.

## B. Phase

`PHASE19_IMMEDIATE_FIX_SETUP_CODES_SIDE_CONSISTENCY_AND_CURRENT10_SHORT_RETROFIT`

## C. Task Type

Repair + infrastructure + validation + controlled side-aware strategy
retrofit.

## D. What Was Done

- Setup-code governance:
  - Added authoritative runtime registry
    `src/intraday/strategies/setup_codes.py` with `SetupCodeSpec`,
    `SETUP_CODES`, `get_setup_codes`, `setup_code_for_side`,
    `all_setup_code_specs`.
  - Added `docs/SETUP_CODE_REGISTRY.md` governance policy.
  - Added `tests/unit/test_setup_code_registry.py` asserting uniqueness,
    int16, expected values, and no leakage of the wrong Phase19B codes.

- Phase19B setup-code namespace repair:
  - Strategies 11-17 now derive `SETUP_CODE_LONG`/`SETUP_CODE_SHORT`
    from the registry: 7101-7107 / 7201-7207.
  - Metadata YAMLs in `configs/strategies/metadata/phase19/` updated
    to nested `setup_codes: {long, short}`.
  - Phase19B inventory artifact and review bundle updated.

- Boolean coercion repair:
  - Added `brooks_bool(signal_config, key, default)` helper in
    `src/intraday/strategies/pa/brooks_common.py`.
  - Replaced every `bool(sig.get(...))` / `bool(config.get(...))`
    pattern in Phase19B strategy modules with `brooks_bool(...)`.
  - Added `tests/unit/test_phase19_immediate_boolean_config_coercion.py`
    with semantics tests and a static-source-scan test.

- Metadata + strategy inspect authority:
  - Extended `StrategyDef` with `setup_code_long`, `setup_code_short`,
    `allowed_side_modes`, `default_side_mode`, `required_feature_columns`.
  - Updated every current-10 and Phase19 core `StrategyDef`
    constructor to register these fields.
  - Updated `src/intraday/cli/strategy_cmds.py::cmd_strategies_inspect`
    to surface them and include `metadata_setup_codes`,
    `metadata_diagnostic_only`, `metadata_grid_inspect_only` as an
    audit cross-check.
  - Current-10 and Phase19 metadata YAMLs aligned with
    `core_or_diagnostic: core`, `diagnostic_only: false`,
    `grid_inspect_only: true`, `side_mode_allowed`/`default_side_mode`.
  - Added `tests/unit/test_strategy_metadata_alignment.py` and
    `tests/unit/test_strategy_inspect_metadata.py`.

- Generic side-aware helpers:
  - Added `compute_short_stop`, `build_side_aware_signal_matrix`,
    `crossed_below` in `src/intraday/strategies/common.py`.
  - Added `validate_side_aware_strategy_base` and
    `CURRENT10_SIDE_MODES` in `src/intraday/strategies/config_validation.py`.

- Current-10 short retrofit:
  - All 10 current-10 strategies now expose a `side_mode`-gated short
    branch with the approved short setup codes (8001 / 9001-9003 /
    10001 / 11001-11002 / 12001 / 13001-13002).
  - Default behavior remains `long_only`; missing `side_mode` validates
    as `long_only`; legacy `signal.side: long_only` still validates.
  - Canonical base configs migrated to `signal.side_mode: long_only`.
  - Added new inspect-only side-aware grid skeletons in
    `configs/strategies/grids/phase19_immediate_fix_current10_side_aware/`.
  - Added new inspect-only Layer1 configs in
    `configs/layer1/phase19_immediate_fix_current10_side_aware_grid_inspect/`.
  - Added new tests: `test_current10_side_aware_configs.py`,
    `test_current10_short_signal_generation.py`,
    `test_current10_side_aware_missing_features.py`,
    `test_current10_side_aware_no_lookahead_session.py`,
    `test_current10_long_only_backward_compatibility.py`.

- Test cleanup:
  - Updated `tests/unit/test_phase19b_side_mode_validation.py` to
    assert that current-10 now accepts all three modes.
  - Updated `tests/unit/test_strategy_loader.py::test_invalid_side_rejected`
    to use an actually invalid side value.
  - Retired stale design-only no-runtime-leakage tests in
    `tests/unit/test_phase19a_no_runtime_leakage.py` and
    `tests/unit/test_phase19_design_no_runtime_leakage.py`; remaining
    tests still enforce that diagnostic strategies 18-20 stay deferred.

## E. What Was Intentionally Not Done

- No actual Layer1 economic grids.
- No expanded / full grids.
- No `select-dry-run`.
- No candidate YAML.
- No promotion.
- No Layer2 / Layer3.
- No WFO / mini-WFO.
- No live / paper configs.
- No strategies 18-20 implementation (still deferred).
- No strategies 21-50.
- No execution PnL/R/accounting semantic change.
- No `should_buy` / `should_short` / outcome-label features.
- No centered pivots.
- No retuning of parameters based on outputs.
- No economic claims.

## F. Key Artifacts

Primary bundle:

`artifacts/phase19_immediate_fix_setup_codes_side_consistency/`

Key files:

- `CHATGPT_REVIEW_BUNDLE.md`
- `SOURCE_MAP.csv`
- `chatgpt_key_tables.csv`
- `validation_results.csv`
- `setup_code_registry.csv`
- `setup_code_policy.md`
- `setup_code_repair_matrix.csv`
- `phase19b_setup_code_repair_matrix.csv`
- `boolean_config_coercion_repair_matrix.csv`
- `metadata_semantics_repair_matrix.csv`
- `strategy_inspect_metadata_repair_summary.md`
- `current10_short_retrofit_design.md`
- `current10_short_retrofit_inventory.csv`
- `current10_side_mode_test_matrix.csv`
- `phase19b_repair_test_matrix.csv`
- `feature_strategy_contract_audit.md`
- `non_promotion_guardrails.md`
- `artifact_schema_validation.csv`
- `phase19_immediate_fix_decision.md`

## G. Validation Results

See `validation_results.csv`. Headline:

- `python -m pytest tests/unit` -> 1105 passed, 4 skipped.
- `python -m pytest tests/smoke` -> 25 passed.
- `ruff check` and `ruff format --check` -> clean.
- `python -m intraday.cli.main doctor` / `validate structure` -> ok.
- `python -m intraday.cli.main strategies inspect ...` -> setup codes,
  required feature columns, allowed side modes, and metadata
  cross-check appear for every strategy.
- `python -m intraday.cli.main layer1 grid-inspect` on a current-10
  side-aware config -> combo_count=12 returned successfully.

## H. Risks / Blockers

- None at the immediate-fix level.
- Pre-existing Phase19A/B design-only no-leakage tests were updated to
  reflect that Phase19B has legitimately implemented strategies 11-17.
- Current-10 short branches are structurally complete but **not**
  economically claimed; any economic decision is gated on a separate
  phase with proper Layer1 evaluation.

## I. Artifact Hygiene

- No heavy/raw/cache/parquet/run artifacts staged.
- No `git add .`.
- `CODEX_REVIEW.md` untouched by Cursor.
- Only the explicit files listed in the SOURCE_MAP plus the canonical
  current-10 base/metadata YAMLs and Phase19 metadata YAMLs were
  modified.

## J. Decision

`PHASE19_IMMEDIATE_FIX_COMPLETE`

## K. Cursor Provisional Recommended Next Step

Open a fresh Codex review on this immediate fix using the focus list in
the task spec. After Codex review, ChatGPT Pro + the user make the
roadmap call (likely either targeted Phase19C polish or a transition to
Layer2 design after confirming current-10 long behavior is unchanged).
This recommendation is **provisional**.

## L. Post-Push Reminder

After Cursor pushes this task, open a NEW Codex review thread and run
the Phase19-immediate-fix Codex review prompt. Codex should:

- not modify source / tests / configs / artifacts,
- not run long commands, actual Layer1 grids, Layer2, WFO, live, or
  paper,
- only create / update `CODEX_REVIEW.md`,
- and only commit `CODEX_REVIEW.md`.
