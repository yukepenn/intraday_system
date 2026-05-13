"""Execution package: ExecutionSpec, TradeIntent, reference + fast simulators."""

from intraday.execution.intent import TradeIntent
from intraday.execution.materialize import MaterializedTrade, materialize_trade
from intraday.execution.records import TradeResult
from intraday.execution.reference import simulate_trade_path_reference
from intraday.execution.spec import ExecutionSpec, load_execution_spec

__all__ = [
    "ExecutionSpec",
    "TradeIntent",
    "TradeResult",
    "MaterializedTrade",
    "materialize_trade",
    "simulate_trade_path_reference",
    "load_execution_spec",
]
