"""Layer1 smoke run result types."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from intraday.backtest.metrics import BacktestMetrics


@dataclass(frozen=True)
class Layer1SmokeResult:
    run_id: str
    symbol: str
    start: str
    end: str
    rows: int
    feature_count: int
    signal_entries: int
    valid_intents: int
    executed_results: int
    metrics: BacktestMetrics
    signal_hash: str
    feature_hash: str
    execution_mode: str
    skip_counts: dict[str, int]
    fast_parity_checked: bool
    runtime_seconds: float


def layer1_smoke_result_to_jsonable(res: Layer1SmokeResult) -> dict[str, Any]:
    """JSON-serializable summary (``inf`` for profit factor → string)."""
    m = res.metrics
    d = asdict(res)
    md = asdict(m)
    pfr = md["profit_factor_r"]
    if pfr == float("inf"):
        md["profit_factor_r"] = "inf"
    d["metrics"] = md
    return d
