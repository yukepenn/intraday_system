# Phase 10 diagnostic conclusion

## Decision

**`PA_RISK_DIAGNOSTIC_COMPLETE_HOLD_PA_PATH`**

## Recommended next step

**`REVIEW_PA_FEATURES_OR_LOGIC`**

## Answers

1. **Drawdown failure reduced?** No. All 12 design and 12 confirmation rows fail `excessive_drawdown` (max_dd > 10R). Design-window max_dd range ~15–33R; confirmation ~14–41R.
2. **atr_buffer vs signal_low?** `signal_low` dominates; `atr_buffer` materially worse in both windows (e.g. combo_0007 −28R H1 vs best signal_low −4.79R).
3. **max_hold 30 vs 50?** Negligible within stop/target pairs (identical metrics for many pairs); not a stabilizer.
4. **Lower target_r?** No consistent cross-window benefit; H1 all negative regardless of target_r.
5. **Reasonable in both H1 and H2?** **0/12** combos positive total_r in both windows; **0/12** with max_dd ≤ 10R in both.
6. **Fresh holdout justified?** No — diagnostic did not surface a stable risk-path candidate set.
7. **Continue PA path?** Hold — risk-path-only retune with fixed signal slice did not restore prior controlled-grid economics.
8. **Minimal features now?** Defer until PA signal/feature logic review; risk grid did not clear the bar.
9. **Pause for another family?** Not required yet; prefer PA logic/feature review before family expansion.
10. **Next phase:** Review PA features/logic (regime use, signal scoring) — not promotion, not Layer2.

## Interpretation label

**`RISK_DIAGNOSTIC_WEAKENS_PA_PATH`**

Fixed signal parameters (body_pct 0.56, no vwap, no rolling_low) plus risk-only sweep produced uniformly weak design-window results vs Phase 6c controlled grid. Risk-path axes alone do not explain prior H1/H2 instability in a promotable way.

## Explicit boundaries

- `promotion_allowed_now=false` on all 24 dry-run rows (12+12).
- No runtime candidate YAML.
- 2024H2 used as stress retest only (Phase 9 hypothesis window); not a fresh holdout.
