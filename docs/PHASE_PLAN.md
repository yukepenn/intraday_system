# PHASE_PLAN — intraday_system

Phase-by-phase build roadmap. This file is the source of truth for "what's next".

## Phase 0 — Bootstrap (Phase 0/1A) — **complete**

Goal: clean repo skeleton, baseline docs, configs skeleton, core utilities, CLI skeleton, tests, data inventory.

Decision label: **`BOOTSTRAP_PHASE0_1A_COMPLETE`**.

## Phase 1 — Data foundation (`BarMatrix`, curated normalization) — **complete**

Goal: load IBKR raw parquet → curated parquet → `BarMatrix`.

Highlights:

- `data/normalize.py` (RTH filter, session tagging, timestamp normalization).
- `data/loader.py` (`load_bars_from_curated` → `BarMatrix`).
- `data/validate.py` (missing/duplicate bars, schema checks).
- Raw layout canonicalization (`data canonicalize-raw`).
- Dataset YAML (`configs/data/ibkr_qqq_1m.yaml`) + expanded `data` CLI.

Acceptance: synthetic tests + local QQQ smoke where data exists; curated parquet remains **local-only** (gitignored).

## Phase 1B — Data foundation repair / handoff hardening — **complete**

Goal: contracts and reviewability for Layer 0 before any execution work.

Highlights:

- Raw timestamp column contract + inspection rules; deterministic `session_id` over load windows.
- Exact `session_date` window filtering + safe **write** rules for canonical monthly partitions.
- Timestamp/session audit CLI + artifacts; Ruff + doc/status synchronization.

Decision label on success: **`DATA_FOUNDATION_PHASE1B_COMPLETE`**.

## Phase 2 — Reference execution engine — **complete**

Goal: canonical accounting truth in pure Python.

Highlights:

- `ExecutionSpec` / `TradeIntent` / `TradeResult` with validation and rejected-row convention.
- `materialize_trade` (next-open entry, session guard, slippage, stop/risk, min-risk, target from actual entry, max-hold selection).
- `simulate_trade_path_reference` (intrabar stop/target, same-bar policy, EOD, max-hold, session roll, truncated-window fallback, PnL and R).
- Synthetic unit + smoke tests (**no QQQ parquet dependency**).

Decision label on success: **`REFERENCE_EXECUTION_ENGINE_COMPLETE`**.

## Phase 3 — Fast execution skeleton + parity — **complete**

Goal: Numba acceleration path parity-tested against reference; no second PnL truth.

Highlights:

- `simulate_trade_path_fast` + `_simulate_trade_path_fast_kernel` (`@njit(cache=True)`); shared `materialize_trade` with reference.
- Deterministic finite guards on intent numerics, entry open, scanned OHLC, finalize raw exit; `RejectReason.INVALID_MARKET_DATA`.
- `parity.py` helpers; `tests/parity/test_execution_fast_parity.py` synthetic matrix (no QQQ dependency for acceptance).

Decision label on success: **`FAST_EXECUTION_PARITY_COMPLETE`**.

## Phase 4 — Feature engine MVP — **complete**

Goal: centralized session-aware market-fact features: `BarMatrix` + YAML + optional `FeatureStore` → deterministic `FeatureMatrix` (`float64`, `feature_hash`); reference kernels only.

Highlights:

- `intraday.features.engine.build_feature_matrix` (`mode="reference"`; `mode="fast"` rejected in Phase 4).
- `configs/features/pa_core_v1.yaml` (runtime truth) + `docs/FEATURE_CONTRACT.md`.
- Kernels: VWAP, ORB, volatility/true range, price action, volume, regime (`src/intraday/features/kernels/`).
- `FeatureStore` under `data/cache/features/` (local-only; gitignored).
- CLI: `features list`, `features inspect`, `features build`.
- Tests: contract/registry/hash/engine/store + per-kernel no-lookahead / session-reset patterns; `pytest` **216** at Phase 4 handoff.

Decision label on success: **`FEATURE_ENGINE_MVP_COMPLETE`**.

## Phase 5 — PA strategy MVP — **complete**

Goal: first strategy signal layer — `BarMatrix` + `FeatureMatrix` + strategy YAML → `SignalMatrix` (no execution/PnL).

Highlights:

- `docs/STRATEGY_CONTRACT.md` + `validate_signal_matrix` / `compute_signal_hash`.
- `pa_buy_sell_close_trend` (long-only; `pa_core_v1` features; stop modes `signal_low` / `rolling_low` / `atr_buffer`).
- Registry, loader, PA config validation; PA base/metadata/grid YAML (grid not swept in Phase 5).
- CLI: `strategies list`, `strategies inspect`, `strategies generate-smoke`.
- Tests: synthetic + no-lookahead; `pytest` **257** at Phase 5 handoff.

Decision label on success: **`PA_STRATEGY_MVP_COMPLETE`**.

## Phase 6 — Layer1 PA smoke run — **complete**

