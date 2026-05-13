# DATA_CONTRACT — intraday_system

This document defines the three data states (raw, curated, hot) and the canonical paths/schemas.

## 1. Raw data

Raw data is exactly what came from the data vendor (IBKR for now). It is **immutable**.

**Canonical raw path**:

```
data/raw/ibkr/asset=equity/symbol=QQQ/timeframe=1m/year=YYYY/month=MM/bars.parquet
```

**Legacy (currently present locally) path**:

```
data/raw/ibkr/equity/bars_1min/symbol=QQQ/year=YYYY/month=MM/data.parquet
```

Canonicalization (folder rename + file rename) is implemented in Phase 1 (`intraday.data.canonicalize` + `data canonicalize-raw`). QQQ raw months are expected in **canonical** layout when present locally; **legacy** paths may remain for other symbols (e.g. SPY) or during transition.

**Raw data rules**:

- Raw files are append-only / replace-by-version-bump.
- Do not edit raw files in place.
- Do not silently dedupe or overwrite.
- One parquet per `(asset, symbol, timeframe, year, month)` partition.

**Observed local QQQ IBKR raw columns (Phase 1 audit)**:

| Column | Type | Notes |
| --- | --- | --- |
| `ts_utc` | timestamp[ns, tz=UTC] | Vendor UTC clock |
| `ts_ny` | timestamp[ns, tz=America/New_York] | Vendor local clock |
| `open` / `high` / `low` / `close` / `volume` | float64 | OHLCV |
| `useRTH` | bool | Present in vendor export; normalization still applies explicit RTH window |
| extras | varies | e.g. `asset`, `source`, `bar_size`, `average`, `barCount`, `symbol` |

**Accepted raw timestamp column names** (exact strings; dataset YAML `raw_timestamp.column` must be one of these):

- `ts_ny`, `ts_utc` (preferred for IBKR QQQ when present)
- `timestamp`, `date`, `datetime` (legacy / synthetic / alternate vendors)

Schema inspection requires a **temporal** Arrow type for the configured column (or at least one accepted temporal column when no config override is supplied).

**Current QQQ dataset selection**: `raw_timestamp.column: ts_ny` (see `configs/data/ibkr_qqq_1m.yaml`).

**Accepted OHLCV column names** (defaults overridable via dataset `ohlcv` mapping):

- `open`, `high`, `low`, `close`, `volume`.

**Raw schema (minimum)**:

| Column | Type | Notes |
| --- | --- | --- |
| one accepted temporal timestamp column | datetime/date | Controlled by dataset YAML |
| `open` | float64 | |
| `high` | float64 | |
| `low` | float64 | |
| `close` | float64 | |
| `volume` | float64 | |

Normalization **standardizes** vendor raw schema into the curated schema below (`ts_utc`, `ts_utc_ns`, `ts_local`, `session_date`, `minute_of_session`, …).

**Exact session window (Phase 1B)**:

After RTH filtering and dedupe, normalization keeps rows whose **NY `session_date`** (derived from bar-start `ts_local`) satisfies `start_date ≤ session_date ≤ end_date` for the requested ISO `start`/`end` (inclusive). This prevents partial calendar requests from silently including whole extra session days that spill from overlapped raw month files.

**Write safety (Phase 1B)**:

`normalize` with `write=True` refuses partial calendar-month windows for canonical monthly curated outputs (raises `ConfigError`) unless a dedicated partial-output root exists in the future. Use dry-run (default without `--write`) to preview counts for arbitrary windows.

## 2. Curated data

Curated data is normalized, session-tagged, RTH-filtered, and backtest-ready.

**Canonical curated path**:

```
data/curated/bars_1m_rth/asset=equity/symbol=QQQ/year=YYYY/month=MM/bars.parquet
```

**Curated schema (Phase 1 — implemented)**:

