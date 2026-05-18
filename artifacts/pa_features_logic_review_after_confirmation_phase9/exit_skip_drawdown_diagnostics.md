# Exit / skip / drawdown diagnostics

## Exit mix (all combos aggregated)

| Reason | Design H1 | Confirmation H2 |
| --- | --- | --- |
| STOP | 819 (39.7%) | 874 (41.5%) |
| TARGET | 677 (32.8%) | 656 (31.1%) |
| MAX_HOLD | 412 (20.0%) | 386 (18.3%) |

**Finding:** Slightly **more STOPs, fewer TARGETs** in H2 — consistent with harder target achievement and adverse paths. MAX_HOLD share similar; rolling_low combos still dominate MAX_HOLD at combo level.

## Drawdown

- Design HOLD rows: max_dd **4.2–7.1R** (under 10R gate).
- Confirmation: **all** combos **14.8–30.7R**.
- Best H2 economics combo_0010 (+7.58R): max_dd **19.88R** → still `excessive_drawdown`.

Gate threshold (10R) is **not** the sole story — path economics degraded materially.

## Skip / session cap

- `max_trades_per_session` skips ~4200–4300 per combo both windows.
- Accepted trades 111–128 — comparable.
- Not a trade-count-driven rejection pattern.

CSV: `exit_skip_drawdown_diagnostics.csv`.
