# PROJECT_STATUS

## Current phase

**Phase 5 — PA strategy signal MVP** (`BarMatrix` + `FeatureMatrix` + strategy YAML → `SignalMatrix`; no execution/PnL).

## Decision

`PA_STRATEGY_MVP_COMPLETE` — `pa_buy_sell_close_trend` registered; registry/loader/validation; `docs/STRATEGY_CONTRACT.md`; PA base/metadata/grid configs; synthetic + no-lookahead tests; `strategies` CLI; Layer1/2/3 not implemented.

## Recommended next step

`IMPLEMENT_LAYER1_PA_SMOKE_RUN`

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Tests: `pytest` green (**257** at Phase 5 handoff) + `ruff format --check` + `ruff check` + `compileall`.
- Raw parquet: **local-only** (gitignored). QQQ canonical raw layout expected after Phase 1/1B; SPY may remain legacy until migrated.
- Curated parquet: **local-only** (gitignored).
- Execution PnL truth: **`src/intraday/execution/reference.py`**; fast path: **`src/intraday/execution/fast.py`** (acceleration only; parity in `tests/parity/`).
- Features: **`src/intraday/features/engine.py`** + `configs/features/pa_core_v1.yaml` + `docs/FEATURE_CONTRACT.md`.
- Strategies: **`src/intraday/strategies/pa/buy_sell_close_trend.py`** + `configs/strategies/base/pa_buy_sell_close_trend.yaml` + `docs/STRATEGY_CONTRACT.md`.

See `NEXT_HANDOFF.md` and `artifacts/strategy_pa_phase5/`.
