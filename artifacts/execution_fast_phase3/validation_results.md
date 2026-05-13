# Phase 3 validation results

Date: 2026-05-13.

| Command | Exit | Result |
| --- | ---: | --- |
| `python -m compileall -q src` | 0 | pass |
| `python -m pytest -q` | 0 | pass, **171** tests |
| `python -m ruff format --check src tests` | 0 | pass |
| `python -m ruff check src tests` | 0 | pass |
| `python -m intraday.cli.main --help` | 0 | pass |
| `python -m intraday.cli.main doctor` | 0 | pass |
| `python -m intraday.cli.main validate structure` | 0 | pass |
| `python -m intraday.cli.main data validate-curated --symbol QQQ --start 2024-01-01 --end 2024-06-30 --data-root data/curated/bars_1m_rth` | 0 | pass (local curated present) |
| `python -m intraday.cli.main data load-bars --symbol QQQ --start 2024-01-01 --end 2024-06-30 --data-root data/curated/bars_1m_rth` | 0 | pass |

Core Phase 3 acceptance is **synthetic parity**; data smoke confirms Layer 0 CLI unchanged.
