# Phase 4 validation results

Run date: **2026-05-13** (local).

| Command | Exit | Result |
| --- | --- | --- |
| `python -m compileall -q src` | 0 | pass |
| `python -m pytest -q` | 0 | **216** passed |
| `python -m ruff format --check src tests` | 0 | pass |
| `python -m ruff check src tests` | 0 | pass |
| `python -m intraday.cli.main --help` | 0 | pass (includes `features`) |
| `python -m intraday.cli.main doctor` | 0 | pass |
| `python -m intraday.cli.main validate structure` | 0 | pass |
| `python -m intraday.cli.main features list` | 0 | JSON builtin groups |
| `python -m intraday.cli.main features inspect --config configs/features/pa_core_v1.yaml` | 0 | 22 columns, feature_hash |
| `python -m intraday.cli.main data validate-curated --symbol QQQ --start 2024-01-01 --end 2024-06-30 --data-root data/curated/bars_1m_rth` | 0 | 48360 rows |
| `python -m intraday.cli.main data load-bars ...` | 0 | BarMatrix summary |
| `python -m intraday.cli.main features build ... --no-cache` | 0 | 48360×22, `facb9338...` |

Notes: synthetic tests are CI truth; local QQQ 2024H1 smoke succeeded where curated data exists.
