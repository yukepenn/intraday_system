# Validation results (Phase 0/1A)

All checks executed locally on `2026-05-12`.

## `python -m compileall -q src`

- Exit code: `0`
- No output (success).

## `python -m pytest -q`

- Result: **40 passed in ~2.0s**
- Tests:
  - `tests/smoke/test_import.py` (3)
  - `tests/smoke/test_cli_help.py` (3)
  - `tests/smoke/test_repo_structure.py` (2)
  - `tests/unit/test_hashing.py` (5)
  - `tests/unit/test_config.py` (5)
  - `tests/unit/test_core_arrays.py` (7)
  - `tests/unit/test_data_catalog.py` (5)
  - `tests/unit/test_layer1_grid.py` (10)

## `python -m ruff check src tests`

- Result: `All checks passed!`

## `python -m intraday.cli.main --help`

- Exit code: `0`
- Shows root help with `doctor`, `data`, `validate` subcommands.

## `python -m intraday.cli.main doctor`

- Exit code: `0`
- Reports:
  - package version: `0.1.0a0`
  - python: `3.11.4`
  - repo root resolved
  - all 9 dependencies importable: numpy, pandas, yaml, pyarrow, polars, pydantic, typer, rich, numba
  - required paths exist: `configs`, `configs/data`, `data/raw/ibkr`, `data/cache`, `artifacts/bootstrap`
  - `data/cache` ignored: `True`

## `python -m intraday.cli.main validate structure`

- Exit code: `0`
- "all required paths present (6 dirs + 27 files)"

## `python -m intraday.cli.main data inventory --root data/raw/ibkr --output artifacts/bootstrap/phase0_1a/raw_data_inventory.csv`

- Exit code: `0`
- Wrote `raw_data_inventory.csv` and `raw_data_inventory.md`.
- 104 files, 34.264 MiB total, 100% `legacy_qt_like`, 100% `safe_normal_git`.

## Forbidden-staged check (after staging)

Checked using PowerShell:

```
git diff --cached --name-only | Select-String -Pattern "data/cache|artifacts/./local|artifacts/./tmp|.npy|.npz|.memmap|pycache|.pytest_cache|.ruff_cache"
```

Expected: empty match set. Recorded at commit time.

## Tracked-files forbidden check

```
git ls-files | Select-String -Pattern "data/cache|artifacts/./local|artifacts/./tmp|.npy|.npz|.memmap|pycache|.pytest_cache|.ruff_cache"
```

Expected: empty match set after the Phase 0/1A commit.
