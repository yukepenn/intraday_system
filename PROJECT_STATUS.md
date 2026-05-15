# PROJECT_STATUS

## Current phase

**Phase 6b — Layer1 PA controlled grid** — small explicit PA grid YAML (`BarMatrix` once, `FeatureMatrix` once) → per-combo resolved strategy config → `SignalMatrix` → `TradeIntent` → reference execution → `TradeResult` → **one** metrics row per combo in `sweep_results.csv`. **No** candidate promotion.

## Decision

`LAYER1_PA_CONTROLLED_GRID_COMPLETE` — controlled Layer1 + grid YAMLs + `resolve_grid_combos` + `run_layer1_controlled_grid` + `write_layer1_grid_artifacts` + `layer1 grid` / `grid-inspect`; `count_rejected_intents` semantics implemented (Option A); **303** `pytest` at handoff; local QQQ grid **skipped** (no curated parquet in workspace; synthetic tests are gate).

## Recommended next step

`REVIEW_LAYER1_PA_GRID_RESULTS` (review sweep summaries once local data exists or in CI with fixtures). **Not** auto-recommending `IMPLEMENT_LAYER1_PA_CANDIDATE_SELECTION` until grid results are reviewed.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Tests: `pytest` green (**303**) + `ruff format --check` + `ruff check` + `compileall`.
- Raw parquet: **local-only** (gitignored). QQQ canonical raw layout expected after Phase 1/1B; SPY may remain legacy until migrated.
- Curated parquet: **local-only** (gitignored).
- Execution PnL truth: **`src/intraday/execution/reference.py`**; fast path: **`src/intraday/execution/fast.py`** (acceleration only; parity in `tests/parity/`).
- Features: **`src/intraday/features/engine.py`** + `configs/features/pa_core_v1.yaml` + `docs/FEATURE_CONTRACT.md`.
- Strategies: **`src/intraday/strategies/pa/buy_sell_close_trend.py`** + `configs/strategies/base/pa_buy_sell_close_trend.yaml` + `docs/STRATEGY_CONTRACT.md`.
- Layer1 smoke: **`run_layer1_smoke`** + `configs/layer1/smoke_pa_qqq_2024h1.yaml`.
- Layer1 grid: **`run_layer1_controlled_grid`** + `configs/layer1/controlled_pa_qqq_2024h1.yaml` + controlled grid under `configs/strategies/grids/`.

See `NEXT_HANDOFF.md` and `artifacts/layer1_pa_controlled_grid_phase6b/`.
