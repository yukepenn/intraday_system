# PROJECT_STATUS

## Current phase

**Phase 9 — PA feature/logic review after confirmation failure (`REVIEW_PA_FEATURES_OR_LOGIC_AFTER_CONFIRMATION_FAILURE`)** — Diagnostic review of why QQQ 2024H2 confirmation rejected all 16 combos; no strategy/feature/grid rerun.

## Decision

**`PA_FEATURE_LOGIC_REVIEW_COMPLETE`** — Confirmation weakness is primarily risk-path/regime instability (rolling_low reversal, universal drawdown gate breach), not infrastructure defect. PA path **not** ready for promotion.

## Recommended next step (exactly one)

**`REFINE_PA_GRID_AND_RERUN`** — Small explicit diagnostic grid on risk axes (≈12 combos); design window first; fresh holdout for confirmation. Not retuning from 2024H2.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Bundle: `artifacts/pa_features_logic_review_after_confirmation_phase9/`
- Prior confirmation bundle: `artifacts/layer1_pa_confirmation_data_repair_phase8b/`
- Confirmation config: `configs/layer1/controlled_pa_qqq_2024h2.yaml`
- `promotion_allowed_now=false` enforced; no runtime candidate YAMLs

See `NEXT_HANDOFF.md` for full checklist.
