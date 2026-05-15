"""ExecutionSpec dataclass."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, get_args

from intraday.core.config import load_yaml, require_keys
from intraday.core.constants import RTH_END_MINUTE, SEMANTICS_VERSION_DEFAULT
from intraday.core.errors import ConfigError

_ENTRY_TIMING_ALLOWED: frozenset[str] = frozenset({"next_open"})
_SAME_BAR_POLICIES: tuple[str, ...] = get_args(
    Literal["stop_first", "target_first", "conservative"]
)


def _coerce_bool(value: Any, *, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "1", "yes", "y", "on"):
            return True
        if lowered in ("false", "0", "no", "n", "off"):
            return False
    raise ConfigError(f"{field} must be a boolean-like value, got {value!r}")


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

    def validate(self) -> None:
        if self.entry_timing not in _ENTRY_TIMING_ALLOWED:
            raise ConfigError(f"entry_timing must be 'next_open', got {self.entry_timing!r}")
        if self.same_bar_policy not in _SAME_BAR_POLICIES:
            raise ConfigError(
                f"same_bar_policy must be one of {_SAME_BAR_POLICIES}, "
                f"got {self.same_bar_policy!r}"
            )
        if self.slippage_per_share < 0:
            raise ConfigError("slippage_per_share must be >= 0")
        if self.commission_per_trade < 0:
            raise ConfigError("commission_per_trade must be >= 0")
        if self.min_risk_per_share < 0:
            raise ConfigError("min_risk_per_share must be >= 0")
        if not (0 <= self.eod_exit_minute <= RTH_END_MINUTE):
            raise ConfigError(
                f"eod_exit_minute must be in [0, {RTH_END_MINUTE}], " f"got {self.eod_exit_minute}"
            )
        if self.max_hold_bars_default is not None and self.max_hold_bars_default < 1:
            raise ConfigError(
                "max_hold_bars_default must be null or an integer >= 1, "
                f"got {self.max_hold_bars_default!r}"
            )
        if not str(self.semantics_version).strip():
            raise ConfigError("semantics_version must be a non-empty string")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

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
        raw_default = config.get("max_hold_bars_default")
        max_hold: int | None
        if raw_default is None:
            max_hold = None
        else:
            max_hold = int(raw_default)

        spec = cls(
            entry_timing=config["entry_timing"],
            same_bar_policy=config["same_bar_policy"],
            slippage_per_share=float(config["slippage_per_share"]),
            commission_per_trade=float(config["commission_per_trade"]),
            min_risk_per_share=float(config["min_risk_per_share"]),
            eod_exit_minute=int(config["eod_exit_minute"]),
            allow_short=_coerce_bool(config["allow_short"], field="allow_short"),
            max_hold_bars_default=max_hold,
            semantics_version=str(config.get("semantics_version", SEMANTICS_VERSION_DEFAULT)),
        )
        spec.validate()
        return spec


def load_execution_spec(path: Path | str) -> ExecutionSpec:
    """Load ``ExecutionSpec`` from a YAML file and validate."""
    data = load_yaml(path)
    return ExecutionSpec.from_config(data)


def merge_execution_spec_with_strategy(
    base: ExecutionSpec,
    strategy_config: Mapping[str, Any],
) -> ExecutionSpec:
    """Apply strategy YAML ``risk`` / ``backtest`` overrides onto a base :class:`ExecutionSpec`.

    Central merge rule: execution YAML is primary; explicit strategy numeric fields override
    slippage, commission, EOD minute, and min risk per share when present.
    """
    slippage = base.slippage_per_share
    commission = base.commission_per_trade
    eod = base.eod_exit_minute
    min_risk = base.min_risk_per_share

    bt = strategy_config.get("backtest")
    if isinstance(bt, Mapping):
        if "slippage_per_share" in bt:
            slippage = float(bt["slippage_per_share"])
        if "commission_per_trade" in bt:
            commission = float(bt["commission_per_trade"])
        if "eod_exit_minute" in bt:
            eod = int(bt["eod_exit_minute"])

    risk = strategy_config.get("risk")
    if isinstance(risk, Mapping) and "min_risk_per_share" in risk:
        min_risk = float(risk["min_risk_per_share"])

    out = ExecutionSpec(
        entry_timing=base.entry_timing,
        same_bar_policy=base.same_bar_policy,
        slippage_per_share=slippage,
        commission_per_trade=commission,
        min_risk_per_share=min_risk,
        eod_exit_minute=eod,
        allow_short=base.allow_short,
        max_hold_bars_default=base.max_hold_bars_default,
        semantics_version=base.semantics_version,
    )
    out.validate()
    return out
