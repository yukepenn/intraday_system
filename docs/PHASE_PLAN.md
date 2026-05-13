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

## Phase 1B — Data foundation repair / handoff hardening — **current gate before Phase 2**

Goal: contracts and reviewability for Layer 0 before any execution work.

Highlights:

- Raw timestamp column contract (`ts_ny` / `ts_utc` / legacy names) + inspection rules.
- Exact `session_date` window filtering + safe **write** rules for canonical monthly partitions.
- Deterministic BarMatrix `session_id` across loaded windows.
- Timestamp/session audit artifacts (`data timestamp-audit`, `data session-coverage`).
- Ruff formatting + doc/status synchronization.

Decision label on success: **`DATA_FOUNDATION_PHASE1B_COMPLETE`**.

## Phase 2 — Reference execution engine — **next after Phase 1B**

Goal: canonical accounting truth.

Tasks:

- Implement `ExecutionSpec`, `TradeIntent`, `TradeResult`.
- Implement `simulate_trade_path_reference` for next-open entry, stop, target, EOD, max-hold, slippage, commission, R-multiple, reject reasons.
- Unit tests for every scenario.

Acceptance: all execution unit scenarios pass.

## Phase 3 — Fast execution skeleton + parity

Goal: discipline-first fast engine (Numba), parity-tested against reference.

## Phase 4 — Feature engine MVP

Goal: PA-required features cached.

## Phase 5 — PA strategy MVP

Goal: port `pa_buy_sell_close_trend`.

## Phase 6 — Layer1 PA smoke run

Goal: end-to-end PA candidate factory.

## Phase 7 — Port GAP and CCI

## Phase 8 — Layer2 controlled router

## Phase 9 — Management modes

## Phase 10 — Layer3 frozen validation

## Phase 11 — Scale and speed

## Decision labels (recent)

- `DATA_FOUNDATION_PHASE1B_COMPLETE`
- `DATA_FOUNDATION_BARMATRIX_COMPLETE` (legacy Phase 1 completion tag)
- `BOOTSTRAP_PHASE0_1A_COMPLETE`
- `HOLD_AND_REVIEW`

Recommended next step after Phase 1B: **`IMPLEMENT_REFERENCE_EXECUTION_ENGINE`**.
