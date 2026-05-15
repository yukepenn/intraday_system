# Backtest metrics summary

- Module: `src/intraday/backtest/metrics.py`
- `summarize_trade_results` → `BacktestMetrics` (aggregates `TradeResult` only)
- Accepted-only: `avg_r`, `median_r`, `win_rate` (r>0), `profit_factor_r`, `max_drawdown_r` (on cumulative R), `avg_bars_held`
- No accepted trades: aggregates 0.0; `profit_factor_r` 0; all-wins → `profit_factor_r` = inf
- Exit/reject counts keyed by enum names
