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

Recommended next step: **`REVIEW_PA_LOGIC_OR_GRID`** (then, only if economics merit, `DESIGN_LAYER1_PA_CANDIDATE_SELECTION`).

## Phase 7 — Port GAP and CCI

## Phase 8 — Layer2 controlled router

## Phase 9 — Management modes

## Phase 10 — Layer3 frozen validation

## Phase 11 — Scale and speed

## Decision labels (recent)

- `LAYER1_PA_GRID_RESULTS_REVIEW_COMPLETE`
- `LAYER1_PA_CONTROLLED_GRID_COMPLETE`
- `LAYER1_PA_SMOKE_COMPLETE`
- `FAST_EXECUTION_PARITY_COMPLETE`
- `REFERENCE_EXECUTION_ENGINE_COMPLETE`
- `DATA_FOUNDATION_PHASE1B_COMPLETE`
- `DATA_FOUNDATION_BARMATRIX_COMPLETE` (legacy Phase 1 completion tag)
- `BOOTSTRAP_PHASE0_1A_COMPLETE`
- `HOLD_AND_REVIEW`

Phase 6b next step was **`REVIEW_LAYER1_PA_GRID_RESULTS`**; Phase 6c executed that review (+ CI path fix). Further work: **`REVIEW_PA_LOGIC_OR_GRID`** before any candidate-selection design.
