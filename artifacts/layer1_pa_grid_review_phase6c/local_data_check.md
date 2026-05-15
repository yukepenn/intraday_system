# Local QQQ 2024H1 curated data check

`python -m intraday.cli.main data validate-curated --symbol QQQ --start 2024-01-01 --end 2024-06-30 --data-root data/curated/bars_1m_rth`

- **row_count:** 48360  
- **session_count:** 124  
- **min_minute / max_minute:** 0 .. 389 (from load-bars)  
- **errors:** []  
- **warnings:** []  

`data load-bars` succeeded with matching rows/sessions and stable `data_hash`.
