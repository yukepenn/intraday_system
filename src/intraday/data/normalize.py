"""Raw -> curated normalization (skeleton).

Phase 1 will implement timestamp normalization, RTH filtering, session_id and
minute_of_session assignment, and curated parquet writing.
"""

from __future__ import annotations

from pathlib import Path

from intraday.core.errors import IntradaySystemError


def normalize_raw_ibkr_to_curated(
    raw_root: Path | str,
    curated_root: Path | str,
    symbol: str,
    start: str,
    end: str,
    *,
    calendar: str = "XNYS",
    rth_only: bool = True,
) -> list[Path]:
    """Normalize raw IBKR parquet to curated parquet. NOT YET IMPLEMENTED.

    Planned behavior:
      - read raw parquet (canonical or legacy_qt_like layout)
      - normalize timestamps to UTC + local ET
      - assign session_id, minute_of_session, bar_index
      - filter RTH when rth_only=True
      - write to data/curated/bars_1m_rth/asset=...
    """
    raise IntradaySystemError(
        "normalize_raw_ibkr_to_curated is not implemented yet (Phase 1)."
    )
