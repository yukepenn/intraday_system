# Phase 1 summary (data foundation)

- Catalog/inventory hardened for repo-root vs raw-root vs temp roots (`layout_root`, `resolved_path`).
- Schema + timestamp helpers added; dataset YAML documents `ts_ny` + `bar_start`.
- Canonicalization tool applied to **QQQ** raw months; **SPY** still legacy.
- Normalization writes curated RTH parquet; fixes: Polars u8 overflow in minute math, `session_date` int64 arithmetic, OHLC column name shadowing.
- Loader + validation + CLI integrated; tests are synthetic-first.
