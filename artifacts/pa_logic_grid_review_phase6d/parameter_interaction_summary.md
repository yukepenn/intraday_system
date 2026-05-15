# Parameter-interaction diagnostics

See **`parameter_interaction_summary.csv`** for numeric aggregates (`mean_*`, median splits, positivity counts).

## Highlights

### `stop_mode × target_r` (four cells × 4 combos each)

| stop_mode / target_r | Mean `total_r` (n = 4) |
| --- | --- |
| `signal_low`, 1.0 | −14.7 |
| `signal_low`, 1.35 | −9.0 |
| **`rolling_low`, 1.0** | **+6.8** |
| **`rolling_low`, 1.35** | **+4.4** |

Interpretation: **Stop mode splits the payoff surface** cleanly; **`target_r` tilts margins within the favorable stop regime.**

### `stop_mode × require_vwap_side`

Approximate pooled means (`n = 4` each):

| Cell | Mean `total_r` |
| --- | --- |
| `signal_low` × vwap=false | −11.0 |
| `signal_low` × vwap=true | −12.7 |
| `rolling_low` × vwap=false | **+6.6** |
| `rolling_low` × vwap=true | **+4.5** |

Interpretation: **VWAP tightening neither rescues nor meaningfully rehabilitates **`signal_low`**** on this slice; **`rolling_low` stays constructive** in both VWAP buckets with a pooled tilt toward **`false`**.

### `stop_mode × body_pct_min`

For **`signal_low`**, body bucket means remain **deeply negative** (both halves).

For **`rolling_low`**, **higher body (`0.56`) lifts pooled mean vs `0.48`**.

### `target_r × require_vwap_side`

Because this crosses **both** stop modes, orthogonal marginal means stay **opaque** — always reconcile with the **`rolling_low`**-conditioned subsets above.
