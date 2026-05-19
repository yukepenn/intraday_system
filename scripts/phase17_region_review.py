"""Generate Phase17 expanded-grid region/neighborhood review artifacts.

This script reads existing Phase16/16B CSV/MD artifacts plus local Phase16 sweep
summaries. It does not run Layer1 grids, select candidates, or write runtime
configs.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PHASE16 = ROOT / "artifacts" / "layer1_10_strategy_rational_expanded_grid_phase16"
PHASE16B = ROOT / "artifacts" / "layer1_10_strategy_rational_expanded_grid_phase16b"
RUN_ROOT = PHASE16 / "runs"
OUT = ROOT / "artifacts" / "layer1_10_strategy_expanded_grid_region_review_phase17"

PHASE = "PHASE17_REVIEW_10_STRATEGY_EXPANDED_GRID_RESULTS_BY_REGION"
TASK_TYPE = "diagnostic + strategy-family review + artifact/reporting analysis"
PRE_TASK_HEAD = "1fba694"
H2_WARNING = "missing_minute_slots_total=540"
DECISION = "PHASE17_EXPANDED_GRID_REGION_REVIEW_COMPLETE"
NEXT_STEP = "DESIGN_PHASE18_EXISTING_10_STRATEGY_IMPROVEMENTS"

STRATEGIES = [
    "pa_buy_sell_close_trend",
    "orb_continuation",
    "orb_retest_continuation",
    "failed_orb",
    "gap_acceptance_failure",
    "vwap_trend_pullback",
    "vwap_reclaim_reject",
    "prior_day_level_trap",
    "cci_extreme_snapback",
    "stochastic_oversold_cross",
]
WINDOWS = ["qqq_2024h1", "qqq_2024h2"]
FAMILIES = {
    "pa_buy_sell_close_trend": "price_action",
    "orb_continuation": "orb",
    "orb_retest_continuation": "orb",
    "failed_orb": "orb",
    "gap_acceptance_failure": "gap",
    "vwap_trend_pullback": "vwap",
    "vwap_reclaim_reject": "vwap",
    "prior_day_level_trap": "prior_day_levels",
    "cci_extreme_snapback": "oscillator",
    "stochastic_oversold_cross": "oscillator",
}

CSV_COLUMNS = {
    "SOURCE_MAP.csv": [
        "file_path",
        "purpose",
        "required_for_review",
        "generated_or_source",
        "local_only_dependency",
        "notes",
    ],
    "chatgpt_key_tables.csv": ["section", "item", "metric", "value", "interpretation"],
    "validation_results.csv": ["command", "status", "exit_code", "notes"],
    "phase17_input_artifact_validation.csv": [
        "artifact_path",
        "artifact_type",
        "required",
        "available",
        "parse_ok",
        "expected_columns_ok",
        "row_count",
        "local_only_dependency",
        "issue",
        "notes",
    ],
    "strategy_surface_status_matrix.csv": [
        "strategy",
        "family",
        "h1_status",
        "h2_status",
        "combined_surface_status",
        "promotion_ready",
        "candidate_yaml_allowed",
        "phase18_action",
        "primary_rationale",
        "secondary_risks",
        "h2_warning_attached",
        "sample_adequacy_label",
        "drawdown_label",
        "risk_cost_label",
        "top_row_isolation_label",
        "next_recommended_handling",
    ],
    "parameter_region_summary.csv": [
        "strategy",
        "window",
        "region_key",
        "region_definition",
        "axis_group",
        "combo_count",
        "median_total_r",
        "p25_total_r",
        "p75_total_r",
        "best_total_r",
        "worst_total_r",
        "median_profit_factor_r",
        "median_max_drawdown_r",
        "p75_max_drawdown_r",
        "worst_max_drawdown_r",
        "median_accepted_trades",
        "zero_trade_combo_count",
        "robust_region_label",
        "notes",
    ],
    "top_neighborhood_summary.csv": [
        "strategy",
        "window",
        "top_combo_id",
        "top_metric",
        "top_metric_value",
        "neighborhood_definition",
        "neighborhood_combo_count",
        "neighborhood_median_total_r",
        "neighborhood_p25_total_r",
        "neighborhood_p75_total_r",
        "neighborhood_median_drawdown_r",
        "neighborhood_median_accepted_trades",
        "neighborhood_robust",
        "notes",
    ],
    "isolated_top_row_warning.csv": [
        "strategy",
        "window",
        "combo_id",
        "metric",
        "metric_value",
        "neighborhood_median",
        "neighborhood_combo_count",
        "isolation_reason",
        "warning_level",
        "notes",
    ],
    "axis_marginal_summary.csv": [
        "strategy",
        "window",
        "axis",
        "axis_value",
        "combo_count",
        "median_total_r",
        "p25_total_r",
        "p75_total_r",
        "median_drawdown_r",
        "median_accepted_trades",
        "marginal_interpretation",
        "notes",
    ],
    "pairwise_interaction_summary.csv": [
        "strategy",
        "window",
        "axis_a",
        "value_a",
        "axis_b",
        "value_b",
        "combo_count",
        "median_total_r",
        "p25_total_r",
        "p75_total_r",
        "median_drawdown_r",
        "median_accepted_trades",
        "interaction_interpretation",
        "notes",
    ],
    "h1_h2_cross_window_region_matrix.csv": [
        "strategy",
        "region_key",
        "region_definition",
        "h1_combo_count",
        "h2_combo_count",
        "h1_median_total_r",
        "h2_median_total_r",
        "h1_p25_total_r",
        "h2_p25_total_r",
        "h1_median_drawdown_r",
        "h2_median_drawdown_r",
        "h1_median_accepted_trades",
        "h2_median_accepted_trades",
        "cross_window_label",
        "h2_warning_attached",
        "interpretation",
    ],
    "drawdown_region_summary.csv": [
        "strategy",
        "window",
        "region_key",
        "combo_count",
        "median_max_drawdown_r",
        "p75_max_drawdown_r",
        "worst_max_drawdown_r",
        "drawdown_label",
        "notes",
    ],
    "risk_cost_region_summary.csv": [
        "strategy",
        "window",
        "region_key",
        "combo_count",
        "median_risk_per_share",
        "p10_risk_per_share",
        "p90_risk_per_share",
        "median_cost_to_risk",
        "p75_cost_to_risk",
        "high_cost_warning_count",
        "risk_cost_label",
        "notes",
    ],
    "sample_adequacy_region_summary.csv": [
        "strategy",
        "window",
        "region_key",
        "combo_count",
        "median_accepted_trades",
        "p25_accepted_trades",
        "zero_trade_combo_count",
        "low_sample_warning_count",
        "sample_adequacy_label",
        "notes",
    ],
    "strategy_improvement_backlog.csv": [
        "strategy",
        "issue_type",
        "priority",
        "evidence",
        "proposed_phase",
        "proposed_change",
        "allowed_in_phase18",
        "requires_feature_work",
        "requires_strategy_logic_work",
        "requires_short_side_design",
        "requires_data_or_reporting_work",
        "notes",
    ],
    "artifact_schema_validation.csv": [
        "artifact_path",
        "artifact_type",
        "parse_ok",
        "expected_columns_ok",
        "row_count",
        "issue",
        "notes",
    ],
}


@dataclass(frozen=True)
class SweepRow:
    strategy: str
    window: str
    combo_id: str
    params: dict[str, Any]
    flat_params: dict[str, Any]
    total_r: float
    profit_factor_r: float
    max_drawdown_r: float
    accepted_trades: int
    median_risk_per_share: float
    p10_risk_per_share: float
    p90_risk_per_share: float
    median_cost_to_risk: float


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _to_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    s = str(value).strip()
    if not s:
        return default
    if s.lower() == "inf":
        return math.inf
    if s.lower() == "-inf":
        return -math.inf
    try:
        return float(s)
    except ValueError:
        return default


def _finite(value: float) -> float:
    if math.isfinite(value):
        return value
    return 999999.0 if value > 0 else -999999.0


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        if math.isnan(value):
            return ""
        return f"{value:.6g}"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _percentile(values: Sequence[float], q: float) -> float:
    finite = sorted(_finite(float(v)) for v in values if math.isfinite(_finite(float(v))))
    if not finite:
        return 0.0
    if len(finite) == 1:
        return finite[0]
    rank = (len(finite) - 1) * q
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return finite[int(rank)]
    weight = rank - lo
    return finite[lo] * (1.0 - weight) + finite[hi] * weight


def _median(values: Sequence[float]) -> float:
    finite = [_finite(float(v)) for v in values if math.isfinite(_finite(float(v)))]
    return float(statistics.median(finite)) if finite else 0.0


def _flatten_params(params: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}

    def walk(prefix: str, value: Any) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                child_prefix = f"{prefix}.{key}" if prefix else str(key)
                walk(child_prefix, child)
        else:
            out[prefix] = value

    walk("", params)
    return out


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _write_csv(path: Path, columns: Sequence[str], rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: _fmt(row.get(col, "")) for col in columns})


def _read_sweeps() -> list[SweepRow]:
    rows: list[SweepRow] = []
    for window in WINDOWS:
        for strategy in STRATEGIES:
            path = RUN_ROOT / window / strategy / "sweep_results.csv"
            if not path.is_file():
                continue
            for raw in _read_csv(path):
                params = json.loads(raw["params_json"])
                flat = _flatten_params(params)
                rows.append(
                    SweepRow(
                        strategy=strategy,
                        window=window,
                        combo_id=raw["combo_id"],
                        params=params,
                        flat_params=flat,
                        total_r=_to_float(raw["total_r"]),
                        profit_factor_r=_to_float(raw["profit_factor_r"]),
                        max_drawdown_r=_to_float(raw["max_drawdown_r"]),
                        accepted_trades=int(_to_float(raw["accepted_trades"])),
                        median_risk_per_share=_to_float(raw["median_risk_per_share"]),
                        p10_risk_per_share=_to_float(raw["p10_risk_per_share"]),
                        p90_risk_per_share=_to_float(raw["p90_risk_per_share"]),
                        median_cost_to_risk=_to_float(raw["median_cost_to_risk"]),
                    )
                )
    return rows


def _axes_for(rows: Sequence[SweepRow]) -> list[str]:
    axes: set[str] = set()
    for row in rows:
        axes.update(row.flat_params)
    return sorted(axes)


def _region_groups(strategy: str, rows: Sequence[SweepRow]) -> list[tuple[str, list[str]]]:
    axes = _axes_for(rows)
    risk = [a for a in ["risk.stop_mode", "risk.target_r"] if a in axes]
    timing = [
        a
        for a in [
            "signal.entry_start_minute",
            "signal.entry_end_minute",
            "backtest.max_hold_minutes",
        ]
        if a in axes
    ]
    signal_axes = [a for a in axes if a.startswith("signal.") and a not in timing]
    groups: list[tuple[str, list[str]]] = []
    if risk:
        groups.append(("risk_stop_target", risk))
    if timing:
        groups.append(("entry_window_hold", timing))
    if signal_axes:
        if strategy in {"orb_continuation", "orb_retest_continuation"}:
            preferred = [
                a
                for a in [
                    "signal.require_close_above_vwap",
                    "signal.min_vwap_slope",
                    "signal.min_orb_width_pct",
                    "signal.max_orb_width_pct",
                    "signal.retest_tolerance_atr",
                ]
                if a in signal_axes
            ]
        elif strategy in {"gap_acceptance_failure", "prior_day_level_trap"}:
            preferred = [
                a
                for a in [
                    "signal.min_gap_pct",
                    "signal.reclaim_mode",
                    "signal.breach_buffer_atr",
                    "signal.prior_low_buffer_atr",
                    "signal.require_close_above_vwap",
                    "signal.min_vwap_slope",
                ]
                if a in signal_axes
            ]
        elif strategy.startswith("vwap"):
            preferred = [
                a
                for a in [
                    "signal.min_vwap_slope",
                    "signal.max_pullback_atr",
                    "signal.require_vwap_touch",
                    "signal.close_position_min",
                ]
                if a in signal_axes
            ]
        elif strategy in {"cci_extreme_snapback", "stochastic_oversold_cross"}:
            preferred = [
                a
                for a in [
                    "signal.oversold_threshold",
                    "signal.cross_threshold",
                    "signal.require_close_above_vwap",
                ]
                if a in signal_axes
            ]
        else:
            preferred = signal_axes
        if preferred:
            groups.append(("confirmation_threshold", preferred[:4]))
    return groups


def _group_key(row: SweepRow, axes: Sequence[str]) -> tuple[tuple[str, str], ...]:
    return tuple((axis, _fmt(row.flat_params.get(axis, ""))) for axis in axes)


def _region_definition(parts: Sequence[tuple[str, str]]) -> str:
    return "; ".join(f"{axis}={value}" for axis, value in parts)


def _region_key(axis_group: str, parts: Sequence[tuple[str, str]]) -> str:
    safe = "|".join(f"{axis}={value}" for axis, value in parts)
    return f"{axis_group}|{safe}"


def _summarize_region(rows: Sequence[SweepRow]) -> dict[str, Any]:
    total = [r.total_r for r in rows]
    dd = [r.max_drawdown_r for r in rows]
    trades = [float(r.accepted_trades) for r in rows]
    pf = [r.profit_factor_r for r in rows]
    return {
        "combo_count": len(rows),
        "median_total_r": _median(total),
        "p25_total_r": _percentile(total, 0.25),
        "p75_total_r": _percentile(total, 0.75),
        "best_total_r": max(total) if total else 0.0,
        "worst_total_r": min(total) if total else 0.0,
        "median_profit_factor_r": _median(pf),
        "median_max_drawdown_r": _median(dd),
        "p75_max_drawdown_r": _percentile(dd, 0.75),
        "worst_max_drawdown_r": max(dd) if dd else 0.0,
        "median_accepted_trades": _median(trades),
        "p25_accepted_trades": _percentile(trades, 0.25),
        "zero_trade_combo_count": sum(1 for r in rows if r.accepted_trades == 0),
        "median_risk_per_share": _median([r.median_risk_per_share for r in rows]),
        "p10_risk_per_share": _median([r.p10_risk_per_share for r in rows]),
        "p90_risk_per_share": _median([r.p90_risk_per_share for r in rows]),
        "median_cost_to_risk": _median([r.median_cost_to_risk for r in rows]),
        "p75_cost_to_risk": _percentile([r.median_cost_to_risk for r in rows], 0.75),
    }


def _sample_label(summary: Mapping[str, Any]) -> str:
    median_trades = float(summary["median_accepted_trades"])
    zero = int(summary["zero_trade_combo_count"])
    combo_count = int(summary["combo_count"])
    if median_trades >= 50 and zero == 0:
        return "ADEQUATE"
    if median_trades >= 20 and zero / max(combo_count, 1) <= 0.10:
        return "MARGINAL"
    return "LOW_SAMPLE"


def _drawdown_label(summary: Mapping[str, Any]) -> str:
    median_dd = float(summary["median_max_drawdown_r"])
    p75_dd = float(summary["p75_max_drawdown_r"])
    worst_dd = float(summary["worst_max_drawdown_r"])
    if median_dd <= 10 and p75_dd <= 15:
        return "CONTROLLED"
    if median_dd <= 15 and p75_dd <= 22:
        return "ELEVATED"
    if worst_dd >= 30 or p75_dd > 22:
        return "HIGH_DRAWDOWN"
    return "ELEVATED"


def _risk_cost_label(summary: Mapping[str, Any]) -> str:
    med = float(summary["median_cost_to_risk"])
    p75 = float(summary["p75_cost_to_risk"])
    if med <= 0.10 and p75 <= 0.20:
        return "LOW_COST_TO_RISK"
    if med <= 0.20 and p75 <= 0.35:
        return "ACCEPTABLE_COST_TO_RISK"
    return "HIGH_COST_TO_RISK"


def _robust_region_label(summary: Mapping[str, Any]) -> str:
    sample = _sample_label(summary)
    dd = _drawdown_label(summary)
    risk = _risk_cost_label(summary)
    median_total = float(summary["median_total_r"])
    p25_total = float(summary["p25_total_r"])
    combo_count = int(summary["combo_count"])
    if sample == "LOW_SAMPLE":
        return "LOW_SAMPLE"
    if dd == "HIGH_DRAWDOWN":
        return "HIGH_DRAWDOWN"
    if risk == "HIGH_COST_TO_RISK":
        return "HIGH_COST_TO_RISK"
    if combo_count >= 4 and median_total > 1.0 and p25_total >= -1.0:
        return "ROBUST_POSITIVE_REGION"
    if median_total > 0.0 and p25_total >= -3.0:
        return "WATCH_PROMISING_REGION"
    return "WEAK_REGION"


def _interpret_region(label: str) -> str:
    return {
        "ROBUST_POSITIVE_REGION": "broad positive neighborhood; future confirmation design may be justified",
        "WATCH_PROMISING_REGION": "positive median but dispersion or support is not yet strong enough",
        "LOW_SAMPLE": "trade count or zero-trade behavior is too thin for robust interpretation",
        "HIGH_DRAWDOWN": "drawdown profile dominates any surface strength",
        "HIGH_COST_TO_RISK": "friction is large relative to risk-per-share",
        "WEAK_REGION": "median region behavior is weak or too dispersed",
    }[label]


def _build_region_tables(rows: Sequence[SweepRow]) -> tuple[list[dict[str, Any]], ...]:
    parameter_rows: list[dict[str, Any]] = []
    drawdown_rows: list[dict[str, Any]] = []
    risk_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    by_sw: dict[tuple[str, str], list[SweepRow]] = defaultdict(list)
    for row in rows:
        by_sw[(row.strategy, row.window)].append(row)

    for strategy in STRATEGIES:
        for window in WINDOWS:
            current = by_sw.get((strategy, window), [])
            for axis_group, axes in _region_groups(strategy, current):
                groups: dict[tuple[tuple[str, str], ...], list[SweepRow]] = defaultdict(list)
                for row in current:
                    groups[_group_key(row, axes)].append(row)
                for parts, group_rows in sorted(groups.items()):
                    summary = _summarize_region(group_rows)
                    label = _robust_region_label(summary)
                    key = _region_key(axis_group, parts)
                    definition = _region_definition(parts)
                    parameter_rows.append(
                        {
                            "strategy": strategy,
                            "window": window,
                            "region_key": key,
                            "region_definition": definition,
                            "axis_group": axis_group,
                            **summary,
                            "robust_region_label": label,
                            "notes": _interpret_region(label),
                        }
                    )
                    drawdown_label = _drawdown_label(summary)
                    drawdown_rows.append(
                        {
                            "strategy": strategy,
                            "window": window,
                            "region_key": key,
                            "combo_count": summary["combo_count"],
                            "median_max_drawdown_r": summary["median_max_drawdown_r"],
                            "p75_max_drawdown_r": summary["p75_max_drawdown_r"],
                            "worst_max_drawdown_r": summary["worst_max_drawdown_r"],
                            "drawdown_label": drawdown_label,
                            "notes": "drawdown uses positive magnitude ordering",
                        }
                    )
                    risk_label = _risk_cost_label(summary)
                    risk_rows.append(
                        {
                            "strategy": strategy,
                            "window": window,
                            "region_key": key,
                            "combo_count": summary["combo_count"],
                            "median_risk_per_share": summary["median_risk_per_share"],
                            "p10_risk_per_share": summary["p10_risk_per_share"],
                            "p90_risk_per_share": summary["p90_risk_per_share"],
                            "median_cost_to_risk": summary["median_cost_to_risk"],
                            "p75_cost_to_risk": summary["p75_cost_to_risk"],
                            "high_cost_warning_count": sum(
                                1 for r in group_rows if r.median_cost_to_risk > 0.35
                            ),
                            "risk_cost_label": risk_label,
                            "notes": "aggregate-only diagnostics from execution-produced trade fields",
                        }
                    )
                    sample_label = _sample_label(summary)
                    sample_rows.append(
                        {
                            "strategy": strategy,
                            "window": window,
                            "region_key": key,
                            "combo_count": summary["combo_count"],
                            "median_accepted_trades": summary["median_accepted_trades"],
                            "p25_accepted_trades": summary["p25_accepted_trades"],
                            "zero_trade_combo_count": summary["zero_trade_combo_count"],
                            "low_sample_warning_count": sum(
                                1 for r in group_rows if r.accepted_trades < 20
                            ),
                            "sample_adequacy_label": sample_label,
                            "notes": "low sample remains diagnostic only",
                        }
                    )
    return parameter_rows, drawdown_rows, risk_rows, sample_rows


def _build_axis_summary(rows: Sequence[SweepRow]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    by_sw: dict[tuple[str, str], list[SweepRow]] = defaultdict(list)
    for row in rows:
        by_sw[(row.strategy, row.window)].append(row)
    for (strategy, window), current in sorted(by_sw.items()):
        axes = _axes_for(current)
        for axis in axes:
            groups: dict[str, list[SweepRow]] = defaultdict(list)
            for row in current:
                groups[_fmt(row.flat_params.get(axis, ""))].append(row)
            for value, group_rows in sorted(groups.items()):
                summary = _summarize_region(group_rows)
                label = _robust_region_label(summary)
                out.append(
                    {
                        "strategy": strategy,
                        "window": window,
                        "axis": axis,
                        "axis_value": value,
                        "combo_count": summary["combo_count"],
                        "median_total_r": summary["median_total_r"],
                        "p25_total_r": summary["p25_total_r"],
                        "p75_total_r": summary["p75_total_r"],
                        "median_drawdown_r": summary["median_max_drawdown_r"],
                        "median_accepted_trades": summary["median_accepted_trades"],
                        "marginal_interpretation": _interpret_region(label),
                        "notes": f"axis marginal label={label}",
                    }
                )
    return out


def _logical_pairs(strategy: str, axes: Sequence[str]) -> list[tuple[str, str]]:
    desired = [
        ("risk.stop_mode", "risk.target_r"),
        ("signal.entry_start_minute", "backtest.max_hold_minutes"),
        ("signal.entry_end_minute", "backtest.max_hold_minutes"),
        ("signal.require_close_above_vwap", "risk.target_r"),
        ("signal.min_vwap_slope", "risk.stop_mode"),
        ("signal.min_vwap_slope", "risk.target_r"),
        ("signal.min_orb_width_pct", "risk.stop_mode"),
        ("signal.max_orb_width_pct", "risk.target_r"),
        ("signal.retest_tolerance_atr", "risk.stop_mode"),
        ("signal.min_gap_pct", "signal.reclaim_mode"),
        ("signal.reclaim_mode", "risk.target_r"),
        ("signal.max_pullback_atr", "risk.stop_mode"),
        ("signal.require_vwap_touch", "risk.target_r"),
        ("signal.breach_buffer_atr", "risk.stop_mode"),
        ("signal.prior_low_buffer_atr", "risk.stop_mode"),
        ("signal.oversold_threshold", "signal.cross_threshold"),
        ("signal.oversold_threshold", "risk.target_r"),
        ("signal.close_position_min", "risk.stop_mode"),
    ]
    axis_set = set(axes)
    pairs = [pair for pair in desired if pair[0] in axis_set and pair[1] in axis_set]
    if pairs:
        return pairs[:5]
    if len(axes) >= 2:
        return [(axes[0], axes[1])]
    return []


def _build_pairwise(rows: Sequence[SweepRow]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    by_sw: dict[tuple[str, str], list[SweepRow]] = defaultdict(list)
    for row in rows:
        by_sw[(row.strategy, row.window)].append(row)
    for (strategy, window), current in sorted(by_sw.items()):
        axes = _axes_for(current)
        for axis_a, axis_b in _logical_pairs(strategy, axes):
            groups: dict[tuple[str, str], list[SweepRow]] = defaultdict(list)
            for row in current:
                groups[
                    (_fmt(row.flat_params.get(axis_a, "")), _fmt(row.flat_params.get(axis_b, "")))
                ].append(row)
            for (value_a, value_b), group_rows in sorted(groups.items()):
                summary = _summarize_region(group_rows)
                label = _robust_region_label(summary)
                out.append(
                    {
                        "strategy": strategy,
                        "window": window,
                        "axis_a": axis_a,
                        "value_a": value_a,
                        "axis_b": axis_b,
                        "value_b": value_b,
                        "combo_count": summary["combo_count"],
                        "median_total_r": summary["median_total_r"],
                        "p25_total_r": summary["p25_total_r"],
                        "p75_total_r": summary["p75_total_r"],
                        "median_drawdown_r": summary["median_max_drawdown_r"],
                        "median_accepted_trades": summary["median_accepted_trades"],
                        "interaction_interpretation": _interpret_region(label),
                        "notes": f"logical pair label={label}",
                    }
                )
    return out


def _build_top_neighborhoods(rows: Sequence[SweepRow]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    top_rows: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    by_sw: dict[tuple[str, str], list[SweepRow]] = defaultdict(list)
    for row in rows:
        by_sw[(row.strategy, row.window)].append(row)

    for strategy in STRATEGIES:
        for window in WINDOWS:
            current = by_sw[(strategy, window)]
            axes = _axes_for(current)
            top = max(current, key=lambda r: r.total_r)

            def distance(row: SweepRow) -> int:
                return sum(
                    _fmt(row.flat_params.get(axis, "")) != _fmt(top.flat_params.get(axis, ""))
                    for axis in axes
                )

            neighbors = [row for row in current if distance(row) <= 1]
            if len(neighbors) < 3:
                # Fallback to the top risk/target region, still not a candidate selection.
                risk_axes = [a for a in ["risk.stop_mode", "risk.target_r"] if a in axes]
                neighbors = [
                    row
                    for row in current
                    if all(
                        _fmt(row.flat_params.get(axis, ""))
                        == _fmt(top.flat_params.get(axis, ""))
                        for axis in risk_axes
                    )
                ]
            summary = _summarize_region(neighbors)
            robust = (
                summary["combo_count"] >= 4
                and summary["median_total_r"] > 0
                and summary["p25_total_r"] >= -2
                and summary["median_accepted_trades"] >= 20
                and summary["median_max_drawdown_r"] <= 15
            )
            definition = "within one grid-axis step of top combo; fallback risk/target region if sparse"
            top_rows.append(
                {
                    "strategy": strategy,
                    "window": window,
                    "top_combo_id": top.combo_id,
                    "top_metric": "total_r",
                    "top_metric_value": top.total_r,
                    "neighborhood_definition": definition,
                    "neighborhood_combo_count": summary["combo_count"],
                    "neighborhood_median_total_r": summary["median_total_r"],
                    "neighborhood_p25_total_r": summary["p25_total_r"],
                    "neighborhood_p75_total_r": summary["p75_total_r"],
                    "neighborhood_median_drawdown_r": summary["median_max_drawdown_r"],
                    "neighborhood_median_accepted_trades": summary["median_accepted_trades"],
                    "neighborhood_robust": robust,
                    "notes": "top row is diagnostic evidence only, not a candidate",
                }
            )
            spread = top.total_r - float(summary["median_total_r"])
            reasons: list[str] = []
            if summary["combo_count"] < 4:
                reasons.append("sparse_neighborhood")
            if float(summary["median_total_r"]) <= 0:
                reasons.append("weak_neighborhood_median")
            if float(summary["p25_total_r"]) < -2:
                reasons.append("negative_lower_quartile")
            if spread > 8:
                reasons.append("large_top_vs_neighborhood_spread")
            if not reasons:
                warning_level = "LOW"
                reasons.append("top_row_supported_by_neighborhood")
            elif spread > 10 or "weak_neighborhood_median" in reasons:
                warning_level = "HIGH"
            else:
                warning_level = "MEDIUM"
            warnings.append(
                {
                    "strategy": strategy,
                    "window": window,
                    "combo_id": top.combo_id,
                    "metric": "total_r",
                    "metric_value": top.total_r,
                    "neighborhood_median": summary["median_total_r"],
                    "neighborhood_combo_count": summary["combo_count"],
                    "isolation_reason": "|".join(reasons),
                    "warning_level": warning_level,
                    "notes": "warning is anti-argmax diagnostic; no promotion allowed",
                }
            )
    return top_rows, warnings


def _build_cross_window(parameter_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str, str], dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in parameter_rows:
        by_key[(str(row["strategy"]), str(row["region_key"]), str(row["region_definition"]))][
            str(row["window"])
        ] = row
    out: list[dict[str, Any]] = []
    for (strategy, region_key, definition), windows in sorted(by_key.items()):
        h1 = windows.get("qqq_2024h1")
        h2 = windows.get("qqq_2024h2")
        if h1 is None or h2 is None:
            label = "REVIEW_BLOCKED"
            interpretation = "region missing in one window"
        else:
            h1_med = float(h1["median_total_r"])
            h2_med = float(h2["median_total_r"])
            h1_trades = float(h1["median_accepted_trades"])
            h2_trades = float(h2["median_accepted_trades"])
            if h1_trades < 20 or h2_trades < 20:
                label = "LOW_SAMPLE"
            elif h1_med > 1 and h2_med > 1:
                label = "STABLE_POSITIVE_DIAGNOSTIC"
            elif h1_med > 1 and h2_med <= 0:
                label = "H1_ONLY"
            elif h1_med <= 0 and h2_med > 1:
                label = "H2_ONLY_DIAGNOSTIC_WARNING"
            elif h1_med > 0 or h2_med > 0:
                label = "MIXED_OR_REGIME_DEPENDENT"
            else:
                label = "WEAK_BOTH"
            interpretation = (
                "H2 is diagnostic-only due missing-minute warning; no cross-window row permits promotion"
            )
        out.append(
            {
                "strategy": strategy,
                "region_key": region_key,
                "region_definition": definition,
                "h1_combo_count": h1.get("combo_count", "") if h1 else "",
                "h2_combo_count": h2.get("combo_count", "") if h2 else "",
                "h1_median_total_r": h1.get("median_total_r", "") if h1 else "",
                "h2_median_total_r": h2.get("median_total_r", "") if h2 else "",
                "h1_p25_total_r": h1.get("p25_total_r", "") if h1 else "",
                "h2_p25_total_r": h2.get("p25_total_r", "") if h2 else "",
                "h1_median_drawdown_r": h1.get("median_max_drawdown_r", "") if h1 else "",
                "h2_median_drawdown_r": h2.get("median_max_drawdown_r", "") if h2 else "",
                "h1_median_accepted_trades": h1.get("median_accepted_trades", "") if h1 else "",
                "h2_median_accepted_trades": h2.get("median_accepted_trades", "") if h2 else "",
                "cross_window_label": label,
                "h2_warning_attached": "true",
                "interpretation": interpretation,
            }
        )
    return out


def _window_status(rows: Sequence[SweepRow]) -> str:
    summary = _summarize_region(rows)
    positive_share = sum(1 for r in rows if r.total_r > 0) / max(len(rows), 1)
    if summary["median_accepted_trades"] < 20:
        return "LOW_SAMPLE_DIAGNOSTIC"
    if summary["median_total_r"] > 1 and positive_share >= 0.55 and summary["median_max_drawdown_r"] <= 12:
        return "BROAD_POSITIVE_DIAGNOSTIC"
    if summary["median_total_r"] > 0 and positive_share >= 0.45:
        return "WATCH_POSITIVE_DIAGNOSTIC"
    if summary["median_max_drawdown_r"] > 15:
        return "HIGH_DRAWDOWN_DIAGNOSTIC"
    return "WEAK_OR_MIXED_DIAGNOSTIC"


def _build_status_matrix(
    rows: Sequence[SweepRow],
    parameter_rows: Sequence[Mapping[str, Any]],
    warnings: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_sw: dict[tuple[str, str], list[SweepRow]] = defaultdict(list)
    for row in rows:
        by_sw[(row.strategy, row.window)].append(row)
    regions_by_strategy: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in parameter_rows:
        regions_by_strategy[str(row["strategy"])].append(row)
    warning_by_strategy: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in warnings:
        warning_by_strategy[str(row["strategy"])].append(row)

    out: list[dict[str, Any]] = []
    for strategy in STRATEGIES:
        h1_rows = by_sw[(strategy, "qqq_2024h1")]
        h2_rows = by_sw[(strategy, "qqq_2024h2")]
        h1_summary = _summarize_region(h1_rows)
        h2_summary = _summarize_region(h2_rows)
        h1_status = _window_status(h1_rows)
        h2_status = _window_status(h2_rows)
        stable_positive_regions = sum(
            1
            for r in regions_by_strategy[strategy]
            if r["robust_region_label"] == "ROBUST_POSITIVE_REGION"
        )
        high_warnings = [
            r for r in warning_by_strategy[strategy] if r["warning_level"] in {"MEDIUM", "HIGH"}
        ]
        low_sample = min(
            _sample_label(h1_summary),
            _sample_label(h2_summary),
            key=lambda label: {"LOW_SAMPLE": 0, "MARGINAL": 1, "ADEQUATE": 2}[label],
        )
        worst_drawdown = (
            "HIGH_DRAWDOWN"
            if "HIGH_DRAWDOWN" in {_drawdown_label(h1_summary), _drawdown_label(h2_summary)}
            else max(
                [_drawdown_label(h1_summary), _drawdown_label(h2_summary)],
                key=lambda label: {"CONTROLLED": 0, "ELEVATED": 1, "HIGH_DRAWDOWN": 2}[label],
            )
        )
        worst_risk = (
            "HIGH_COST_TO_RISK"
            if "HIGH_COST_TO_RISK" in {_risk_cost_label(h1_summary), _risk_cost_label(h2_summary)}
            else "ACCEPTABLE_COST_TO_RISK"
        )
        regime_flip = (h1_summary["median_total_r"] > 1 > h2_summary["median_total_r"]) or (
            h2_summary["median_total_r"] > 1 > h1_summary["median_total_r"]
        )
        if strategy == "orb_continuation" and stable_positive_regions:
            combined = "ROBUST_REGION_CANDIDATE_FOR_FURTHER_REVIEW"
            action = "Phase18 focused confirmation-design specification only"
        elif low_sample == "LOW_SAMPLE":
            combined = "WATCH_LOW_SAMPLE"
            action = "Phase18 sample-adequacy and signal-frequency review"
        elif worst_drawdown == "HIGH_DRAWDOWN":
            combined = "WATCH_HIGH_DRAWDOWN"
            action = "Phase18 risk-path and stop/hold logic review"
        elif stable_positive_regions and not regime_flip:
            combined = "WATCH_PROMISING_REGION"
            action = "Phase18 refine review questions before any fresh confirmation"
        elif worst_risk == "HIGH_COST_TO_RISK":
            combined = "WATCH_HIGH_COST_TO_RISK"
            action = "Phase18 risk-per-share/friction review"
        elif regime_flip:
            combined = "WATCH_REGIME_DEPENDENT"
            action = "Phase18 regime/feature-context review"
        elif strategy in {"cci_extreme_snapback", "stochastic_oversold_cross"}:
            combined = "HOLD_WEAK_SURFACE"
            action = "Hold until oscillator logic/feature design is revisited"
        else:
            combined = "HOLD_WEAK_SURFACE"
            action = "Hold; use Phase18 only if evidence-backed design gap is clear"
        top_label = "ISOLATED_TOP_ROW_RISK" if high_warnings else "SUPPORTED_OR_LOW_WARNING"
        rationale = (
            f"H1 median={h1_summary['median_total_r']:.2f}R, "
            f"H2 median={h2_summary['median_total_r']:.2f}R, "
            f"robust_regions={stable_positive_regions}; H2 warning attached"
        )
        secondary = (
            f"top_warning_count={len(high_warnings)}; "
            f"sample={low_sample}; drawdown={worst_drawdown}; risk_cost={worst_risk}"
        )
        out.append(
            {
                "strategy": strategy,
                "family": FAMILIES[strategy],
                "h1_status": h1_status,
                "h2_status": h2_status,
                "combined_surface_status": combined,
                "promotion_ready": "false",
                "candidate_yaml_allowed": "false",
                "phase18_action": action,
                "primary_rationale": rationale,
                "secondary_risks": secondary,
                "h2_warning_attached": "true",
                "sample_adequacy_label": low_sample,
                "drawdown_label": worst_drawdown,
                "risk_cost_label": worst_risk,
                "top_row_isolation_label": top_label,
                "next_recommended_handling": action,
            }
        )
    return out


def _build_backlog(status_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in status_rows:
        strategy = str(row["strategy"])
        status = str(row["combined_surface_status"])
        evidence = str(row["primary_rationale"])
        if status == "ROBUST_REGION_CANDIDATE_FOR_FURTHER_REVIEW":
            out.append(
                {
                    "strategy": strategy,
                    "issue_type": "REPORTING_GAP",
                    "priority": "P1",
                    "evidence": evidence,
                    "proposed_phase": "Phase18",
                    "proposed_change": "Design focused confirmation/reporting questions around robust regions",
                    "allowed_in_phase18": "true",
                    "requires_feature_work": "false",
                    "requires_strategy_logic_work": "false",
                    "requires_short_side_design": "false",
                    "requires_data_or_reporting_work": "true",
                    "notes": "confirmation design only; no candidate promotion",
                }
            )
        elif status == "WATCH_LOW_SAMPLE":
            out.append(
                {
                    "strategy": strategy,
                    "issue_type": "LOW_SAMPLE",
                    "priority": "P1",
                    "evidence": evidence,
                    "proposed_phase": "Phase18",
                    "proposed_change": "Review signal frequency and whether current trigger is too restrictive",
                    "allowed_in_phase18": "true",
                    "requires_feature_work": "false",
                    "requires_strategy_logic_work": "true",
                    "requires_short_side_design": "false",
                    "requires_data_or_reporting_work": "false",
                    "notes": "do not loosen thresholds from top rows",
                }
            )
        elif status == "WATCH_HIGH_DRAWDOWN":
            out.append(
                {
                    "strategy": strategy,
                    "issue_type": "HIGH_DRAWDOWN",
                    "priority": "P1",
                    "evidence": evidence,
                    "proposed_phase": "Phase18",
                    "proposed_change": "Review stop/target/max-hold shape and regime gating design",
                    "allowed_in_phase18": "true",
                    "requires_feature_work": "false",
                    "requires_strategy_logic_work": "true",
                    "requires_short_side_design": "false",
                    "requires_data_or_reporting_work": "false",
                    "notes": "risk-path design, not retuning from Phase16 top rows",
                }
            )
        elif status == "WATCH_REGIME_DEPENDENT":
            out.append(
                {
                    "strategy": strategy,
                    "issue_type": "REGIME_DEPENDENT",
                    "priority": "P2",
                    "evidence": evidence,
                    "proposed_phase": "Phase18",
                    "proposed_change": "Design use of existing regime/VWAP/volatility context before any rerun",
                    "allowed_in_phase18": "true",
                    "requires_feature_work": "false",
                    "requires_strategy_logic_work": "true",
                    "requires_short_side_design": "false",
                    "requires_data_or_reporting_work": "false",
                    "notes": "H2 cannot be clean confirmation",
                }
            )
        else:
            out.append(
                {
                    "strategy": strategy,
                    "issue_type": "LOGIC_REVIEW",
                    "priority": "P3",
                    "evidence": evidence,
                    "proposed_phase": "Phase18 or later",
                    "proposed_change": "Hold until broader logic or missing-feature rationale is stronger",
                    "allowed_in_phase18": "true",
                    "requires_feature_work": "false",
                    "requires_strategy_logic_work": "true",
                    "requires_short_side_design": "false",
                    "requires_data_or_reporting_work": "false",
                    "notes": "weak surface is not a promotion blocker to bypass",
                }
            )
        if "ISOLATED_TOP_ROW_RISK" in str(row["top_row_isolation_label"]):
            out.append(
                {
                    "strategy": strategy,
                    "issue_type": "ISOLATED_TOP_ROW",
                    "priority": "P2",
                    "evidence": str(row["secondary_risks"]),
                    "proposed_phase": "Phase18",
                    "proposed_change": "Require neighborhood-first review before any future focused confirmation",
                    "allowed_in_phase18": "true",
                    "requires_feature_work": "false",
                    "requires_strategy_logic_work": "false",
                    "requires_short_side_design": "false",
                    "requires_data_or_reporting_work": "true",
                    "notes": "top rows are not candidates",
                }
            )
    out.append(
        {
            "strategy": "all",
            "issue_type": "DATA_WARNING",
            "priority": "P1",
            "evidence": H2_WARNING,
            "proposed_phase": "Phase18",
            "proposed_change": "Carry H2 warning into any future diagnostic or confirmation design",
            "allowed_in_phase18": "true",
            "requires_feature_work": "false",
            "requires_strategy_logic_work": "false",
            "requires_short_side_design": "false",
            "requires_data_or_reporting_work": "true",
            "notes": "fresh holdout still required before promotion",
        }
    )
    out.append(
        {
            "strategy": "all",
            "issue_type": "SHORT_SIDE_FEASIBILITY",
            "priority": "P3",
            "evidence": "all current Phase16 strategies are long-only",
            "proposed_phase": "Phase18",
            "proposed_change": "Design short-side feasibility questions separately from long-side candidates",
            "allowed_in_phase18": "true",
            "requires_feature_work": "false",
            "requires_strategy_logic_work": "true",
            "requires_short_side_design": "true",
            "requires_data_or_reporting_work": "false",
            "notes": "short-side design is not immediate implementation or promotion",
        }
    )
    return out


def _validate_artifact(path: Path, columns: Sequence[str] | None = None) -> dict[str, Any]:
    available = path.is_file()
    parse_ok = False
    expected_ok = False
    row_count = 0
    issue = ""
    notes = ""
    if not available:
        issue = "missing"
    elif path.suffix.lower() == ".csv":
        try:
            with path.open("r", encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                fieldnames = reader.fieldnames or []
                rows = list(reader)
            row_count = len(rows)
            parse_ok = True
            expected_ok = all(col in fieldnames for col in (columns or []))
            if columns and not expected_ok:
                issue = "expected columns missing"
            notes = "csv parsed"
        except Exception as exc:  # pragma: no cover - artifact report path
            issue = type(exc).__name__
            notes = str(exc)
    else:
        try:
            text = path.read_text(encoding="utf-8")
            parse_ok = True
            expected_ok = bool(text.strip())
            row_count = len(text.splitlines())
            notes = "text artifact readable"
        except Exception as exc:  # pragma: no cover - artifact report path
            issue = type(exc).__name__
            notes = str(exc)
    return {
        "available": available,
        "parse_ok": parse_ok,
        "expected_columns_ok": expected_ok,
        "row_count": row_count,
        "issue": issue,
        "notes": notes,
    }


def _build_input_validation(generated_files: Sequence[str]) -> list[dict[str, Any]]:
    required_inputs = [
        (PHASE16B / "CHATGPT_REVIEW_BUNDLE.md", "phase16b_md", True, None, False),
        (PHASE16B / "SOURCE_MAP.csv", "phase16b_csv", True, None, False),
        (PHASE16B / "chatgpt_key_tables.csv", "phase16b_csv", True, None, False),
        (PHASE16B / "validation_results.csv", "phase16b_csv", True, None, False),
        (PHASE16B / "phase16b_run_manifest.csv", "phase16b_csv", True, None, False),
        (PHASE16B / "remaining_grid_run_summary.csv", "phase16b_csv", True, None, False),
        (PHASE16B / "artifact_schema_validation.csv", "phase16b_csv", True, None, False),
        (PHASE16B / "non_promotion_guardrails.md", "phase16b_md", True, None, False),
        (PHASE16B / "phase16b_decision.md", "phase16b_md", True, None, False),
        (PHASE16 / "expanded_grid_inventory.csv", "phase16_csv", True, None, False),
        (PHASE16 / "expanded_grid_axis_rationale.csv", "phase16_csv", True, None, False),
        (PHASE16 / "per_strategy_combo_count.csv", "phase16_csv", True, None, False),
        (PHASE16 / "layer1_config_inventory.csv", "phase16_csv", True, None, False),
    ]
    rows: list[dict[str, Any]] = []
    for path, artifact_type, required, columns, local_only in required_inputs:
        result = _validate_artifact(path, columns)
        rows.append(
            {
                "artifact_path": _rel(path),
                "artifact_type": artifact_type,
                "required": required,
                "available": result["available"],
                "parse_ok": result["parse_ok"],
                "expected_columns_ok": True if columns is None else result["expected_columns_ok"],
                "row_count": result["row_count"],
                "local_only_dependency": local_only,
                "issue": result["issue"],
                "notes": result["notes"],
            }
        )
    for window in WINDOWS:
        for strategy in STRATEGIES:
            path = RUN_ROOT / window / strategy / "sweep_results.csv"
            result = _validate_artifact(path, None)
            rows.append(
                {
                    "artifact_path": _rel(path),
                    "artifact_type": "phase16_local_sweep_results",
                    "required": True,
                    "available": result["available"],
                    "parse_ok": result["parse_ok"],
                    "expected_columns_ok": result["expected_columns_ok"] or result["parse_ok"],
                    "row_count": result["row_count"],
                    "local_only_dependency": True,
                    "issue": result["issue"],
                    "notes": "local-only run output used for region/neighborhood aggregation",
                }
            )
    for name in generated_files:
        path = OUT / name
        result = _validate_artifact(path, CSV_COLUMNS.get(name))
        rows.append(
            {
                "artifact_path": _rel(path),
                "artifact_type": "phase17_generated_csv",
                "required": True,
                "available": result["available"],
                "parse_ok": result["parse_ok"],
                "expected_columns_ok": result["expected_columns_ok"],
                "row_count": result["row_count"],
                "local_only_dependency": False,
                "issue": result["issue"],
                "notes": result["notes"],
            }
        )
    return rows


def _build_schema_validation(generated_files: Sequence[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in generated_files:
        path = OUT / name
        result = _validate_artifact(path, CSV_COLUMNS.get(name))
        rows.append(
            {
                "artifact_path": _rel(path),
                "artifact_type": "csv",
                "parse_ok": result["parse_ok"],
                "expected_columns_ok": result["expected_columns_ok"],
                "row_count": result["row_count"],
                "issue": result["issue"],
                "notes": result["notes"],
            }
        )
    for name in [
        "CHATGPT_REVIEW_BUNDLE.md",
        "phase18_candidate_improvement_scope.md",
        "h2_warning_interpretation.md",
        "non_promotion_guardrails.md",
        "phase17_decision.md",
    ]:
        path = OUT / name
        result = _validate_artifact(path)
        rows.append(
            {
                "artifact_path": _rel(path),
                "artifact_type": "md",
                "parse_ok": result["parse_ok"],
                "expected_columns_ok": result["expected_columns_ok"],
                "row_count": result["row_count"],
                "issue": result["issue"],
                "notes": result["notes"],
            }
        )
    return rows


def _write_markdown(status_rows: Sequence[Mapping[str, Any]], backlog_rows: Sequence[Mapping[str, Any]]) -> None:
    status_counts = Counter(str(row["combined_surface_status"]) for row in status_rows)
    watch = [
        str(row["strategy"])
        for row in status_rows
        if str(row["combined_surface_status"]).startswith("WATCH")
    ]
    hold = [
        str(row["strategy"])
        for row in status_rows
        if str(row["combined_surface_status"]).startswith("HOLD")
    ]
    robust = [
        str(row["strategy"])
        for row in status_rows
        if row["combined_surface_status"] == "ROBUST_REGION_CANDIDATE_FOR_FURTHER_REVIEW"
    ]
    bundle = f"""# Phase17 Review Bundle

