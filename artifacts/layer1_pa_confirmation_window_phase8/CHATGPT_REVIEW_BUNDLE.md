# Phase 8 — Layer1 PA confirmation window (partial)

## Git baseline

- Branch: `main`
- HEAD at task start: `dbeaddbe9c5e6a5ec1187f100fd9729df70f1f41` (matched `origin/main`)
- Prior handoff: `LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN_COMPLETE` → `RUN_LAYER1_PA_CONFIRMATION_WINDOW`
- Codex reviewed `dbeaddb`: **PASS_WITH_WARNINGS** (numeric parsing + output-root)

## Why Phase 8

Anti-overfit validation after Phase 7b dry-run: run the **same** 16-combo PA controlled grid on a non-overlapping QQQ window, then `layer1 select-dry-run`, and compare to design window (2024H1). No retuning, no promotion.

## CI help fix

- **Issue:** `test_select_dry_run_help` expected `sweep-results` in subprocess stdout (GitHub Actions).
- **Fix:** Typer `CliRunner` assertions + subprocess with `NO_COLOR=1`, `TERM=dumb`, `COLUMNS=120`; ANSI strip; verify `--sweep-results`, `--base-config`, `--grid-config`, `--output-root`.

## Numeric parsing hardening

- Added `parse_finite_float` / `parse_finite_int` in `selection.py`.
- Malformed / missing / `nan` / `inf` metrics → per-row `REJECT_FOR_SELECTION_DESIGN` with `invalid_metrics`; dry-run does not abort on one bad row.

## Output-root guardrail

- `validate_selection_dry_run_output_root`: repo-relative under `artifacts/` only; rejects absolute paths and `configs/candidates/`.

## Confirmation window

| Window | Status |
| --- | --- |
| QQQ 2024H2 (preferred) | **NO_DATA** |
| QQQ 2023H2 | **NO_DATA** |
| QQQ 2025H1 | **NO_DATA** |
| QQQ 2024H1 | design only (not used) |

`data validate-curated` failed: no parquet under `data/curated/bars_1m_rth`.

## Confirmation config

- `configs/layer1/controlled_pa_qqq_2024h2.yaml` — same grid/feature/execution as 2024H1; dates `2024-07-01`–`2024-12-31`.
- `grid-inspect`: **combo_count=16**.

## Confirmation grid / dry-run

**SKIPPED** — no curated data. No `confirmation_sweep_results.csv` produced.

## Design vs confirmation

**CONFIRMATION_SKIPPED_NO_DATA** — comparison deferred until local curated parquet exists.

## Promotion boundary

- `promotion_allowed_now=false` remains enforced in code and tests.
- No files under `configs/candidates/**/*.yaml`.

## Validation

- `pytest` smoke+unit: **352 passed**
- Ruff format/check: PASS
- `layer1 select-dry-run --help`: PASS
- Confirmation grid run: SKIP (no data)

## Decision

**`FIX_LOCAL_CURATED_DATA`**

## Recommended next step

**`FIX_LOCAL_CURATED_DATA`** — Curate QQQ 2024H2 (or nearest non-overlapping window), then re-run Phase 8 grid + dry-run + comparison without retuning.
