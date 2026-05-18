# Feature CLI smoke

| Command | Exit | Notes |
| --- | --- | --- |
| `features inspect --config configs/features/orb_core_v1.yaml` | 0 | 9 columns; hash `e3c3df12...` |
| `features build ... QQQ 2024H1` | skipped | No local curated QQQ parquet |
| `features build ... QQQ 2024H2` | skipped | No local curated QQQ parquet |

Inspect columns: `vwap`, `vwap_slope_5`, `orb_high_15`, `orb_low_15`, `orb_mid_15`, `orb_range_15`, `orb_width_pct_15`, `atr_like_20`, `range_mean_20`.
