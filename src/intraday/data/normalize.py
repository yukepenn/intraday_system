"""Raw → curated normalization for IBKR 1m equity bars."""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Literal

import polars as pl

from intraday.core.errors import ConfigError, DataContractError
from intraday.data.catalog import build_raw_data_inventory
from intraday.data.schema import raw_timestamp_column_is_accepted

TimestampSemantics = Literal["bar_start", "bar_end"]


def _parse_iso_date(s: str) -> date:
    return date.fromisoformat(s[:10])


def _month_in_range(y: int, m: int, start_d: date, end_d: date) -> bool:
    cur = date(y, m, 1)
    start_m = date(start_d.year, start_d.month, 1)
    end_m = date(end_d.year, end_d.month, 1)
    return start_m <= cur <= end_m


def _covers_full_calendar_month_window(start_d: date, end_d: date) -> bool:
    """True when ``start_d`` is the first calendar day of its month and ``end_d`` the last."""
    if start_d.day != 1:
        return False
    last = calendar.monthrange(end_d.year, end_d.month)[1]
    if end_d.day != last:
        return False
    return True


def _session_date_key(d: date) -> int:
    return d.year * 10_000 + d.month * 100 + d.day


@dataclass
class NormalizationResult:
    """Summary of a normalization run."""

    symbol: str
    start: str
    end: str
    rows_in: int = 0
    rows_out: int = 0
    rows_rth: int = 0
    duplicate_identical_count: int = 0
    months_touched: list[str] = field(default_factory=list)
    output_paths: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dry_run: bool = True


def _pick_raw_paths(
    raw_root: Path,
    *,
    symbol: str,
    asset: str,
    timeframe: str,
    start: str,
    end: str,
    base: Path | None,
) -> list[Path]:
    start_d = _parse_iso_date(start)
    end_d = _parse_iso_date(end)
    rows = build_raw_data_inventory(raw_root, base=base)
    paths: list[Path] = []
    for inv in rows:
        if inv.get("symbol") != symbol:
            continue
        if inv.get("asset") != asset:
            continue
        if inv.get("timeframe") != timeframe:
            continue
        y, m = inv.get("year"), inv.get("month")
        if y is None or m is None:
            continue
        if not _month_in_range(int(y), int(m), start_d, end_d):
            continue
        paths.append(Path(inv["resolved_path"]))
    paths.sort(key=lambda p: p.as_posix())
    return paths


def _to_ny_bar_start(
    series: pl.Series,
    tz_if_naive: str,
    semantics: TimestampSemantics,
) -> pl.Series:
    """Interpret raw timestamps as America/New_York wall clock; return bar-start NY."""
    dtype = series.dtype
    if dtype == pl.Date:
        series = series.cast(pl.Datetime("ns"))
        dtype = series.dtype
    if not isinstance(dtype, pl.Datetime):
        raise DataContractError(f"timestamp column must be Datetime or Date, got {dtype}")
    tz = dtype.time_zone
    if tz is None:
        s = series.cast(pl.Datetime("ns")).dt.replace_time_zone(tz_if_naive)
    else:
        s = series.dt.convert_time_zone("America/New_York")
    if semantics == "bar_end":
        s = s.dt.offset_by("-1m")
    return s


def _dedupe_timestamps(
    df: pl.DataFrame,
    *,
    value_cols: list[str],
) -> tuple[pl.DataFrame, int]:
    """Drop duplicate ``ts_utc_ns``; identical rows keep one; conflicts raise."""
    if df.is_empty():
        return df, 0
    n0 = len(df)
    key = "ts_utc_ns"
    agg_exprs = [pl.col(c).n_unique().alias(f"nu_{c}") for c in value_cols]
    g = df.group_by(key).agg([pl.len().alias("_n"), *agg_exprs])
    conflict_expr = pl.col(f"nu_{value_cols[0]}") > 1
    for c in value_cols[1:]:
        conflict_expr = conflict_expr | (pl.col(f"nu_{c}") > 1)
    conflict = g.filter((pl.col("_n") > 1) & conflict_expr)
    if len(conflict) > 0:
        raise DataContractError(f"conflicting duplicate timestamps: {conflict.head(5).to_dicts()}")
    dup_groups = g.filter(pl.col("_n") > 1)
    identical_dropped = (
        int(dup_groups.select((pl.col("_n") - 1).sum()).item()) if len(dup_groups) else 0
    )
    out = df.sort(key).unique(subset=[key], keep="first")
    assert len(out) == n0 - identical_dropped
    return out, identical_dropped


