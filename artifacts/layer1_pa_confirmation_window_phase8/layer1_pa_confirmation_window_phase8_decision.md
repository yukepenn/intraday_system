# Phase 8 decision

**Decision:** `FIX_LOCAL_CURATED_DATA`

**Recommended next step:** `FIX_LOCAL_CURATED_DATA`

## Rationale

Phase 8 repaired CI help coverage, hardened finite numeric metric parsing, and enforced `artifacts/`-only dry-run output roots. The confirmation-window controlled grid and selection dry-run were **not** executed because no QQQ curated 1m RTH parquet exists locally for QQQ 2024H2, 2023H2, or 2025H1 (non-overlapping with design window 2024H1).

Confirmation config `configs/layer1/controlled_pa_qqq_2024h2.yaml` was prepared (same grid/strategy/feature/execution as design window; dates only). `layer1 grid-inspect` reports **16** combos.

Do **not** claim `LAYER1_PA_CONFIRMATION_WINDOW_COMPLETE` until curated data exists and grid + dry-run artifacts are produced.

## Completed in this phase

- CI `select-dry-run --help` smoke test hardening (CliRunner + subprocess)
- `parse_finite_float` / `parse_finite_int` fail-closed per row
- `validate_selection_dry_run_output_root` under `artifacts/`
- Tests: gates, dry-run, reports, CLI smoke

## Explicit non-goals (unchanged)

No candidate promotion, no runtime candidate YAML, no Layer2/3, no WFO, no live/paper, no PA logic/grid retuning.
