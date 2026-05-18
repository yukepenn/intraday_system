# CHATGPT_REVIEW_BUNDLE — Phase 12 generic feature foundation

## Git baseline

- Branch: `main`
- Pre-task HEAD: `fabba9678ae020393905c3fbdefcdc839e08891f` (matched `origin/main`)
- Task: `DESIGN_GENERIC_FEATURE_FOUNDATION_FOR_SECOND_FAMILY`

## Why Phase 12

Phase 11 selected **ORB continuation** as second MVP family. Phase 11 required small generic features (`vwap_slope_5`, `orb_width_pct`) before strategy MVP. This phase implements Layer 0 facts only — not strategy signals.

## Codex context

- Target reviewed: `5353d48` (Phase 11)
- Verdict: `PASS_WITH_WARNINGS`
- Warning repaired: `PROJECT_STATUS.md` snapshot now points to Phase 12 bundle
- `CODEX_REVIEW.md` not modified by Cursor

## Feature semantics

| Column | Formula |
| --- | --- |
| `vwap_slope_5` | `(vwap[t]-vwap[t-4])/4` same session, finite VWAP |
| `orb_width_pct_15` | `orb_range_15/orb_mid_15` after ORB complete, mid≠0 |

Session-contained, no-lookahead, NaN until defined.

## Feature config

- **New:** `configs/features/orb_core_v1.yaml` (9 columns, hash `e3c3df12...`)
- **Unchanged:** `configs/features/pa_core_v1.yaml`

## Implementation

- `kernels/vwap.py` — `vwap_slope_5`
- `kernels/orb.py` — `orb_width_pct` → `orb_width_pct_15`
- `specs.py`, `registry.py` — allowed outputs

## Tests

12+ new unit tests: warmup, session reset, no-lookahead, engine hash stability, `pa_core_v1` hash unchanged.

## CLI smoke

- `features inspect orb_core_v1` — PASS
- `features build` — skipped (no local curated QQQ)

## ORB readiness

Label: **`ORB_FEATURE_FOUNDATION_COMPLETE`**. Strategy MVP still required; do not promote.

## Validation

403 pytest, ruff, compileall, CLI doctor/validate — PASS. No Layer1 grid.

## Not implemented

ORB/GAP/CCI/VWAP strategy runtime, candidate YAML, Layer2/3, WFO, live/paper, PA changes, Layer1 grids.

## Risks

- Real-data feature build not run locally (no curated parquet in workspace).
- Strategy phase must not add strategy-specific feature columns.

## Decision

**`GENERIC_FEATURE_FOUNDATION_SECOND_FAMILY_COMPLETE`**

## Cursor provisional next step

**`IMPLEMENT_SECOND_STRATEGY_FAMILY_MVP`**

Final roadmap: user + ChatGPT Pro after Codex review.
