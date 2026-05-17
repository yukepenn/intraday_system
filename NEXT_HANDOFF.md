# NEXT_HANDOFF

Last updated: **2026-05-17** (`DESIGN_LAYER1_PA_CANDIDATE_SELECTION` / Phase **7** closed).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Phase 7 commit: see local `git log -1`
- HEAD should match **`origin/main`** after push (**non-force** only)

---

## B. Task scope (Phase `DESIGN_LAYER1_PA_CANDIDATE_SELECTION` / Phase 7)

- Authored Layer1 PA **candidate-selection design** (doctrine, schema, gates, multi-window policy).
- Implemented `reconstruct_resolved_config_for_combo` + pure `evaluate_selection_gates` (no promotion side effects).
- Dry-run selection on Phase **6c** 16-row sweep (**7** hold, **9** reject; top preview `combo_0015`).
- Sample candidate YAML under **`artifacts/` only** (SAMPLE ONLY).
- **Did not** write runtime candidate YAMLs, promote candidates, or implement Layer2/3.

---

## C. Candidate-selection doctrine

- Selection ≠ promotion; CSV/MD dry-run only in Phase 7.
- No single-window argmax; QQQ 2024H1 is diagnostic.
- Full resolved config required in future YAML; `params_json` is grid deltas only.
- See `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md` + `artifacts/layer1_pa_candidate_selection_design_phase7/selection_doctrine.*`

---

## D. Candidate YAML schema design

- Design schema `layer1_candidate_v2` documented; sample: `artifacts/.../sample_candidate_schema.yaml` (**NOT runtime**).
- Future root: `configs/candidates/l1_pa_controlled_v1/` (README only now).

---

## E. Resolved-config reconstruction

- `reconstruct_resolved_config_for_combo` in `intraday.layer1.grid` — **16/16** combos hash-verify against Phase 6c CSV.
- Recommend `resolved_config_json` in sweep CSV before promotion (`FIX_GRID_REPORTING_SCHEMA`).

---

## F. Selection gates / reject reasons

- Gate label: **`PA_L1_SELECTION_DESIGN_V1`**
- Hard: trades≥100, PF≥1.05, total_r>0, max_dd≤10R, reconstruction safe
- Soft: `single_window_only`, `stop_mode_dominance`, `needs_multi_window_validation`
- `promotion_allowed_now=false` for every dry-run row

---

## G. Dry-run selection table

| Metric | Value |
| --- | --- |
| Rows | 16 |
| Hard pass | 7 |
| HOLD | 7 |
| REJECT | 9 |
| Top preview | `combo_0015` (rank 1) |

Artifacts: `dry_run_selection_results.csv`, `dry_run_selection_summary.md`

---

## H. Multi-window / anti-overfit policy

- Design window: QQQ 2024H1 — `SINGLE_WINDOW_DESIGN_ONLY`
- Confirmation required before promotion — `NEEDS_CONFIRMATION_WINDOW`
- No Layer3/WFO/live in this phase

---

## I. Candidate root policy

- `configs/candidates/l1_pa_controlled_v1/README.md` — placeholder only
- No `.yaml` under `configs/candidates/` except README trees

---

## J. Grid reporting schema recommendation

- Implement reconstruction helper now (done).
- Add `resolved_config_json` per sweep row before runtime promotion.
- Promotion must verify `config_hash` equality.

---

## K. Tests / validation

| Check | Status |
| --- | --- |
| `compileall src` | PASS |
| `pytest` (`-q`) | **340 passed** |
| Ruff format/check | PASS |
| CLI (`doctor`, `validate structure`, `layer1 grid-inspect`) | PASS |
| Repeat `layer1 grid` | **Skipped** (Phase 6c reuse) |

---

## L. Explicit still-not-implemented

Real candidate YAML promotion, runtime promotion code, Layer2 candidate loading/router, Layer3 validation, GAP/CCI strategies, broad PA grids, WFO, management overlays, portfolio sizing, live/paper trading.

---

## M. Risks / blockers

| Risk | Mitigation |
| --- | --- |
| Single-window overfit | HOLD + confirmation window required |
| Stop-mode dominance | Warn on rolling_low-only hard-pass cluster |
| Serialization drift | Reconstruction helper + future `resolved_config_json` |

No hard HOLD for implementing dry-run CLI path.

---

## N. Files changed (high-level)

`docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`, `src/intraday/layer1/{grid,selection}.py`, tests, `configs/candidates/**/README.md`, `artifacts/layer1_pa_candidate_selection_design_phase7/**`, status docs.

---

## O. Artifact hygiene

- No parquet/cache/npy/candidate YAML under `configs/candidates/`
- Sample YAML artifacts-only with SAMPLE header

---

## P. Decision (exactly one)

### `LAYER1_PA_CANDIDATE_SELECTION_DESIGN_COMPLETE`

---

## Q. Recommended next step (exactly one)

### `IMPLEMENT_LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN`

(Repeatable CLI/report for selection dry-run — still no runtime YAML promotion.)
