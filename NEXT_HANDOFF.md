# NEXT_HANDOFF

Last updated: **2026-05-18** (Phase **11** — strategy-family onboarding design).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Task commit: see `git log -1` after push
- Pre-task HEAD: `fab6c6f` (matched `origin/main`)

---

## B. Task scope (Phase 11)

- Design-only: strategy-family **onboarding contract**, feasibility matrix, feature audit, QT guardrails, second MVP family selection.
- **Did not:** implement ORB/GAP/CCI/VWAP, new feature kernels, Layer1 grids, candidate YAML, PA changes, Layer2/3, WFO, live/paper.
- Bundle: `artifacts/strategy_family_onboarding_phase11/`

---

## C. PA path hold

- PA canary vertical slice **complete** (Phases 5–10).
- Phase 10: 0/12 risk-diagnostic combos positive in both H1/H2; all dry-run REJECT.
- **Hold** PA promotion path; **do not** refine PA grids while onboarding ORB.
- PA not permanently abandoned — idea bank only.

---

## D. Onboarding interface

- **Ready:** `StrategyDef`, registry, PA configs, Layer1 smoke/grid/dry-run, selection gates.
- **Gap (closed in docs):** `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`.
- **Still missing at runtime:** non-PA strategies; `indicators`/`levels` feature groups.

---

## E. QT reference

- Read-only: `QT/src/features/`, `QT/src/strategies/strategy/orb_continuation.py`.
- No QT import; no architecture copy.
- Guardrails: `artifacts/strategy_family_onboarding_phase11/qt_migration_guardrails.md`

---

## F. Feasibility matrix

| Family | Status |
| --- | --- |
| ORB continuation | **Selected** — READY_FOR_MVP_DESIGN |
| GAP | NEEDS_GENERIC_FEATURE_FOUNDATION |
| CCI | NEEDS_GENERIC_FEATURE_FOUNDATION |
| VWAP | NEEDS_GENERIC_FEATURE_FOUNDATION |
| PA | HOLD |

CSV: `strategy_family_feasibility_matrix.csv`

---

## G. Feature audit

- ORB: reuse `pa_core_v1`; add `vwap_slope_5` (+ optional `orb_width_pct`) in mini foundation phase.
- GAP/CCI blocked on levels/CCI kernels.

CSV: `feature_requirements_audit.csv`

---

## H. Onboarding contract

`docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md` — required files, tests, Layer1 sequence, gates, prohibitions.

---

## I. Second family decision

**ORB continuation** (`orb_continuation`) — future implementation only.  
Rationale: best feature coverage, clear signal, diversifies PA, low arch risk.  
Not based on expected alpha.

---

## J. Future implementation plan

`second_family_implementation_plan.md` — feature foundation → strategy MVP → Layer1 smoke/grid → diagnostics. **Not started.**

---

## K. Tests / validation

| Check | Status |
| --- | --- |
| compileall | PASS |
| pytest smoke+unit | 356 PASS |
| pytest full | 391 PASS |
| ruff | PASS |
| CLI help/doctor/validate | PASS |
| Layer1 grid | skipped |

---

## L. Not implemented

ORB/GAP/CCI/VWAP runtime code, feature kernels, candidate YAML, Layer2/3, WFO, live/paper, PA grid/logic changes.

---

## M. Risks

- ORB needs small feature additions before QT-parity filters.
- Must not run multiple family implementations in parallel.
- Promotion still blocked until multi-window doctrine passes.

---

## N. Files changed

`docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`, `docs/PHASE_PLAN.md`, `docs/STRATEGY_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, status docs, `artifacts/strategy_family_onboarding_phase11/**`

---

## O. Artifact hygiene

- No parquet/cache/candidate YAML staged
- `CODEX_REVIEW.md` not modified by Cursor
- Phase 10 comparison CSV: use dedicated dry-run CSVs (`phase10_artifact_reading_note.md`)

---

## P. Decision (exactly one)

### `STRATEGY_FAMILY_ONBOARDING_COMPLETE_SECOND_FAMILY_SELECTED`

---

## Q. Recommended next step (exactly one)

### `DESIGN_GENERIC_FEATURE_FOUNDATION_FOR_SECOND_FAMILY`

Small generic features for ORB (`vwap_slope`, optional `orb_width_pct`) → then `IMPLEMENT_SECOND_STRATEGY_FAMILY_MVP`. **Not** promotion.

---

## R. Review reminder

After push: new **Codex** thread + **ChatGPT Pro** review. Cursor provisional steps are not final roadmap until reviewed.
