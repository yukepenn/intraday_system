# Phase 1 — ChatGPT review bundle (GitHub-friendly)

## Git baseline

- Bootstrap baseline SHA: `f29babb49164bc4fa4766c2d13dab5834d5a1ce9`
- Phase 1 implements data foundation; see latest `main` commit after merge.

## Purpose

Establish trustworthy Layer 0 pipeline: raw parquet → audit → optional canonical layout → curated RTH parquet → `BarMatrix` + validation + CLI + tests.

## Architecture boundaries

No strategies, execution simulator, Layer1/2/3 runners, Numba fast path, or QT imports.

## Raw inventory / schema / timestamps

- Inventory: `artifacts/data_foundation_phase1/raw_data_inventory_cli.csv`
- Schema inspect JSON: `artifacts/data_foundation_phase1/raw_schema_inspect_stdout.json`
- Timestamp semantics: `configs/data/ibkr_qqq_1m.yaml` documents `ts_ny` + `bar_start`

## Canonicalization

- QQQ raw months migrated to canonical paths; SPY remains legacy.

## Curated normalization + BarMatrix

- QQQ 2024H1 curated: **48360** rows; validate clean; load-bars OK.

## CLI / tests

See `NEXT_HANDOFF.md` command list. `pytest` **55** green.

## Decision

`DATA_FOUNDATION_BARMATRIX_COMPLETE`

## Next step

`IMPLEMENT_REFERENCE_EXECUTION_ENGINE`
