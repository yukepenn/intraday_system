"""Strategy registry tests."""

from __future__ import annotations

import pytest
from intraday.core.errors import ConfigError
from intraday.strategies.base import StrategyDef
from intraday.strategies.registry import (
    clear_strategy_registry,
    get_strategy,
    list_strategies,
    register_builtin_strategies,
    register_strategy,
)


def setup_function() -> None:
    clear_strategy_registry()


def test_builtin_pa_registered() -> None:
    register_builtin_strategies()
    names = list_strategies()
    assert "pa_buy_sell_close_trend" in names
    defn = get_strategy("pa_buy_sell_close_trend")
    assert defn.family == "pa"


def test_unknown_strategy_raises() -> None:
    register_builtin_strategies()
    with pytest.raises(ConfigError, match="unknown strategy"):
        get_strategy("not_a_strategy")


def test_duplicate_registration_raises() -> None:
    register_builtin_strategies()
    defn = get_strategy("pa_buy_sell_close_trend")

    def _noop(_b, _f, _c):
        return None  # type: ignore[return-value]

    dup = StrategyDef(
        name=defn.name,
        family="x",
        version="v",
        required_feature_set="x",
        signal_contract_version="signal_v1",
        generate_reference=_noop,
    )
    with pytest.raises(ConfigError, match="already registered"):
        register_strategy(dup)