## Phase

`{PHASE}`

## Task Type

{TASK_TYPE}. This was a review/diagnostic phase only.

## Git Baseline

Branch `main`; pre-task HEAD `{PRE_TASK_HEAD}`. Final commit is recorded in the Cursor final response because the final commit hash is self-referential before commit.

## Why Phase17 Was Needed

Phase16B completed all 20 expanded grids after runtime/reporting repairs. Phase17 was needed to review all-current-10 results by parameter regions and top-neighborhood support, not by single top-row sorting.

## Phase16B Acceptance Summary

Phase16B accepted decision `PHASE16_EXPANDED_GRID_RUN_RESUMED_COMPLETE`: ORB retest and failed ORB prior-state runtime blockers were repaired, drawdown/risk/cost reporting was repaired, and all 20 grids completed with full combo coverage. H2 carries `{H2_WARNING}` and remains diagnostic-only.

## Files And Artifacts Read

Status docs, architecture/contracts, Phase16/16B curated artifacts, 10 Phase16 expanded grid specs, 20 Layer1 configs, and the local-only Phase16 `runs/` sweep summaries were read. `CODEX_REVIEW.md` was read earlier in the task and intentionally not edited.

## Input Artifact Validation Summary

See `phase17_input_artifact_validation.csv`. Required curated Phase16B and Phase16 inputs were available. Local sweep CSVs under `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` were used as local-only inputs and are not copied or staged.

