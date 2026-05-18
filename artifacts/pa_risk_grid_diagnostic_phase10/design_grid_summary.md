# Design-window (2024H1) diagnostic grid summary

| Metric | Value |
| --- | --- |
| combo_count | 12 |
| best total_r | **−4.79R** (`combo_0005`: signal_low, target_r 1.2, max_hold 30) |
| best profit_factor_r | **0.932** (`combo_0005`) |
| max_drawdown_r range | ~15.5 – 33.0 R |
| accepted_trades per combo | 124 |
| dry-run | 12/12 REJECT (`excessive_drawdown`, `negative_total_r`, `weak_profit_factor`) |
| promotion_allowed_now | false (all) |

All design-window combos negative total_r — risk diagnostic with fixed signal slice underperforms Phase 6c controlled grid on same symbol/window.
