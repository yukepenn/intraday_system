# Phase 10 summary — PA risk diagnostic grid

- **Grid:** `pa_buy_sell_close_trend_risk_diagnostic_small.yaml` (12 combos)
- **Windows:** QQQ 2024H1 design, QQQ 2024H2 stress (not fresh holdout)
- **Design best total_r:** combo_0005 −4.79R (signal_low, target_r 1.2, max_hold 30)
- **Confirmation best total_r:** combo_0005 +4.68R (same params) — still REJECT (max_dd 19.8R)
- **Dry-run:** 12/12 REJECT each window; `promotion_allowed_now=false` everywhere
- **Cross-window stable positive:** 0/12
- **No** strategy/feature/execution changes; **no** candidate YAML

See `diagnostic_conclusion.md` and `CHATGPT_REVIEW_BUNDLE.md`.