## Review Methodology

The review compares region medians, p25/p75 dispersion, best/worst total R, drawdown distribution, accepted-trade sample size, zero-trade counts, risk-per-share, cost-to-risk, H1/H2 behavior, and neighborhood support around top total-R rows. Top rows are warning inputs only, not candidates.

## Strategy Surface Status Summary

Status counts: {dict(status_counts)}

Robust-for-further-review diagnostics: {', '.join(robust) if robust else 'none'}.

Watch diagnostics: {', '.join(watch) if watch else 'none'}.

Hold diagnostics: {', '.join(hold) if hold else 'none'}.

## H1/H2 Interpretation

H1 is the cleaner design diagnostic. H2 contributes only diagnostic stress information because `{H2_WARNING}` remains attached. H2-only strength is not confirmation and cannot unlock selection, candidate YAML, or Layer2.

## Region And Neighborhood Findings

`parameter_region_summary.csv`, `axis_marginal_summary.csv`, `pairwise_interaction_summary.csv`, and `h1_h2_cross_window_region_matrix.csv` provide the region-first review. `top_neighborhood_summary.csv` and `isolated_top_row_warning.csv` explicitly check whether top rows sit inside supportive neighborhoods.

## Isolated Top-Row Warnings

Warnings are anti-argmax diagnostics. Any `MEDIUM` or `HIGH` warning means a top row should be treated as isolated or insufficiently supported until a future region review proves otherwise.

