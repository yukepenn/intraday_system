# data/raw/

Immutable vendor data. Do not edit files in place. Do not dedupe in place. Do not overwrite silently.

## Canonical layout

```
data/raw/<vendor>/asset=<asset>/symbol=<symbol>/timeframe=<tf>/year=<YYYY>/month=<MM>/bars.parquet
```

For IBKR equity 1-minute QQQ:

```
data/raw/ibkr/asset=equity/symbol=QQQ/timeframe=1m/year=2024/month=06/bars.parquet
```

## Current local state

The local repo holds parquet under the legacy QT-like layout:

```
data/raw/ibkr/equity/bars_1min/symbol=QQQ/year=YYYY/month=MM/data.parquet
data/raw/ibkr/equity/bars_1min/symbol=SPY/year=YYYY/month=MM/data.parquet
```

Phase 0/1A intentionally does NOT move files. Phase 1 will either canonicalize the layout (preserving bytes) or implement a layout-aware loader.

## Tracking decision

All current files are `<1 MiB` and total `~36 MiB`. Safe for normal Git. See `artifacts/bootstrap/phase0_1a/data_tracking_decision.md` for the policy.
