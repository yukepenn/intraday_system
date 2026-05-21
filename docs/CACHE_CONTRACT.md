# CACHE_CONTRACT — intraday_system

The cache system is central. It prevents repeated computation across sweeps, routers, and folds.

## 1. Cache layers

| Cache | Contents | Path |
| --- | --- | --- |
| Data cache | `BarMatrix` arrays | `data/cache/arrays/...` |
| Feature cache | `FeatureMatrix` | `data/cache/features/...` |
| Signal cache | `SignalMatrix` per candidate | `data/cache/signals/...` |
| Layer2 precompute | Candidate signals + router context | `data/cache/layer2_precompute/...` |
| Metrics cache | Optional summary outputs | `data/cache/metrics/...` |

All `data/cache/**` is gitignored. Cache is reproducible from raw + curated + configs; it is never the source of truth.

## 2. Cache keys (hashes)

Every cache key is deterministic and content-addressed.

| Hash | Built from |
| --- | --- |
| `data_hash` | `(asset, symbol, timeframe, window, file manifest of (relpath,size,mtime))` |
| `feature_config_hash` | The feature config YAML, canonically dumped (sorted keys) |
| `strategy_config_hash` | Base + fixed + combo, canonically dumped |
| `execution_spec_hash` | `ExecutionSpec` fields, canonically dumped |
| `candidate_hash` | `(strategy_config_hash, execution_spec_hash, feature_config_hash, data_window)` |
| `router_config_hash` | The Layer2 router subsection, canonically dumped |
| `layer2_config_hash` | Full Layer2 run config, canonically dumped |
| `fold_hash` | `(fold_name, start, end)` |

Hashing utilities live in `src/intraday/core/hashing.py`. The canonical serialization is JSON with `sort_keys=True`, no trailing whitespace, UTF-8.

## 3. Cache layout

### 3.1 Feature cache

Phase 4 on-disk layout (implemented by `FeatureStore`):

```
data/cache/features/
  data_hash=<data_hash>/
    feature_hash=<feature_hash>/
      matrix.npz
      columns.json
      meta.json
```

`matrix.npz` contains array `values` (`float64`, shape `N × K`). `meta.json` records `data_hash`, `feature_hash`, row/column counts, and `feature_engine_semantic_version`.

### 3.2 Signal cache

```
data/cache/signals/
  candidate_hash=<hash>/
    data_hash=<hash>/
      signal_matrix.npz
      meta.json
```

### 3.3 Layer2 precompute cache

```
data/cache/layer2_precompute/
  layer2_config_hash=<hash>/
    data_hash=<hash>/
      candidate_signals.npz
      candidate_meta.json
      router_context.npz
```

## 4. Invalidation rules

- Changing a strategy threshold must **not** rebuild features.
- Changing a router rule must **not** rebuild Layer1 signals.
- Changing execution cost must **not** rebuild features/signals.
- Changing raw bars (new data_hash) invalidates every downstream cache for the affected window.
- Migrating a strategy config key, such as `signal.side` to canonical
  `signal.side_mode`, can legitimately change `strategy_config_hash` and
  `signal_hash` even when generated long-only behavior is equivalent.

If a cache miss occurs, the engine recomputes and writes the cache (when caching is enabled). If a cache hit occurs, the loaded artifact's `meta.json` must match the expected hashes — mismatch is a hard error.

## 5. `meta.json` shape (FeatureStore, Phase 4)

```json
{
  "kind": "feature_matrix",
  "data_hash": "...",
  "feature_hash": "...",
  "n_bars": 123456,
  "n_columns": 22,
  "feature_engine_semantic_version": "feature_engine_mvp_v1",
  "dtype": "float64"
}
```

`columns.json` is a JSON array of column names in index order (`0..K-1`).

## 6. Hot path priorities

1. Bars are loaded once per run.
2. Features are computed once per `(feature_config_hash, data_hash)`.
3. Signals are computed once per `(strategy_config_hash, feature_config_hash, data_hash)`.
4. Execution is per-intent; not cached (cheap relative to feature/signal compute).
5. Layer2 precomputes signal matrices for all candidates before routing.

## 7. Cache hygiene

- Cache writes are atomic: write `tmp/*` then rename.
- Cache reads validate `meta.json` hashes before using the cached array.
- A `--no-cache` CLI flag (future) forces recompute and skips writes.
- A `cache prune` CLI command (future) removes entries older than N days.

## 8. Forbidden

- Committing `data/cache/**`.
- Using cache contents to override config truth.
- Hashing pandas DataFrames directly (use canonical dict/JSON form).
- Mutable hash inputs (e.g. dicts with unsorted keys).

## 9. Config-key migration and cache identity

Behavioral equivalence does not imply hash identity. `compute_signal_hash(...)`
includes `hash_config(resolved_strategy_config)`, so two configs with identical
runtime behavior but different key spelling or explicit/default fields may
produce different `strategy_config_hash` / `signal_hash` values. Phase19 polish
therefore treats `signal.side` -> `signal.side_mode` migration as a cache
identity change unless a test intentionally proves identical resolved config
identity.
