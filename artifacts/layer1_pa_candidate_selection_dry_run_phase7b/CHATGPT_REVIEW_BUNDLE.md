# Phase 7b — Layer1 PA candidate-selection dry-run (review bundle)

## Git baseline

- Branch: `main`
- Pre-work HEAD: `4e394fea20ebb8f958f5a9c221d72af17e42b411` (matched `origin/main`)
- Remote: `https://github.com/yukepenn/intraday_system.git`

## Why Phase 7b was needed

Phase 7 completed selection **design** and a one-off dry-run script. Phase 7b turns that into a **repeatable** library + CLI path with strict CSV boolean parsing (Codex warning) and idempotent review artifacts — still **no** candidate YAML promotion.

## Codex review context

- Reviewed Cursor commit: `4e64e29` — `PASS_WITH_WARNINGS`
- Warning addressed: `bool("False")` on `config_reconstruction_safe` when reading CSV strings
- `CODEX_REVIEW.md` was **not** modified by Cursor (Codex-owned)

## Input normalization / bool parsing fix

- `intraday.layer1.selection.parse_bool_like` + `_config_reconstruction_gate`
- Invalid strings fail closed → `config_reconstruction_failed`
- Tests in `test_layer1_selection_gates.py` (parametrized true/false/yes/no/0/1/nonsense)

## Repeatable dry-run function

- `run_layer1_candidate_selection_dry_run` in `selection.py`
- Reads Phase 6c `sweep_results_review.csv`, reconstructs + hash-verifies each combo, evaluates `PA_L1_SELECTION_DESIGN_V1` gates
- Returns `SelectionDryRunResult` with pass/hold/reject counts

## Dry-run artifact writer

- `write_layer1_candidate_selection_dry_run_artifacts` in `selection_reports.py`
- Writes `dry_run_selection_results.*`, rejects, warnings, summary CSV/MD
- Idempotent overwrite; `promotion_allowed_now=false` on every row

## Layer1 select-dry-run CLI

```bash
python -m intraday.cli.main layer1 select-dry-run \
  --sweep-results artifacts/layer1_pa_grid_review_phase6c/sweep_results_review.csv \
  --base-config configs/strategies/base/pa_buy_sell_close_trend.yaml \
  --grid-config configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml \
  --output-root artifacts/layer1_pa_candidate_selection_dry_run_phase7b
```

Sweep CSV is **audit input only**, not runtime trading config.

## Current 16-row grid dry-run result

| Metric | Value |
| --- | --- |
| row_count | 16 |
| hold | 7 |
| reject | 9 |
| pass | 0 |
| reconstruction pass | 16 |
| promotion_allowed_now | false (all) |
| top preview | combo_0015 (rank 1) |

## Promotion boundary

- No files under `configs/candidates/**/*.yaml` (except README trees)
- `candidate_id_preview` is display-only
- HOLD rows are review-eligible only, not promoted

## Validation results

- `pytest`: **371** passed
- Ruff format/check: PASS
- CLI: doctor, validate structure, grid-inspect, select-dry-run — PASS
- See `validation_results.md`

## Explicit non-implemented items

Real candidate YAML promotion, runtime promotion code, Layer2 loading/router, Layer3 validation, GAP/CCI strategies, broad PA grids, WFO, management overlays, portfolio sizing, live/paper trading.

## Risks / blockers

- Single-window overfit (QQQ 2024H1 only)
- Stop-mode dominance in hard-pass cluster (rolling_low)
- Future promotion still needs `resolved_config_json` in sweep reporting or pinned reconstruction manifest

## Decision

**`LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN_COMPLETE`**

## Recommended next step

**`RUN_LAYER1_PA_CONFIRMATION_WINDOW`**