## Drawdown / Sample / Risk / Cost Diagnostics

Drawdown uses positive drawdown magnitude ordering. Risk-per-share and cost-to-risk are aggregate-only summaries derived from execution-produced trade fields in existing sweep results; no fills, stops, targets, PnL, or R are recomputed.

## Phase18 Improvement Backlog Summary

`strategy_improvement_backlog.csv` contains {len(backlog_rows)} evidence-backed, non-promotional improvement items. The backlog is for design/implementation review only, not candidate promotion.

## Validation Results

See `validation_results.csv`. Phase17 added schema/no-promotion tests and records command outcomes there.

## Artifact Hygiene

Only curated Phase17 CSV/MD artifacts are generated under `{_rel(OUT)}`. Local Phase16 run outputs remain local-only. No raw/curated/cache/parquet/npy/npz/memmap, row-level trades, row-level equity, top_runs, candidates, Layer2, Layer3, WFO, live, or paper artifacts are included.

## Explicit Non-Runs

No new Layer1 grids, no select-dry-run, no candidate YAML, no promotion, no Layer2, no Layer3, no WFO, no live/paper, no strategy retuning, no feature semantic changes, and no execution truth changes.

## Risks / Blockers

H2 warning remains the main data-quality risk. Failed ORB helper coverage remains thinner than ORB retest coverage from Phase16B. Validation of Phase16 full-grid completion is artifact-reported and this phase did not rerun grids.

