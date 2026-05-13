"""Execution package: ExecutionSpec, TradeIntent, reference + fast simulators."""

from intraday.execution.intent import TradeIntent
from intraday.execution.records import TradeResult
from intraday.execution.spec import ExecutionSpec

__all__ = ["ExecutionSpec", "TradeIntent", "TradeResult"]
