# Phase 5 validation results

| command | exit | result | notes |
|---------|------|--------|-------|
| `python -m compileall -q src` | 0 | pass | |
| `python -m pytest -q` | 0 | pass | 257 passed |
| `python -m ruff format --check src tests` | 0 | pass | after format |
| `python -m ruff check src tests` | 0 | pass | |
| `python -m intraday.cli.main --help` | 0 | pass | strategies subcommand present |
| `python -m intraday.cli.main doctor` | 0 | pass | |
| `python -m intraday.cli.main validate structure` | 0 | pass | includes STRATEGY_CONTRACT.md |
| `python -m intraday.cli.main strategies list` | 0 | pass | pa_buy_sell_close_trend |
| `python -m intraday.cli.main strategies inspect ...` | 0 | pass | |
| `python -m intraday.cli.main strategies generate-smoke ...` | 0 | pass | QQQ 2024H1 local |
| `data validate-curated` QQQ 2024H1 | 0 | pass | local curated |
| `data load-bars` QQQ 2024H1 | 0 | pass | |
| `features inspect` pa_core_v1 | 0 | pass | |
