# Phase19 Brooks PA Design Review Bundle

Phase name: `PHASE19_DESIGN_BROOKS_PA_STRATEGIES_11_TO_20_WITH_SIDE_SUPPORT`.

Task type: design-only + multi-strategy design + side-support architecture design + Brooks PA feature/strategy design + onboarding plan.

Git baseline: branch `main`, pre-task HEAD `cd11ed9`.

## Why Phase19 design was needed

Phase18D operationalized existing contracts into the Phase19-22 onboarding checklist and Phase19 strategy-addition template, and confirmed the refined current-10 v2 package is inspectable and integration-ready. Project recommendation was `DESIGN_PHASE19_STRATEGIES_11_TO_20` — but design work was not done in Phase18D. Phase19 design produces the executable design package the future implementation phase requires, including:

- a system-wide side-support foundation (long/short within a single strategy file)
- a Brooks PA feature foundation that is market-fact-only
- ten Brooks PA strategy designs (strategies 11-20) that are explicitly non-duplicates of current-10
- file/test/validation plans for the future implementation phase
- explicit non-goals and non-promotion guardrails

## Phase18D acceptance summary

Phase18D decision was `PHASE18D_CURRENT10_REFINED_READINESS_COMPLETE`. All inspect/validation checks passed; no actual Layer1 grids; no candidate YAML; no promotion; no Layer2/3; no WFO; no live/paper; H2 diagnostic-only; current-10 long-only and behaviorally unchanged.

## Codex Phase18D warnings carried forward

1. Validation/inspect claims are credible from artifacts/tests but not independently rerun by Codex.
2. Local untracked Phase16 `runs/` tree (`artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/`) remains hygiene debt and must NOT be staged.
3. `FeatureMatrix.column()` missing-feature error-shape change from `KeyError` to `ConfigError` is contract-aligned but should be remembered.
4. Phase18D readiness means integration/checklist readiness only, not economic validation.

Phase19 design respects all four warnings:

- Phase19 design did not modify runtime code; no Codex rerun is needed for runtime behavior.
- The local Phase16 `runs/` tree is not staged. Verified by selective `git add` and final `git diff --cached --name-only`.
- Phase19 design assumes and relies on the `ConfigError` shape for missing required feature columns; Phase19 missing-feature tests are designed to assert `ConfigError` explicitly.
- Phase19 design makes zero economic claims and contains no top-row ranking.

## Side-support design summary

Phase19A introduces `signal.side_mode ∈ {long_only, short_only, both}` as a per-strategy YAML field. The existing `Side` enum, `ExecutionSpec.allow_short`, and `RejectReason.SHORT_NOT_ALLOWED` are already short-aware in execution. The Phase19 implementation phase must extend `validate_signal_matrix` and `build_trade_intents_from_signals` to round-trip `side=-1` end-to-end, while preserving long-only behavior byte-for-byte when only longs are present. The default execution config and all current-10 YAMLs are unchanged. Short execution is gated by execution `allow_short`, which stays `false` in the default. A reserved setup-code namespace (`7101..7110` long, `7201..7210` short) is allocated for Phase19 strategies. See `side_support_design.md` and `side_support_test_plan.csv`.

## Brooks PA feature foundation design summary

Four future feature config groups are designed (`pa_brooks_core_v1`, `pa_brooks_range_v1`, `pa_brooks_opening_v1`, `pa_brooks_reversal_v1`) plus one optional (`pa_brooks_magnet_v1`). All features are market facts only; no outcome labels, no future-bar dependencies, no centered pivots. Swing/wedge/MTR proxies are prior-exclusive or delayed-confirmed. Existing kernels (VWAP, ORB, ATR, range, body/wick, levels, indicators) are reused wherever possible. The design includes a four-slice implementation plan (F1 mandatory before any Phase19 strategy ships; F2 before strategy 14; F3 before strategies 18-20; F4 optional). A formal split-into-sub-phases escape hatch is recorded for the implementation phase. See `brooks_pa_feature_foundation_design.md` and `brooks_pa_feature_audit_matrix.csv`.

## Strategies 11-20 summary

Strategies 11-20 are designed as side-aware Brooks PA setups. Strategies 11-17 are core; strategies 18-20 are diagnostic-only.

| # | Strategy | Family | Side modes |
|---|----------|--------|------------|
| 11 | `pa_second_entry_pullback` | pa | long_only / short_only / both |
| 12 | `pa_trading_range_bls_hs` | pa | long_only / short_only / both |
| 13 | `pa_failed_breakout_trap` | pa | long_only / short_only / both |
| 14 | `pa_opening_reversal_sr` | pa | long_only / short_only / both |
| 15 | `pa_breakout_pullback_continuation` | pa | long_only / short_only / both |
| 16 | `pa_tight_channel_pullback` | pa | long_only / short_only / both |
| 17 | `pa_broad_channel_zone` | pa | long_only / short_only / both |
| 18 | `pa_mtr_reversal_diagnostic` | pa | long_only / short_only / both (diagnostic_only) |
| 19 | `pa_wedge_reversal_diagnostic` | pa | long_only / short_only / both (diagnostic_only) |
| 20 | `pa_climax_reversal_diagnostic` | pa | long_only / short_only / both (diagnostic_only) |

Each strategy has long+short setups, stop geometry, target_r policy (always `fixed_r`), required features, validation rules, rational bounded grid skeletons, and per-strategy test plans. See `brooks_pa_strategy_specs.md` and `brooks_pa_strategy_design_matrix.csv`.

