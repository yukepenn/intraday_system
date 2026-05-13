"""ExecutionSpec dataclass."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from intraday.core.config import require_keys
from intraday.core.constants import SEMANTICS_VERSION_DEFAULT


@dataclass(frozen=True)
class ExecutionSpec:
    """Canonical execution semantics. Mirrors configs/execution/intraday_default.yaml."""

    entry_timing: Literal["next_open"]
    same_bar_policy: Literal["stop_first", "target_first", "conservative"]
    slippage_per_share: float
    commission_per_trade: float
    min_risk_per_share: float
    eod_exit_minute: int
    allow_short: bool
    max_hold_bars_default: int | None = None
    semantics_version: str = SEMANTICS_VERSION_DEFAULT

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> ExecutionSpec:
        require_keys(
            config,
            (
                "entry_timing",
                "same_bar_policy",
                "slippage_per_share",
                "commission_per_trade",
                "min_risk_per_share",
                "eod_exit_minute",
                "allow_short",
            ),
            where="execution config",
        )
        return cls(
            entry_timing=config["entry_timing"],
            same_bar_policy=config["same_bar_policy"],
            slippage_per_share=float(config["slippage_per_share"]),
            commission_per_trade=float(config["commission_per_trade"]),
            min_risk_per_share=float(config["min_risk_per_share"]),
            eod_exit_minute=int(config["eod_exit_minute"]),
            allow_short=bool(config["allow_short"]),
            max_hold_bars_default=(
                int(config["max_hold_bars_default"])
                if config.get("max_hold_bars_default") is not None
                else None
            ),
            semantics_version=str(
                config.get("semantics_version", SEMANTICS_VERSION_DEFAULT)
            ),
        )
