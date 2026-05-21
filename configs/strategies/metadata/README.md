# configs/strategies/metadata/

Routing metadata per strategy, decoupled from the strategy's signal/risk logic. Layer2 consumes this metadata for default priority, family assignment, conflict grouping, default management mode, and active-time windows.

Example fields (Phase 5+):

```yaml
strategy: pa_buy_sell_close_trend
family: pa
default_priority: 80
conflict_group: QQQ_directional
default_management_mode: fixed_r
default_active_start_minute: 60
default_active_end_minute: 300
```

Required current fields:

- `core_or_diagnostic`
- `diagnostic_only`
- `grid_inspect_only`
- `side_mode_allowed`
- `default_side_mode`
- `setup_codes.long` / `setup_codes.short`
- `required_feature_columns`
- `broad_sweep_allowed`
- `economic_claims_allowed`
- `candidate_eligible_now`
- `promotion_allowed_now`

Metadata is an audit mirror. Runtime setup-code truth lives in
`src/intraday/strategies/setup_codes.py` and runtime strategy metadata is
exposed by `StrategyDef` / `strategies inspect`.