| Column | Type | Notes |
| --- | --- | --- |
| `ts_utc` | timestamp[ns, UTC] | Bar **start** instant in UTC |
| `ts_utc_ns` | int64 | `ts_utc` as epoch nanoseconds |
| `ts_local` | timestamp[ns, America/New_York] | Bar **start** in US/Eastern |
| `session_date` | int32 | `YYYYMMDD` (NY session date) |
| `session_id` | int32 | Dense rank of `session_date` **within the normalization output** (per-file ranks may reset monthly; treat as diagnostic when inspecting parquet) |
| `bar_index` | int64 | Row index after global `ts_utc_ns` sort |
| `minute_of_session` | int16 | Minutes since 09:30 NY inclusive; full RTH runs `0..389` |
| `open` | float64 | |
| `high` | float64 | |
| `low` | float64 | |
| `close` | float64 | |
| `volume` | float64 | |
| `source` | string | e.g. `ibkr` |
| `is_rth` | bool | Always `true` in `bars_1m_rth/...` |

**Timestamp semantics**:

- Curated `ts_utc` / `ts_local` always represent **bar START**.
- If raw timestamps are **bar END** (dataset `raw_timestamp.semantics: bar_end`), normalization subtracts **one minute** (in NY) before assigning `minute_of_session`.
- RTH filter uses bar-start local time: **09:30 ≤ bar_start \< 16:00** (`America/New_York`).
- `minute_of_session` = minutes since 09:30 NY, based on bar-start time.
- EOD minute convention for downstream engines continues to treat the last full RTH minute index as **389**.

## 3. Hot arrays — `BarMatrix`

The backtest engine never operates on parquet directly. Parquet is storage. The engine operates on the `BarMatrix` defined in `src/intraday/core/arrays.py`:

```python
@dataclass(frozen=True)
class BarMatrix:
    open: np.ndarray           # float64
    high: np.ndarray           # float64
    low: np.ndarray            # float64
    close: np.ndarray          # float64
    volume: np.ndarray         # float64
    session_id: np.ndarray     # int32
    session_date: np.ndarray   # int32 YYYYMMDD
    minute: np.ndarray         # int16 (minute_of_session)
    ts_ns: np.ndarray          # int64 (UTC nanoseconds)
    symbol_id: int             # mapped from configs/data/symbols.yaml
    data_hash: str             # deterministic over (file paths, sizes, mtimes, schema, window)
```

**BarMatrix rules**:

- Arrays must share the same length.
- `session_id` must be monotonically non-decreasing.
- `minute` must reset to 0 at each session start (first bar of each `session_id` segment).
- `ts_ns` must be strictly increasing.
- `data_hash` is the cache key seed for everything downstream.

**BarMatrix `session_id` semantics (Phase 1B)**:

`load_bars_from_curated(...)` **recomputes** `session_id` after concatenating, filtering, and sorting the requested window: unique `session_date` values sorted ascending map to dense IDs `0..N-1`. Execution and downstream features must rely on **BarMatrix** `session_id`, not on parquet-local ranks that may reset across monthly files.

## 4. RTH and session constants

For US equity 1-minute RTH:

```
RTH_START_MINUTE = 0      # 09:30 ET
RTH_END_MINUTE   = 389    # 16:00 ET (exclusive boundary marker)
MINUTES_PER_RTH_SESSION = 390
```

`eod_exit_minute` defaults to `389` (the last RTH minute index).

## 5. Layout enforcement

The catalog tool (`intraday.data.catalog`) inventories every parquet under `data/raw/ibkr/` and classifies each file as:

- `canonical` — matches the canonical layout exactly.
- `legacy_qt_like` — matches `equity/bars_1min/symbol=*/year=*/month=*/data.parquet`.
- `unknown` — anything else (flagged for manual review).

The catalog proposes a canonical path for every file and records it in `artifacts/bootstrap/phase0_1a/raw_data_inventory.csv`. Phase 1 will execute the relocation (or use a layout-aware loader in the interim).

## 6. Data identity and `data_hash`

The `data_hash` is built from a manifest of `(relative_path, size_bytes, mtime_ns)` plus the requested window. It is **not** a content hash of every byte (which would be too slow). For audits, a full content hash can be computed on-demand and stored under `artifacts/diagnostics/data_validation/`.

## 7. Forbidden

- Editing raw parquet in place.
- Writing curated parquet that contains non-RTH bars in an `*_rth` path.
- Strategies reading parquet directly (must go through `BarMatrix`).
- Putting strategy-specific columns into `BarMatrix`.
