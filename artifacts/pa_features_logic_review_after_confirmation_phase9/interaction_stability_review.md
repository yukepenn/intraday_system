# Interaction stability review

## stop_mode × target_r

| Window | rolling_low + 1.0 | rolling_low + 1.35 | signal_low + 1.0 | signal_low + 1.35 |
| --- | --- | --- | --- | --- |
| Design mean total_r | +6.75 | +4.39 | -14.71 | -8.97 |
| Confirmation mean total_r | -9.89 | -14.53 | -1.24 | **+2.44** |

**Finding:** Confirmation collapse is **rolling_low at both target_r levels**. signal_low + 1.35 is the only interaction with positive mean R in H2 (still gate-fails on DD).

## stop_mode × require_vwap_side

- Design: rolling_low + vwap_true best for rank-1 (combo_0015).
- Confirmation: rolling_low + vwap_false **worse** (-15.02 mean) than vwap_true (-9.40) but both deeply negative.

## stop_mode × body_pct_min

- rolling_low + 0.56 was best in design (+7.00 mean); same pair **worst in confirmation** (-12.70 mean).
- signal_low + 0.56 best in confirmation (+3.59 mean) — aligns with combo_0010.

CSV: `interaction_stability_review.csv`.

Interpretation: caution — 2×2 cells have only 4 combos each. Use for **diagnostic direction**, not alpha claims.