Goal: first **end-to-end plumbing** check — `BarMatrix` → `FeatureMatrix` → `SignalMatrix` → `TradeIntent` → execution → `TradeResult` → metrics → small artifacts — **not** a candidate factory sweep.

Highlights:

- `configs/layer1/smoke_pa_qqq_2024h1.yaml` + `load_layer1_smoke_config` / `validate_layer1_smoke_config`
- `intraday.backtest.signal_adapter`, `intraday.backtest.metrics`
- `run_layer1_smoke` + `layer1` CLI (`run` / `inspect`)
- `merge_execution_spec_with_strategy`; docs `LAYER1_CONTRACT` + `BACKTEST_CONTRACT`
- Preflight: `parse_bool_like`, `score_mode` validation
- `pytest` **286** at Phase 6 handoff

Decision label on success: **`LAYER1_PA_SMOKE_COMPLETE`**.

## Phase 6b — Layer1 PA controlled grid — **complete**

Goal: **small**, explicit PA parameter grids behind Layer1 gates (not broad research).

Highlights:

- `configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml` (16 explicit combos) + `configs/layer1/controlled_pa_qqq_2024h1.yaml`
- `load_layer1_controlled_grid_config` / `validate_layer1_controlled_grid_config`; `ResolvedGridCombo`, `resolve_grid_combos`, `run_layer1_controlled_grid`, `Layer1GridResult`
- `layer1 grid` / `layer1 grid-inspect`; `summarize_trade_results(..., count_rejected_in_metrics=...)` + skip diagnostics `execution_rejected_included` / `execution_rejected_excluded`
- Tests: `test_layer1_grid*`, `test_layer1_grid_cli`; `pytest` **303** at handoff

Decision label on success: **`LAYER1_PA_CONTROLLED_GRID_COMPLETE`** (local QQQ grid skipped when curated data absent; synthetic tests are acceptance).

Recommended next step: **`REVIEW_LAYER1_PA_GRID_RESULTS`**.

## Phase 6c — Layer1 PA grid results review — **complete**

Goal: fix **cross-platform** `artifact_root` validation for Layer1 loaders; run and **review** the shipped **16-combo** QQQ 2024H1 controlled grid when curated data exists; commit **sanitized** CSV/MD only (no `local_run`/parquet/caches).

Highlights:

- `intraday.core.paths.is_absolute_path_like` + Layer1 config wiring; tests `test_core_paths`, extended `test_layer1_config` / `test_layer1_grid_config`
- Local curated QQQ 2024H1 validation + `layer1 grid` full sweep; `artifacts/layer1_pa_grid_review_phase6c/` review bundle (`CHATGPT_REVIEW_BUNDLE.md`, `sweep_results_review.csv`, etc.)
- `pytest` **324** at handoff

Decision label on success: **`LAYER1_PA_GRID_RESULTS_REVIEW_COMPLETE`**.

## Phase 6d — PA logic / controlled-grid diagnostics — **complete**

Goal: quantify **axes + interactions**, exit/skip pathologies, MVP logic sanity, and promotion serialization hygiene using **existing** Phase **6c** sweep artifacts (**no rerun unless missing**).

Highlights:

- `artifacts/pa_logic_grid_review_phase6d/` Markdown + tidy CSV summaries (artifact validation checklist, marginal + pairwise parameter tables, readiness label, serialization audit memo, GitHub-renderable bundle).
- Reaffirms dominant sensitivity to **`risk.stop_mode`** partition on sampled window; reinforces single-window caveat.
- Policy: **`READY_TO_DESIGN_SELECTION`** pertains to authoring selection doctrine — **distinct** from asserting tradable expectancy or activating promotion code paths.

Decision label on success: **`PA_GRID_REVIEW_COMPLETE_READY_FOR_SELECTION_DESIGN`**.

Recommended next step: **`DESIGN_LAYER1_PA_CANDIDATE_SELECTION`**.

Promotion engineering remains gated by sweep schema uplift (`FIX_GRID_REPORTING_SCHEMA` posture) until **`resolved_config_json`** (or equivalent deterministic helper) closes drift risk documented in artifacts.

## Phase 7 — Layer1 PA candidate selection design — **complete**

Goal: selection doctrine, future candidate YAML schema, reconstruction helper, provisional gates, dry-run tables — **no** runtime candidate promotion.

Highlights:

- `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`; `reconstruct_resolved_config_for_combo`; `evaluate_selection_gates` (`PA_L1_SELECTION_DESIGN_V1`)
- Dry-run on Phase **6c** sweep: **7** hold / **9** reject; `promotion_allowed_now=false` everywhere
- `artifacts/layer1_pa_candidate_selection_design_phase7/` bundle; `configs/candidates/l1_pa_controlled_v1/README.md` only
- `pytest` **340** at handoff

Decision label on success: **`LAYER1_PA_CANDIDATE_SELECTION_DESIGN_COMPLETE`**.

Recommended next step: **`IMPLEMENT_LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN`**.

## Phase 7b — Layer1 PA candidate-selection dry-run (repeatable) — **complete**

Goal: repeatable CLI + library path for selection dry-run on Phase **6c** sweep artifacts — **no** runtime candidate YAML promotion.

