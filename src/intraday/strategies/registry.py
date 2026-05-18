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
    from intraday.strategies.cci.extreme_snapback import CCI_EXTREME_SNAPBACK_DEF
    from intraday.strategies.gap.acceptance_failure import GAP_ACCEPTANCE_FAILURE_DEF
    from intraday.strategies.levels.prior_day_level_trap import PRIOR_DAY_LEVEL_TRAP_DEF
    from intraday.strategies.orb.continuation import ORB_CONTINUATION_DEF
    from intraday.strategies.orb.failed_orb import FAILED_ORB_DEF
    from intraday.strategies.orb.retest_continuation import ORB_RETEST_CONTINUATION_DEF
    from intraday.strategies.pa.buy_sell_close_trend import PA_BUY_SELL_CLOSE_TREND_DEF
    from intraday.strategies.stochastic.oversold_cross import STOCHASTIC_OVERSOLD_CROSS_DEF
    from intraday.strategies.vwap.reclaim_reject import VWAP_RECLAIM_REJECT_DEF
    from intraday.strategies.vwap.trend_pullback import VWAP_TREND_PULLBACK_DEF

    for defn in (
        PA_BUY_SELL_CLOSE_TREND_DEF,
        ORB_CONTINUATION_DEF,
        ORB_RETEST_CONTINUATION_DEF,
        FAILED_ORB_DEF,
        GAP_ACCEPTANCE_FAILURE_DEF,
        VWAP_TREND_PULLBACK_DEF,
        VWAP_RECLAIM_REJECT_DEF,
        PRIOR_DAY_LEVEL_TRAP_DEF,
        CCI_EXTREME_SNAPBACK_DEF,
        STOCHASTIC_OVERSOLD_CROSS_DEF,
    ):
        register_strategy(defn)
    _BUILTIN_REGISTERED = True
