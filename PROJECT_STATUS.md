# PROJECT_STATUS

## Current phase

**Phase 3 — Fast execution skeleton + parity** (Numba path parity-tested vs reference).

## Decision

`FAST_EXECUTION_PARITY_COMPLETE` — `simulate_trade_path_fast` + Numba kernel mirror Phase 2 reference semantics on synthetic parity matrix; reference + shared `materialize_trade` remain canonical; finite-input / finite-OHLC rejects via `INVALID_MARKET_DATA`.

## Recommended next step

`IMPLEMENT_FEATURE_ENGINE_MVP`

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Tests: `pytest` green (**171** at Phase 3 handoff) + `ruff format --check` + `ruff check` + `compileall`.
- Raw parquet: **local-only** (gitignored). QQQ canonical raw layout expected after Phase 1/1B; SPY may remain legacy until migrated.
- Curated parquet: **local-only** (gitignored).
- Execution PnL truth: **`src/intraday/execution/reference.py`**; fast path: **`src/intraday/execution/fast.py`** (acceleration only; parity in `tests/parity/`).

See `NEXT_HANDOFF.md` and `artifacts/execution_fast_phase3/`.