Highlights:

- `parse_bool_like` for `config_reconstruction_safe` (fixes CSV `"False"` truthiness bug flagged by Codex).
- `run_layer1_candidate_selection_dry_run` + `write_layer1_candidate_selection_dry_run_artifacts`.
- CLI `layer1 select-dry-run`; bundle `artifacts/layer1_pa_candidate_selection_dry_run_phase7b/`.
- 16-row QQQ 2024H1 dry-run: **7** hold / **9** reject; **16/16** reconstruction pass; `promotion_allowed_now=false` everywhere.
- `pytest` **371** at handoff.

Decision label on success: **`LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN_COMPLETE`**.

Recommended next step: **`RUN_LAYER1_PA_CONFIRMATION_WINDOW`**.

## Phase 8 — Layer1 PA confirmation window (anti-overfit) — **complete (8b)**

Goal: same 16-combo PA controlled grid on a non-overlapping QQQ window (2024H2); `select-dry-run` on confirmation sweep; design vs confirmation comparison — **no** retuning, **no** promotion.

Highlights:

- Phase 8 partial: CI help, finite parsing, output-root guardrail, confirmation config prepared.
- Phase 8b: curated QQQ 2024H2 locally; grid **16/16**; dry-run **16** reject; comparison **`CONFIRMATION_WEAKENS_SELECTION_DESIGN`**.
- Bundle `artifacts/layer1_pa_confirmation_data_repair_phase8b/`.

Decision label: **`LAYER1_PA_CONFIRMATION_WINDOW_COMPLETE`**.

Recommended next step: **`REVIEW_PA_FEATURES_OR_LOGIC`** (not real promotion).

## Phase 9 — PA feature/logic review after confirmation — **complete**

Goal: diagnose why QQQ 2024H2 confirmation rejected all 16 controlled-grid rows and choose the next **system-building** step — **no** strategy/feature changes, **no** grid rerun, **no** promotion.

Highlights:

- Reconfirmed **`CONFIRMATION_WEAKENS_SELECTION_DESIGN`**; design rank-1 `combo_0015` HOLD → H2 REJECT.
- **stop_mode ranking reversed** (rolling_low H1 best → H2 worst).
- Universal `excessive_drawdown` on confirmation (max_dd > 10R gate).
- Bundle `artifacts/pa_features_logic_review_after_confirmation_phase9/`.
- `pytest` **391** at handoff.

Decision label: **`PA_FEATURE_LOGIC_REVIEW_COMPLETE`**.

Recommended next step: **`REFINE_PA_GRID_AND_RERUN`** (≤12-combo risk diagnostic; design window first; fresh holdout — not 2024H2 retuning).

## Phase 10 — PA risk-path diagnostic grid — **complete**

Goal: run ≤12-combo explicit risk diagnostic (`stop_mode`, `target_r`, `max_hold`) on QQQ 2024H1 design + 2024H2 stress retest — **no** strategy/feature changes, **no** promotion.

Highlights:

- Grid `pa_buy_sell_close_trend_risk_diagnostic_small.yaml` (12 combos); Layer1 configs `pa_risk_diag_qqq_2024h*.yaml`.
- H1: all combos negative total_r; best −4.79R. H2: best +4.68R but all REJECT on gates.
- **0/12** positive total_r in both windows; `signal_low` >> `atr_buffer`.
- Bundle `artifacts/pa_risk_grid_diagnostic_phase10/`.

Decision label: **`PA_RISK_DIAGNOSTIC_COMPLETE_HOLD_PA_PATH`**.

Recommended next step: **`REVIEW_PA_FEATURES_OR_LOGIC`** (not promotion; not fresh holdout until path revives).

## Phase 11 — Strategy-family onboarding + second MVP selection — **complete**

Goal: define reusable **strategy-family onboarding contract**, audit features, map QT reference, select second MVP family — **no** runtime strategy/feature implementation, **no** Layer1 grids, **no** PA refinement.

Highlights:

- `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`
- `artifacts/strategy_family_onboarding_phase11/` — feasibility matrix, feature audit, QT guardrails, PA hold summary
- Second family selected: **ORB continuation** (`orb_continuation`) for **future** implementation only
- PA path **held** after Phase 10 (canary complete; not promotion-ready)

Decision label: **`STRATEGY_FAMILY_ONBOARDING_COMPLETE_SECOND_FAMILY_SELECTED`**.

Recommended next step: **`DESIGN_GENERIC_FEATURE_FOUNDATION_FOR_SECOND_FAMILY`** (small ORB feature gaps) → **`IMPLEMENT_SECOND_STRATEGY_FAMILY_MVP`**.

## Phase 12 — Generic feature foundation for second family — **complete**

Goal: add minimal generic market facts for ORB continuation (`vwap_slope_5`, `orb_width_pct_15`) and `orb_core_v1` config — **no** ORB strategy, **no** Layer1, **no** promotion.

Highlights:

