# Reporting summary

`write_layer1_grid_artifacts`:

- `sweep_results.csv` — one row per combo (includes `params_json`, metrics, JSON-encoded count blobs)
- `controlled_grid_summary.md` / `.csv`
- `config_inventory.csv`, `grid_inventory.csv`
- `exit_reason_distribution.csv`, `reject_reason_distribution.csv`, `skip_reason_distribution.csv` (aggregated across combos)
- `top_rows_by_total_r.csv`, `top_rows_by_profit_factor.csv` — human review only

CSV: `reporting_summary.csv`.
