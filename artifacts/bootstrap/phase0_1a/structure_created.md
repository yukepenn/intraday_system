# Structure created (Phase 0/1A)

This document enumerates the directories and notable files added by Phase 0/1A.

## Top-level files

- `pyproject.toml`
- `README.md`
- `Makefile`
- `.gitignore`
- `.gitattributes`
- `PROJECT_STATUS.md`
- `PROGRESS.md`
- `CHANGES.md`
- `NEXT_HANDOFF.md`

## `docs/`

- `ARCHITECTURE.md`
- `PROJECT_STRUCTURE.md`
- `DATA_CONTRACT.md`
- `CONFIG_CONTRACT.md`
- `CACHE_CONTRACT.md`
- `EXECUTION_CONTRACT.md`
- `LAYER_FLOW.md`
- `PHASE_PLAN.md`
- `QT_REFERENCE_POLICY.md`
- `DEVELOPMENT_WORKFLOW.md`
- `DESIGN_BASELINE.md`

## `configs/`

- `README.md`
- `data/data_roots.yaml`, `ibkr_qqq_1m.yaml`, `symbols.yaml`, `sessions_us_equity.yaml`
- `execution/intraday_default.yaml`
- `features/pa_core_v1.yaml`, `gap_core_v1.yaml`, `cci_core_v1.yaml`
- `strategies/{base,grids,metadata}/README.md`
- `candidates/README.md`
- `layer1/README.md`, `layer2/README.md`, `layer3/README.md`
- `reports/default_report.yaml`

## `data/`

- `README.md`, `raw/README.md`, `raw/ibkr/README.md`, `curated/README.md`, `cache/README.md`

## `artifacts/`

- `README.md`
- `bootstrap/phase0_1a/` audit + decision bundle (this doc lives here)

## `src/intraday/`

Implemented (non-skeleton):

- `core/`: `types.py`, `arrays.py`, `hashing.py`, `config.py`, `paths.py`, `errors.py`, `registry.py`, `constants.py`
- `data/`: `catalog.py`, `schema.py`, `sessions.py`, `calendar.py`
- `execution/`: `spec.py`, `intent.py`, `records.py`, `cost.py` (partial)
- `management/modes.py`
- `layer1/grid.py`, `layer1/candidate.py` (dataclass)
- `cli/main.py` (Typer + argparse fallback)
- `utils/`: `io.py`, `yaml.py`, `logging.py`, `time.py`

Skeleton-only (raises `NotImplementedError` or empty stubs):

- `data/loader.py`, `data/normalize.py`, `data/validate.py` (parts implemented; loader/normalize raise)
- `features/` (engine, store, specs, cache_key, base, registry, kernels/*)
- `strategies/{base,registry,loader,contracts,config_validation,pa,gap,cci,vwap,orb}`
- `execution/{reference,fast,materialize,parity}`
- `management/{fixed_r,scaleout,trailing,no_followthrough,builders}`
- `backtest/{engine,sweep,metrics,records,result_store,explain}`
- `layer1/{config,runner,selection,promotion,reports}`
- `layer2/*`
- `layer3/*`
- `portfolio/*`
- `reports/*`
- `research/*`

## `tests/`

- `unit/test_hashing.py`, `test_config.py`, `test_core_arrays.py`, `test_data_catalog.py`, `test_layer1_grid.py`
- `smoke/test_import.py`, `test_cli_help.py`, `test_repo_structure.py`
- `parity/`, `integration/`, `regression/` — README placeholders only

## `notebooks/`

- `exploration_only/README.md`

## `scripts/`

- `README.md`, `validate_repo.py`, `bootstrap_from_qt.py` (placeholder)

## `.github/workflows/`

- `ci.yml`
