# Phase 8b — PA confirmation data repair and rerun

Date: 2026-05-17

## Git baseline

- HEAD at artifact generation: `ce4814ef69bdee8d6b29f9c7b1a652f06c155df2`
- Branch: `main`

## Why Phase 8b

Phase 8 prepared confirmation config and infra fixes but could not run the grid because **non-overlapping QQQ 2024H2 curated parquet** was missing (design window 2024H1 existed locally).

## Preflight repairs

- Selection report Markdown: malformed/non-finite metrics render as `invalid` without aborting.
- Output-root validator: rejects `.` and empty paths with `ConfigError`.
- Handoff wording corrected: curated root had H1 only; blocker was missing H2.

## Data

- Normalized QQQ 2024-07-01 .. 2024-12-31 from raw IBKR (49380 rows, 6 months).
- Validated curated load; local-only parquet not committed.

## Confirmation grid

- Config: `configs/layer1/controlled_pa_qqq_2024h2.yaml`
- 16 combos, reference execution, no retuning.
- Best total_r: `combo_0010` → 7.58

## Confirmation selection dry-run

- 16 rows, 0 HOLD, 16 REJECT, promotion_allowed_now=false for all.

## Design vs confirmation

- **CONFIRMATION_WEAKENS_SELECTION_DESIGN**: design-window HOLD previews (e.g. combo_0015) did not pass gates on 2024H2.

## Promotion boundary

No candidate YAMLs. No promotion. Layer2/3/WFO/live not implemented.

## Decision

- **LAYER1_PA_CONFIRMATION_WINDOW_COMPLETE**
- Recommended next step: **REVIEW_PA_FEATURES_OR_LOGIC**
