"""Raw and curated schema constants."""

from __future__ import annotations

# Exact raw column names accepted as a vendor timestamp for IBKR-like datasets.
# Dataset YAML ``raw_timestamp.column`` must be one of these (or inspection fails).
RAW_TIMESTAMP_ACCEPTED_COLUMNS: frozenset[str] = frozenset(
    {
        "ts_ny",
        "ts_utc",
        "timestamp",
        "date",
        "datetime",
    }
)

# Legacy tuple name kept for docs/search compatibility; logical minimum is timestamp + OHLCV.
RAW_REQUIRED_COLUMNS: tuple[str, ...] = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
)


def raw_timestamp_column_is_accepted(name: str) -> bool:
    return name in RAW_TIMESTAMP_ACCEPTED_COLUMNS


CURATED_SCHEMA_VERSION: str = "bars_1m_rth_v1"

CURATED_REQUIRED_COLUMNS: tuple[str, ...] = (
    "ts_utc",
    "ts_utc_ns",
    "ts_local",
    "session_date",
    "session_id",
    "bar_index",
    "minute_of_session",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "source",
    "is_rth",
)

CANONICAL_RAW_LAYOUT: str = (
    "data/raw/ibkr/asset=equity/symbol={symbol}/timeframe={timeframe}/"
    "year={year}/month={month:02d}/bars.parquet"
)

LEGACY_QT_LIKE_LAYOUT: str = (
    "data/raw/ibkr/equity/bars_1min/symbol={symbol}/" "year={year}/month={month:02d}/data.parquet"
)
