# FeatureStore

- **Root:** default `data/cache/features` (gitignored)
- **Layout:** `data_hash=<h>/feature_hash=<h>/matrix.npz`, `columns.json`, `meta.json`
- **get:** validates meta + shapes; corrupt → `IntradaySystemError`
- **put:** temp dir then atomic replace into entry path

Tests: `test_feature_store.py`
