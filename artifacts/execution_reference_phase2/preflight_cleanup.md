# Phase 0A — Preflight cleanup

Small documentation and schema-constant clarification before execution implementation.

## Summary

| file_path | issue | action_taken | behavior_changed |
| --- | --- | --- | --- |
| `data/README.md` | Stale Phase 0/1A tracking + legacy-only narrative | Rewrote for gitignored raw/curated, canonical QQQ, legacy SPY, relative config paths, accepted timestamp names | no |
| `data/raw/README.md` | Legacy-only QQQ emphasis | Rewrote canonical vs legacy + timestamp column names | no |
| `data/raw/ibkr/README.md` | Implied fixed `timestamp` column | Rewrote OHLCV + config-driven temporal column | no |
| `data/curated/README.md` | “Empty until Phase 1” | Updated to local-only gitignored + schema pointer | no |
| `src/intraday/data/schema.py` | `RAW_REQUIRED_COLUMNS` included misleading `timestamp` | Added `RAW_REQUIRED_OHLCV_COLUMNS`; `RAW_REQUIRED_COLUMNS` alias to OHLCV tuple with deprecation comment | no |

No normalization or loader behavior changed; tests did not require runtime code changes beyond the constant rename/alias.
