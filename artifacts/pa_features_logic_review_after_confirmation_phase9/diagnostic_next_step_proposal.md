# Diagnostic next-step proposal

## Decision

| Field | Value |
| --- | --- |
| Phase decision | **`PA_FEATURE_LOGIC_REVIEW_COMPLETE`** |
| Recommended next step | **`REFINE_PA_GRID_AND_RERUN`** |

## Rationale

1. Confirmation failure is **broad** on design HOLD rows but **not** infrastructure-blocked.
2. **Stop-mode × target_r × hold** interaction reversed between windows — warrants a **small explicit diagnostic grid**, not promotion schema.
3. Feature gap is real but **second priority** after risk-path diagnostic (per Phase 6d and confirmation evidence).
4. Do **not** retune from H2 winners; design new grid doctrine on **hypothesis** (risk stability), then validate on fresh holdout.

## Proposed tiny diagnostic grid (do not run in Phase 9)

| Axis | Values | Notes |
| --- | --- | --- |
| `risk.stop_mode` | `signal_low`, `atr_buffer` | Drop rolling_low from primary diagnostic; atr_buffer already in strategy code |
| `risk.target_r` | `0.8`, `1.0`, `1.2` | Lower targets — config-only |
| `backtest.max_hold_minutes` | `30`, `50` | If grid schema supports override |
| `signal.body_pct_min` | `0.56` | Fix one body level to limit combos |
| `signal.require_vwap_side` | `false` | Reduce interaction noise |

**Max combos:** 2 × 3 × 2 × 1 × 1 = **12** (if atr_buffer + max_hold in grid YAML).

**Windows:** Re-run on **2024H1 design** first; only then non-overlapping confirmation (e.g. 2025H1 or next reserved slice) — **not** iterative retune on 2024H2.

## Rejected next steps (this phase)

| Step | Why not |
| --- | --- |
| `DESIGN_LAYER1_PA_CANDIDATE_PROMOTION_SCHEMA` | Confirmation weakened all design HOLD rows |
| `PROPOSE_MINIMAL_PA_FEATURE_DIAGNOSTIC` | Defer until risk grid diagnostic completes |
| `HOLD_CANDIDATE_SELECTION` | Actionable grid refinement exists |
| Real promotion / Layer2 / WFO | Explicitly out of scope |

CSV: `diagnostic_next_step_proposal.csv`.