- Kernels: `vwap_slope_5`, `orb_width_pct` → `orb_width_pct_15`
- Config: `configs/features/orb_core_v1.yaml` (does not mutate `pa_core_v1`)
- Unit tests: no-lookahead, session reset, hash stability
- Bundle `artifacts/generic_feature_foundation_second_family_phase12/`

Decision label: **`GENERIC_FEATURE_FOUNDATION_SECOND_FAMILY_COMPLETE`**.

Recommended next step: **`IMPLEMENT_SECOND_STRATEGY_FAMILY_MVP`** (ORB continuation strategy only; after Codex review).

## Phase 13 — Pre-Layer2 strategy library runtime sprint — **complete**

Goal: batch-onboard long-only strategy runtimes and generic feature configs for a diversified pre-Layer2 library — **no** Layer1 research, promotion, Layer2/3, WFO, live/paper.

Highlights:

- Feature groups: `levels`, `indicators`; configs `opening_core_v1`, `gap_level_core_v1`, `vwap_level_core_v1`, `indicator_core_v1`, `strategy_library_core_v1`
- Strategies: ORB×3, gap, VWAP×2, prior-day trap, CCI, stochastic (+ existing PA)
- Base/metadata/controlled-small grid YAML per strategy (≤24 combos)
- Bundle `artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/`

Decision label: **`PRE_LAYER2_STRATEGY_LIBRARY_RUNTIME_COMPLETE`**.

Recommended next step: **`RUN_LAYER1_STRATEGY_LIBRARY_SMALL_GRID`** (plumbing smoke; not promotion).

## Phase 14 — Preflight and Layer1 strategy-library small-grid diagnostic — **complete**

Goal: repair Phase 13 artifact/status hygiene and prove the pre-Layer2 strategy library can run through Layer1 controlled-grid plumbing on a tiny diagnostic surface — **not** candidate promotion, Layer2, WFO, live/paper, or alpha proof.

Highlights:

- Repaired malformed Phase 13 CSV audit artifacts with parseable schemas.
- Added one Layer1 controlled-grid diagnostic config per active strategy for QQQ 2024H1.
- Added exact QQQ 2024H2 repeat configs because local curated data exists; H2 is a sanity repeat, not confirmation or promotion.
- Grid-inspect passed for all 20 configs; all 10 active strategies ran on H1 and H2.
- Bundle `artifacts/layer1_strategy_library_small_grid_phase14/`.

Decision label: **`LAYER1_STRATEGY_LIBRARY_SMALL_GRID_DIAGNOSTIC_COMPLETE`**.

Recommended next step: **`REVIEW_LAYER1_STRATEGY_LIBRARY_SMALL_GRID_RESULTS`**.

Longer roadmap: Phase 15 may design a focused diagnostic grid only after review. Candidate promotion remains gated by evidence and schema/reconstruction safety. Layer2 remains locked until a candidate pool exists.

## Phase 15 ? Layer1 strategy-library result review + focused-grid design ? **complete**

Goal: review existing Phase14 diagnostic artifacts and design a future focused diagnostic grid ? **no new grid run, no select-dry-run, no candidate YAML, no promotion, no Layer2/3, no WFO, no live/paper**.

Decision label: **`LAYER1_STRATEGY_LIBRARY_RESULT_REVIEW_COMPLETE`**.

Superseded next step: `RUN_LAYER1_STRATEGY_LIBRARY_FOCUSED_DIAGNOSTIC_GRID` was replaced by the Phase16 all-current-10 rational expanded-grid decision. Tiny Phase14 grids are plumbing/triage diagnostics only and do not permanently reject other families.

## Phase 16 ? Current-10 rational expanded grid design + run ? **complete after Phase 16B repair**

Goal: pre-register rational expanded grids for the current 10 active strategies, document axes/combo counts, inspect all configs, and run diagnostic Layer1 grids where feasible.

Status:

- Expanded grid YAMLs created for all 10 current strategies.
- 20 QQQ H1/H2 Layer1 diagnostic configs created.
- Data validation passed; H2 warning `missing_minute_slots_total=540` remains diagnostic-only.
- Grid-inspect passed for all 20 configs.
- H1 PA and H1 ORB continuation grids ran; the original full run stopped at ORB retest runtime blocker.

Decision label: **`LAYER1_10_STRATEGY_RATIONAL_EXPANDED_GRID_DESIGN_COMPLETE_RUN_BLOCKED`**.

Recommended next step: **`RESOLVE_PHASE16_GRID_RUN_BLOCKER`**.

## Phase 16B ? Expanded-grid runtime/reporting repair + controlled rerun ? **complete**

Goal: repair Phase16 runtime/reporting blockers without strategy retuning, feature semantic changes, execution truth changes, prefix slicing, post-result grid shrinking, candidate promotion, or Layer2.

Status:

- Repaired ORB retest prior-breakout state and failed ORB prior-breach state with O(n) session-local cumulative passes.
- Added synthetic old-vs-new equivalence tests for the repaired prior-state helpers.
- Added aggregate-only risk/cost diagnostics derived from execution-produced fields.
- Added drawdown aggregation guard for positive drawdown magnitude ordering.
- Validated QQQ 2024H1/H2 curated data; H2 warning `missing_minute_slots_total=540` remains diagnostic-only.
- Grid-inspect passed for all 20 Phase16 configs.
- Full Layer1 grid rerun completed for all 20 configs with full combo coverage.

