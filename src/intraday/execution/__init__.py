"""Execution package: ExecutionSpec, TradeIntent, reference + fast simulators."""

from intraday.execution.fast import simulate_trade_path_fast
from intraday.execution.intent import TradeIntent
from intraday.execution.materialize import MaterializedTrade, materialize_trade
from intraday.execution.parity import assert_trade_results_equal, compare_trade_results
from intraday.execution.records import TradeResult
from intraday.execution.reference import simulate_trade_path_reference
from intraday.execution.spec import (
    ExecutionSpec,
    load_execution_spec,
    merge_execution_spec_with_strategy,
)

__all__ = [
    "ExecutionSpec",
    "TradeIntent",
    "TradeResult",
    "MaterializedTrade",
    "materialize_trade",
    "simulate_trade_path_reference",
    "simulate_trade_path_fast",
    "load_execution_spec",
    "merge_execution_spec_with_strategy",
    "compare_trade_results",
    "assert_trade_results_equal",
]
