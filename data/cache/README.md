# data/cache/

Local-only hot caches. **Always gitignored.**

## Layout

```
data/cache/
  arrays/                      # BarMatrix .npz / .memmap files
  features/                    # FeatureMatrix .npz + meta.json
    feature_hash=<hash>/data_hash=<hash>/{matrix.npz, columns.json, meta.json}
  signals/                     # SignalMatrix .npz + meta.json
    candidate_hash=<hash>/data_hash=<hash>/{signal_matrix.npz, meta.json}
  layer2_precompute/           # candidate signal matrices + router context
    layer2_config_hash=<hash>/data_hash=<hash>/{candidate_signals.npz, ...}
  metrics/                     # optional summary outputs
```

Cache is reproducible from raw + curated + configs. It is never the source of truth. See `docs/CACHE_CONTRACT.md` for hash rules.
