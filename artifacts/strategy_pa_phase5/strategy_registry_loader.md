# Strategy registry / loader / validation

- `register_strategy`, `get_strategy`, `list_strategies`, `register_builtin_strategies`, `clear_strategy_registry`
- Built-in: `pa_buy_sell_close_trend`
- Loader: `load_strategy_config`, `load_strategy_metadata`, `load_strategy_grid`, `resolve_strategy_config`, `validate_strategy_config`
- PA validation: entry window, side, stop_mode, target_r, feature set

Tests: `test_strategy_registry.py`, `test_strategy_loader.py`, `test_strategy_config_validation.py`
