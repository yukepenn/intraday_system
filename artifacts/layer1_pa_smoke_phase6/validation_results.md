# Phase 6 validation results

Recorded after implementation; host: Windows, Python 3.11.

| Command | Exit | Pass/Fail | Notes |
| --- | --- | --- | --- |
| `python -m compileall -q src` | 0 | pass | |
| `python -m pytest -q` | 0 | pass | **286** passed |
| `python -m ruff format --check src tests` | 0 | pass | |
| `python -m ruff check src tests` | 0 | pass | |
| `python -m intraday.cli.main --help` | 0 | pass | Typer |
| `python -m intraday.cli.main doctor` | 0 | pass | |
| `python -m intraday.cli.main validate structure` | 0 | pass | 32 required files |
| `python -m intraday.cli.main layer1 --help` | 0 | pass | |
| `python -m intraday.cli.main layer1 inspect --config configs/layer1/smoke_pa_qqq_2024h1.yaml` | 0 | pass | |
| `python -m intraday.cli.main layer1 run --config configs/layer1/smoke_pa_qqq_2024h1.yaml` | 0 | pass | Local QQQ curated present |
| `python -m intraday.cli.main data validate-curated --symbol QQQ --start 2024-01-01 --end 2024-06-30 --data-root data/curated/bars_1m_rth` | 0 | pass | 48360 rows |
| `python -m intraday.cli.main features inspect --config configs/features/pa_core_v1.yaml` | 0 | pass | feature_hash recorded |
| `python -m intraday.cli.main strategies inspect --strategy pa_buy_sell_close_trend --config configs/strategies/base/pa_buy_sell_close_trend.yaml` | 0 | pass | |

If curated QQQ is missing locally, rely on synthetic unit/smoke tests; Phase 6 can still complete with documented skip.