Decision label: **`PHASE16_EXPANDED_GRID_RUN_RESUMED_COMPLETE`**.

Recommended next step: **`REVIEW_10_STRATEGY_EXPANDED_GRID_RESULTS_BY_REGION`** after Codex and ChatGPT Pro review.

## Phase 17 ? Expanded-result region/neighborhood review ? **complete**

Goal: review completed Phase16/16B expanded-grid results by parameter region/neighborhood, not top-row ranking.

Status:

- Reviewed all 10 active strategy surfaces.
- Generated region, top-neighborhood, isolated-top-row, axis, interaction, H1/H2, drawdown, sample, risk/cost, and Phase18 backlog artifacts.
- Preserved H2 warning `missing_minute_slots_total=540`; H2 remains diagnostic-only.
- No new grids, no select-dry-run, no candidate YAML, no promotion, no Layer2/3, no WFO, no live/paper.

Decision label: **`PHASE17_EXPANDED_GRID_REGION_REVIEW_COMPLETE`**.

Recommended next step: **`DESIGN_PHASE18_EXISTING_10_STRATEGY_IMPROVEMENTS`** after Codex and ChatGPT Pro review.

## Phase 18 ? Existing-10 strategy improvement design ? **complete**

Goal: convert Phase17 strategy-surface evidence and backlog into bounded improvement design for the current 10 active strategies.

Status:

- Generated per-strategy improvement design, feature-gap, and short-side feasibility matrices for exactly the current 10 strategies.
- Generated risk-path, signal-frequency, and regime/context improvement plans.
- Generated implementation-priority, non-goal, promotion-blocked, local reproducibility, H2 carryforward, schema, and decision artifacts.
- Preserved H2 warning `missing_minute_slots_total=540`; H2 remains diagnostic-only.
- No runtime strategy changes, feature semantic changes, execution changes, new grids, select-dry-run, candidate YAML, promotion, Layer2/3, WFO, live/paper, H2 confirmation, top-row retuning, or strategies 11-50.

Decision label: **`PHASE18_EXISTING_10_STRATEGY_IMPROVEMENT_DESIGN_COMPLETE`**.

Recommended next step: **`IMPLEMENT_PHASE18_APPROVED_EXISTING_10_STRATEGY_IMPROVEMENTS`** after Codex and ChatGPT Pro review.

## Phase 18B ? Existing-10 v2 refinement implementation ? **complete**

Goal: implement explicitly approved optional/config-driven v2 refinements for exactly the current 10 active strategies, plus v2 feature configs, validation hardening, v2 base/grid skeletons, tests, and grid-inspect readiness artifacts.

Status:

- Created `opening_core_v2`, `vwap_level_core_v2`, `gap_level_core_v2`, `indicator_core_v2`, and `pa_core_v2` from existing generic/no-label feature kernels.
- Added optional v2 refinement branches for all 10 current strategies; v1 configs remain valid and execution/accounting truth is unchanged.
- Added Phase18B v2 base configs, 8-combo v2 rational grid skeletons, and grid-inspect-only Layer1 configs for all 10 strategies.
- Added validation hardening and Phase18B feature/config/generation/no-runtime-leakage/artifact-schema tests.
- Grid-inspect passed for all 10 Phase18B configs; no full Layer1 grid runs or expanded sweeps were run.
- Preserved H2 warning `missing_minute_slots_total=540`; H2 remains diagnostic-only.
- No candidate YAML, promotion, select-dry-run, Layer2/3, WFO, live/paper, broad short-side implementation, top-row retuning, or strategies 11-50.

Decision label: **`PHASE18B_EXISTING_10_REFINEMENT_IMPLEMENTATION_COMPLETE`**.

Recommended next step: **`PHASE18C_REPAIR_EXISTING_10_V2_VALIDATION_AND_BRANCH_TESTS`** after Codex `NEEDS_FIX` review.

## Phase 18C ? Existing-10 v2 validation and branch-test repair ? **complete**

Goal: repair Phase18B acceptance gaps by hardening runtime-used v2 strategy config validation and adding targeted invalid-value, branch behavior, missing-feature, and no-lookahead/session tests.

Status:

- Inventoried runtime-used v2 fields across all 10 current strategies.
- Repaired finite/type/range/int/enum/bool validation gaps without changing execution/accounting truth.
- Added Phase18C invalid-value, branch behavior, missing-feature, artifact-schema, and no-runtime-leakage tests.
- Generated curated Phase18C repair artifacts.
- No new grids, no Layer1 grid run, no select-dry-run, no candidate YAML, no promotion, no Layer2/3, no WFO/live/paper, no short side, and no strategies 11-50.

Decision label: **`PHASE18C_V2_VALIDATION_AND_BRANCH_TEST_REPAIR_COMPLETE`**.

