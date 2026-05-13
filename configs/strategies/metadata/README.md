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

Phase 0/1A intentionally does NOT commit real metadata.
