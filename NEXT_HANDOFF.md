# NEXT_HANDOFF

Last updated: **2026-05-17** (`FIX_LOCAL_CURATED_DATA_AND_RERUN_CONFIRMATION_WINDOW` / Phase **8b**).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Task commit: see local `git log -1` after push
- HEAD should match **`origin/main`** after push (**non-force** only)

---

## B. Task scope (Phase 8b)

- Repaired local curated QQQ **2024H2** from raw IBKR (non-overlapping vs design 2024H1).
- Preflight: selection report Markdown metric hardening; output-root `.` rejection; handoff wording fix.
- Ran confirmation controlled grid (16 combos, same grid, no retuning).
- Ran confirmation `select-dry-run` (review-only; `promotion_allowed_now=false` all rows).
- Design-vs-confirmation comparison: **CONFIRMATION_WEAKENS_SELECTION_DESIGN**.
- **Did not** promote candidates or write runtime candidate YAMLs.

---

## C. Preflight repairs

- `selection_reports.py`: `_format_metric_for_md` — malformed/non-finite → `invalid` in MD table.
- `validate_selection_dry_run_output_root`: rejects `.`, empty, whitespace-only paths.
- Tests: malformed metric artifact writer; output-root edge cases.
- Artifacts: `artifacts/layer1_pa_confirmation_data_repair_phase8b/preflight_repairs.*`

---

## D. Local raw/curated confirmation data inventory

| Item | Status |
| --- | --- |
| Raw QQQ | 104 months (canonical IBKR layout) |
| Curated before | 2024H1 only (design window) |
| Curated added | 2024H2 (Jul–Dec 2024) |
| Chosen window | **QQQ 2024H2** (preferred, non-overlapping) |

Prior Phase 8 wording “curated root empty” was inaccurate — blocker was **missing non-overlapping confirmation-window parquet**.

---

## E. Confirmation normalization / validation

- Normalize dry-run + write: **49380** rows, 6 months, warnings `short_sessions_count=3`
- `validate-curated` QQQ 2024H2: **PASS** (0 errors)
- `load-bars`: 128 sessions, `data_hash` verified
- Local parquet: **not committed**

---

## F. Confirmation config

- `configs/layer1/controlled_pa_qqq_2024h2.yaml`
- Same feature / strategy base / controlled grid / execution as 2024H1
- `grid-inspect`: **combo_count=16**

---

## G. Confirmation controlled grid run

- **16/16** combos, reference execution
- Best `total_r`: **combo_0010** → 7.58
- Best `profit_factor_r`: **combo_0010** → 1.11
- Accepted trades per combo: 111–128
- Artifacts: `artifacts/layer1_pa_confirmation_data_repair_phase8b/confirmation_*`

---

## H. Confirmation selection dry-run

- Rows: **16** | PASS: **0** | HOLD: **0** | REJECT: **16**
- Reconstruction pass: **16/16**
- `promotion_allowed_now=false` for every row
- Common reject: `excessive_drawdown` (all 16)

---

## I. Design-vs-confirmation comparison

- Label: **CONFIRMATION_WEAKENS_SELECTION_DESIGN**
- Design rank-1 preview `combo_0015` (HOLD, +8.88R H1) → REJECT on H2 (-9.08R)
- All 7 design HOLD rows → REJECT on confirmation gates
- No retuning performed

---

## J. Tests / validation

| Check | Status |
| --- | --- |
| `compileall src` | PASS |
| `pytest` smoke+unit | PASS (see commit) |
| Ruff format/check | PASS |
| Confirmation grid + dry-run | PASS |
| `promotion_allowed_now=true` anywhere | **none** |

---

## K. Explicit still-not-implemented

Real candidate YAML promotion, Layer2/3, WFO, live/paper, broad PA grids, PA logic changes, retuning after confirmation.

---

## L. Risks / blockers

| Risk | Status |
| --- | --- |
| Single-window overfit | Mitigated by confirmation run; design holds did not replicate |
| Drawdown gate sensitivity | All confirmation rows hit `excessive_drawdown` |

---

## M. Files changed (high-level)

`selection_reports.py`, `layer1_cmds.py`, tests, `artifacts/layer1_pa_confirmation_data_repair_phase8b/**`, docs/status.

---

## N. Artifact hygiene

- No parquet/cache/candidate YAML staged
- `CODEX_REVIEW.md` not modified by Cursor

---

## O. Decision (exactly one)

### `LAYER1_PA_CONFIRMATION_WINDOW_COMPLETE`

Confirmation workflow executed end-to-end on QQQ 2024H2 without retuning.

---

## P. Recommended next step (exactly one)

### `REVIEW_PA_FEATURES_OR_LOGIC`

Confirmation weakened design-window selection previews; review PA features/logic before promotion schema or grid refinement — **not** real candidate promotion.
