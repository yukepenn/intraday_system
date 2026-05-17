# Confirmation window selection

Design window (do not reuse): **QQQ 2024-01-01 → 2024-06-30** (2024H1).

## Candidate windows probed

| Priority | Window | Dates | Result |
| --- | --- | --- | --- |
| 1 | QQQ 2024H2 | 2024-07-01 → 2024-12-31 | **NO_DATA** — no curated parquet |
| 2 | QQQ 2023H2 | 2023-07-01 → 2023-12-31 | **NO_DATA** |
| 3 | QQQ 2025H1 | 2025-01-01 → 2025-06-30 | **NO_DATA** |

Command used:

```bash
python -m intraday.cli.main data validate-curated --symbol QQQ --start <START> --end <END> --data-root data/curated/bars_1m_rth
```

## Selected window

**None** — local curated data missing for all non-overlapping candidates.

## Next action

Curate QQQ 2024H2 (preferred) via existing `data normalize --write` pipeline, then re-run:

1. `layer1 grid --config configs/layer1/controlled_pa_qqq_2024h2.yaml`
2. `layer1 select-dry-run` on confirmation sweep
3. Design vs confirmation comparison artifacts
