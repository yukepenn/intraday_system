"""Project-wide numeric constants."""

from __future__ import annotations

RTH_START_MINUTE: int = 0
RTH_END_MINUTE: int = 389
MINUTES_PER_RTH_SESSION: int = 390

HALF_DAY_MINUTES: int = 210

DEFAULT_EOD_EXIT_MINUTE: int = 389
DEFAULT_SLIPPAGE_PER_SHARE: float = 0.01
DEFAULT_MIN_RISK_PER_SHARE: float = 0.03

SEMANTICS_VERSION_DEFAULT: str = "execution_v1"
