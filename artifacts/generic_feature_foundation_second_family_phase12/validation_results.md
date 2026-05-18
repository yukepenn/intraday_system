# Validation results — Phase 12

| Command | Exit | Pass |
| --- | --- | --- |
| `python -m compileall -q src` | 0 | yes |
| `pytest -q tests/smoke tests/unit` | 0 | 368 passed |
| `pytest -q` (full) | 0 | 403 passed |
| `ruff format --check src tests` | 0 | yes (after format orb test file) |
| `ruff check src tests` | 0 | yes |
| `intraday.cli.main --help` | 0 | yes |
| `intraday.cli.main doctor` | 0 | yes |
| `intraday.cli.main validate structure` | 0 | yes |
| `features inspect orb_core_v1` | 0 | yes |
| `features build QQQ` | skipped | no local data |

Not run: Layer1 grid, select-dry-run, strategies, WFO, live/paper.
