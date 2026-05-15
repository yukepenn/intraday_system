# Backtest orchestration contract (Phase 6)

## Role

Backtest orchestration (Layer1 smoke runner in Phase 6) **may**:

- Load bars from curated data.
- Build `FeatureMatrix` from feature YAML.
- Run a registered strategy to produce `SignalMatrix`.
- Adapt signals to `TradeIntent` via the signal adapter (no PnL).
- Call **reference** or **fast** execution (`simulate_trade_path_reference` / `simulate_trade_path_fast`).
- Collect `TradeResult` rows and compute **summary metrics that only aggregate** execution outputs.

## Non-goals

Orchestration **must not**:

- Compute fills, stop/target triggers, PnL, or R-multiples independently of execution.
- Override execution semantics or re-derive economics.
- Treat CSV/MD as runtime config (YAML only).

## Signal adapter

- One `SignalMatrix` entry row → at most one `TradeIntent` (invalid rows skipped with counted reasons).
- Maps `backtest.quantity` → `TradeIntent.qty`, `backtest.max_hold_minutes` → `TradeIntent.max_hold_bars` (1m bars for Phase 6).

## Metrics

- `BacktestMetrics` / `summarize_trade_results` use **only** `TradeResult` fields (including execution-provided `r_multiple`, `exit_reason`, `reject_reason`).

## Reference

- `docs/EXECUTION_CONTRACT.md` — fills, PnL, R ownership.
- `docs/LAYER1_CONTRACT.md` — Layer1 smoke scope.
