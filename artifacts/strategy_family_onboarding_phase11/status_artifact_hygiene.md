# Phase 11 status / artifact hygiene

| Item | Issue | Action | Behavior changed |
| --- | --- | --- | --- |
| README.md | Still lists `REFINE_PA_GRID_AND_RERUN` as next | Update to Phase 11 pivot + PA hold | yes |
| PROJECT_STATUS.md | Phase 10 only | Add Phase 11 onboarding status | yes |
| PROGRESS.md / CHANGES.md | Latest next step stale | Add Phase 11 entries | yes |
| Phase 10 comparison CSV | Blank `selection_decision_*` / `reject_reasons_*` columns | Document limitation; point to dedicated dry-run CSVs | no |
| Phase 10 dry-run CSVs | Authoritative selection columns | Add `phase10_artifact_reading_note.md` under Phase 11 | no |
| .gitignore | `local_run` / `_pytest` patterns | Already present; verified | no |
| CODEX_REVIEW.md | Cursor must not edit | Left unmodified | no |

## Phase 10 comparison table limitation

`artifacts/pa_risk_grid_diagnostic_phase10/design_vs_confirmation_diagnostic_comparison.csv` merges sweep metrics only. Selection decisions and reject reasons live in:

- `artifacts/pa_risk_grid_diagnostic_phase10/selection_dry_run_h1.csv`
- `artifacts/pa_risk_grid_diagnostic_phase10/selection_dry_run_h2.csv`

Do not rerun Phase 10 to backfill comparison columns.
