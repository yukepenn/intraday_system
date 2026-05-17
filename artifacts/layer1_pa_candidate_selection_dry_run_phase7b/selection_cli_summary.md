# Layer1 select-dry-run CLI

```bash
python -m intraday.cli.main layer1 select-dry-run \
  --sweep-results artifacts/layer1_pa_grid_review_phase6c/sweep_results_review.csv \
  --base-config configs/strategies/base/pa_buy_sell_close_trend.yaml \
  --grid-config configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml \
  --output-root artifacts/layer1_pa_candidate_selection_dry_run_phase7b
```

Reads prior sweep CSV as **review/audit input only** (exception documented in selection contract). Does not rerun grid or read parquet. Does not write under `configs/candidates/`.
