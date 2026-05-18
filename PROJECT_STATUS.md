# PROJECT_STATUS

## Current phase

**Phase 10 — PA risk-path diagnostic grid (`REFINE_PA_GRID_AND_RERUN`)** — 12-combo risk diagnostic on QQQ 2024H1/H2; no strategy/feature changes; no promotion.

## Decision

**`PA_RISK_DIAGNOSTIC_COMPLETE_HOLD_PA_PATH`** — Risk-path-only grid did not restore design economics or cross-window stability (0/12 positive in both windows; all rows fail drawdown gates). Hold PA candidate path.

## Recommended next step (exactly one)

**`REVIEW_PA_FEATURES_OR_LOGIC`** — Review PA signal scoring, regime feature use, and grid fixed-parameter doctrine before further diagnostics or holdout. Not promotion.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Bundle: `artifacts/pa_risk_grid_diagnostic_phase10/`
- Prior Phase 9 bundle: `artifacts/pa_features_logic_review_after_confirmation_phase9/`
- Prior confirmation bundle: `artifacts/layer1_pa_confirmation_data_repair_phase8b/`
- Confirmation config: `configs/layer1/controlled_pa_qqq_2024h2.yaml`
- `promotion_allowed_now=false` enforced; no runtime candidate YAMLs

See `NEXT_HANDOFF.md` for full checklist.
