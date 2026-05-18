# PROJECT_STATUS

## Current phase

**Phase 8b — Layer1 PA confirmation window complete (`FIX_LOCAL_CURATED_DATA_AND_RERUN_CONFIRMATION_WINDOW`)** — QQQ 2024H2 curated locally, confirmation grid + dry-run executed without retuning.

## Decision

**`LAYER1_PA_CONFIRMATION_WINDOW_COMPLETE`** — Non-overlapping confirmation window (QQQ 2024H2) validated, 16-combo grid run, selection dry-run completed. Design-window HOLD previews did not survive confirmation gates (**CONFIRMATION_WEAKENS_SELECTION_DESIGN**).

## Recommended next step (exactly one)

**`REVIEW_PA_FEATURES_OR_LOGIC`** — Review PA features/logic after confirmation weakened design selection; not real candidate promotion.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Bundle: `artifacts/layer1_pa_confirmation_data_repair_phase8b/`
- Confirmation config: `configs/layer1/controlled_pa_qqq_2024h2.yaml`
- `promotion_allowed_now=false` enforced; no runtime candidate YAMLs

See `NEXT_HANDOFF.md` for full checklist.
