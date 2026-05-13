"""Strategy registry."""

from __future__ import annotations

from intraday.core.registry import Registry
from intraday.strategies.base import StrategyDef

STRATEGY_REGISTRY: Registry[StrategyDef] = Registry("strategy")
