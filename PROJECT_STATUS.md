# PROJECT_STATUS

## Current phase

**Phase 7b — Layer1 PA candidate-selection dry-run (`IMPLEMENT_LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN`)** — repeatable CLI + library path; reads Phase **6c** sweep as audit input; **no** runtime candidate YAMLs.

## Decision

**`LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN_COMPLETE`** — `layer1 select-dry-run` on 16-row sweep; **16/16** reconstruction pass; **7** hold / **9** reject; `promotion_allowed_now=false` for all rows; Codex bool-parsing warning addressed.

## Recommended next step (exactly one)

**`RUN_LAYER1_PA_CONFIRMATION_WINDOW`** — Add out-of-sample window before promotion schema or YAML writes.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Latest validation (Phase 7b): **`pytest 371`** + Ruff + CLI (`doctor`, `validate structure`, `layer1 grid-inspect`, `layer1 select-dry-run`)
- Bundle: `artifacts/layer1_pa_candidate_selection_dry_run_phase7b/`
- Dry-run: 7 hold / 9 reject; top preview `combo_0015`; reconstruction 16/16

See `NEXT_HANDOFF.md` for full checklist.