Recommended next step: **`PHASE18D_CURRENT10_REFINED_SMOKE_AND_GRID_INSPECT_REVIEW`** after Codex and ChatGPT Pro review.

## Phase 18D ? Current-10 refined readiness and onboarding checklist ? **complete**

Goal: validate the refined current-10 v2 package as inspectable/integration-ready and operationalize existing contracts into a Phase19-22 onboarding checklist.

Status:

- Re-ran inspect checks for all five v2 feature configs.
- Re-ran strategy inspect for all 10 current v2 strategy configs.
- Rechecked all 10 v2 rational grid skeletons and all 10 Phase18B Layer1 grid-inspect-only configs.
- Standardized missing feature-column failures to `ConfigError`.
- Generated `artifacts/current10_refined_readiness_phase18d/`, including the current-10 readiness matrix, contract alignment, `strategy_onboarding_checklist_v2.md`, `phase19_strategy_addition_template.md`, and non-promotion guardrails.
- No actual Layer1 grids, select-dry-run, candidate YAML, promotion, Layer2/3, WFO, live/paper, economic claims, H2 confirmation, top-row retuning, execution truth changes, or strategies 11-50.

Decision label: **`PHASE18D_CURRENT10_REFINED_READINESS_COMPLETE`**.

Recommended next step: **`DESIGN_PHASE19_STRATEGIES_11_TO_20`** after Codex and ChatGPT Pro review.

## Phase 19 design ? Design Brooks PA strategies 11-20 with side support ? **complete**

Goal: design (not implement) the system-wide side-support foundation, Brooks PA feature foundation, strategies 11-20, and the future implementation/file/test/validation plan.

Status:

- Generated `artifacts/phase19_brooks_pa_design/` with the review bundle, source map, key tables, validation results, Phase19A side-support design and test plan, Phase19B Brooks PA feature foundation design and audit matrix, Phase19C strategy design matrix / strategy specs (10 strategies; 7 core + 3 diagnostic) / duplicate-avoidance matrix (rejecting current-10 duplicates), Phase19D file plan / test plan / validation plan, non-goals, non-promotion guardrails, decision artifact, and artifact-schema validation.
- Reserved Phase19 setup-code namespace (long 7101-7110; short 7201-7210), disjoint from current-10.
- Added Phase19 design-only artifact-schema and no-runtime-leakage tests under `tests/unit/`.
- No runtime implementation; no strategy source files; no feature kernels; no edits to signal_adapter, contracts, execution, current-10; no new Phase19 runtime YAMLs; no actual Layer1 grids; no select-dry-run; no candidate YAML; no promotion; no Layer2/3; no WFO/live/paper; no economic claims; no H2 confirmation; no top-row retuning; no QT runtime dependency; no strategies 21-50.

Decision label: **`PHASE19_BROOKS_PA_DESIGN_COMPLETE`**.

Recommended next step: **`IMPLEMENT_PHASE19A_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`** (alternative **`SPLIT_PHASE19_IMPLEMENTATION_INTO_SIDE_SUPPORT_AND_BROOKS_FEATURE_FOUNDATION`**) after Codex and ChatGPT Pro review.

## Phase 19A ? Side support + Brooks feature foundation slice ? **complete**

Goal: implement the shared side-support foundation and Brooks PA Slice F1 feature facts before any strategy 11-20 code ships.

Status:

- Extended SignalMatrix validation to accept long and short entries with side-specific stop geometry when reference closes are supplied.
- Added shared side-mode parsing helpers for `long_only`, `short_only`, and `both`.
- Made the signal adapter side-aware with conservative default long-only behavior; shorts require explicit adapter allowance and execution `allow_short` remains the final authority.
- Added Brooks Slice F1 feature configs `pa_brooks_core_v1` and `pa_brooks_range_v1`.
- Resolved swing-core packaging: lightweight swing facts live inside `pa_brooks_core_v1`; no separate swing YAML in Phase19A.
- Added no-lookahead/session-reset tests and current-10 long-only regression tests.
- No strategies 11-20 source files, Phase19 strategy runtime YAMLs, Layer1 grids, select-dry-run, candidate YAML, promotion, Layer2/3, WFO, live/paper, current-10 short retrofits, execution accounting changes, or economic claims.

Decision label: **`PHASE19A_SIDE_SUPPORT_AND_FEATURE_SLICE_COMPLETE`**.

Follow-up repair completed before Phase19B strategy implementation.

## Phase 19A Repair - Layer1 side runtime wiring - **complete**

Goal: complete the bridge from strategy config `signal.side_mode` to Layer1 validation and adapter intent construction, without changing execution PnL/R semantics or implementing strategies 11-20.

Status:

