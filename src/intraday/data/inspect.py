"""Parquet schema inspection (metadata-first, no full table scans)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import pyarrow as pa
import pyarrow.parquet as pq

from intraday.data.catalog import build_raw_data_inventory, infer_raw_layout
from intraday.data.schema import RAW_TIMESTAMP_ACCEPTED_COLUMNS, raw_timestamp_column_is_accepted

SchemaStatus = Literal[
    "usable",
    "missing_timestamp",
    "missing_ohlc",
    "missing_volume",
    "unknown",
]


def _arrow_field_is_temporal(field: pa.Field) -> bool:
    t = field.type
    return pa.types.is_timestamp(t) or pa.types.is_date(t)


_OHLC_OPEN = re.compile(r"^open$", re.I)
_OHLC_HIGH = re.compile(r"^high$", re.I)
_OHLC_LOW = re.compile(r"^low$", re.I)
_OHLC_CLOSE = re.compile(r"^close$", re.I)
_VOL = re.compile(r"^volume$|^vol$|^size$", re.I)


@dataclass(frozen=True)
class RawParquetSchemaInfo:
    """Schema audit row for one parquet file."""

    relative_path: str
    file_size_bytes: int
    row_count: int | None
    columns: tuple[str, ...]
    dtypes: tuple[str, ...]
    timestamp_candidate_columns: tuple[str, ...]
    open_candidates: tuple[str, ...]
    high_candidates: tuple[str, ...]
    low_candidates: tuple[str, ...]
    close_candidates: tuple[str, ...]
    volume_candidates: tuple[str, ...]
    symbol_inferred: str | None
    year_inferred: int | None
    month_inferred: int | None
    layout_type: str
    schema_status: SchemaStatus
    notes: str


def _dtype_str(t: Any) -> str:
    return str(t)


def inspect_raw_parquet_schema(
    path: Path | str,
    *,
    base: Path | str | None = None,
    configured_timestamp_column: str | None = None,
) -> RawParquetSchemaInfo:
    """Read Parquet footer/schema only (no row materialization)."""
    p = Path(path)
    stat = p.stat()
    rel = p.resolve().as_posix()
    if base is not None:
        try:
            rel = p.resolve().relative_to(Path(base).resolve()).as_posix()
        except ValueError:
            rel = p.resolve().as_posix()

    layout = infer_raw_layout(p, base=base)
    row_count: int | None = None
    col_names: list[str] = []
    dtypes: list[str] = []
    try:
        pf = pq.ParquetFile(p)
        meta = pf.metadata
        if meta is not None:
            row_count = int(meta.num_rows)
        schema = pf.schema_arrow
        col_names = [schema.names[i] for i in range(len(schema.names))]
        dtypes = [_dtype_str(schema.types[i]) for i in range(len(schema.types))]
    except Exception as exc:  # noqa: BLE001
        return RawParquetSchemaInfo(
            relative_path=rel,
            file_size_bytes=int(stat.st_size),
            row_count=None,
            columns=tuple(),
            dtypes=tuple(),
            timestamp_candidate_columns=tuple(),
            open_candidates=tuple(),
            high_candidates=tuple(),
            low_candidates=tuple(),
            close_candidates=tuple(),
            volume_candidates=tuple(),
            symbol_inferred=layout.symbol,
            year_inferred=layout.year,
            month_inferred=layout.month,
            layout_type=layout.layout_type,
            schema_status="unknown",
            notes=f"parquet_read_error: {exc}",
        )

    name_to_field = {schema.names[i]: schema.field(i) for i in range(len(schema.names))}

    def temporal_accepted(name: str) -> bool:
        if name not in RAW_TIMESTAMP_ACCEPTED_COLUMNS:
            return False
        fld = name_to_field.get(name)
        return fld is not None and _arrow_field_is_temporal(fld)

    ts_cands = tuple(c for c in col_names if temporal_accepted(c))
    o_cands = tuple(c for c in col_names if _OHLC_OPEN.match(c))
    h_cands = tuple(c for c in col_names if _OHLC_HIGH.match(c))
    l_cands = tuple(c for c in col_names if _OHLC_LOW.match(c))
    c_cands = tuple(c for c in col_names if _OHLC_CLOSE.match(c))
    v_cands = tuple(c for c in col_names if _VOL.match(c))

    notes_parts: list[str] = []
    status: SchemaStatus = "usable"
    if configured_timestamp_column:
        if configured_timestamp_column not in col_names:
            status = "missing_timestamp"
            notes_parts.append(f"configured_timestamp_missing:{configured_timestamp_column}")
        elif not raw_timestamp_column_is_accepted(configured_timestamp_column):
            status = "missing_timestamp"
            notes_parts.append(f"configured_timestamp_not_accepted:{configured_timestamp_column}")
        else:
            fld = name_to_field.get(configured_timestamp_column)
            if fld is None or not _arrow_field_is_temporal(fld):
                status = "missing_timestamp"
                notes_parts.append(
                    f"configured_timestamp_not_temporal:{configured_timestamp_column}"
                )
    elif not ts_cands:
        status = "missing_timestamp"
        notes_parts.append("no_accepted_temporal_timestamp_column")

    if not (o_cands and h_cands and l_cands and c_cands):
        status = "missing_ohlc" if status == "usable" else status
        notes_parts.append("incomplete_ohlc")
    if not v_cands:
        status = "missing_volume" if status == "usable" else status
        notes_parts.append("no_volume_like_column")

    return RawParquetSchemaInfo(
        relative_path=rel,
        file_size_bytes=int(stat.st_size),
        row_count=row_count,
        columns=tuple(col_names),
        dtypes=tuple(dtypes),
        timestamp_candidate_columns=ts_cands,
        open_candidates=o_cands,
        high_candidates=h_cands,
        low_candidates=l_cands,
        close_candidates=c_cands,
        volume_candidates=v_cands,
        symbol_inferred=layout.symbol,
        year_inferred=layout.year,
        month_inferred=layout.month,
        layout_type=layout.layout_type,
        schema_status=status,
        notes="; ".join(notes_parts) if notes_parts else "",
    )


def inspect_raw_dataset_schema(
    root: Path | str,
    *,
    symbol: str | None = None,
    base: Path | str | None = None,
    raw_timestamp_column: str | None = None,
) -> list[dict[str, Any]]:
    """Inspect every parquet under ``root``, optionally filtered by inventory symbol."""
    root_path = Path(root).resolve()
    rows_inv = build_raw_data_inventory(root_path, base=base)
    out: list[dict[str, Any]] = []
    for inv in rows_inv:
        if symbol is not None and inv.get("symbol") != symbol:
            continue
        fp = Path(inv["resolved_path"])
        info = inspect_raw_parquet_schema(
            fp,
            base=base,
            configured_timestamp_column=raw_timestamp_column,
        )
        out.append(
            {
                "relative_path": info.relative_path,
                "file_size_bytes": info.file_size_bytes,
                "row_count": info.row_count,
                "columns": "|".join(info.columns),
                "dtypes": "|".join(info.dtypes),
                "timestamp_candidate_columns": "|".join(info.timestamp_candidate_columns),
                "open_candidates": "|".join(info.open_candidates),
                "high_candidates": "|".join(info.high_candidates),
                "low_candidates": "|".join(info.low_candidates),
                "close_candidates": "|".join(info.close_candidates),
                "volume_candidates": "|".join(info.volume_candidates),
                "symbol_inferred": info.symbol_inferred,
                "year_inferred": info.year_inferred,
                "month_inferred": info.month_inferred,
                "layout_type": info.layout_type,
                "schema_status": info.schema_status,
                "notes": info.notes,
            }
        )
    return out
