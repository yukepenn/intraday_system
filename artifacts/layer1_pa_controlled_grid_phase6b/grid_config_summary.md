# Grid config summary

- **Layer1 runtime:** `configs/layer1/controlled_pa_qqq_2024h1.yaml`
- **Strategy grid:** `configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml`
- **Combos:** `2 × 2 × 2 × 2 = 16` (axes: `signal.body_pct_min`, `signal.require_vwap_side`, `risk.stop_mode`, `risk.target_r`)
- **Execution:** `reference` (`configs/execution/intraday_default.yaml`)
- **Scan policy:** `max_trades_per_session: 1`, `skip_while_trade_open: true`, `count_rejected_intents: true`

CSV mirror: `grid_config_summary.csv`.
