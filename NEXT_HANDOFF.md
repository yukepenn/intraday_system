# NEXT_HANDOFF

Last updated: **2026-05-17** (`IMPLEMENT_LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN` / Phase **7b** closed).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Phase 7b commit: see local `git log -1` after push
- HEAD should match **`origin/main`** after push (**non-force** only)

---

## B. Task scope (Phase `IMPLEMENT_LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN` / Phase 7b)

- Fixed CSV/string boolean parsing for `config_reconstruction_safe` (`parse_bool_like`, fail closed).
- Implemented `run_layer1_candidate_selection_dry_run` + `SelectionDryRunResult`.
- Implemented `write_layer1_candidate_selection_dry_run_artifacts`.
- Added CLI `layer1 select-dry-run` (reads Phase 6c sweep as audit input).
- Ran dry-run on **16**-row Phase 6c sweep; wrote `artifacts/layer1_pa_candidate_selection_dry_run_phase7b/`.
- **Did not** promote candidates, write runtime candidate YAMLs, or implement Layer2/3.

---

## C. Codex review context

- Codex reviewed Phase 7 commit `4e64e29` — **PASS_WITH_WARNINGS**
- Warning fixed in 7b: `bool("False")` truthiness on reconstruction gate from CSV
- **`CODEX_REVIEW.md` not modified by Cursor** (Codex-owned)

---

## D. Input normalization / boolean parsing fix

- `intraday.layer1.selection.parse_bool_like` + `_config_reconstruction_gate`
- Tests: `tests/unit/test_layer1_selection_gates.py` (parametrized + invalid string fail closed)
- Artifact matrix: `artifacts/.../input_normalization_fix.*`

---

## E. Repeatable dry-run function

- `run_layer1_candidate_selection_dry_run` — reconstruct, hash-verify, gate evaluate, rank PASS/HOLD
- `promotion_allowed_now=false` on every decision
- Tests: `tests/unit/test_layer1_selection_dry_run.py`

---

## F. Dry-run artifact writer

- `write_layer1_candidate_selection_dry_run_artifacts` in `selection_reports.py`
- Outputs: `dry_run_selection_results.csv`, rejects, warnings, summaries (CSV + MD)
- Tests: `tests/unit/test_layer1_selection_reports.py`

---

## G. Layer1 select-dry-run CLI

```bash
python -m intraday.cli.main layer1 select-dry-run \
  --sweep-results artifacts/layer1_pa_grid_review_phase6c/sweep_results_review.csv \
  --base-config configs/strategies/base/pa_buy_sell_close_trend.yaml \
  --grid-config configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml \
  --output-root artifacts/layer1_pa_candidate_selection_dry_run_phase7b
```

- Tests: `tests/smoke/test_layer1_selection_cli.py`

---

## H. Current 16-row grid dry-run result

| Metric | Value |
| --- | --- |
| Rows | 16 |
| Hard pass | 7 |
| HOLD | 7 |
| REJECT | 9 |
| Reconstruction pass | 16 |
| Top preview | `combo_0015` (rank 1) |
| promotion_allowed_now | false (all rows) |

---

## I. Tests / validation

| Check | Status |
| --- | --- |
| `compileall src` | PASS |
| `pytest` (`-q`) | **371 passed** |
| Ruff format/check | PASS |
| CLI (`doctor`, `validate structure`, `layer1 grid-inspect`, `select-dry-run`) | PASS |
| Repeat `layer1 grid` | **Skipped** (Phase 6c reuse) |

---

## J. Explicit still-not-implemented

Real candidate YAML promotion, runtime promotion code, Layer2 candidate loading/router, Layer3 validation, GAP/CCI strategies, broad PA grids, WFO, management overlays, portfolio sizing, live/paper trading.

---

## K. Risks / blockers

| Risk | Mitigation |
| --- | --- |
| Single-window overfit | HOLD + confirmation window required |
| Stop-mode dominance | Warn on rolling_low hard-pass cluster |
| Serialization drift | Reconstruction helper + future `resolved_config_json` |

No hard HOLD for confirmation-window work.

---

## L. Files changed (high-level)

`src/intraday/layer1/{selection,selection_reports}.py`, `src/intraday/cli/{layer1_cmds,main}.py`, tests (`test_layer1_selection_*`), docs (`LAYER1_CANDIDATE_SELECTION_CONTRACT`, `LAYER1_CONTRACT`, `PHASE_PLAN`), `artifacts/layer1_pa_candidate_selection_dry_run_phase7b/**`, status docs.

---

## M. Artifact hygiene

- No parquet/cache/npy/candidate YAML under `configs/candidates/`
- Dry-run outputs are CSV/MD review only
- `CODEX_REVIEW.md` not staged by Cursor

---

## N. Decision (exactly one)

### `LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN_COMPLETE`

---

## O. Recommended next step (exactly one)

### `RUN_LAYER1_PA_CONFIRMATION_WINDOW`

(Out-of-sample window before promotion schema or runtime YAML writes.)
