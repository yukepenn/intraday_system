# CHATGPT_REVIEW_BUNDLE — Phase 10 PA risk diagnostic grid

Task: `REFINE_PA_GRID_AND_RERUN`  
Artifact root: `artifacts/pa_risk_grid_diagnostic_phase10/`

---

## Git baseline

- Branch: `main`
- HEAD at work start: `d938753763ad299c7446b5a824c3654ee2e29285` (matched `origin/main`)
- Prior handoff: `PA_FEATURE_LOGIC_REVIEW_COMPLETE` → `REFINE_PA_GRID_AND_RERUN`
- Codex Phase 9 target: `a239184` — `PASS_WITH_WARNINGS`

## Why Phase 10 was needed

Phase 9 recommended a ≤12-combo risk-path diagnostic (`stop_mode`, `target_r`, `max_hold`) after QQQ 2024H2 confirmation rejected all controlled-grid rows. Phase 10 implements and runs that grid on H1 (design) and H2 (stress retest), with dry-run gates — **no** promotion, **no** strategy/feature changes.

## Schema / hygiene preflight

- `atr_buffer` + `backtest.max_hold_minutes` supported (PASS). See `schema_preflight.md`.
- CHANGES Phase 6d stale heading fixed.
- Phase 10 `local_run` under gitignored `artifacts/pa_risk_grid_diagnostic_phase10/local_run/`.

## Diagnostic grid design

- Path: `configs/strategies/grids/pa_buy_sell_close_trend_risk_diagnostic_small.yaml`
- 12 combos: 2 stop × 3 target_r × 2 max_hold; fixed signal slice (body 0.56, no vwap); **no rolling_low**.
- Layer1: `pa_risk_diag_qqq_2024h1.yaml`, `pa_risk_diag_qqq_2024h2.yaml`

## Design-window result (2024H1)

| Metric | Value |
| --- | --- |
| Best total_r | −4.79R (`combo_0005`) |
| Best PF | 0.932 |
| max_dd range | ~15.5–33.0 R |
| Dry-run | 12/12 REJECT |

**All combos negative total_r** — weaker than Phase 6c controlled grid on same window.

## Confirmation-window result (2024H2 stress)

| Metric | Value |
| --- | --- |
| Best total_r | +4.68R (`combo_0005`) |
| Best PF | 1.070 (`combo_0003`) |
| max_dd range | ~14.1–41.2 R |
| Dry-run | 12/12 REJECT (`excessive_drawdown` all) |

## Selection dry-run

- Design + confirmation: `promotion_allowed_now=false` all rows; reconstruction 12/12 pass each.
- No candidate YAML.

## Design vs confirmation comparison

- **0/12** positive total_r in **both** windows.
- **0/12** max_dd ≤ 10R in both.
- `signal_low` >> `atr_buffer`; max_hold 30 vs 50 negligible.
- Label: **`RISK_DIAGNOSTIC_WEAKENS_PA_PATH`**

See `design_vs_confirmation_diagnostic_comparison.csv`.

## Diagnostic conclusion

Risk-path-only diagnostic did **not** surface promotable stability. Hold PA candidate path; review PA features/logic next.

## Promotion boundary

No promotion. No Layer2/3/WFO/live/paper. 2024H2 is stress retest only — fresh holdout still required if path revives.

## Validation results

See `validation_results.md` — compileall, pytest, ruff, CLI, grid-inspect, grid, select-dry-run.

## Explicit non-implemented items

Candidate YAML, Layer2/3, WFO, live/paper, GAP/CCI, PA strategy changes, feature kernels, execution semantics, broad grids, H2-winner retuning.

## Risks / blockers

Fixed signal slice may differ materially from Phase 6c grid (explains H1 all-negative vs prior +8.88R rank-1). Any future grid must document fixed-parameter doctrine.

## Decision

**`PA_RISK_DIAGNOSTIC_COMPLETE_HOLD_PA_PATH`**

## Recommended next step

**`REVIEW_PA_FEATURES_OR_LOGIC`**
