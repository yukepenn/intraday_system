# PROJECT_STATUS

## Current phase

**Phase 6c — Layer1 PA grid results review** — cross-platform **`artifact_root`** validation; local **QQQ 2024H1** **16-combo** controlled grid executed when curated data exists; **sanitized** review CSV/MD under `artifacts/layer1_pa_grid_review_phase6c/`. **No** candidate promotion.

## Decision

`LAYER1_PA_GRID_RESULTS_REVIEW_COMPLETE` — CI path bug fixed; **324** `pytest` green; grid **16/16** rows; interpretation **`GRID_RESULTS_NEED_REVIEW_BEFORE_SELECTION`**.

## Recommended next step

`REVIEW_PA_LOGIC_OR_GRID` — review PA / risk stop semantics and grid economics **before** `DESIGN_LAYER1_PA_CANDIDATE_SELECTION`.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Tests: `pytest` green (**324**) + `ruff format --check` + `ruff check` + `compileall`.
- Raw parquet: **local-only** (gitignored). QQQ canonical raw layout expected after Phase 1/1B; SPY may remain legacy until migrated.
- Curated parquet: **local-only** (gitignored).
- Execution PnL truth: **`src/intraday/execution/reference.py`**; fast path: **`src/intraday/execution/fast.py`** (acceleration only; parity in `tests/parity/`).
- Features: **`src/intraday/features/engine.py`** + `configs/features/pa_core_v1.yaml` + `docs/FEATURE_CONTRACT.md`.
- Strategies: **`src/intraday/strategies/pa/buy_sell_close_trend.py`** + `configs/strategies/base/pa_buy_sell_close_trend.yaml` + `docs/STRATEGY_CONTRACT.md`.
- Layer1 smoke: **`run_layer1_smoke`** + `configs/layer1/smoke_pa_qqq_2024h1.yaml`.
- Layer1 grid: **`run_layer1_controlled_grid`** + `configs/layer1/controlled_pa_qqq_2024h1.yaml` + controlled grid under `configs/strategies/grids/`.

See `NEXT_HANDOFF.md`, `artifacts/layer1_pa_grid_review_phase6c/`, and `artifacts/layer1_pa_controlled_grid_phase6b/` (Phase 6b infra notes).
