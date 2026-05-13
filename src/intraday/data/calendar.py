"""Trading calendar helpers (skeleton).

Phase 1 will integrate exchange_calendars (XNYS) for real fold and session work.
For now this module exports the RTH constants for downstream imports.
"""

from __future__ import annotations

from intraday.core.constants import (
    MINUTES_PER_RTH_SESSION,
    RTH_END_MINUTE,
    RTH_START_MINUTE,
)

DEFAULT_CALENDAR: str = "XNYS"

__all__ = [
    "DEFAULT_CALENDAR",
    "MINUTES_PER_RTH_SESSION",
    "RTH_END_MINUTE",
    "RTH_START_MINUTE",
]
