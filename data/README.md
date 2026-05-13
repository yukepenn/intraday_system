# data/

Three states:

| Subfolder | Role | Tracking |
| --- | --- | --- |
| `raw/` | Immutable vendor parquet | **Local-only / gitignored** in normal workflows |
| `curated/` | Normalized, session-tagged, RTH-filtered parquet | **Local-only / gitignored** (not committed) |
| `cache/` | Local hot caches (BarMatrix arrays, FeatureMatrix, SignalMatrix, etc.) | **Never tracked** (`.gitignore`) |

Runtime configs under `configs/` use **paths relative to the repo root** (or absolute paths if you opt in).

## QQQ vs SPY

- **QQQ** raw data is expected under the **canonical** layout after Phase 1/1B (see `configs/data/ibkr_qqq_1m.yaml` and `docs/DATA_CONTRACT.md`).
- **SPY** may still use a **legacy** QT-like tree and is **not** the active normalization pipeline until migrated.

## Raw timestamps

Accepted raw timestamp **column names** include: `ts_ny`, `ts_utc`, `timestamp`, `date`, `datetime` (see `intraday.data.schema.RAW_TIMESTAMP_ACCEPTED_COLUMNS`).

See `docs/DATA_CONTRACT.md` for schemas, canonical paths, and `BarMatrix` rules.
