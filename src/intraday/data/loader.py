"""BarMatrix loader (skeleton).

Phase 1 will implement curated parquet -> BarMatrix. This stub raises a clear
error when called and documents the planned signature.
"""

from __future__ import annotations

from pathlib import Path

from intraday.core.arrays import BarMatrix
from intraday.core.errors import IntradaySystemError


def load_bars_from_curated(
    symbol: str,
    start: str,
    end: str,
    *,
    data_root: Path | str,
    columns: list[str] | None = None,
) -> BarMatrix:
    """Load curated parquet into a BarMatrix. NOT YET IMPLEMENTED.

    Planned signature stable as of Phase 0/1A. Implementation lands in Phase 1
    once the curated normalization is in place.
    """
    raise IntradaySystemError(
        "load_bars_from_curated is not implemented yet (Phase 1). "
        "Curated parquet under data/curated/bars_1m_rth/... does not exist "
        "until normalize_raw_ibkr_to_curated runs."
    )