def normalize_raw_ibkr_to_curated(
    raw_root: Path | str,
    curated_root: Path | str,
    symbol: str,
    start: str,
    end: str,
    *,
    asset: str = "equity",
    timeframe: str = "1m",
    timestamp_column: str,
    timestamp_timezone_if_naive: str = "America/New_York",
    timestamp_semantics: TimestampSemantics,
    ohlcv: dict[str, str] | None = None,
    rth_only: bool = True,
    write: bool = False,
    source_tag: str = "ibkr",
    base: Path | str | None = None,
) -> NormalizationResult:
    """Read monthly raw parquet, normalize to curated schema, optionally write.

    Curated ``ts_utc`` / ``ts_local`` represent **bar start**. If
    ``timestamp_semantics`` is ``bar_end``, one minute is subtracted in NY
    before UTC conversion and session/minute assignment.
    """
    start_d = _parse_iso_date(start)
    end_d = _parse_iso_date(end)
    if write and not _covers_full_calendar_month_window(start_d, end_d):
        raise ConfigError(
            "write mode refuses partial calendar-month windows for canonical monthly "
            "curated partitions (would risk overwriting a full month with a truncated "
            f"subset). Requested {start!r}..{end!r}. Use --dry-run, expand to full "
            "months (start on month-first, end on month-last), or add an explicit "
            "partial-output curated root when supported."
        )
    if not raw_timestamp_column_is_accepted(timestamp_column):
        raise DataContractError(
            f"timestamp column {timestamp_column!r} is not in accepted raw names "
            "(see intraday.data.schema.RAW_TIMESTAMP_ACCEPTED_COLUMNS)."
        )

    ohlcv = ohlcv or {}
    o = ohlcv.get("open", "open")
    h = ohlcv.get("high", "high")
    lcol = ohlcv.get("low", "low")
    c = ohlcv.get("close", "close")
    v = ohlcv.get("volume", "volume")

    raw_root_p = Path(raw_root).resolve()
    curated_root_p = Path(curated_root).resolve()
    base_p = Path(base).resolve() if base is not None else None

    result = NormalizationResult(
        symbol=symbol,
        start=start,
        end=end,
        dry_run=not write,
    )

    paths = _pick_raw_paths(
        raw_root_p,
        symbol=symbol,
        asset=asset,
        timeframe=timeframe,
        start=start,
        end=end,
        base=base_p,
    )
    if not paths:
        result.warnings.append("no_raw_files_matched_range")
        return result

    inv_rows = build_raw_data_inventory(raw_root_p, base=base_p)
    inv_by_path = {str(Path(r["resolved_path"]).resolve()): r for r in inv_rows}

    frames: list[pl.DataFrame] = []
    for fp in paths:
        df = pl.read_parquet(fp, columns=[timestamp_column, o, h, lcol, c, v])
        result.rows_in += len(df)
        df = df.rename(
            {
                timestamp_column: "_raw_ts",
                o: "open",
                h: "high",
                lcol: "low",
                c: "close",
                v: "volume",
            }
        )
        ny_start = _to_ny_bar_start(
            df["_raw_ts"],
            timestamp_timezone_if_naive,
            timestamp_semantics,
        )
        df = df.drop("_raw_ts").with_columns(
            ny_start.alias("ts_local"),
        )
        df = df.with_columns(
            pl.col("ts_local").dt.convert_time_zone("UTC").alias("ts_utc"),
        )
        df = df.with_columns(
            pl.col("ts_utc").dt.epoch(time_unit="ns").alias("ts_utc_ns"),
        )
        bad = df.filter(
            (pl.col("high") < pl.max_horizontal(["open", "close", "low"]))
            | (pl.col("low") > pl.min_horizontal(["open", "close", "high"]))
            | pl.col("open").is_nan()
            | pl.col("high").is_nan()
            | pl.col("low").is_nan()
            | pl.col("close").is_nan()
        )
        if len(bad) > 0:
            raise DataContractError(f"OHLC contract violations in {fp}: {len(bad)} row(s)")
        neg_v = df.filter(pl.col("volume") < 0)
        if len(neg_v) > 0:
            raise DataContractError(f"negative volume in {fp}: {len(neg_v)} row(s)")

        if rth_only:
            hour = pl.col("ts_local").dt.hour().cast(pl.Int32)
            minute_i = pl.col("ts_local").dt.minute().cast(pl.Int32)
            mos = hour * 60 + minute_i - (9 * 60 + 30)
            df = df.filter((mos >= 0) & (mos < 390))

        df = df.with_columns(
            (
                pl.col("ts_local").dt.year().cast(pl.Int64) * 10_000
                + pl.col("ts_local").dt.month().cast(pl.Int64) * 100
                + pl.col("ts_local").dt.day().cast(pl.Int64)
            )
            .cast(pl.Int32)
            .alias("session_date"),
            (
                pl.col("ts_local").dt.hour().cast(pl.Int32) * 60
                + pl.col("ts_local").dt.minute().cast(pl.Int32)
                - (9 * 60 + 30)
            )
            .cast(pl.Int16)
            .alias("minute_of_session"),
            pl.lit(True).alias("is_rth"),
            pl.lit(source_tag).alias("source"),
        )
        inv_row = inv_by_path.get(str(fp.resolve()), {})
        yv, mv = inv_row.get("year"), inv_row.get("month")
        if yv is not None and mv is not None:
            result.months_touched.append(f"{int(yv):04d}-{int(mv):02d}")
        frames.append(df)

    out = pl.concat(frames, how="vertical")
    result.rows_rth = len(out)
    out = out.sort("ts_utc_ns")
    out, dup_ident = _dedupe_timestamps(
        out,
        value_cols=["open", "high", "low", "close", "volume"],
    )
    result.duplicate_identical_count = dup_ident

    n_pre_session_filter = len(out)
    start_key = _session_date_key(start_d)
    end_key = _session_date_key(end_d)
    out = out.filter((pl.col("session_date") >= start_key) & (pl.col("session_date") <= end_key))
    dropped = n_pre_session_filter - len(out)
    if dropped > 0:
        result.warnings.append(f"session_date_filter_dropped_rows={dropped}")

    sess = out.select("session_date").unique().sort("session_date").with_row_index("session_id")
    out = out.join(sess, on="session_date", how="left").with_columns(
        pl.col("session_id").cast(pl.Int32),
    )
    out = out.sort("ts_utc_ns").with_row_index("bar_index")
    out = out.with_columns(pl.col("bar_index").cast(pl.Int64))

    out = out.select(
        [
            pl.col("ts_utc").cast(pl.Datetime("ns", "UTC")),
            "ts_utc_ns",
            pl.col("ts_local").cast(pl.Datetime("ns", "America/New_York")),
            "session_date",
            "session_id",
            "bar_index",
            "minute_of_session",
            pl.col("open").cast(pl.Float64),
            pl.col("high").cast(pl.Float64),
            pl.col("low").cast(pl.Float64),
            pl.col("close").cast(pl.Float64),
            pl.col("volume").cast(pl.Float64),
            "source",
            "is_rth",
        ]
    )
    result.rows_out = len(out)

    out = out.with_columns(
        pl.col("ts_local").dt.year().alias("_y"),
        pl.col("ts_local").dt.month().alias("_m"),
    )
    keys = out.select(["_y", "_m"]).unique().sort(["_y", "_m"])
    planned_paths: list[str] = []
    for row in keys.iter_rows(named=True):
        y, m = int(row["_y"]), int(row["_m"])
        if not _month_in_range(y, m, start_d, end_d):
            continue
        sub = out.filter((pl.col("_y") == y) & (pl.col("_m") == m)).drop(["_y", "_m"])
        rel_dir = f"asset={asset}/symbol={symbol}/year={y}/month={m:02d}"
        out_path = curated_root_p / rel_dir / "bars.parquet"
        planned_paths.append(out_path.as_posix())
        if write:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            sub.write_parquet(out_path)

    result.output_paths = planned_paths

    short = out.group_by("session_date").agg(pl.len().alias("n")).filter(pl.col("n") < 390)
    if len(short) > 0:
        result.warnings.append(f"short_sessions_count={len(short)}")

    return result
