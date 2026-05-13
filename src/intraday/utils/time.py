"""Time helpers (skeleton)."""

from __future__ import annotations

from datetime import UTC, datetime


def utcnow_iso() -> str:
    """Return the current UTC time as an ISO-8601 string with second precision."""
    return datetime.now(tz=UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
