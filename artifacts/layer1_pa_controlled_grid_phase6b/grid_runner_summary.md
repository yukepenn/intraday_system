# Grid runner summary

- **Entry:** `run_layer1_controlled_grid(Path)`
- **Shared scan:** `layer1_scan_trade_intents` (same session rules as smoke)
- **Feature reuse:** one `build_feature_matrix` call per grid run
- **Per combo:** validate strategy config → reference signals → adapter → scan → `summarize_trade_results`

CSV: `grid_runner_summary.csv`.
