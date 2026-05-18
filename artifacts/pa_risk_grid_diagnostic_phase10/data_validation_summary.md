# Data validation summary

| window | rows | sessions | minute range | errors | warnings |
| --- | --- | --- | --- | --- | --- |
| 2024H1 design | 48360 | 124 | 0–389 | none | none |
| 2024H2 stress | 49380 | 128 | 0–389 | none | missing_minute_slots_total=540 (3 short sessions) |

Curated parquet is **local-only** (gitignored). Both windows load successfully.
