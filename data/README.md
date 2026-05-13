# data/

Three states:

| Subfolder | Role | Tracking |
| --- | --- | --- |
| `raw/` | Immutable vendor data (parquet) | Tracked in Git if size is safe; otherwise local-only / LFS |
| `curated/` | Normalized, session-tagged, RTH-filtered parquet | Generated; tracked only if intentionally curated for review |
| `cache/` | Local hot caches (BarMatrix arrays, FeatureMatrix, SignalMatrix, etc.) | **Never tracked** (`.gitignore`) |

See `docs/DATA_CONTRACT.md` for schemas, canonical paths, and `BarMatrix` rules.

## Current local state (Phase 0/1A inventory)

- Raw IBKR equity 1-minute parquet exists locally for QQQ and SPY across multiple years.
- Layout is currently **legacy QT-like**:
  - `data/raw/ibkr/equity/bars_1min/symbol=*/year=*/month=*/data.parquet`
- Canonical target layout (Phase 1 will migrate):
  - `data/raw/ibkr/asset=equity/symbol=*/timeframe=1m/year=*/month=*/bars.parquet`
- All files are well under 50 MiB; safe for normal Git tracking.
- See `artifacts/bootstrap/phase0_1a/raw_data_inventory.csv` (and `.md`) for the full audit.