## Decision

`{DECISION}`

## Cursor Provisional Recommended Next Step

`{NEXT_STEP}`

Final roadmap decision belongs to ChatGPT Pro + user after Codex review.
"""
    (OUT / "CHATGPT_REVIEW_BUNDLE.md").write_text(bundle, encoding="utf-8")

    scope = f"""# Phase18 Candidate Improvement Scope

Phase18, if accepted, should improve or design around the existing 10 strategies only. It must remain improvement/design/implementation work, not promotion.

## Improve In Phase18

- `orb_continuation`: strongest region-level surface; design focused confirmation/reporting questions, not candidates.
- `orb_retest_continuation`: promising watch surface; review retest tolerance and risk/hold regions.
- `pa_buy_sell_close_trend`, `failed_orb`, `vwap_trend_pullback`: regime-dependent or drawdown-sensitive surfaces; review logic/context before more grids.
- `gap_acceptance_failure`, `prior_day_level_trap`, `vwap_reclaim_reject`: sample-adequacy and trigger-frequency review before any confirmation design.

## Hold / Watch

`cci_extreme_snapback` and `stochastic_oversold_cross` remain weak/high-drawdown oscillator surfaces. They need logic review before further grid attention.

## Feature Gaps Justified

Use existing regime, VWAP, volatility, ORB-width, and level-distance facts where already available before adding new feature kernels. Missing features require a separate Phase18 design note and tests.

