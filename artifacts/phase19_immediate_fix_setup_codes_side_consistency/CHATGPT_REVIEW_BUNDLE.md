# ChatGPT Review Bundle — Phase19 Immediate Fix

- **Phase**: PHASE19_IMMEDIATE_FIX_SETUP_CODES_SIDE_CONSISTENCY_AND_CURRENT10_SHORT_RETROFIT
- **Task type**: repair + infrastructure + validation + controlled side-aware retrofit
- **Git baseline**: `ca216cb` (origin/main at start of this phase)
- **Final commit**: filled after commit

> Final roadmap decision belongs to ChatGPT Pro + the user after the
> subsequent Codex review.

## Why this phase was needed

Codex review of Phase19B (`PHASE19B_CORE_BROOKS_STRATEGIES_11_TO_17_*`)
returned NEEDS_FIX with two blocker-level findings:

1. **Setup-code namespace drift**: Phase19B implemented strategies
   11-17 with setup codes `1101/1102 .. 1701/1702`. The Phase19 design
   had accepted `7101-7110 / 7201-7210`. This was unacceptable.
2. **Boolean config coercion mismatch**: validation accepted
   boolean-like strings via `parse_bool_like`, but runtime used
   `bool(sig.get(...))`, so `"false"` could pass validation and execute
   as `True`.

A lower-priority issue was the weak inspect/metadata authority for new
strategies. The user instruction was to treat setup-code drift as
unacceptable, make all setup-code / side-mode policy generic and
consistent, and retrofit current-10 with short branches where
structurally supported — all under a controlled non-promotional
Phase19 Immediate Fix.

## Setup-code registry summary

- New runtime registry: `src/intraday/strategies/setup_codes.py`.
- Governance doc: `docs/SETUP_CODE_REGISTRY.md`.
- `SetupCodeSpec` dataclass, `SETUP_CODES` dict, helpers
  `get_setup_codes`, `setup_code_for_side`, `all_setup_code_specs`.
- All codes unique and fit `int16`. Tests in
  `tests/unit/test_setup_code_registry.py` enforce uniqueness, int16,
  expected values, and absence of the wrong 1101-1702 codes from
  current source/configs/metadata.

## Phase19B setup-code repair summary

- Strategies 11-17 now import setup codes from the registry. Hardcoded
  constants `SETUP_CODE_LONG`/`SETUP_CODE_SHORT` derive from
  `get_setup_codes(STRATEGY_NAME)` so source and registry cannot drift.
- Metadata YAMLs in `configs/strategies/metadata/phase19/` updated to
  nested `setup_codes: {long, short}` with the correct values.
- Phase19B inventory/artifacts updated accordingly.
- All Phase19B tests pass with the corrected values; no test still
  asserts 1101-1702.

## Boolean coercion repair summary

- New `brooks_bool(signal_config, key, default)` helper in
  `src/intraday/strategies/pa/brooks_common.py` that uses
  `parse_bool_like` so runtime semantics match validation.
- Every `bool(sig.get(...))` / `bool(config.get(...))` pattern in
  Phase19B strategy modules replaced with `brooks_bool`.
- `tests/unit/test_phase19_immediate_boolean_config_coercion.py` asserts
  semantics (`true`/`false`/`0`/`1`/invalid) and includes a static
  source-scan test that fails if the pattern reappears.

## Metadata / inspect repair summary

- `StrategyDef` extended with optional `setup_code_long`,
  `setup_code_short`, `allowed_side_modes`, `default_side_mode`,
  `required_feature_columns`.
- Every current-10 and Phase19 core strategy registers these fields.
- CLI `strategies inspect` now surfaces these from `StrategyDef` and
  cross-checks against metadata YAML (`metadata_setup_codes`,
  `metadata_diagnostic_only`, `metadata_grid_inspect_only`).
- All current-10 and Phase19 metadata YAMLs set
  `core_or_diagnostic: core`, `diagnostic_only: false`,
  `grid_inspect_only: true`, with `side_mode_allowed`/`default_side_mode`.
- Tests: `test_strategy_metadata_alignment.py`,
  `test_strategy_inspect_metadata.py`.

## Current-10 short retrofit summary

- New generic helpers in `src/intraday/strategies/common.py`:
  `compute_short_stop`, `build_side_aware_signal_matrix`, `crossed_below`.
- New `validate_side_aware_strategy_base` and `CURRENT10_SIDE_MODES`
  in `config_validation.py`.
- All 10 current-10 strategies now expose a short branch behind
  `signal.side_mode`. Default behavior remains `long_only`.
- Canonical base configs migrated from legacy `signal.side: long_only`
  to `signal.side_mode: long_only`.
- New inspect-only side-aware grid skeletons in
  `configs/strategies/grids/phase19_immediate_fix_current10_side_aware/`.
- New inspect-only Layer1 configs in
  `configs/layer1/phase19_immediate_fix_current10_side_aware_grid_inspect/`.

## Validation results

See `validation_results.csv`. Summary:

- `python -m pytest tests/unit` -> 1105 passed, 4 skipped.
- `python -m pytest tests/smoke` -> 25 passed.
- `ruff check` and `ruff format --check` -> clean.
- `python -m intraday.cli.main doctor` / `validate structure` -> ok.
- `python -m intraday.cli.main strategies list` -> 17 strategies.
- `python -m intraday.cli.main strategies inspect ...` -> setup codes
  and required features now appear for every strategy.
- `python -m intraday.cli.main layer1 grid-inspect` on a current-10
  side-aware config -> combo_count=12 returned successfully.

## Explicit non-runs

- No actual Layer1 economic grids.
- No expanded / full grids.
- No `select-dry-run`.
- No candidate YAML created.
- No promotion.
- No Layer2 / Layer3.
- No WFO / mini-WFO.
- No live / paper configs.
- No execution PnL/R/accounting semantic change.
- No new feature kernels.
- No QT runtime dependency added.

## Risks / blockers

- None at the immediate-fix level. Pre-existing Phase19A/B
  "design-only no-leakage" tests were updated to reflect that Phase19B
  has legitimately implemented strategies 11-17 (diagnostic strategies
  18-20 remain explicitly deferred).
- The current-10 short branches share generic-feature heuristics. They
  are structurally complete but **not** economically claimed; any
  economic decision is gated on a separate phase with proper Layer1
  evaluation, which is intentionally outside this phase's scope.

## Decision

`PHASE19_IMMEDIATE_FIX_COMPLETE`

## Cursor provisional recommended next step

Open a fresh Codex review on this immediate fix, focusing on the audit
points listed in the original task spec. Roadmap decision after that
review belongs to ChatGPT Pro + the user.
