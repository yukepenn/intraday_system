# execution_fast_phase3 — decision

**Decision:** `FAST_EXECUTION_PARITY_COMPLETE`

**Recommended next step:** `IMPLEMENT_FEATURE_ENGINE_MVP`

## Rationale

- Reference path remains canonical; fast path uses the same `materialize_trade` and a Numba scan kernel that parity-matches `simulate_trade_path_reference` on the full synthetic matrix (long/short, costs, same-bar, EOD/max-hold ordering, session roll, truncation, finite-data rejects).
- `compare_trade_results` compares every `TradeResult` field with explicit float/NaN policy.
- `management_plan != None` raises the same `IntradaySystemError` class and message prefix as reference.
- No PnL logic was added outside `src/intraday/execution/`.
- Tests, ruff, compileall, and CLI checks pass; local QQQ curated smoke passed (optional).

## Still not implemented

Feature kernels, strategies, Layer1 runner, candidate generation, Layer2 router, Layer3 validation, scale-out/trailing/no-followthrough inside execution, portfolio sizing, broad sweeps, production/live trading, batch `simulate_trade_paths_fast`.

## Blockers

None identified for Phase 3 scope.
