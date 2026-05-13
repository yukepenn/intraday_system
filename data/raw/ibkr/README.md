# data/raw/ibkr/

IBKR-sourced raw data. One parquet per `(asset, symbol, timeframe, year, month)` partition in the canonical layout.

Parquet here is **local-only** and **gitignored** — do not commit raw vendor files.

## Notes

- Minimum bar columns include **OHLCV**; the timestamp column name is **config-driven** (accepted names include `ts_ny`, `ts_utc`, `timestamp`, `date`, `datetime`). See `intraday.data.schema.RAW_TIMESTAMP_ACCEPTED_COLUMNS`.
- Vendor extras (e.g. `barCount`, `wap`) may appear.
- **QQQ** is expected under the canonical path after Phase 1/1B; **SPY** may remain on a legacy layout until migrated.
- Curated parquet under `data/curated/bars_1m_rth/...` is downstream, **local-only**, and gitignored.
