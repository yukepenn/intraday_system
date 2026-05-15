# Local QQQ 2024H1 controlled grid

**Status:** **Skipped** in this workspace — no curated `QQQ` parquet under `data/curated/bars_1m_rth` (expected gitignored).

With local data, run:

```bash
python -m intraday.cli.main layer1 grid --config configs/layer1/controlled_pa_qqq_2024h1.yaml
```

Outputs go to `artifacts/layer1_pa_controlled_grid_phase6b/local_run/` (gitignored). **Not** candidate selection or profitability proof.

CSV: `local_qqq_controlled_grid.csv`.
