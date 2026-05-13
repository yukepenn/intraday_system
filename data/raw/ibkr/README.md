# data/raw/ibkr/

IBKR-sourced raw data. One parquet per `(asset, symbol, timeframe, year, month)` partition.

## Current contents

- Equity 1-minute bars for QQQ (Jan 2020 — late 2026 partial), legacy layout.
- Equity 1-minute bars for SPY (Jan 2020 — Apr 2026 partial), legacy layout.

## Notes

- Raw schema (minimum): `timestamp, open, high, low, close, volume`.
- Vendor extras (e.g. `barCount`, `wap`) may appear.
- Curated parquet under `data/curated/bars_1m_rth/...` is downstream and generated in Phase 1.
