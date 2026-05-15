# Grid results interpretation (Phase 6c)

## Did all 16 combos run?

Yes — `sweep_results_review.csv` contains **16** rows; CLI `combo_count` = 16.

## Plausible metrics?

Yes — trade counts align with **124** trading sessions and `max_trades_per_session: 1` (executed trades per combo are **114–124** because `require_vwap_side` / signal filters reduce entries, not ghost rows). Skip totals are dominated by session intent cap and open-trade skips, consistent with smoke behavior. No execution rejects in this run.

## Nontrivially promising?

Only a **subset** of axis settings look positive on this single window: **`rolling_low` stop** variants show positive `total_r` and PF ≥ 1 for several combos; **`signal_low` stop** variants are **negative** on `total_r` across the grid. Best PF (~**1.23**) and best `total_r` (~**8.9R**) occur for **`combo_0015`** (`rolling_low`, `target_r=1.0`, `body_pct_min=0.56`, `require_vwap_side=true`). This is **exploratory** only — not evidence of tradable edge.

## Trade counts adequate?

~**114–124** accepted trades per combo is enough for **sanity / plumbing** review but **thin** for robust performance claims (one trade max per session design).

## Sample-size dominance?

Yes — results are **window-specific** (QQQ 2024H1 only) and **high variance**; do not treat ranks as stable.

## Exit reasons

Aggregate mix: **STOP** > **TARGET**; **MAX_HOLD** appears only for `rolling_low` combos (longer holds). Not pathological for this strategy profile.

## `require_vwap_side`

When paired with **`signal_low`**, it generally **does not rescue** negative totals. When paired with **`rolling_low`**, the best row uses `require_vwap_side=true`, but other **`rolling_low`** rows are strong with `false` — **ambiguous** filter value in this tiny grid.

## Stop modes

**Meaningful** split: `signal_low` vs `rolling_low` is the clearest axis in this run.

## `target_r` (1.0 vs 1.35)

Effects exist but are **secondary** to stop mode; 1.35 tends to shift exits without uniformly improving `total_r`.

## Readiness for candidate selection design?

**Not yet** on strength of economics alone. **Infra is ready**; **strategy/grid economics** merit human review before any selection design.

## Interpretation label

`GRID_RESULTS_NEED_REVIEW_BEFORE_SELECTION`
