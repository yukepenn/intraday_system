"""Backtest metrics from :class:`TradeResult` rows only (no bar recompute)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from intraday.core.types import ExitReason, RejectReason
from intraday.execution.records import TradeResult


@dataclass(frozen=True)
class BacktestMetrics:
    """Aggregates over :class:`TradeResult` — uses execution-provided R, PnL, exits."""

    total_results: int
    accepted_trades: int
    rejected_trades: int
    total_r: float
    avg_r: float
    median_r: float
    win_rate: float
    profit_factor_r: float
    max_drawdown_r: float
    avg_bars_held: float
    exit_reason_counts: dict[str, int]
    reject_reason_counts: dict[str, int]


def _enum_name(enum_cls: type, code: int) -> str:
    try:
        return enum_cls(int(code)).name
    except ValueError:
        return f"UNKNOWN_{int(code)}"


def _max_drawdown_r(cumulative: list[float]) -> float:
    if not cumulative:
        return 0.0
    peak = cumulative[0]
    max_dd = 0.0
    for v in cumulative:
        peak = max(peak, v)
        max_dd = max(max_dd, peak - v)
    return float(max_dd)


def summarize_trade_results(
    results: Sequence[TradeResult],
    *,
    count_rejected_in_metrics: bool = True,
) -> BacktestMetrics:
    """Aggregate acceptance, R-multiples, exits, and rejections from ``results`` only.

    Conventions (Phase 6):

    - ``avg_r``, ``median_r``, ``win_rate``, ``profit_factor_r``, ``max_drawdown_r``,
      and ``avg_bars_held`` use **accepted** trades only. With no accepted trades,
      these are ``0.0`` except ``median_r`` (``0.0``) and ``profit_factor_r`` (``0.0``).
    - ``profit_factor_r`` = sum of positive R divided by abs(sum of negative R).
      If there are no negative Rs but at least one positive R, returns ``inf``.
      If there are no positive Rs, returns ``0.0``.
    - ``max_drawdown_r`` is the maximum peak-to-trough drop on the **cumulative sum**
      of accepted ``r_multiple`` values (not equity curve dollars).

    If ``count_rejected_in_metrics`` is ``False`` (Layer1 grid/smoke option), rejected
    rows remain in ``total_results`` but do not populate ``rejected_trades`` or
    ``reject_reason_counts`` — use runner ``skip_counts`` / diagnostics for rejects.
    """
    seq = tuple(results)
    total_results = len(seq)
    accepted = [r for r in seq if r.accepted]
    rejected = [r for r in seq if not r.accepted]

    exit_reason_counts: dict[str, int] = {}
    reject_reason_counts: dict[str, int] = {}

    for r in accepted:
        key = _enum_name(ExitReason, r.exit_reason)
        exit_reason_counts[key] = exit_reason_counts.get(key, 0) + 1
    if count_rejected_in_metrics:
        for r in rejected:
            key = _enum_name(RejectReason, r.reject_reason)
            reject_reason_counts[key] = reject_reason_counts.get(key, 0) + 1

    n_acc = len(accepted)
    rej_metric_count = len(rejected) if count_rejected_in_metrics else 0
    if n_acc == 0:
        return BacktestMetrics(
            total_results=total_results,
            accepted_trades=0,
            rejected_trades=rej_metric_count,
            total_r=0.0,
            avg_r=0.0,
            median_r=0.0,
            win_rate=0.0,
            profit_factor_r=0.0,
            max_drawdown_r=0.0,
            avg_bars_held=0.0,
            exit_reason_counts=exit_reason_counts,
            reject_reason_counts=reject_reason_counts,
        )

    rs = [float(r.r_multiple) for r in accepted]
    pos = sum(x for x in rs if x > 0)
    neg = sum(x for x in rs if x < 0)
    wins = sum(1 for x in rs if x > 0)

    if neg == 0.0:
        pf = math.inf if pos > 0 else 0.0
    else:
        pf = pos / abs(neg)

    cum: list[float] = []
    s = 0.0
    for x in rs:
        s += x
        cum.append(s)

    sorted_r = sorted(rs)
    mid = n_acc // 2
    if n_acc % 2:
        med = sorted_r[mid]
    else:
        med = 0.5 * (sorted_r[mid - 1] + sorted_r[mid])

    bars_held = [float(r.bars_held) for r in accepted]

    return BacktestMetrics(
        total_results=total_results,
        accepted_trades=n_acc,
        rejected_trades=rej_metric_count,
        total_r=float(sum(rs)),
        avg_r=float(sum(rs) / n_acc),
        median_r=float(med),
        win_rate=float(wins / n_acc),
        profit_factor_r=float(pf) if math.isfinite(pf) else pf,
        max_drawdown_r=_max_drawdown_r(cum),
        avg_bars_held=float(sum(bars_held) / n_acc),
        exit_reason_counts=exit_reason_counts,
        reject_reason_counts=reject_reason_counts,
    )
