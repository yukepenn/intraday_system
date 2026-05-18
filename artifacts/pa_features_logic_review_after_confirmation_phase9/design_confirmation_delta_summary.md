# Design vs confirmation delta summary

Windows: QQQ **2024H1** (design) vs **2024H2** (confirmation). Same 16-combo controlled grid, no retuning.

## Headline

| Combo | Design | Confirmation | Delta total_r |
| --- | --- | --- | --- |
| **combo_0015** (design rank-1 HOLD) | +8.88R, PF 1.23, dd 4.65 | -9.08R, PF 0.80, dd 21.78 | **-17.96R** |
| **combo_0010** (confirmation best total_r) | -9.61R REJECT | +7.58R REJECT | +17.19R |
| All 7 design HOLD rows | HOLD | REJECT | All sign-flipped or deeply negative |

## Answers (task questions 1–4)

1. **Why all confirmation rejects?** Every row breached `max_drawdown_r` gate (limit 10.0R); 12/16 also `negative_total_r` and/or `weak_profit_factor`. Not insufficient trades (111–128 accepted).

2. **Main issue?** **Market/regime + risk-path economics** (rolling_low + MAX_HOLD path), not artifact bug. Drawdown gate correctly flags instability. Grid construction exposed stop/target coupling; PA logic did not change between windows.

3. **rolling_low vs signal_low in confirmation?** **Ranking reversed.** Design: rolling_low mean +5.57R vs signal_low -11.84R. Confirmation: rolling_low mean -12.21R vs signal_low +0.60R. rolling_low did **not** persist dominance.

4. **target_r / require_vwap_side / body_pct_min?**
   - `target_r`: H2 slightly favors 1.35 on mean total_r (-6.04 vs -5.56 for 1.0) but both negative for rolling_low; signal_low×1.35 best pair (combo_0010).
   - `require_vwap_side`: false slightly better mean total_r in H2 (-5.72 vs -5.88); design favored true for best HOLD (combo_0015).
   - `body_pct_min`: 0.56 better in H2 (-4.55 vs -7.05 mean); design also favored 0.56 for top HOLD rows.

Full per-combo table: `design_confirmation_delta_summary.csv`.
