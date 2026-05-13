# PHASE_PLAN — intraday_system

Phase-by-phase build roadmap. This file is the source of truth for "what's next".

## Phase 0 — Bootstrap (this phase: Phase 0/1A)

Goal: clean repo skeleton, baseline docs, configs skeleton, core utilities, CLI skeleton, tests, data inventory.

Deliverables:

- Repo skeleton (top-level files, `src/intraday/`, `tests/`, `configs/`, `docs/`).
- pyproject + Makefile + .gitignore + .gitattributes.
- Doc suite (this set).
- Core utilities: `types.py`, `arrays.py`, `hashing.py`, `config.py`, `paths.py`, `errors.py`, `registry.py`, `constants.py`.
- Data inventory under `artifacts/bootstrap/phase0_1a/`.
- CLI: `--help`, `doctor`, `validate structure`, `data inventory`.
- Unit + smoke tests.
- Bootstrap review bundle.

Decision label on completion: **`BOOTSTRAP_PHASE0_1A_COMPLETE`**.

## Phase 1 — Data foundation (`BarMatrix`, curated normalization)

Goal: load IBKR raw parquet → curated parquet → `BarMatrix`.

Tasks:

- Implement `data/normalize.py` (RTH filter, session_id, minute_of_session, timestamp normalization).
- Implement `data/loader.py` (`load_bars` → `BarMatrix`).
- Implement `data/validate.py` (missing/duplicate bars, schema checks).
- Decide: canonicalize raw layout (`equity/bars_1min/...` → `asset=equity/symbol=*/timeframe=1m/...`) OR keep layout-aware loader.
- Add `configs/data/ibkr_qqq_1m.yaml` real fields.
- Tests: load QQQ 2024H1 into `BarMatrix`; shape, session arrays, minute arrays.

Acceptance: `BarMatrix` round-trips through the cache.

## Phase 2 — Reference execution engine

Goal: canonical accounting truth.

Tasks:

- Implement `ExecutionSpec`, `TradeIntent`, `TradeResult`.
- Implement `simulate_trade_path_reference` for next-open entry, stop, target, EOD, max-hold, slippage, commission, R-multiple, reject reasons.
- Unit tests for every scenario.

Acceptance: all execution unit scenarios pass.

## Phase 3 — Fast execution skeleton + parity

Goal: discipline-first fast engine.

Tasks:

- Numba kernel for basic long target/stop path.
- Parity tests for normal target, normal stop, EOD, max-hold, long.

Acceptance: fast engine matches reference for covered scenarios.

## Phase 4 — Feature engine MVP

Goal: PA-required features cached.

Tasks:

- VWAP, ORB, ATR-like, price-action (body/wick), swing high/low, volume windows, regime inputs.
- `FeatureDef`, `FeatureStore`, `feature_config_hash`, columns map.

Acceptance: PA feature matrix built and cache-hit verified for QQQ 2024H1.

## Phase 5 — PA strategy MVP

Goal: port `pa_buy_sell_close_trend`.

Tasks:

- `StrategyDef`, strategy registry, strategy config schema.
- PA signal logic (from QT reference).
- Standard `SignalMatrix` output.
- Base config + focused grid config.

Acceptance: PA strategy emits `SignalMatrix`; no PnL inside strategy.

## Phase 6 — Layer1 PA smoke run

Goal: end-to-end PA candidate factory.

Tasks:

- Grid resolver (fixed/grid merge with overlap check).
- `run_layer1` CLI command.
- Metrics summary.
- Candidate selection gates.
- Candidate YAML writing.

Acceptance: `intraday layer1 run --config configs/layer1/smoke_pa_qqq_2024h1.yaml` writes sweep + candidate YAML.

## Phase 7 — Port GAP and CCI

Goal: first multi-strategy set.

## Phase 8 — Layer2 controlled router

Goal: priority router with daily risk state, cooldowns, conflict resolution.

## Phase 9 — Management modes

Goal: fixed_r → scaleout → trailing → no-followthrough, with execution parity.

## Phase 10 — Layer3 frozen validation

Goal: fold runner + decision doc.

## Phase 11 — Scale and speed

Goal: fast feature kernels, fast strategy kernels, fast Layer2 router, batch WFO.

## Decision labels (Phase 0/1A only)

For this bootstrap:

- `BOOTSTRAP_PHASE0_1A_COMPLETE` (default success)
- `FIX_BOOTSTRAP_STRUCTURE`
- `FIX_DATA_LAYOUT`
- `FIX_DATA_TRACKING_POLICY`
- `RESTORE_TEST_COVERAGE`
- `HOLD_AND_REVIEW`

Recommended next step on success: `IMPLEMENT_DATA_FOUNDATION_BARMATRIX_NORMALIZATION`.
