# Phase 10 validation results

| command | exit | pass/fail | notes |
| --- | --- | --- | --- |
| `python -m compileall -q src` | 0 | PASS | |
| `python -m pytest -q tests/smoke tests/unit` | 0 | PASS | 356 passed |
| `python -m pytest -q` | 0 | PASS | 391 passed |
| `python -m ruff format --check src tests` | 0 | PASS | |
| `python -m ruff check src tests` | 0 | PASS | |
| `python -m intraday.cli.main --help` | 0 | PASS | |
| `python -m intraday.cli.main doctor` | 0 | PASS | |
| `python -m intraday.cli.main validate structure` | 0 | PASS | |
| `data validate-curated` QQQ H1/H2 | 0 | PASS | see data_validation_summary |
| `layer1 grid-inspect` H1/H2 | 0 | PASS | combo_count=12 |
| `layer1 grid` H1/H2 | 0 | PASS | see design/confirmation sweep |
| `layer1 select-dry-run` H1/H2 | 0 | PASS | promotion_allowed_now=false all |

All rows: `promotion_allowed_now=false`. No candidate YAML created.
