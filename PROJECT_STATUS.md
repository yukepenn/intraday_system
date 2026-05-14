# PROJECT_STATUS

## Current phase

**Phase 4 — Feature engine MVP** (centralized market-fact `FeatureMatrix` from `BarMatrix` + YAML + optional `FeatureStore`).

## Decision

`FEATURE_ENGINE_MVP_COMPLETE` — reference kernels (VWAP, ORB, volatility, price action, volume, regime); `build_feature_matrix` + deterministic `feature_hash`; `FeatureStore` + `features` CLI; no strategy/Layer1/2/3 code; execution unchanged.

## Recommended next step

`IMPLEMENT_PA_STRATEGY_MVP`

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Tests: `pytest` green (**216** at Phase 4 handoff) + `ruff format --check` + `ruff check` + `compileall`.
- Raw parquet: **local-only** (gitignored). QQQ canonical raw layout expected after Phase 1/1B; SPY may remain legacy until migrated.
- Curated parquet: **local-only** (gitignored).
- Execution PnL truth: **`src/intraday/execution/reference.py`**; fast path: **`src/intraday/execution/fast.py`** (acceleration only; parity in `tests/parity/`).
- Features: **`src/intraday/features/engine.py`** + `configs/features/pa_core_v1.yaml` + `docs/FEATURE_CONTRACT.md`.

See `NEXT_HANDOFF.md` and `artifacts/feature_engine_phase4/`.
