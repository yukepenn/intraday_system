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


@dataclass(frozen=True)
class Layer1GridRow:
    run_id: str
    combo_id: str
    config_hash: str
    params_json: str
    signal_entries: int
    valid_intents: int
    executed_results: int
    accepted_trades: int
    rejected_trades: int
    total_r: float
    avg_r: float
    median_r: float
    win_rate: float
    profit_factor_r: float
    max_drawdown_r: float
    avg_bars_held: float
    avg_risk_per_share: float
    median_risk_per_share: float
    p10_risk_per_share: float
    p90_risk_per_share: float
    avg_cost_to_risk: float
    median_cost_to_risk: float
    exit_reason_counts_json: str
    reject_reason_counts_json: str
    skip_reason_counts_json: str
    adapter_skip_reasons_json: str
    feature_hash: str
    signal_hash: str
    execution_mode: str


@dataclass(frozen=True)
class Layer1GridResult:
    run_id: str
    symbol: str
    start: str
    end: str
    combo_count: int
    rows: tuple[Layer1GridRow, ...]
    feature_hash: str
    execution_mode: str
