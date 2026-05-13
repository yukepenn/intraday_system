# Bootstrap summary (Phase 0/1A)

## Scope

Establish the clean intraday_system repo skeleton: docs, configs, core code, data inventory, CLI surface, tests. No strategy/execution/feature/Layer1/Layer2/Layer3 implementation work.

## Outcome

- Repo skeleton created end-to-end.
- 40 tests passing (smoke + unit).
- CLI works (`--help`, `doctor`, `validate structure`, `data inventory`).
- Ruff clean across `src/` and `tests/`.
- Data inventory generated for 104 parquet files (34.3 MiB total, 100% `legacy_qt_like`, 100% `safe_normal_git`).
- Canonical raw layout documented; bytes intentionally not moved (Phase 1 will handle).
- Git LFS intentionally not enabled (no file approaches large thresholds).
- Raw parquet not staged in this commit; manifest committed.

## Files created

See `structure_created.md` and `structure_created.csv`.

## Files NOT created (intentionally)

- No strategy base/grid YAMLs.
- No feature kernel implementations.
- No execution simulator implementations.
- No Layer1/Layer2/Layer3 runners.
- No curated parquet.
- No raw-layout canonicalization moves.
- No `intraday layer1`, `layer2`, `layer3`, `features`, `strategies` CLI subcommands.

## Decision

`BOOTSTRAP_PHASE0_1A_COMPLETE`.

## Recommended next step

`IMPLEMENT_DATA_FOUNDATION_BARMATRIX_NORMALIZATION` (Phase 1):

1. Implement `normalize_raw_ibkr_to_curated` (legacy- and canonical-aware).
2. Implement `load_bars_from_curated` -> `BarMatrix`.
3. Implement `validate_bar_data`.
4. Add unit + integration tests for QQQ 2024H1.
5. Decide whether to canonicalize raw layout this phase.
