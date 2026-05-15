# PROJECT_STATUS

## Current phase

**Phase 6 — Layer1 PA smoke run** (one strategy, one window: `BarMatrix` → `FeatureMatrix` → `SignalMatrix` → `TradeIntent` → execution → `TradeResult` → `BacktestMetrics`; no grid/candidates).

## Decision

`LAYER1_PA_SMOKE_COMPLETE` — smoke YAML + validation; signal adapter; TradeResult-only metrics; `run_layer1_smoke`; `layer1` CLI; `docs/LAYER1_CONTRACT.md` + `docs/BACKTEST_CONTRACT.md`; PA preflight bool/`score_mode`; synthetic + local QQQ smoke; **286** `pytest` at handoff.

## Recommended next step

`IMPLEMENT_LAYER1_PA_CONTROLLED_GRID` (or repair labels if smoke reveals blocking issues).

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Tests: `pytest` green (**286**) + `ruff format --check` + `ruff check` + `compileall`.
- Raw parquet: **local-only** (gitignored). QQQ canonical raw layout expected after Phase 1/1B; SPY may remain legacy until migrated.
- Curated parquet: **local-only** (gitignored).
- Execution PnL truth: **`src/intraday/execution/reference.py`**; fast path: **`src/intraday/execution/fast.py`** (acceleration only; parity in `tests/parity/`).
- Features: **`src/intraday/features/engine.py`** + `configs/features/pa_core_v1.yaml` + `docs/FEATURE_CONTRACT.md`.
- Strategies: **`src/intraday/strategies/pa/buy_sell_close_trend.py`** + `configs/strategies/base/pa_buy_sell_close_trend.yaml` + `docs/STRATEGY_CONTRACT.md`.
- Layer1 smoke: **`src/intraday/layer1/runner.py`** + `configs/layer1/smoke_pa_qqq_2024h1.yaml` + `docs/LAYER1_CONTRACT.md`.

See `NEXT_HANDOFF.md` and `artifacts/layer1_pa_smoke_phase6/`.
