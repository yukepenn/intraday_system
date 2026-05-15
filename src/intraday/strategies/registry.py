"""Strategy registry."""

from __future__ import annotations

from intraday.core.errors import ConfigError
from intraday.core.registry import Registry
from intraday.strategies.base import StrategyDef

STRATEGY_REGISTRY: Registry[StrategyDef] = Registry("strategy")

_BUILTIN_REGISTERED = False


def register_strategy(defn: StrategyDef) -> None:
    """Register a strategy (duplicate name raises ConfigError)."""
    try:
        STRATEGY_REGISTRY.register(defn.name, defn)
    except KeyError as exc:
        raise ConfigError(str(exc)) from exc


def get_strategy(name: str) -> StrategyDef:
    try:
        return STRATEGY_REGISTRY.get(name)
    except KeyError as exc:
        raise ConfigError(f"unknown strategy: {name!r}") from exc


def list_strategies() -> list[str]:
    return STRATEGY_REGISTRY.names()


def clear_strategy_registry() -> None:
    """Remove all registrations (tests)."""
    global _BUILTIN_REGISTERED
    STRATEGY_REGISTRY.clear()
    _BUILTIN_REGISTERED = False


def register_builtin_strategies() -> None:
    """Register built-in strategies (idempotent)."""
    global _BUILTIN_REGISTERED
    if _BUILTIN_REGISTERED:
        return
    from intraday.strategies.pa.buy_sell_close_trend import PA_BUY_SELL_CLOSE_TREND_DEF

    register_strategy(PA_BUY_SELL_CLOSE_TREND_DEF)
    _BUILTIN_REGISTERED = True