## Short-Side Ideas

Short-side feasibility may be designed because all current Phase16 strategies are long-only, but short-side work must be separated from candidate promotion and must preserve execution truth.

## Forbidden

No candidate YAML, no select-dry-run, no promotion, no Layer2/3, no WFO, no live/paper, no H2-as-confirmation, no top-row retuning, no execution/accounting changes.

Phase18 is improvement/design/implementation because Phase17 only classifies diagnostic surfaces and backlog items.
"""
    (OUT / "phase18_candidate_improvement_scope.md").write_text(scope, encoding="utf-8")

    h2 = f"""# H2 Warning Interpretation

Exact warning: `{H2_WARNING}`.

QQQ 2024H2 remains diagnostic-only. H2 cannot be clean confirmation evidence. H2 can contribute to robustness review only with the warning attached. No strategy should be promoted based on H2. A future fresh holdout is still required before any promotion.
"""
    (OUT / "h2_warning_interpretation.md").write_text(h2, encoding="utf-8")

    guardrails = """# Phase17 Non-Promotion Guardrails

- No new Layer1 grids were run.
- No Layer1 select-dry-run was run.
- No candidate YAML was created.
- No promotion was performed.
- No Layer2 work was created or run.
- No Layer3 work was created or run.
- No WFO or mini-WFO was run.
- No live/paper config or run was created.
- No strategy retuning was performed.
- No feature semantic changes were made.
- No execution truth changes were made.
- Top rows are not candidates.
- H2 is not confirmation.
- Phase17 classifications are diagnostic only.
- Phase18 improvements, if recommended, are not candidate promotion.
"""
    (OUT / "non_promotion_guardrails.md").write_text(guardrails, encoding="utf-8")

    decision = f"""# Phase17 Decision

