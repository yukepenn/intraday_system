# Parameter-axis diagnostics — 16-combo PA controlled grid (QQQ 2024H1)

Source CSV: `artifacts/layer1_pa_grid_review_phase6c/sweep_results_review.csv`.

All summaries treat each combo as equally weighted (**n = 8** within each axis value for this factorial design).

Quantitative aggregates are in **`parameter_axis_summary.csv`**.

---

## `risk.stop_mode`

| Metric | `signal_low` | `rolling_low` |
| --- | ---: | ---: |
| Combo count | 8 | 8 |
| Mean `total_r` | −11.84 | **+5.57** |
| Median `total_r` | ≈ −11.4 | ≈ +5.0 |
| Combos with `total_r > 0` | **0** | **8** |
| Combos with PF > 1 | **0** | **8** |
| Mean `profit_factor_r` | 0.83 | **1.13** |
| Mean `max_drawdown_r` | ≈ 19.0 | ≈ 5.8 |
| Mean `accepted_trades` | ≈ 119 | ≈ 119 |

**Interpretation (non-exhaustive):** On **this window only**, **`rolling_low` dominates** economically relative to **`signal_low`**. This is axis-wide (not one lucky isolate within `signal_low`). Trade counts remain comparable across stop modes conditional on other axes (sessions remain 124 capped).

---

## `risk.target_r`

| Metric | **1.0** | **1.35** |
| --- | ---: | ---: |
| Mean `total_r` | −3.98 | −2.29 |
| Combos with `total_r > 0` | 4 | 4 |
| Combos with PF > 1 | 4 | 4 |

**Interpretation:** Target choice **modulates**, but positives exist only inside the **`rolling_low`** half-matrix (see `parameter_interaction_summary.md`). Across **all sixteen** rows, **`target_r` alone does not salvage** negatives when paired with **`signal_low`**.

---

## `signal.body_pct_min`

| Metric | **0.48** | **0.56** |
| --- | ---: | ---: |
| Mean `total_r` | −4.10 | −2.17 |
| Combos with `total_r > 0` | 4 | 4 |

**Interpretation:** The **slightly larger body threshold** mildly improves pooled mean `total_r` here, but positivity still clusters with **`rolling_low`**. Difference magnitude is modest vs stop-mode pivot.

---

## `signal.require_vwap_side`

| Metric | **`false`** | **`true`** |
| --- | ---: | ---: |
| Mean `total_r` | −2.19 | −4.08 |
| Combos with `total_r > 0` | 4 | 4 |

**Interpretation:** Pooled averages favor **`false`**, yet Phase 6c notes the **single best row** mixes **`rolling_low`**, **`body_pct_min=0.56`**, and **`require_vwap_side=true`** (`combo_0015`). Conclusion: **ambiguous / interaction-heavy**, not a clean universal filter signal on this microscopic grid.

---

## Meta

- Avoid claims of statistical significance — **six months / one ETF / capped trades**.
- Diagnostics support **engineering trust** plus **economics-informed selection design**, not live trading assertions.
