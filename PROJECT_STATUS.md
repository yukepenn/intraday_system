# PROJECT_STATUS

## Current phase

**Phase 7 — Layer1 PA candidate selection design (`DESIGN_LAYER1_PA_CANDIDATE_SELECTION`)** — doctrine, schema, reconstruction helper, provisional gates, dry-run on Phase **6c** sweep (**no** runtime candidate YAMLs).

## Decision

**`LAYER1_PA_CANDIDATE_SELECTION_DESIGN_COMPLETE`** — Selection contract + hash-verified reconstruction for all **16** combos; dry-run gates applied; promotion blocked (`promotion_allowed_now=false`).

## Recommended next step (exactly one)

**`IMPLEMENT_LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN`** — Repeatable CLI/report path for selection dry-run (still **not** YAML promotion).

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Latest validation (Phase 7): **`pytest 340`** + Ruff + CLI (`doctor`, `validate structure`, `layer1 grid-inspect`)
- Bundle: `artifacts/layer1_pa_candidate_selection_design_phase7/`
- Dry-run: 7 hold / 9 reject; top preview `combo_0015`

See `NEXT_HANDOFF.md` for full checklist.