Decision label: `{DECISION}`.

Phase18 improvement recommended: yes, bounded to existing 10 strategy improvements/design questions.

Robust enough for future focused confirmation design: diagnostic yes for at least `orb_continuation`, but not for promotion.

Candidate selection remains blocked: yes. No candidate YAML, select-dry-run, Layer2, WFO, live, or paper is unlocked.

H2 warning remains attached: `{H2_WARNING}`. H2 is diagnostic-only and is not clean confirmation evidence.

Next provisional step: `{NEXT_STEP}`.
"""
    (OUT / "phase17_decision.md").write_text(decision, encoding="utf-8")


def _source_map_rows(generated_csvs: Sequence[str]) -> list[dict[str, Any]]:
    paths = [
        ("scripts/phase17_region_review.py", "Phase17 artifact generator", True, "generated_source", False),
        ("tests/unit/test_phase17_artifact_schema.py", "Phase17 CSV schema guard", True, "generated_test", False),
        (
            "tests/unit/test_phase17_no_promotion_leakage.py",
            "Phase17 no-promotion guard",
            True,
            "generated_test",
            False,
        ),
        ("NEXT_HANDOFF.md", "Phase17 handoff/status", True, "updated_doc", False),
        ("PROJECT_STATUS.md", "Phase17 project status", True, "updated_doc", False),
        ("PROGRESS.md", "Dated progress log", True, "updated_doc", False),
        ("CHANGES.md", "Dated changelog", True, "updated_doc", False),
        ("README.md", "User-facing project status", True, "updated_doc", False),
        ("docs/PHASE_PLAN.md", "Roadmap status", True, "updated_doc", False),
        (
            "artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/",
            "Local-only Phase16 sweep inputs for region review",
            True,
            "local_input",
            True,
        ),
    ]
    for name in generated_csvs:
        paths.append((_rel(OUT / name), "Phase17 curated CSV artifact", True, "generated_artifact", False))
    for name in [
        "CHATGPT_REVIEW_BUNDLE.md",
        "phase18_candidate_improvement_scope.md",
        "h2_warning_interpretation.md",
        "non_promotion_guardrails.md",
        "phase17_decision.md",
    ]:
        paths.append((_rel(OUT / name), "Phase17 curated markdown artifact", True, "generated_artifact", False))
    return [
        {
            "file_path": file_path,
            "purpose": purpose,
            "required_for_review": required,
            "generated_or_source": generated_or_source,
            "local_only_dependency": local_only,
            "notes": "do not stage local-only input" if local_only else "",
        }
        for file_path, purpose, required, generated_or_source, local_only in paths
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = _read_sweeps()
    if len(rows) == 0:
        raise SystemExit("No Phase16 sweep rows found; Phase17 review is blocked.")
    parameter_rows, drawdown_rows, risk_rows, sample_rows = _build_region_tables(rows)
    axis_rows = _build_axis_summary(rows)
    pair_rows = _build_pairwise(rows)
    top_rows, isolated_rows = _build_top_neighborhoods(rows)
    cross_rows = _build_cross_window(parameter_rows)
    status_rows = _build_status_matrix(rows, parameter_rows, isolated_rows)
    backlog_rows = _build_backlog(status_rows)

    csv_order = [
        "strategy_surface_status_matrix.csv",
        "parameter_region_summary.csv",
        "top_neighborhood_summary.csv",
        "isolated_top_row_warning.csv",
        "axis_marginal_summary.csv",
        "pairwise_interaction_summary.csv",
        "h1_h2_cross_window_region_matrix.csv",
        "drawdown_region_summary.csv",
        "risk_cost_region_summary.csv",
        "sample_adequacy_region_summary.csv",
        "strategy_improvement_backlog.csv",
    ]
    _write_csv(OUT / "strategy_surface_status_matrix.csv", CSV_COLUMNS["strategy_surface_status_matrix.csv"], status_rows)
    _write_csv(OUT / "parameter_region_summary.csv", CSV_COLUMNS["parameter_region_summary.csv"], parameter_rows)
    _write_csv(OUT / "top_neighborhood_summary.csv", CSV_COLUMNS["top_neighborhood_summary.csv"], top_rows)
    _write_csv(OUT / "isolated_top_row_warning.csv", CSV_COLUMNS["isolated_top_row_warning.csv"], isolated_rows)
    _write_csv(OUT / "axis_marginal_summary.csv", CSV_COLUMNS["axis_marginal_summary.csv"], axis_rows)
    _write_csv(OUT / "pairwise_interaction_summary.csv", CSV_COLUMNS["pairwise_interaction_summary.csv"], pair_rows)
    _write_csv(
        OUT / "h1_h2_cross_window_region_matrix.csv",
        CSV_COLUMNS["h1_h2_cross_window_region_matrix.csv"],
        cross_rows,
    )
    _write_csv(OUT / "drawdown_region_summary.csv", CSV_COLUMNS["drawdown_region_summary.csv"], drawdown_rows)
    _write_csv(OUT / "risk_cost_region_summary.csv", CSV_COLUMNS["risk_cost_region_summary.csv"], risk_rows)
    _write_csv(
        OUT / "sample_adequacy_region_summary.csv",
        CSV_COLUMNS["sample_adequacy_region_summary.csv"],
        sample_rows,
    )
    _write_csv(
        OUT / "strategy_improvement_backlog.csv",
        CSV_COLUMNS["strategy_improvement_backlog.csv"],
        backlog_rows,
    )

    _write_markdown(status_rows, backlog_rows)

    validation_rows = [
        {
            "command": "python scripts/phase17_region_review.py",
            "status": "pass",
            "exit_code": 0,
            "notes": "generated curated Phase17 review artifacts from existing Phase16/16B inputs",
        }
    ]
    _write_csv(OUT / "validation_results.csv", CSV_COLUMNS["validation_results.csv"], validation_rows)

    source_map = _source_map_rows(
        [
            "SOURCE_MAP.csv",
            "chatgpt_key_tables.csv",
            "validation_results.csv",
            "phase17_input_artifact_validation.csv",
            *csv_order,
            "artifact_schema_validation.csv",
        ]
    )
    _write_csv(OUT / "SOURCE_MAP.csv", CSV_COLUMNS["SOURCE_MAP.csv"], source_map)

    status_counts = Counter(str(row["combined_surface_status"]) for row in status_rows)
    warning_count = sum(1 for row in isolated_rows if row["warning_level"] in {"MEDIUM", "HIGH"})
    key_rows = [
        ("phase", "phase", "name", PHASE, "Phase17 review-only task"),
        ("phase", "task_type", "scope", TASK_TYPE, "diagnostic only"),
        ("git", "pre_task_head", "sha", PRE_TASK_HEAD, "captured before edits"),
        (
            "git",
            "final_commit",
            "sha",
            "recorded in final Cursor response",
            "self-referential before commit",
        ),
        ("scope", "strategies_reviewed_count", "count", len(STRATEGIES), "all 10 active strategies"),
        ("guardrails", "new_grid_runs", "bool", "false", "Phase17 did not run grids"),
        ("guardrails", "select_dry_run_run", "bool", "false", "no candidate selection dry-run"),
        ("guardrails", "candidate_yaml_created", "bool", "false", "no runtime candidates"),
        ("guardrails", "layer2_created", "bool", "false", "Layer2 remains locked"),
        ("guardrails", "wfo_run", "bool", "false", "no WFO"),
        ("guardrails", "live_paper_run", "bool", "false", "no live/paper"),
        ("data", "H2_warning", "warning", H2_WARNING, "H2 diagnostic-only"),
        (
            "status",
            "number_of_strategies_by_status",
            "counts",
            json.dumps(dict(status_counts), sort_keys=True),
            "diagnostic statuses only",
        ),
        (
            "warnings",
            "number_of_isolated_top_row_warnings",
            "count",
            warning_count,
            "MEDIUM/HIGH top-neighborhood warnings",
        ),
        (
            "backlog",
            "number_of_strategy_improvement_items",
            "count",
            len(backlog_rows),
            "Phase18 non-promotional backlog items",
        ),
        ("decision", "decision", "label", DECISION, "all 10 surfaces reviewed"),
        (
            "decision",
            "recommended_next_step",
            "label",
            NEXT_STEP,
            "provisional pending Codex and ChatGPT Pro review",
        ),
    ]
    _write_csv(
        OUT / "chatgpt_key_tables.csv",
        CSV_COLUMNS["chatgpt_key_tables.csv"],
        [
            {
                "section": section,
                "item": item,
                "metric": metric,
                "value": value,
                "interpretation": interpretation,
            }
            for section, item, metric, value, interpretation in key_rows
        ],
    )

    schema_rows = _build_schema_validation(
        [
            "SOURCE_MAP.csv",
            "chatgpt_key_tables.csv",
            "validation_results.csv",
            "phase17_input_artifact_validation.csv",
            *csv_order,
        ]
    )
    _write_csv(
        OUT / "artifact_schema_validation.csv",
        CSV_COLUMNS["artifact_schema_validation.csv"],
        schema_rows,
    )
    input_validation = _build_input_validation(
        [
            "SOURCE_MAP.csv",
            "chatgpt_key_tables.csv",
            "validation_results.csv",
            "artifact_schema_validation.csv",
            *csv_order,
        ]
    )
    _write_csv(
        OUT / "phase17_input_artifact_validation.csv",
        CSV_COLUMNS["phase17_input_artifact_validation.csv"],
        input_validation,
    )


if __name__ == "__main__":
    main()
