# Phase15 Focused-Grid Design Recommendation

Phase: `PHASE15_LAYER1_STRATEGY_LIBRARY_RESULT_REVIEW_AND_FOCUSED_GRID_DESIGN`

## Recommendation

A future focused diagnostic grid is warranted, but only as a bounded Phase16 diagnostic. The first focused diagnostic scope should include `orb_continuation` only. It must not create candidate YAML, run select-dry-run, promote rows, start Layer2, or tune thresholds from Phase14 top rows.

## Eligible Families

- `orb_continuation`: eligible because H1 and H2 both show positive best rows, positive median total_r, adequate accepted-trade counts, and clean plumbing. H2 remains sanity/plumbing only because `missing_minute_slots_total=540` is attached.

## Watch / Hold Families

- `pa_buy_sell_close_trend`: `LEGACY_HOLD` - Phase10 held PA; Phase14 has positive best rows but negative medians in both windows and high drawdown, so this does not revive PA tuning.
- `orb_continuation`: `FOCUSED_DIAGNOSTIC_CANDIDATE` - Only family with positive best and positive median total_r in both observed windows, with clean plumbing and enough sample for a bounded future diagnostic design.
- `orb_retest_continuation`: `WATCH_REGIME_FLIP` - H1 median is positive but H2 median turns negative; best rows alone are not enough for focused status.
- `failed_orb`: `HOLD_WEAK_OR_NEGATIVE` - H1 best row is negative and both window medians are negative; H2 best row is not confirmation evidence.
- `gap_acceptance_failure`: `WATCH_LOW_SAMPLE` - Small-N and infinite profit-factor artifacts dominate; positive best rows are not stable evidence.
- `vwap_trend_pullback`: `WATCH_HIGH_DRAWDOWN` - Best rows are positive, but medians are negative and drawdown is too high for focused status.
- `vwap_reclaim_reject`: `WATCH_REGIME_FLIP` - H1 is weak across best and median while H2 is positive; H2 cannot be confirmation due phase scope and data warning.
- `prior_day_level_trap`: `WATCH_REGIME_FLIP` - H2 median is positive but H1 median is negative; this is a watch item, not a focused candidate.
- `cci_extreme_snapback`: `WATCH_HIGH_DRAWDOWN` - Positive best rows coexist with strongly negative medians and severe drawdown, so top-row interpretation is unsafe.
- `stochastic_oversold_cross`: `WATCH_HIGH_DRAWDOWN` - Both medians are near -10R despite positive best rows; drawdown risk dominates.

## Proposed Combo Caps

- `orb_continuation`: maximum 36 combos for the future focused diagnostic grid.
- All watch/hold families: 0 combos in the first focused grid unless a later prompt explicitly defines a separate diagnostic shadow bucket.

## Proposed Window Policy

- QQQ 2024H1 may be reused only as an observed design diagnostic window.
- QQQ 2024H2 may be reused only as an observed sanity/plumbing repeat with data caveat.
- Neither H1 nor H2 is a clean promotion holdout now.
- Any future promotion requires at least one fresh, not-yet-used window and ideally another symbol/regime.

## Proposed Reporting Requirements

- Capture full resolved config or deterministic reconstruction manifest with hash verification.
- Preserve per-combo signal, accepted/rejected, median/best/worst, drawdown, zero-signal, and data-quality fields.
- Keep CSV/MD audit-only; YAML remains runtime truth.

## Non-Goals

No promotion, candidate YAML, select-dry-run, Layer2, Layer3, WFO, live/paper, strategy retuning, feature semantic changes, or execution truth changes. Phase16, if accepted, is still diagnostic only.
