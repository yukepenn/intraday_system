# Phase 11 — Strategy family onboarding (ChatGPT review bundle)

**Repo:** https://github.com/yukepenn/intraday_system  
**Task:** `DESIGN_STRATEGY_FAMILY_ONBOARDING_AND_SECOND_MVP_SELECTION`  
**Type:** design-only — no runtime strategy/feature implementation

---

## A. Git baseline

| Item | Value |
| --- | --- |
| Branch | `main` |
| Pre-work HEAD | `fab6c6f` (matched `origin/main`) |
| Codex last reviewed | `17bd54e` (Phase 10); verdict `PASS_WITH_WARNINGS` |
| `CODEX_REVIEW.md` | Not modified by Cursor |

---

## B. Why Phase 11 was needed

Phase 10 held the PA path: risk-only diagnostic did not restore cross-window stability (0/12 combos positive in both H1/H2; all dry-run REJECT). Continuing PA grids risks overfit. The master plan is a **multi-strategy candidate factory**; Phase 11 defines how new families enter the same pipeline PA validated.

---

## C. PA path hold

- PA MVP = successful **canary vertical slice** (data → features → signals → execution → Layer1 → dry-run).
- **Not promotion-ready** after Phases 8b–10.
- **Do not** refine PA grids while onboarding ORB.
- Evidence: `artifacts/pa_risk_grid_diagnostic_phase10/diagnostic_conclusion.md`, `pa_path_hold_summary.md`.

---

## D. Onboarding interface inventory

**Ready:** `StrategyDef`, registry, loader, `SignalMatrix`, Layer1 smoke/grid/dry-run, PA configs.  
**Missing:** non-PA strategies, family templates (now in contract), `indicators`/`levels` features.  
Detail: `onboarding_interface_inventory.md`.

---

## E. QT reference

- Inspected: `QT/src/features/`, `QT/src/strategies/strategy/`
- **No import, no port, no runtime dependency**
- ORB: `orb_continuation.py` — logic reference for second family
- GAP/CCI need `levels` / CCI kernels not in intraday yet  
Detail: `qt_reference_inventory.md`, `qt_migration_guardrails.md`.

---

## F. Feasibility matrix

| Family | Status |
| --- | --- |
| **ORB continuation** | **READY_FOR_MVP_DESIGN** (selected) |
| GAP | NEEDS_GENERIC_FEATURE_FOUNDATION |
| CCI | NEEDS_GENERIC_FEATURE_FOUNDATION |
| VWAP reclaim | NEEDS_GENERIC_FEATURE_FOUNDATION |
| PA refine | HOLD |

No profitability claims. Selection = pipeline fit + feature readiness.

CSV: `strategy_family_feasibility_matrix.csv`

---

## G. Feature requirements audit

ORB reuses `pa_core_v1` (ORB, VWAP, ATR). Gaps: `vwap_slope_5` (recommended generic), optional `orb_width_pct`. Breakout timing uses `BarMatrix.minute` + ORB columns (strategy logic). GAP/CCI/VWAP deferred for missing levels/CCI/session features.

CSV: `feature_requirements_audit.csv`

---

## H. Onboarding contract

**Doc:** [`docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`](../../docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md)

Requires per family: strategy module, base/grid/metadata YAML, unit tests, Layer1 smoke → grid → dry-run, review artifacts. Prohibits: candidate YAML during MVP, Layer2/3, WFO, live/paper, QT import, strategy-specific feature hacks.

---

## I. Selected second family

**ORB continuation** (`orb_continuation`) — long-only MVP, QT reference `orb_continuation.py`, future phase `IMPLEMENT_ORB_STRATEGY_FAMILY_MVP`.

Alternatives deferred: GAP (levels), CCI (indicator kernel), VWAP (session priors), PA (held).

Detail: `selected_second_family_decision.md`

---

## J. Future implementation plan

Phases A–D in `second_family_implementation_plan.md` (feature mini-foundation → strategy → Layer1 → diagnostics). **Not executed in Phase 11.**

---

## K. Validation

| Check | Result |
| --- | --- |
| compileall | PASS |
| pytest smoke+unit | 356 PASS |
| pytest full | 391 PASS |
| ruff | PASS |
| CLI help/doctor/validate | PASS |
| Layer1 grid | skipped (design phase) |

`validation_results.csv`

---

## L. Explicit non-implemented

- Runtime ORB/GAP/CCI/VWAP strategy code
- New feature kernels
- Runtime candidate YAML
- Layer2/3, WFO, live/paper
- PA logic/grid changes
- Layer1 grid runs
- `CODEX_REVIEW.md` edits

---

## M. Risks / blockers

| Risk | Mitigation |
| --- | --- |
| ORB feature gaps | Mini foundation before signal MVP |
| Single-family overfit | PA held; one new family at a time |
| QT architecture creep | Guardrails + contract |
| Premature promotion | Same dry-run gates as PA |

---

## N. Decision

**`STRATEGY_FAMILY_ONBOARDING_COMPLETE_SECOND_FAMILY_SELECTED`**

---

## O. Cursor provisional next step

**`DESIGN_GENERIC_FEATURE_FOUNDATION_FOR_SECOND_FAMILY`**

Then **`IMPLEMENT_SECOND_STRATEGY_FAMILY_MVP`** for `orb_continuation`.

---

## P. Final review ownership

User + **ChatGPT Pro** + **Codex** after push. Cursor does not set production roadmap alone.

---

## Artifact index

| File | Purpose |
| --- | --- |
| `phase11_summary.md` | Executive summary |
| `strategy_family_onboarding_phase11_decision.md` | Decision record |
| `SOURCE_MAP.csv` | File map |
| `chatgpt_key_tables.csv` | Key metrics |
