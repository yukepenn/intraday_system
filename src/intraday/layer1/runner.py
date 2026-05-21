"""Layer1 smoke runner: bars → features → signals → intents → execution → metrics."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from intraday.backtest.metrics import summarize_trade_results, summarize_trade_risk_cost
from intraday.backtest.signal_adapter import SignalAdapterResult, build_trade_intents_from_signals
from intraday.core.arrays import BarMatrix
from intraday.core.paths import repo_root
from intraday.data.loader import load_bars_from_curated
from intraday.execution import (
    assert_trade_results_equal,
    simulate_trade_path_fast,
    simulate_trade_path_reference,
)
from intraday.execution.records import TradeResult
from intraday.execution.spec import (
    ExecutionSpec,
    load_execution_spec,
    merge_execution_spec_with_strategy,
)
from intraday.features.engine import build_feature_matrix
from intraday.features.specs import load_feature_config
from intraday.layer1 import reports
from intraday.layer1.config import (
    load_layer1_controlled_grid_config,
    load_layer1_smoke_config,
    validate_layer1_controlled_grid_config,
    validate_layer1_smoke_config,
)
from intraday.layer1.grid import load_grid_document, resolve_grid_combos
from intraday.layer1.result import (
    Layer1GridResult,
    Layer1GridRow,
    Layer1SmokeResult,
    layer1_smoke_result_to_jsonable,
)
from intraday.strategies.contracts import (
    allowed_sides_for_mode,
    normalize_side_mode,
    validate_signal_matrix,
)
from intraday.strategies.loader import load_strategy_config, validate_strategy_config
from intraday.strategies.registry import get_strategy, register_builtin_strategies


def _resolve(root: Path, p: str) -> Path:
    path = Path(p)
    return path if path.is_absolute() else (root / path)


def _max_trades_for_run(
    max_trades_per_session: int,
    strategy_cfg: Mapping[str, Any],
) -> int:
    m = max_trades_per_session
    if m > 0:
        return m
    risk = strategy_cfg.get("risk")
    if isinstance(risk, Mapping) and "max_trades_per_day" in risk:
        v = int(risk["max_trades_per_day"])
        if v > 0:
            return v
    return 1


def _qty_and_hold(strategy_cfg: Mapping[str, Any]) -> tuple[float, int]:
    bt = strategy_cfg.get("backtest")
    if not isinstance(bt, Mapping):
        return 1.0, 0
    qty = float(bt.get("quantity", 1.0))
    hold = int(bt.get("max_hold_minutes", 0))
    return qty, hold


def _allowed_sides_from_strategy_cfg(strategy_cfg: Mapping[str, Any]) -> tuple[int, ...]:
    signal_cfg = strategy_cfg.get("signal")
    if not isinstance(signal_cfg, Mapping):
        signal_cfg = {}
    side_mode = normalize_side_mode(signal_cfg)
    return allowed_sides_for_mode(side_mode)


ExecutionMode = Literal["reference", "fast", "both"]


def layer1_scan_trade_intents(
    *,
    bars: BarMatrix,
    adapter: SignalAdapterResult,
    spec: ExecutionSpec,
    strategy_cfg: Mapping[str, Any],
    max_trades_per_session: int,
    skip_while_trade_open: bool,
    count_rejected_intents: bool,
    execution_mode: ExecutionMode,
) -> tuple[list[TradeResult], dict[str, int], bool]:
    """Session scan policy shared by smoke and controlled grid (Phase 6 / 6b)."""
    skip_counts: dict[str, int] = {
        "invalid_signal": int(adapter.skipped_invalid),
        "max_trades_per_session": 0,
        "trade_open": 0,
        "execution_rejected_included": 0,
        "execution_rejected_excluded": 0,
    }

    intents_sorted = sorted(adapter.intents, key=lambda x: x.signal_bar)
    max_trades = _max_trades_for_run(max_trades_per_session, strategy_cfg)

    results: list[TradeResult] = []
    current_session: int | None = None
    accepted_in_session = 0
    next_min_signal_bar = 0
    fast_checked = False

    for intent in intents_sorted:
        sid = int(bars.session_id[intent.signal_bar])
        if current_session is None or sid != current_session:
            current_session = sid
            accepted_in_session = 0
            next_min_signal_bar = 0

        if skip_while_trade_open and intent.signal_bar < next_min_signal_bar:
            skip_counts["trade_open"] += 1
            continue

        if accepted_in_session >= max_trades:
            skip_counts["max_trades_per_session"] += 1
            continue

        if execution_mode == "reference":
            res = simulate_trade_path_reference(bars, intent, spec)
        elif execution_mode == "fast":
            res = simulate_trade_path_fast(bars, intent, spec)
        else:
            ref = simulate_trade_path_reference(bars, intent, spec)
            fast = simulate_trade_path_fast(bars, intent, spec)
            assert_trade_results_equal(ref, fast)
            fast_checked = True
            res = ref

        results.append(res)
        if not res.accepted:
            if count_rejected_intents:
                skip_counts["execution_rejected_included"] += 1
            else:
                skip_counts["execution_rejected_excluded"] += 1
            continue

        accepted_in_session += 1
        next_min_signal_bar = int(res.exit_bar) + 1

    parity_done = fast_checked or (execution_mode == "both")
    return results, skip_counts, parity_done


def run_layer1_smoke(config_path: Path) -> Layer1SmokeResult:
    """Execute one Layer1 smoke path from YAML config."""
    t0 = time.perf_counter()
    smoke = load_layer1_smoke_config(config_path)
    validate_layer1_smoke_config(smoke)

    root = repo_root()
    data_root = _resolve(root, smoke.data_root)
    feat_path = _resolve(root, smoke.feature_config)
    strat_path = _resolve(root, smoke.strategy_config)
    exe_path = _resolve(root, smoke.execution_config)
    artifact_root = _resolve(root, smoke.artifact_root)

    bars = load_bars_from_curated(
        smoke.symbol,
        smoke.start,
        smoke.end,
        data_root=str(data_root),
        asset=smoke.asset,
    )

    raw_feat = load_feature_config(feat_path)
    fm = build_feature_matrix(
        bars,
        raw_feat,
        use_cache=smoke.feature_use_cache,
        store=None,
    )

    strat_cfg = load_strategy_config(strat_path)
    register_builtin_strategies()
    validate_strategy_config(smoke.strategy_name, strat_cfg)
    defn = get_strategy(smoke.strategy_name)
    signals = defn.generate_reference(bars, fm, strat_cfg)
    allowed_sides = _allowed_sides_from_strategy_cfg(strat_cfg)
    validate_signal_matrix(signals, bars.n_bars, reference_close=bars.close)

    qty, max_hold_bars = _qty_and_hold(strat_cfg)
    adapter = build_trade_intents_from_signals(
        signals,
        qty=qty,
        max_hold_bars=max_hold_bars,
        candidate_id=1,
        allowed_sides=allowed_sides,
    )

    base_spec = load_execution_spec(exe_path)
    spec = merge_execution_spec_with_strategy(base_spec, strat_cfg)

    results, skip_counts, parity_done = layer1_scan_trade_intents(
        bars=bars,
        adapter=adapter,
        spec=spec,
        strategy_cfg=strat_cfg,
        max_trades_per_session=smoke.max_trades_per_session,
        skip_while_trade_open=smoke.skip_while_trade_open,
        count_rejected_intents=smoke.count_rejected_intents,
        execution_mode=smoke.execution_mode,
    )

    metrics = summarize_trade_results(
        results,
        count_rejected_in_metrics=smoke.count_rejected_intents,
    )

    elapsed = time.perf_counter() - t0
    result = Layer1SmokeResult(
        run_id=smoke.run_id,
        symbol=smoke.symbol,
        start=smoke.start,
        end=smoke.end,
        rows=bars.n_bars,
        feature_count=fm.n_columns,
        signal_entries=adapter.total_entries,
        valid_intents=adapter.valid_intents,
        executed_results=len(results),
        metrics=metrics,
        signal_hash=signals.signal_hash,
        feature_hash=fm.feature_hash,
        execution_mode=smoke.execution_mode,
        skip_counts=skip_counts,
        fast_parity_checked=parity_done,
        runtime_seconds=elapsed,
    )

    reports.write_layer1_smoke_artifacts(
        artifact_root,
        smoke=smoke,
        result=result,
        adapter_skip_reasons=dict(adapter.skip_reasons),
    )
    return result


def run_layer1_controlled_grid(config_path: Path) -> Layer1GridResult:
    """Run Layer1 scan for each resolved combo in a controlled grid YAML."""
    cfg = load_layer1_controlled_grid_config(config_path)
    validate_layer1_controlled_grid_config(cfg)

    root = repo_root()
    data_root = _resolve(root, cfg.data_root)
    feat_path = _resolve(root, cfg.feature_config)
    exe_path = _resolve(root, cfg.execution_config)
    artifact_root = _resolve(root, cfg.artifact_root)
    grid_path = _resolve(root, cfg.strategy_grid_path)

    bars = load_bars_from_curated(
        cfg.symbol,
        cfg.start,
        cfg.end,
        data_root=str(data_root),
        asset=cfg.asset,
    )

    raw_feat = load_feature_config(feat_path)
    fm = build_feature_matrix(
        bars,
        raw_feat,
        use_cache=cfg.feature_use_cache,
        store=None,
    )

    gdoc = load_grid_document(grid_path)
    combos = resolve_grid_combos(gdoc, repo_base=root)
    register_builtin_strategies()
    defn = get_strategy(cfg.strategy_name)
    base_spec = load_execution_spec(exe_path)

    rows_out: list[Layer1GridRow] = []
    for combo in combos:
        strat_cfg = combo.resolved_config
        validate_strategy_config(cfg.strategy_name, strat_cfg)
        signals = defn.generate_reference(bars, fm, strat_cfg)
        allowed_sides = _allowed_sides_from_strategy_cfg(strat_cfg)
        validate_signal_matrix(signals, bars.n_bars, reference_close=bars.close)

        qty, max_hold_bars = _qty_and_hold(strat_cfg)
        adapter = build_trade_intents_from_signals(
            signals,
            qty=qty,
            max_hold_bars=max_hold_bars,
            candidate_id=1,
            allowed_sides=allowed_sides,
        )
        spec = merge_execution_spec_with_strategy(base_spec, strat_cfg)

        results, skip_counts, _parity = layer1_scan_trade_intents(
            bars=bars,
            adapter=adapter,
            spec=spec,
            strategy_cfg=strat_cfg,
            max_trades_per_session=cfg.max_trades_per_session,
            skip_while_trade_open=cfg.skip_while_trade_open,
            count_rejected_intents=cfg.count_rejected_intents,
            execution_mode=cfg.execution_mode,
        )

        metrics = summarize_trade_results(
            results,
            count_rejected_in_metrics=cfg.count_rejected_intents,
        )
        risk_cost = summarize_trade_risk_cost(
            results,
            slippage_per_share=spec.slippage_per_share,
            commission_per_trade=spec.commission_per_trade,
        )

        rows_out.append(
            Layer1GridRow(
                run_id=cfg.run_id,
                combo_id=combo.combo_id,
                config_hash=combo.config_hash,
                params_json=combo.params_json,
                signal_entries=adapter.total_entries,
                valid_intents=adapter.valid_intents,
                executed_results=len(results),
                accepted_trades=metrics.accepted_trades,
                rejected_trades=metrics.rejected_trades,
                total_r=metrics.total_r,
                avg_r=metrics.avg_r,
                median_r=metrics.median_r,
                win_rate=metrics.win_rate,
                profit_factor_r=metrics.profit_factor_r,
                max_drawdown_r=metrics.max_drawdown_r,
                avg_bars_held=metrics.avg_bars_held,
                avg_risk_per_share=metrics.avg_risk_per_share,
                median_risk_per_share=metrics.median_risk_per_share,
                p10_risk_per_share=metrics.p10_risk_per_share,
                p90_risk_per_share=metrics.p90_risk_per_share,
                avg_cost_to_risk=risk_cost.avg_cost_to_risk,
                median_cost_to_risk=risk_cost.median_cost_to_risk,
                exit_reason_counts_json=json.dumps(metrics.exit_reason_counts, sort_keys=True),
                reject_reason_counts_json=json.dumps(metrics.reject_reason_counts, sort_keys=True),
                skip_reason_counts_json=json.dumps(skip_counts, sort_keys=True),
                adapter_skip_reasons_json=json.dumps(dict(adapter.skip_reasons), sort_keys=True),
                feature_hash=fm.feature_hash,
                signal_hash=signals.signal_hash,
                execution_mode=cfg.execution_mode,
            )
        )

    result = Layer1GridResult(
        run_id=cfg.run_id,
        symbol=cfg.symbol,
        start=cfg.start,
        end=cfg.end,
        combo_count=len(rows_out),
        rows=tuple(rows_out),
        feature_hash=fm.feature_hash,
        execution_mode=cfg.execution_mode,
    )

    reports.write_layer1_grid_artifacts(result, artifact_root)
    return result


def print_layer1_smoke_summary(res: Layer1SmokeResult) -> None:
    """Rich-ish plain text summary for CLI."""
    m = res.metrics
    pfr = m.profit_factor_r
    pfr_s = "inf" if pfr == float("inf") else f"{pfr:.6g}"
    print(json.dumps(layer1_smoke_result_to_jsonable(res), indent=2))
    print("\n--- summary ---")
    print(f"run_id={res.run_id} rows={res.rows} features={res.feature_count}")
    print(
        f"signal_entries={res.signal_entries} valid_intents={res.valid_intents} "
        f"executed={res.executed_results}"
    )
    print(
        f"accepted={m.accepted_trades} rejected={m.rejected_trades} "
        f"total_r={m.total_r:.6g} avg_r={m.avg_r:.6g} win_rate={m.win_rate:.4f} "
        f"pf_r={pfr_s} max_dd_r={m.max_drawdown_r:.6g}"
    )
    print(f"skip_counts={res.skip_counts}")
    print(f"fast_parity_checked={res.fast_parity_checked} runtime_s={res.runtime_seconds:.3f}")


def print_layer1_grid_summary(res: Layer1GridResult, *, artifact_root: str) -> None:
    """Plain summary lines for controlled grid CLI."""
    best_tr = max(res.rows, key=lambda r: r.total_r)

    def _pf_key(r: Layer1GridRow) -> float:
        return float("inf") if r.profit_factor_r == float("inf") else r.profit_factor_r

    best_pf = max(res.rows, key=_pf_key)
    total_acc = sum(r.accepted_trades for r in res.rows)
    print(
        json.dumps(
            {
                "run_id": res.run_id,
                "combo_count": res.combo_count,
                "feature_hash": res.feature_hash,
                "execution_mode": res.execution_mode,
                "best_total_r": {"combo_id": best_tr.combo_id, "total_r": best_tr.total_r},
                "best_profit_factor_r": {
                    "combo_id": best_pf.combo_id,
                    "profit_factor_r": best_pf.profit_factor_r,
                },
                "total_accepted_trades": total_acc,
                "artifact_root": artifact_root,
            },
            indent=2,
        )
    )
