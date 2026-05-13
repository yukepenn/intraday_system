# Cost and R conventions

- **Entry slippage (adverse)**: long `+slip`, short `−slip` on the open reference.
- **Exit slippage (adverse)**: long `−slip` on raw exit; short `+slip` on raw exit.
- **Gross PnL**: `side * (exit − entry) * qty`.
- **Net PnL**: `gross − commission_per_trade` (fixed per trade).
- **R-multiple**: `net_pnl / (risk_per_share * qty)` — commission and both slippages flow through net and fills.

See `src/intraday/execution/cost.py`.
