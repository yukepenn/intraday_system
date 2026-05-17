# Phase 7b validation results

| Command | Exit | Result | Notes |
| --- | --- | --- | --- |
| `python -m compileall -q src` | 0 | PASS | |
| `python -m pytest -q` | 0 | PASS | **371** passed |
| `python -m ruff format --check src tests` | 0 | PASS | |
| `python -m ruff check src tests` | 0 | PASS | |
| `python -m intraday.cli.main --help` | 0 | PASS | |
| `python -m intraday.cli.main doctor` | 0 | PASS | |
| `python -m intraday.cli.main validate structure` | 0 | PASS | |
| `layer1 grid-inspect` | 0 | PASS | 16 combos |
| `layer1 select-dry-run --help` | 0 | PASS | |
| `layer1 select-dry-run` (Phase 6c sweep) | 0 | PASS | 16 rows; promotion_allowed_now=false all |

Layer1 grid **not** rerun (Phase 6c artifact reuse per policy).
