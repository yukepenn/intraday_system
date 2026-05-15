# Signal adapter summary

- Module: `src/intraday/backtest/signal_adapter.py`
- API: `build_trade_intents_from_signals` / `signal_matrix_to_intents` → `SignalAdapterResult`
- Entry rows only → `TradeIntent` with `signal_bar`, `side`, `raw_stop_price`, `target_r`, `score`, `setup_code`, `qty`, `max_hold_bars`, `candidate_id` (smoke uses `1`)
- Skip reasons counted: nonfinite stop, invalid target_r/side, qty≤0, negative max_hold
- No execution / PnL
