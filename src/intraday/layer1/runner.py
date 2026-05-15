"""Layer1 smoke runner: bars → features → signals → intents → execution → metrics."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from intraday.backtest.metrics import summarize_trade_results
from intraday.backtest.signal_adapter import build_trade_intents_from_signals
from intraday.core.paths import repo_root
from intraday.data.loader import load_bars_from_curated
from intraday.execution import (
    assert_trade_results_equal,
    simulate_trade_path_fast,
    simulate_trade_path_reference,
)
from intraday.execution.records import TradeResult
from intraday.execution.spec import load_execution_spec, merge_execution_spec_with_strategy
from intraday.features.engine import build_feature_matrix
from intraday.features.specs import load_feature_config
from intraday.layer1 import reports
from intraday.layer1.config import (
    Layer1SmokeConfig,
    load_layer1_smoke_config,
    validate_layer1_smoke_config,
)
from intraday.layer1.result import Layer1SmokeResult, layer1_smoke_result_to_jsonable
from intraday.strategies.contracts import validate_signal_matrix
from intraday.strategies.loader import load_strategy_config, validate_strategy_config
from intraday.strategies.registry import get_strategy, register_builtin_strategies


def _resolve(root: Path, p: str) -> Path:
    path = Path(p)
    return path if path.is_absolute() else (root / path)


def _max_trades_for_run(smoke: Layer1SmokeConfig, strategy_cfg: Mapping[str, Any]) -> int:
    m = smoke.max_trades_per_session
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
    validate_signal_matrix(signals, bars.n_bars)

    qty, max_hold_bars = _qty_and_hold(strat_cfg)
    adapter = build_trade_intents_from_signals(
        signals,
        qty=qty,
        max_hold_bars=max_hold_bars,
        candidate_id=1,
    )

    base_spec = load_execution_spec(exe_path)
    spec = merge_execution_spec_with_strategy(base_spec, strat_cfg)

    skip_counts: dict[str, int] = {
        "invalid_signal": int(adapter.skipped_invalid),
        "max_trades_per_session": 0,
        "trade_open": 0,
        "execution_rejected": 0,
    }

    intents_sorted = sorted(adapter.intents, key=lambda x: x.signal_bar)
    max_trades = _max_trades_for_run(smoke, strat_cfg)

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

        if smoke.skip_while_trade_open and intent.signal_bar < next_min_signal_bar:
            skip_counts["trade_open"] += 1
            continue

        if accepted_in_session >= max_trades:
            skip_counts["max_trades_per_session"] += 1
            continue

        if smoke.execution_mode == "reference":
            res = simulate_trade_path_reference(bars, intent, spec)
        elif smoke.execution_mode == "fast":
            res = simulate_trade_path_fast(bars, intent, spec)
        else:
            ref = simulate_trade_path_reference(bars, intent, spec)
            fast = simulate_trade_path_fast(bars, intent, spec)
            assert_trade_results_equal(ref, fast)
            fast_checked = True
            res = ref

        results.append(res)
        if not res.accepted:
            skip_counts["execution_rejected"] += 1
            continue

        accepted_in_session += 1
        next_min_signal_bar = int(res.exit_bar) + 1

    metrics = summarize_trade_results(results)

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
        fast_parity_checked=fast_checked or (smoke.execution_mode == "both"),
        runtime_seconds=elapsed,
    )

    reports.write_layer1_smoke_artifacts(
        artifact_root,
        smoke=smoke,
        result=result,
        adapter_skip_reasons=dict(adapter.skip_reasons),
    )
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
