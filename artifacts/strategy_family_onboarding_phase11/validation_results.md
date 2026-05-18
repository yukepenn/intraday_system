# Phase 11 validation results

| Command | Exit | Result | Notes |
| --- | ---: | --- | --- |
| `python -m compileall -q src` | 0 | PASS | |
| `python -m pytest -q tests/smoke tests/unit` | 0 | PASS | 356 passed |
| `python -m pytest -q` | 0 | PASS | 391 passed |
| `python -m ruff format --check src tests` | 0 | PASS | 184 files formatted |
| `python -m ruff check src tests` | 0 | PASS | |
| `python -m intraday.cli.main --help` | 0 | PASS | |
| `python -m intraday.cli.main doctor` | 0 | PASS | |
| `python -m intraday.cli.main validate structure` | 0 | PASS | |

## Skipped (by design)

- `layer1 grid` / `grid-inspect` / `select-dry-run` — no Layer1 runs in design phase
- Layer2/3, WFO, live/paper
- PA or ORB research grids
