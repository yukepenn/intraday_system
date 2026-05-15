# Smoke config summary

- Path: `configs/layer1/smoke_pa_qqq_2024h1.yaml`
- `run_id`: `L1_PA_QQQ_2024H1_SMOKE_V1`
- Symbol / window: QQQ 2024-01-01 .. 2024-06-30
- Feature: `configs/features/pa_core_v1.yaml`, `use_cache: false`
- Strategy: `pa_buy_sell_close_trend` + `configs/strategies/base/pa_buy_sell_close_trend.yaml`
- Execution: `configs/execution/intraday_default.yaml`, `mode: reference`
- Backtest policy: `max_trades_per_session: 1`, `skip_while_trade_open: true`, `save_row_level_trades: false`
- Output: `artifacts/layer1_pa_smoke_phase6/local_run/` (local-only; gitignored)
