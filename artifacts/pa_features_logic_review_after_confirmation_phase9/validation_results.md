# Phase 9 validation results

| Command | Exit | Pass/Fail | Notes |
| --- | --- | --- | --- |
| `python -m compileall -q src` | 0 | PASS | |
| `python -m pytest -q tests/smoke tests/unit` | 0 | PASS | 356 passed |
| `python -m pytest -q` | 0 | PASS | 391 passed |
| `python -m ruff format --check src tests` | 0 | PASS | 184 files |
| `python -m ruff check src tests` | 0 | PASS | |
| `python -m intraday.cli.main --help` | 0 | PASS | |
| `python -m intraday.cli.main doctor` | 0 | PASS | |
| `python -m intraday.cli.main validate structure` | 0 | PASS | |
| `python -m intraday.cli.main layer1 grid-inspect --config configs/layer1/controlled_pa_qqq_2024h2.yaml` | 0 | PASS | combo_count=16 |

## Skipped (by design)

- `layer1 grid` / `select-dry-run` rerun
- WFO / live / paper
- Broad PA grids
