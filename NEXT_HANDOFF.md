# NEXT_HANDOFF

Last updated: **2026-05-17** (`REVIEW_PA_FEATURES_OR_LOGIC_AFTER_CONFIRMATION_FAILURE` / Phase **9**).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Task commit: see local `git log -1` after push
- HEAD should match **`origin/main`** after push (**non-force** only)

---

## B. Task scope (Phase 9)

- Diagnostic review of PA strategy logic, `pa_core_v1` features, 16-combo grid axes, and QQQ 2024H2 confirmation failure.
- **Did not** change PA strategy, features, execution, or rerun broad/confirmation grids.
- **Did not** promote candidates or write runtime candidate YAMLs.
- Produced `artifacts/pa_features_logic_review_after_confirmation_phase9/` review bundle.

---

## C. Artifact / hygiene preflight

- Phase 8b artifacts complete (16-row sweep + dry-run + design-vs-confirmation).
- `configs/candidates/**` — README only; no candidate YAML.
- `CODEX_REVIEW.md` not modified by Cursor.
- `.gitignore` extended for `local_run` / `_pytest` artifact dirs.
- `controlled_pa_qqq_2024h2.yaml` `artifact_root` documented as local-only (path unchanged; no grid rerun).

---

## D. Design-vs-confirmation failure decomposition

- Label: **CONFIRMATION_WEAKENS_SELECTION_DESIGN** (reconfirmed).
- Design rank-1 `combo_0015`: HOLD +8.88R (H1) → REJECT -9.08R (H2).
- Confirmation best `combo_0010`: +7.58R — still REJECT (`excessive_drawdown`, max_dd 19.88R).
- All **7** design HOLD rows → confirmation REJECT.
- Primary gate: `excessive_drawdown` on **16/16** (max_dd > 10.0R limit).

---

## E. Parameter-axis stability review

- **stop_mode:** rolling_low dominated H1 (+5.57R mean) → collapsed H2 (-12.21R); signal_low improved H2 (+0.60R mean). **Ranking reversed.**
- **target_r:** No stable H2 edge; signal_low×1.35 best interaction cell.
- **body_pct_min:** 0.56 relatively better both windows.
- **require_vwap_side:** Weak/noisy; not a stabilizer.

---

## F. Exit / skip / drawdown diagnostics

- STOP share ↑, TARGET share ↓ in H2 (aggregate exit distribution).
- Accepted trades 111–128 — comparable; not trade-count failure.
- Drawdown failures reflect economics + path risk, not gate-only artifact.

---

## G. PA feature / logic sufficiency review

- PA MVP over-relies on bar anatomy + simple trend score; no regime filter in strategy.
- `pa_core_v1` adequate for infrastructure; **not** sufficient for promotion without risk diagnostic and/or strategy use of regime context.
- Defer minimal feature diagnostic until after tiny risk grid refinement.

---

## H. Diagnostic next-step proposal

- **Recommended:** `REFINE_PA_GRID_AND_RERUN` — ≤12-combo diagnostic on risk path (`stop_mode`, `target_r`, `max_hold`), design window first, fresh holdout for confirmation.
- **Not recommended now:** promotion schema, broad grid, 2024H2 retuning, Layer2/3.

---

## I. Tests / validation

| Check | Status |
| --- | --- |
| `compileall src` | PASS |
| `pytest` smoke+unit | PASS (356) |
| `pytest` full | PASS (391) |
| Ruff format/check | PASS |
| CLI help/doctor/validate | PASS |
| `layer1 grid-inspect` 2024H2 | PASS (16 combos) |
| Grid / dry-run rerun | **skipped** (artifacts sufficient) |

---

## J. Explicit still-not-implemented

Real candidate YAML promotion, Layer2/3, WFO, live/paper, GAP/CCI, PA logic changes, feature kernel changes, broad PA grids, retuning from 2024H2 confirmation.

---

## K. Risks / blockers

| Risk | Status |
| --- | --- |
| H1 rolling_low false confidence | Address via diagnostic grid without rolling_low primary |
| Regime shift QQQ H2 | Fresh holdout required after tiny grid |
| Feature creep before risk test | Deferred per Phase 9 decision |

---

## L. Files changed (high-level)

`artifacts/pa_features_logic_review_after_confirmation_phase9/**`, `.gitignore`, `configs/layer1/controlled_pa_qqq_2024h2.yaml` (comment), status/docs.

---

## M. Artifact hygiene

- No parquet/cache/candidate YAML staged
- `CODEX_REVIEW.md` not modified by Cursor

---

## N. Decision (exactly one)

### `PA_FEATURE_LOGIC_REVIEW_COMPLETE`

Phase 9 diagnostic review complete. PA path not ready for promotion.

---

## O. Recommended next step (exactly one)

### `REFINE_PA_GRID_AND_RERUN`

Define and run a **small explicit diagnostic grid** (≈12 combos) on risk/stop/target/hold — design window first, then fresh non-overlapping confirmation. **Not** retuning from 2024H2 winners.