- `run_layer1_smoke(...)` passes `reference_close=bars.close` into `validate_signal_matrix(...)`.
- `run_layer1_controlled_grid(...)` passes `reference_close=bars.close` into `validate_signal_matrix(...)`.
- Both runner paths derive `allowed_sides` from strategy config `signal.side_mode` via shared contract helpers.
- Both runner paths pass `allowed_sides` into `build_trade_intents_from_signals(...)`.
- Execution remains final authority for `allow_short` / `SHORT_NOT_ALLOWED`.
- Current-10 default long-only behavior is preserved.
- No strategies 11-20, feature work, actual grids, select-dry-run, candidate YAML, promotion, Layer2/3, WFO/live/paper, execution truth changes, or economic claims.

Decision label: **`PHASE19A_LAYER1_SIDE_RUNTIME_WIRING_REPAIR_COMPLETE`**.

Recommended next step: **`IMPLEMENT_PHASE19B_CORE_BROOKS_PA_STRATEGIES_11_TO_17`** after Codex and ChatGPT Pro review.

## Phase 19B - Add core Brooks PA strategies 11-17 - **complete**

Goal: enforce the side-mode validation gate before strategy onboarding, then implement only core Brooks PA strategies 11-17 against Phase19A side-support and Slice F1 feature facts.

Status:

- Current-10 validators reject unsupported non-long `signal.side_mode` values while preserving missing/`long_only` behavior.
- Implemented and registered exactly strategies 11-17:
  - `pa_second_entry_pullback`
  - `pa_trading_range_bls_hs`
  - `pa_failed_breakout_trap`
  - `pa_opening_reversal_sr`
  - `pa_breakout_pullback_continuation`
  - `pa_tight_channel_pullback`
  - `pa_broad_channel_zone`
- Added Phase19 base configs, metadata, controlled-small grid skeletons, Layer1 grid-inspect-only configs, focused unit tests, and curated artifacts.
- Strategy inspect and Layer1 grid-inspect passed for all seven strategies. No actual Layer1 economic grids were run.
- No strategies 18-20 or 21-50, select-dry-run, candidate YAML, promotion, Layer2/3, WFO/live/paper, current-10 short retrofit, execution truth change, or economic claims.

Decision label: **`PHASE19B_CORE_BROOKS_STRATEGIES_11_TO_17_ONBOARDED`**.

Recommended next step: **`REVIEW_PHASE19B_CORE_BROOKS_PA_STRATEGIES`** after Codex and ChatGPT Pro review. Phase19C diagnostic strategies 18-20 may be designed only after review; Phase20 should wait.

## Phase 19 Immediate Fix - setup codes, side consistency, current-10 short retrofit - **complete**

Goal: resolve the Codex-flagged Phase19B blockers (setup-code namespace drift 1101-1702, runtime boolean coercion mismatch) and the lower-priority metadata/inspect weakness; make all setup-code / side-mode / feature-strategy policy generic and consistent; retrofit current-10 with short branches where structurally supported while keeping long-only the default.

- Authoritative runtime setup-code registry: `src/intraday/strategies/setup_codes.py` plus governance doc `docs/SETUP_CODE_REGISTRY.md`.
- Phase19B strategies 11-17 now derive setup codes from the registry; codes corrected to 7101-7107 (long) / 7201-7207 (short); current-10 short codes assigned at 8001 / 9001-9003 / 10001 / 11001-11002 / 12001 / 13001-13002; future ranges 7301-7810 reserved.
- `brooks_bool` helper added to `src/intraday/strategies/pa/brooks_common.py`; every `bool(sig.get(...))` / `bool(config.get(...))` pattern in Phase19B strategies replaced; static source scan in tests prevents reintroduction.
- `StrategyDef` extended with `setup_code_long`, `setup_code_short`, `allowed_side_modes`, `default_side_mode`, `required_feature_columns`; CLI `strategies inspect` now reports them with a metadata cross-check.
- Generic helpers added in `src/intraday/strategies/common.py` (`compute_short_stop`, `build_side_aware_signal_matrix`, `crossed_below`) and `config_validation.py` (`validate_side_aware_strategy_base`, `CURRENT10_SIDE_MODES`).
- All 10 current-10 strategies retrofitted with `signal.side_mode`-gated short branches; canonical base configs migrated to `signal.side_mode: long_only`; new inspect-only side-aware grid skeletons and Layer1 configs added.
- Tests: setup-code registry, boolean coercion + static scan, metadata alignment, inspect metadata, current-10 side-aware configs, short-signal generation, missing-feature, no-lookahead/session, long-only backcompat.
- No actual Layer1 grids, expanded/full grids, select-dry-run, candidate YAML, promotion, Layer2/3, WFO/live/paper, execution truth change, or economic claims.

Decision label: **`PHASE19_IMMEDIATE_FIX_COMPLETE`**.

Recommended next step: **`REVIEW_PHASE19_IMMEDIATE_FIX`** with Codex and ChatGPT Pro. Final roadmap decision (whether to do Phase19C diagnostic 18-20 design, a targeted Phase19D polish phase, or move on to Layer2 design) belongs to ChatGPT Pro + the user after that review.

## Phase 19 Immediate Fix Polish - runtime tests and doc/config consistency - **complete**

Phase label:
`PHASE19_IMMEDIATE_FIX_POLISH_RUNTIME_TESTS_AND_DOC_CONFIG_CONSISTENCY`

