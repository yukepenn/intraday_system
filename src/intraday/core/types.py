"""Enumerations shared across layers.

These integer enums are stable across the codebase. Numba-compatible (int values).
"""

from __future__ import annotations

from enum import IntEnum


class Side(IntEnum):
    """Trade side. Stored as int8 in NumPy arrays."""

    FLAT = 0
    LONG = 1
    SHORT = -1


class ExitReason(IntEnum):
    """Why a trade exited. Stored as int16 in NumPy arrays."""

    NONE = 0
    STOP = 1
    TARGET = 2
    EOD = 3
    MAX_HOLD = 4
    SCALE_OUT = 5
    TRAILING_STOP = 6
    NO_FOLLOWTHROUGH = 7
    REJECTED = 8


class RejectReason(IntEnum):
    """Why an intent was rejected before becoming a trade."""

    NONE = 0
    RISK_TOO_SMALL = 1
    NO_NEXT_BAR = 2
    CROSS_SESSION_ENTRY = 3
    INVALID_STOP = 4
    SHORT_NOT_ALLOWED = 5
    OUTSIDE_TRADING_WINDOW = 6


class EngineMode(IntEnum):
    """Reference vs fast execution path selector."""

    REFERENCE = 0
    FAST = 1
