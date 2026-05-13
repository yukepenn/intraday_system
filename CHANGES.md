# CHANGES

Curated changelog. Follows the spirit of [Keep a Changelog](https://keepachangelog.com/) with project-specific decision/phase entries.

## [Unreleased] – 2026-05-13

### Added

- Feat(data): raw parquet schema inspection, timestamp sampling helpers, guarded raw canonicalization, IBKR→curated normalization, curated BarMatrix loader, and `DataValidationReport` validation.
- Feat(cli): `data inspect`, `data canonicalize-raw`, `data normalize`, `data validate-curated`, `data load-bars`.
- Test(unit): data foundation tests (catalog edge cases, schema inspection, timestamps, normalize, loader, validate).
- Test(smoke): `data` CLI smoke paths.
- Docs(data): update `DATA_CONTRACT.md` for observed IBKR columns (`ts_ny`/`ts_utc`) and curated semantics.
- Docs(qt): sanitize `QT_REFERENCE_POLICY.md` to use `<qt-reference-root>` (no drive letters).
- Chore(gitignore): ignore raw/curated parquet by default; artifacts under `artifacts/data_foundation_phase1/`.
- Feat(repo): bootstrap intraday_system architecture skeleton (Phase 0/1A).
- Feat(core): introduce `BarMatrix`, `FeatureMatrix`, `SignalMatrix`, `TradeRecordArray` containers with shape validation.
- Feat(core): introduce deterministic `hash_config`, `hash_file`, `hash_paths_manifest` utilities.
- Feat(data): introduce raw-data catalog with canonical / legacy_qt_like / unknown layout classification.
- Feat(data): introduce `intraday data inventory` CLI command writing CSV + MD audit.
- Feat(layer1): introduce `grid.py` resolver with fixed/grid overlap check and full unit-test coverage.
- Feat(cli): introduce `intraday` CLI with `--help`, `doctor`, `validate structure`, `data inventory` (Typer + argparse fallback).
- Docs(architecture): add canonical layered architecture, data, config, cache, and execution contracts.
- Docs(workflow): describe plan -> execute -> review -> commit loop, hashing rules, and audit hygiene.
- Test(unit): add coverage for hashing, config, BarMatrix/FeatureMatrix/SignalMatrix, catalog inference, layer1.grid.
- Test(smoke): add coverage for import, CLI help/doctor/validate, and repo structure.
- Chore(ci): add GitHub Actions workflow running compile + lint (informational) + tests.

### Intentionally NOT included

- No strategy logic (PA/GAP/CCI signals).
- No execution simulator implementation (`reference.py` / `fast.py` are skeletons).
- No feature kernels beyond placeholders.
- No Layer1/Layer2/Layer3 runners.
- No curated parquet **committed** (normalization writes are local-only by `.gitignore`).
- Raw canonicalization is **optional**; QQQ raw months are now canonical locally; SPY remains legacy until migrated.
- No CSV/MD runtime config.

### Data tracking decision

- All 104 raw parquet files locally classified `safe_normal_git` (each `<1 MiB`, total `~34.3 MiB`).
- Git LFS NOT enabled by default; revisit if datasets grow.
- Raw parquet is **not** staged in this Phase 0/1A commit; the inventory manifest is committed.

### Decision

- `BOOTSTRAP_PHASE0_1A_COMPLETE` (pending push verification).
- Recommended next step: `IMPLEMENT_DATA_FOUNDATION_BARMATRIX_NORMALIZATION`.
