# configs/layer1/

Layer1 run configs. Each file defines a candidate-factory run:

- `run_id` (e.g. `L1_QQQ_CONTROLLED_2023_2024_V1`)
- `symbol`, `asset`, `timeframe`, `start`, `end`, `data_root`
- `execution_config` reference
- `strategies:` list (each entry has `name` + `grid:` path)
- `selection:` gates (min_trades, min_profit_factor_r, etc.)
- `output:` (artifact_root, candidate_root)

Config categories:

- Smoke: one strategy/config plumbing checks.
- Controlled diagnostic: small authorized economic diagnostics from prior phases.
- Grid-inspect-only: validates config/grid shape without running economic grids.
- Actual Layer1 grid: forbidden unless a phase explicitly authorizes it.

`phase19_brooks_pa_grid_inspect/` and
`phase19_immediate_fix_current10_side_aware_grid_inspect/` are inspect-only.
Actual Layer1 economic grids are forbidden in Phase19 polish.
