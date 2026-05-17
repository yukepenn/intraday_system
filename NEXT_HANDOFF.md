# NEXT_HANDOFF

Last updated: **2026-05-17** (`RUN_LAYER1_PA_CONFIRMATION_WINDOW_AND_FIX_CI` / Phase **8** partial).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Task commit: see local `git log -1` after push
- HEAD should match **`origin/main`** after push (**non-force** only)

---

## B. Task scope (Phase 8)

- Fixed CI `select-dry-run --help` smoke test (CliRunner + robust subprocess env).
- Hardened finite numeric metric parsing (`parse_finite_float` / `parse_finite_int`).
- Enforced `artifacts/`-only `--output-root` for dry-run CLI.
- Prepared confirmation config `configs/layer1/controlled_pa_qqq_2024h2.yaml` (same grid, no retuning).
- **Did not** run confirmation grid or dry-run — **no local curated QQQ parquet** for 2024H2/2023H2/2025H1.
- **Did not** promote candidates or write runtime candidate YAMLs.

---

## C. CI select-dry-run help fix

- `tests/smoke/test_layer1_selection_cli.py`: Typer `CliRunner` + `NO_COLOR`/`TERM`/`COLUMNS` subprocess; ANSI strip; asserts `sweep-results`, `base-config`, `grid-config`, `output-root`.
- Artifacts: `artifacts/layer1_pa_confirmation_window_phase8/ci_cli_help_fix.*`

---

## D. Numeric metric parsing hardening

- `parse_finite_float`, `parse_finite_int`, `_parse_row_metrics` in `selection.py`
- Per-row `invalid_metrics` reject; malformed row does not abort full dry-run
- Tests: extended `test_layer1_selection_gates.py`, `test_layer1_selection_dry_run.py`

---

## E. Output-root guardrail

- `validate_selection_dry_run_output_root` — repo-relative under `artifacts/` only
- Rejects absolute paths and `configs/candidates/`
- Tests: `test_layer1_selection_reports.py`, CLI smoke rejection tests

---

## F. Confirmation window selection

| Window | Status |
| --- | --- |
| QQQ 2024H2 (preferred) | **NO_DATA** |
| QQQ 2023H2 | NO_DATA |
| QQQ 2025H1 | NO_DATA |

`data/curated/bars_1m_rth` empty in workspace.

---

## G. Confirmation config

- `configs/layer1/controlled_pa_qqq_2024h2.yaml`
- `grid-inspect`: **combo_count=16**
- Same feature/strategy grid/execution as 2024H1 design window

---

## H. Confirmation controlled grid run

**SKIPPED** — no curated data.

---

## I. Confirmation selection dry-run

**SKIPPED** — no confirmation sweep CSV.

---

## J. Design-vs-confirmation comparison

**CONFIRMATION_SKIPPED_NO_DATA** — deferred.

---

## K. Tests / validation

| Check | Status |
| --- | --- |
| `compileall src` | PASS |
| `pytest` smoke+unit (`-q`) | **352 passed** |
| Ruff format/check | PASS |
| `layer1 select-dry-run --help` | PASS |
| `data validate-curated` QQQ 2024H2 | FAIL (no data) |
| Confirmation `layer1 grid` | SKIP |

---

## L. Explicit still-not-implemented

Real candidate YAML promotion, Layer2/3, WFO, live/paper, broad PA grids, PA logic changes, confirmation grid execution (blocked on data).

---

## M. Risks / blockers

| Risk | Status |
| --- | --- |
| Missing curated QQQ confirmation window | **BLOCKER** |
| Single-window overfit | Unmitigated until confirmation run |

---

## N. Files changed (high-level)

`src/intraday/layer1/selection.py`, `src/intraday/cli/layer1_cmds.py`, `src/intraday/cli/main.py`, tests (`test_layer1_selection_*`), `configs/layer1/controlled_pa_qqq_2024h2.yaml`, `artifacts/layer1_pa_confirmation_window_phase8/**`, docs/status.

---

## O. Artifact hygiene

- No parquet/cache/candidate YAML staged
- `CODEX_REVIEW.md` not modified by Cursor

---

## P. Decision (exactly one)

### `FIX_LOCAL_CURATED_DATA`

(Not `LAYER1_PA_CONFIRMATION_WINDOW_COMPLETE` — confirmation grid not executed.)

---

## Q. Recommended next step (exactly one)

### `FIX_LOCAL_CURATED_DATA`

Curate QQQ 2024H2 (or nearest non-overlapping window), then re-run confirmation grid + dry-run + comparison **without retuning**.
