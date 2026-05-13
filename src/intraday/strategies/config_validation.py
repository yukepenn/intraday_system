"""Strategy config validation (skeleton)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from intraday.core.config import require_keys


def validate_strategy_base(config: Mapping[str, Any]) -> None:
    """Validate the shape of a strategy base config (minimal Phase 0 check)."""
    require_keys(config, ("strategy", "version"), where="strategy base config")


def validate_strategy_grid(config: Mapping[str, Any]) -> None:
    """Validate the shape of a strategy grid config (minimal Phase 0 check)."""
    require_keys(config, ("strategy", "base_config"), where="strategy grid config")
