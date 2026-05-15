# Validation results (Phase 6c final pass)

| Command | Exit | Pass/Fail |
|---------|------|-----------|
| `python -m compileall -q src` | 0 | pass |
| `python -m pytest -q tests/smoke tests/unit` | 0 | pass |
| `python -m pytest -q` | 0 | pass |
| `python -m ruff format --check src tests` | 0 | pass |
| `python -m ruff check src tests` | 0 | pass |
| `python -m intraday.cli.main --help` | 0 | pass |
| `python -m intraday.cli.main doctor` | 0 | pass |
| `python -m intraday.cli.main validate structure` | 0 | pass |

Data/smoke/grid commands repeated per Phase 10 checklist with same outcomes as recorded in `local_data_check.md`, `prior_layer_smoke.md`, `local_grid_run.md`.
