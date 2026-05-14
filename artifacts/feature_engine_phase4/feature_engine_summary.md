# Feature engine summary

- **Entrypoint:** `intraday.features.engine.build_feature_matrix`
- **Order:** canonical group order `vwap` → `orb` → `volatility` → `price_action` → `volume` → `regime`; windows preserve YAML list order
- **Cache:** optional `FeatureStore` under `data_hash=* / feature_hash=*`; `use_cache=False` skips get and put
- **Validation:** `resolve_feature_config` before compute; unknown groups / bad windows / duplicate output names rejected

Tests: `test_feature_engine.py`
