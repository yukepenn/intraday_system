# configs/layer1/

Layer1 run configs. Each file defines a candidate-factory run:

- `run_id` (e.g. `L1_QQQ_CONTROLLED_2023_2024_V1`)
- `symbol`, `asset`, `timeframe`, `start`, `end`, `data_root`
- `execution_config` reference
- `strategies:` list (each entry has `name` + `grid:` path)
- `selection:` gates (min_trades, min_profit_factor_r, etc.)
- `output:` (artifact_root, candidate_root)

Phase 0/1A intentionally does NOT commit real Layer1 configs. Smoke and controlled configs land in Phase 6 and Phase 7.
