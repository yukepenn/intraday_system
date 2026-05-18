# Phase 9 decision

**Task:** `REVIEW_PA_FEATURES_OR_LOGIC_AFTER_CONFIRMATION_FAILURE`

## Decision (exactly one)

### `PA_FEATURE_LOGIC_REVIEW_COMPLETE`

Diagnostic review of PA strategy logic, `pa_core_v1` features, controlled grid axes, and QQQ 2024H2 confirmation failure is complete. No trading logic, features, or grids were changed in this phase.

## Recommended next step (exactly one)

### `REFINE_PA_GRID_AND_RERUN`

Run a **small explicit diagnostic grid** (≈12 combos) focused on risk path (`stop_mode`, `target_r`, `max_hold_minutes`) on the **design window first**, then validate on a **fresh non-overlapping holdout** — not retuning from 2024H2 confirmation winners.

## Key conclusions

1. All 16 confirmation rows **REJECT** — primarily `excessive_drawdown` (all max_dd > 10R) plus weak economics on former design HOLD combos.
2. Failure is **not** mainly artifact/reporting — sweep and dry-run evidence are consistent.
3. **rolling_low did not beat signal_low in confirmation** — ranking **reversed**.
4. `target_r` / `require_vwap_side` / `body_pct_min` shifts are secondary to stop-mode path instability.
5. **pa_core_v1** is adequate for MVP; strategy under-uses regime features — address **after** risk grid diagnostic.
6. PA MVP path: **refine, do not promote**; Layer2/3/WFO/live/paper remain not implemented.

## Non-promotion warning

`promotion_allowed_now=false` for all rows. No runtime candidate YAML. Confirmation weakness must not be used to retune directly on 2024H2.