## Duplicate avoidance summary

The duplicate-avoidance matrix explicitly rejects strategies that overlap with current-10:

- `pa_opening_breakout_continuation` — duplicates `orb_continuation`.
- `pa_gap_open_reversal_failure` — duplicates `gap_acceptance_failure`.
- `pa_prior_day_level_trap` — duplicates `prior_day_level_trap`.
- `pa_vwap_reclaim_reject` — duplicates `vwap_reclaim_reject`.
- `pa_orb_retest` — duplicates `orb_retest_continuation`.
- `pa_orb_continuation` — duplicates `orb_continuation`.

The matrix also rejects feature/filter/management concepts as standalone strategies:

- `pa_market_cycle_router` (Layer2 router work)
- `pa_tight_tr_no_trade_filter`, `pa_final_flag_filter`, `pa_time_of_day_swing_filter` (filter/feature only)
- `pa_measured_move_target_engine`, `pa_magnet_target_engine` (management/Layer2)
- discretionary Brooks concepts (scale-in, lower-timeframe early entry, EOD close-auction, complex nested pattern classifier)

See `brooks_pa_duplicate_avoidance_matrix.csv`.

## Future implementation file plan summary

The future implementation phase must create:

- 1 shared helper module `src/intraday/strategies/pa/brooks_common.py`.
- 10 Phase19 strategy source files under `src/intraday/strategies/pa/`.
- 4 Brooks feature YAMLs under `configs/features/` (plus optional magnet).
- 10 base configs under `configs/strategies/base/phase19/`.
- 10 metadata configs under `configs/strategies/metadata/phase19/`.
- 10 controlled-small grid configs under `configs/strategies/grids/phase19/`.
- 10 Layer1 grid-inspect-only configs under `configs/layer1/phase19_brooks_pa_grid_inspect/`.
- 3 source edits: `src/intraday/strategies/contracts.py`, `src/intraday/backtest/signal_adapter.py`, `src/intraday/strategies/registry.py`. Optionally extend `src/intraday/strategies/config_validation.py`.

See `phase19_file_plan.csv`.

## Future test plan summary

- `tests/unit/test_phase19_side_support_contract.py` — Phase19A contract tests.
- `tests/unit/test_phase19_signal_adapter_short_support.py` — Phase19A adapter tests.
- `tests/unit/test_phase19_brooks_features.py` — feature-foundation tests.
- `tests/unit/test_phase19_brooks_strategy_configs.py` — config validators.
- `tests/unit/test_phase19_brooks_strategy_signals.py` — signal-generation tests.
- `tests/unit/test_phase19_missing_features.py` — fail-closed `ConfigError`.
- `tests/unit/test_phase19_no_lookahead.py` — no-lookahead and session-reset.
- `tests/unit/test_phase19_no_runtime_leakage.py` — guardrail.
- `tests/unit/test_phase19_artifact_schema.py` — Phase19 design artifact schema.

See `phase19_test_plan.csv`.

## Validation results

The Phase19 design phase ran only design-validation commands. See `validation_results.csv`. No runtime implementation command was executed.

## Artifact hygiene

Phase19 design artifacts contain only `.md` and `.csv` files under `artifacts/phase19_brooks_pa_design/`. No `.parquet`, `.npy`, `.npz`, `.memmap`, `.log`, raw, curated, cache, candidate YAML, Layer2 config, Layer3 config, WFO config, live/paper config, top_runs, row-level trades, or row-level equity files exist in this directory. The local untracked Phase16 `runs/` tree (`artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/`) is NOT staged. `CODEX_REVIEW.md` is not modified. `git add .` was not used.

## Explicit non-runs

- No runtime implementation code.
- No edits to `signal_adapter.py`, `contracts.py`, execution code, current-10 strategies/configs/grids/metadata.
- No new strategy source files in this phase.
- No new feature kernels in this phase.
- No new runtime feature YAMLs in this phase.
- No new runtime strategy config YAMLs in this phase.
- No actual `layer1 grid` runs.
- No expanded/full grid runs.
- No `layer1 select-dry-run` runs.
- No candidate YAML created.
- No promotion.
- No Layer2/3.
- No WFO / mini-WFO.
- No live / paper.
- No economic claims.
- No top-row ranking.
- No H2 confirmation.
- No QT runtime dependency.

## Risks / blockers

No design blocker that prevents handoff to Codex.

Known risks for the future implementation phase:

- Brooks feature foundation may exceed the two-new-groups guidance of `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md` §9 if implemented in one PR. The split escape hatch is recorded as `SPLIT_PHASE19_IMPLEMENTATION_INTO_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION` in the decision artifact.
- Side support is system-wide infrastructure; if any future agent retrofits short branches onto current-10 strategies as part of Phase19 implementation, that violates Phase19 design.
- Diagnostic strategies (18-20) must remain `diagnostic_only` in implementation until later evidence justifies promotion.
- `target_r`-only contract must not be relaxed in the strategy layer, even where natural target-price interpretations exist (range mid, magnet, climax extreme). Those belong in management/Layer2.

## Decision

`PHASE19_BROOKS_PA_DESIGN_COMPLETE`

## Cursor provisional recommended next step

`IMPLEMENT_PHASE19A_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`

Alternative if the implementation phase finds the bundle too broad:

`SPLIT_PHASE19_IMPLEMENTATION_INTO_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`

## Note

Final roadmap decision belongs to ChatGPT Pro + user after Codex review. Cursor recommendation is provisional only.
