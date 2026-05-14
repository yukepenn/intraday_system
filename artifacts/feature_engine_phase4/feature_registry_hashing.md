# Registry and hashing

- **Built-in groups:** `vwap`, `orb`, `volatility`, `price_action`, `volume`, `regime`
- **API:** `register_feature`, `get_feature`, `list_features`, `clear_feature_registry`, `register_builtin_features` (idempotent)
- **Hash:** `hash_feature_config(resolve_feature_config(raw))` includes `FEATURE_ENGINE_SEMANTIC_VERSION` and resolved config (sorted JSON via `hash_config`)
- **Duplicates:** `ConfigError` on duplicate registration

Tests: `test_feature_registry.py`, `test_feature_hashing.py`
