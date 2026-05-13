# Materialization summary

`materialize_trade(bars, intent, spec) -> MaterializedTrade | TradeResult`

- **Next-open**: `entry_bar = signal_bar + 1`.
- **NO_NEXT_BAR** if `entry_bar >= n_bars`.
- **CROSS_SESSION_ENTRY** if `session_id[entry_bar] != session_id[signal_bar]`.
- **OUTSIDE_TRADING_WINDOW** if `minute[entry_bar] > eod_exit_minute` (entry on EOD minute allowed).
- **SHORT_NOT_ALLOWED** for short when `allow_short` is false.
- **Entry fill**: `apply_entry_slippage(open[entry_bar], side, slippage)`.
- **Stop / risk**: long needs `stop < entry`; short needs `stop > entry`; else **INVALID_STOP**; `risk_per_share` from entry−stop geometry; **RISK_TOO_SMALL** if `< min_risk_per_share`.
- **Target**: `entry ± target_r * risk_per_share`.
- **Max hold**: `intent.max_hold_bars` if `>0` else `spec.max_hold_bars_default` else `None`.
