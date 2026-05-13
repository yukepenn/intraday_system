# PROJECT_STATUS

## Current phase

**Phase 2 — Reference execution engine** (canonical Python trade path).

## Decision

`REFERENCE_EXECUTION_ENGINE_COMPLETE` — `ExecutionSpec` / `TradeIntent` / `TradeResult` hardened; `materialize_trade` + `simulate_trade_path_reference` implemented and covered by synthetic tests; `execution.fast` remains non-active.

## Recommended next step

`IMPLEMENT_FAST_EXECUTION_SKELETON_AND_PARITY`

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Tests: `pytest` green (`127` at Phase 2 handoff) + `ruff format --check` + `ruff check` + `compileall`.
- Raw parquet: **local-only** (gitignored). QQQ canonical raw layout expected after Phase 1/1B; SPY may remain legacy until migrated.
- Curated parquet: **local-only** (gitignored).
- Execution PnL truth: **`src/intraday/execution/reference.py`** only (Phase 2 scope).

See `NEXT_HANDOFF.md` and `artifacts/execution_reference_phase2/`.
