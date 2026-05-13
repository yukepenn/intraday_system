# data/raw/

Immutable vendor data. Do not edit files in place. Do not dedupe in place. Do not overwrite silently.

Parquet under this tree is **local-only** and **gitignored** in normal workflows (do not commit raw vendor files).

## Canonical layout

```
data/raw/<vendor>/asset=<asset>/symbol=<symbol>/timeframe=<tf>/year=<YYYY>/month=<MM>/bars.parquet
```

For IBKR equity 1-minute QQQ (example):

```
data/raw/ibkr/asset=equity/symbol=QQQ/timeframe=1m/year=2024/month=06/bars.parquet
```

## Legacy layout

Some symbols (e.g. **SPY**) may still appear under a legacy QT-like tree until migrated. **QQQ** is expected in the canonical layout after Phase 1/1B.

## Raw timestamps

Vendor files may use any accepted timestamp column name: `ts_ny`, `ts_utc`, `timestamp`, `date`, `datetime` — the active column is selected per dataset YAML (`raw_timestamp.column`).