Goal: resolve Codex PASS_WITH_WARNINGS items without moving into economic
research or promotion.

Scope:

- Broaden direct synthetic current-10 short runtime tests to all 10 current
  strategies.
- Repair `strategies generate-smoke` invalid-stop diagnostics so long and short
  stops are checked side-aware.
- Correct the long-only compatibility policy: behavior equivalence matters;
  raw `signal_hash` identity is not required after config-key migration.
- Refresh normative docs and config READMEs around `signal.side_mode`,
  setup-code registry authority, and YAML-runtime-truth policy.
- Add doc/config consistency tests and curated review artifacts.
- No actual Layer1 economic grids, expanded/full grids, candidate YAML,
  select-dry-run, promotion, Layer2/3, WFO, live/paper, strategies 18-20,
  strategies 21-50, execution PnL/R changes, or economic claims.

Recommended next step after completion: **`REVIEW_PHASE19_IMMEDIATE_FIX_POLISH`**.

## Phase 20 ? Add strategies 21-30 ? **future**

Continue strategy-library expansion after review.

## Phase 21 ? Add strategies 31-40 ? **future**

Continue strategy-library expansion after review.

## Phase 22 ? Add strategies 41-50 ? **future**

Complete the planned 50-strategy universe.

## Phase 23 ? Full 50-strategy integration audit ? **future**

Audit contracts, features, configs, strategy registry, Layer1 wiring, and artifact hygiene across all 50 strategies.

## Phase 24 ? Expanded grids for all 50 strategies ? **future**

Run bounded rational expanded grids for all 50 strategies. Diagnostic only.

## Phase 25 ? All-50 region/neighborhood review ? **future**

Review expanded all-50 results by region/neighborhood. No promotion.

## Phase 26 ? Candidate selection dry-run ? **future / conditional**

Run candidate selection dry-run only if region evidence supports it. No YAML promotion yet.

## Phase 27 ? Candidate YAML promotion ? **future / conditional**

Promote candidate YAML only after fresh-window confirmation and schema gates.

## Phase 28+ ? Layer2 controlled router ? **future / locked**

Begin Layer2 only after a real candidate YAML pool exists.

## Phase 8-R — Port GAP and CCI (original roadmap; superseded by Phase 11 ORB-first plan)

## Phase 11 — Layer2 controlled router (original roadmap Phase 9)

## Phase 12 — Management modes

## Phase 13 — Layer3 frozen validation

## Phase 14 — Scale and speed

## Decision labels (recent)

- `PA_RISK_DIAGNOSTIC_COMPLETE_HOLD_PA_PATH`
- `REVIEW_PA_FEATURES_OR_LOGIC`
- `PA_FEATURE_LOGIC_REVIEW_COMPLETE`
- `REFINE_PA_GRID_AND_RERUN`
- `LAYER1_PA_CONFIRMATION_WINDOW_COMPLETE`
- `REVIEW_PA_FEATURES_OR_LOGIC`
- `FIX_LOCAL_CURATED_DATA`
- `LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN_COMPLETE`
- `LAYER1_PA_CANDIDATE_SELECTION_DESIGN_COMPLETE`
- `PA_GRID_REVIEW_COMPLETE_READY_FOR_SELECTION_DESIGN`
- `LAYER1_PA_GRID_RESULTS_REVIEW_COMPLETE`
- `LAYER1_PA_CONTROLLED_GRID_COMPLETE`
- `LAYER1_PA_SMOKE_COMPLETE`
- `FAST_EXECUTION_PARITY_COMPLETE`
- `REFERENCE_EXECUTION_ENGINE_COMPLETE`
- `DATA_FOUNDATION_PHASE1B_COMPLETE`
- `DATA_FOUNDATION_BARMATRIX_COMPLETE` (legacy Phase 1 completion tag)
- `BOOTSTRAP_PHASE0_1A_COMPLETE`
- `HOLD_AND_REVIEW`

Superseded legacy note: Phase **12** completed generic ORB feature foundation (`orb_core_v1`, `vwap_slope_5`, `orb_width_pct_15`). The old next step **`IMPLEMENT_SECOND_STRATEGY_FAMILY_MVP`** and "Port GAP/CCI deferred until after ORB pipeline proof" note were superseded by Phase **13** (`PRE_LAYER2_STRATEGY_LIBRARY_RUNTIME_COMPLETE`), Phase **14** (`PHASE14_PREFLIGHT_AND_LAYER1_STRATEGY_LIBRARY_SMALL_GRID_DIAGNOSTIC`), Phase **15** (`PHASE15_LAYER1_STRATEGY_LIBRARY_RESULT_REVIEW_AND_FOCUSED_GRID_DESIGN`), Phase **16/16B** expanded-grid completion, Phase **17** region/neighborhood review, Phase **18** existing-10 improvement design, and Phase **19** side-aware Brooks/current-10 setup-code work. Current next step: **`REVIEW_PHASE19_IMMEDIATE_FIX_POLISH`**; candidate selection/promotion and Layer2 remain locked.
