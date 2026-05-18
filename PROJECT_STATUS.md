# PROJECT_STATUS

## Current phase

**Phase 12 — Generic feature foundation for second family (`DESIGN_GENERIC_FEATURE_FOUNDATION_FOR_SECOND_FAMILY`)** — `vwap_slope_5`, `orb_width_pct_15`, `configs/features/orb_core_v1.yaml`; no ORB strategy, Layer1, or promotion.

## Decision

**`GENERIC_FEATURE_FOUNDATION_SECOND_FAMILY_COMPLETE`** — ORB continuation generic market facts added; ORB strategy **not** implemented.

## Recommended next step (exactly one)

**`IMPLEMENT_SECOND_STRATEGY_FAMILY_MVP`** — ORB continuation strategy MVP using `orb_core_v1` (after Codex review). Not promotion.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Bundle: `artifacts/generic_feature_foundation_second_family_phase12/`
- Prior Phase 11 bundle: `artifacts/strategy_family_onboarding_phase11/`
- Prior Phase 9 bundle: `artifacts/pa_features_logic_review_after_confirmation_phase9/`
- Prior confirmation bundle: `artifacts/layer1_pa_confirmation_data_repair_phase8b/`
- Confirmation config: `configs/layer1/controlled_pa_qqq_2024h2.yaml`
- `promotion_allowed_now=false` enforced; no runtime candidate YAMLs

See `NEXT_HANDOFF.md` for full checklist.
