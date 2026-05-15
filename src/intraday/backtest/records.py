"""Backtest record aggregation.

Phase 6: per-trade rows are :class:`intraday.execution.records.TradeResult` (execution-owned).
Batch array layouts (`TradeRecordArray`) may be added later for Layer1 sweeps.
"""

from __future__ import annotations
