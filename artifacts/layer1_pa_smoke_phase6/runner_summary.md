# Layer1 smoke runner summary

- Entry: `run_layer1_smoke(Path)` in `src/intraday/layer1/runner.py`
- Flow: load smoke YAML → bars → `FeatureMatrix` → `SignalMatrix` → intents → session scan → `simulate_trade_path_reference` (or `fast`, or `both` with parity assert)
- `merge_execution_spec_with_strategy` in `execution/spec.py` applies strategy `backtest`/`risk` overrides
- Result: `Layer1SmokeResult` (`src/intraday/layer1/result.py`)
- Artifacts: `reports.write_layer1_smoke_artifacts` (summary JSON + distribution CSVs)
