# Commands run (Phase 1B)

```
python -m compileall -q src
python -m pytest -q
python -m ruff format --check src tests
python -m ruff check src tests
python -m intraday.cli.main --help
python -m intraday.cli.main doctor
python -m intraday.cli.main validate structure
python -m intraday.cli.main data inventory --root data/raw/ibkr --output artifacts/data_foundation_phase1b/raw_data_inventory_cli_final.csv
python -m intraday.cli.main data inspect --dataset configs/data/ibkr_qqq_1m.yaml --symbol QQQ
python -m intraday.cli.main data normalize --dataset configs/data/ibkr_qqq_1m.yaml --symbol QQQ --start 2024-01-01 --end 2024-06-30
python -m intraday.cli.main data timestamp-audit --dataset configs/data/ibkr_qqq_1m.yaml --symbol QQQ --output-dir artifacts/data_foundation_phase1b
python -m intraday.cli.main data validate-curated --symbol QQQ --start 2024-01-01 --end 2024-06-30 --data-root data/curated/bars_1m_rth
python -m intraday.cli.main data load-bars --symbol QQQ --start 2024-01-01 --end 2024-06-30 --data-root data/curated/bars_1m_rth
python -m intraday.cli.main data session-coverage --symbol QQQ --start 2024-01-01 --end 2024-06-30 --data-root data/curated/bars_1m_rth --output-dir artifacts/data_foundation_phase1b
```
All completed with exit code 0 where applicable.
