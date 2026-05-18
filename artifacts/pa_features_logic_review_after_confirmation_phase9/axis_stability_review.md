# Parameter-axis stability review

## stop_mode

| Window | rolling_low mean total_r | signal_low mean total_r | Best combo |
| --- | --- | --- | --- |
| Design H1 | **+5.57** | -11.84 | combo_0015 (rolling) |
| Confirmation H2 | **-12.21** | +0.60 | combo_0010 (signal_low) |

**Finding:** Dominance **did not persist**. Confirmation weakness is concentrated in rolling_low (+ MAX_HOLD heavy exits).

## target_r

| Window | 1.0 mean | 1.35 mean |
| --- | --- | --- |
| Design H1 | -3.98 | -2.29 |
| Confirmation H2 | -5.56 | -6.04 |

**Finding:** Higher target_r was mildly better in H1; **no stable advantage in H2**. Interaction: signal_low×1.35 best in H2 (combo_0010).

## body_pct_min

| Window | 0.48 mean | 0.56 mean |
| --- | --- | --- |
| Design H1 | -4.10 | -2.17 |
| Confirmation H2 | -7.05 | -4.55 |

**Finding:** Stricter body (0.56) **relatively** better in both windows; absolute performance still poor for rolling_low.

## require_vwap_side

| Window | false mean | true mean |
| --- | --- | --- |
| Design H1 | -2.19 | -4.08 |
| Confirmation H2 | -5.72 | -5.88 |

**Finding:** VWAP filter **not a reliable stabilizer**; design rank-1 used true but failed in H2.

CSV: `axis_stability_review.csv`.
