"""ExecutionSpec merge with strategy YAML (Layer1 smoke)."""

from __future__ import annotations

from intraday.core.paths import repo_root
from intraday.execution.spec import load_execution_spec, merge_execution_spec_with_strategy
from intraday.strategies.loader import load_strategy_config


def test_merge_overrides_slippage_and_min_risk() -> None:
    root = repo_root()
    base = load_execution_spec(root / "configs/execution/intraday_default.yaml")
    strat = load_strategy_config(root / "configs/strategies/base/pa_buy_sell_close_trend.yaml")
    merged = merge_execution_spec_with_strategy(base, strat)
    assert merged.slippage_per_share == float(strat["backtest"]["slippage_per_share"])
    assert merged.commission_per_trade == float(strat["backtest"]["commission_per_trade"])
    assert merged.eod_exit_minute == int(strat["backtest"]["eod_exit_minute"])
    assert merged.min_risk_per_share == float(strat["risk"]["min_risk_per_share"])
