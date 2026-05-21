"""Phase19A Layer1 side-runtime wiring repair tests."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest
from intraday.backtest.signal_adapter import (
    SignalAdapterResult,
)
from intraday.backtest.signal_adapter import (
    build_trade_intents_from_signals as real_build_trade_intents,
)
from intraday.core.arrays import FeatureMatrix, SignalMatrix
from intraday.core.config import load_yaml
from intraday.core.paths import repo_root
from intraday.core.types import RejectReason, Side
from intraday.execution.records import TradeResult
from intraday.layer1 import runner
from intraday.layer1.runner import run_layer1_controlled_grid, run_layer1_smoke
from intraday.strategies.contracts import (
    SIDE_MODE_LONG_ONLY,
    allowed_sides_for_mode,
)
from intraday.strategies.contracts import (
    validate_signal_matrix as real_validate_signal_matrix,
)

from tests.helpers.bars import make_bar_matrix


def _bars() -> Any:
    return make_bar_matrix(
        [100.0, 100.0, 100.0, 100.0],
        [100.5, 100.5, 100.5, 100.5],
        [99.5, 99.5, 97.0, 99.5],
        [100.0, 100.0, 100.0, 100.0],
        session_id=[0, 0, 0, 0],
        minute=[0, 1, 2, 3],
    )


def _features(n_bars: int) -> FeatureMatrix:
    return FeatureMatrix(
        values=np.zeros((n_bars, 1), dtype=np.float64),
        columns={"x": 0},
        feature_hash="phase19a_layer1_side_runtime",
    )


def _strategy_cfg(side_mode: str | None = None) -> dict[str, Any]:
    signal: dict[str, Any] = {}
    if side_mode is not None:
        signal["side_mode"] = side_mode
    return {
        "strategy": "synthetic_phase19a_side_runtime",
        "version": "strategy_v1",
        "signal": signal,
        "risk": {"max_trades_per_day": 10, "min_risk_per_share": 0.01},
        "backtest": {"quantity": 1.0, "max_hold_minutes": 2},
    }


def _signals(sides_by_bar: Mapping[int, int], *, invalid_short_stop: bool = False) -> SignalMatrix:
    n = 4
    entry = np.zeros(n, dtype=bool)
    side = np.zeros(n, dtype=np.int8)
    stop = np.full(n, np.nan, dtype=np.float64)
    target_r = np.full(n, np.nan, dtype=np.float64)
    score = np.full(n, np.nan, dtype=np.float64)
    setup_code = np.zeros(n, dtype=np.int16)
    for bar, side_value in sides_by_bar.items():
        entry[bar] = True
        side[bar] = side_value
        if side_value == int(Side.SHORT):
            stop[bar] = 99.0 if invalid_short_stop else 102.0
            setup_code[bar] = 7201
        else:
            stop[bar] = 98.0
            setup_code[bar] = 7101
        target_r[bar] = 1.0
        score[bar] = 1.0
    return SignalMatrix(entry, side, stop, target_r, score, setup_code, "phase19a_layer1")


def _write_smoke_yaml(path: Path, artifact_root: Path) -> None:
    root = repo_root()
    rel_artifact = artifact_root.relative_to(root).as_posix()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""
run_id: PHASE19A_LAYER1_SIDE_RUNTIME_SMOKE
description: unit
symbol: QQQ
asset: equity
timeframe: 1m
start: 2024-01-01
end: 2024-01-02
data:
  data_root: data/curated/bars_1m_rth
feature:
  config: configs/features/pa_core_v1.yaml
  use_cache: false
strategy:
  name: synthetic_phase19a_side_runtime
  config: configs/strategies/base/pa_buy_sell_close_trend.yaml
execution:
  config: configs/execution/intraday_default.yaml
  mode: reference
backtest:
  max_trades_per_session: 10
  skip_while_trade_open: false
  count_rejected_intents: true
  save_row_level_trades: false
output:
  artifact_root: {rel_artifact}
""",
        encoding="utf-8",
    )


def _write_grid_yaml(path: Path, artifact_root: Path, base_cfg: dict[str, Any]) -> None:
    root = repo_root()
    path.parent.mkdir(parents=True, exist_ok=True)
    base_path = path.parent / "synthetic_strategy_base.yaml"
    base_path.write_text(
        "strategy: synthetic_phase19a_side_runtime\n"
        "version: strategy_v1\n"
        "signal: {}\n"
        "risk:\n"
        "  max_trades_per_day: 10\n"
        "  min_risk_per_share: 0.01\n"
        "backtest:\n"
        "  quantity: 1.0\n"
        "  max_hold_minutes: 2\n",
        encoding="utf-8",
    )
    base_ref = base_path.as_posix()
    grid_path = path.parent / "synthetic_grid.yaml"
    side_mode = base_cfg.get("signal", {}).get("side_mode", SIDE_MODE_LONG_ONLY)
    grid_path.write_text(
        f"""
strategy: synthetic_phase19a_side_runtime
base_config: "{base_ref}"
fixed:
  signal.side_mode: {side_mode}
grid: {{}}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    grid_ref = grid_path.as_posix()
    rel_artifact = artifact_root.relative_to(root).as_posix()
    path.write_text(
        f"""
run_id: PHASE19A_LAYER1_SIDE_RUNTIME_GRID
description: unit
symbol: QQQ
start: 2024-01-01
end: 2024-01-02
data:
  data_root: data/curated/bars_1m_rth
feature:
  config: configs/features/pa_core_v1.yaml
  use_cache: false
strategy:
  name: synthetic_phase19a_side_runtime
  base_config: "{base_ref}"
  grid: "{grid_ref}"
execution:
  config: configs/execution/intraday_default.yaml
  mode: reference
backtest:
  max_trades_per_session: 10
  skip_while_trade_open: false
  count_rejected_intents: true
  save_row_level_trades: false
grid:
  max_combos: null
  allow_prefix_slicing: false
  require_no_fixed_grid_overlap: true
output:
  artifact_root: {rel_artifact}
""",
        encoding="utf-8",
    )


def _accepted_result(side: int) -> TradeResult:
    return TradeResult.accepted_trade(
        candidate_id=1,
        signal_bar=0,
        entry_bar=1,
        exit_bar=2,
        side=side,
        qty=1.0,
        entry_price=100.0,
        stop_price=102.0 if side == int(Side.SHORT) else 98.0,
        target_price=98.0 if side == int(Side.SHORT) else 102.0,
        exit_price=98.0 if side == int(Side.SHORT) else 102.0,
        gross_pnl=2.0,
        net_pnl=2.0,
        r_multiple=1.0,
        exit_reason=2,
        bars_held=2,
    )


def _run_smoke(
    monkeypatch: pytest.MonkeyPatch,
    tmp_name: str,
    strategy_cfg: dict[str, Any],
    signals: SignalMatrix,
    *,
    simulate: Callable[..., TradeResult] | None = None,
) -> Any:
    root = repo_root()
    artifact_root = root / "artifacts" / "phase19a_layer1_side_runtime_wiring_repair" / "_pytest"
    bars = _bars()
    defn = MagicMock()
    defn.generate_reference.return_value = signals
    monkeypatch.setattr(runner, "load_bars_from_curated", lambda *args, **kwargs: bars)
    monkeypatch.setattr(
        runner, "build_feature_matrix", lambda *args, **kwargs: _features(bars.n_bars)
    )
    monkeypatch.setattr(runner, "load_strategy_config", lambda path: strategy_cfg)
    monkeypatch.setattr(runner, "validate_strategy_config", lambda name, cfg: None)
    monkeypatch.setattr(runner, "get_strategy", lambda name: defn)
    monkeypatch.setattr(
        runner.reports, "write_layer1_smoke_artifacts", lambda *args, **kwargs: None
    )
    if simulate is not None:
        monkeypatch.setattr(runner, "simulate_trade_path_reference", simulate)
    with TemporaryDirectory(prefix=f"{tmp_name}_") as tmp_dir:
        cfg_path = Path(tmp_dir) / "smoke.yaml"
        _write_smoke_yaml(cfg_path, artifact_root)
        return run_layer1_smoke(cfg_path)


def _run_grid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_name: str,
    strategy_cfg: dict[str, Any],
    signals: SignalMatrix,
    *,
    simulate: Callable[..., TradeResult] | None = None,
) -> Any:
    root = repo_root()
    artifact_root = root / "artifacts" / "phase19a_layer1_side_runtime_wiring_repair" / "_pytest"
    bars = _bars()
    defn = MagicMock()
    defn.generate_reference.return_value = signals
    monkeypatch.setattr(runner, "load_bars_from_curated", lambda *args, **kwargs: bars)
    monkeypatch.setattr(
        runner, "build_feature_matrix", lambda *args, **kwargs: _features(bars.n_bars)
    )
    monkeypatch.setattr(runner, "validate_strategy_config", lambda name, cfg: None)
    monkeypatch.setattr(runner, "get_strategy", lambda name: defn)
    monkeypatch.setattr(runner.reports, "write_layer1_grid_artifacts", lambda *args, **kwargs: None)
    if simulate is not None:
        monkeypatch.setattr(runner, "simulate_trade_path_reference", simulate)
    with TemporaryDirectory(prefix=f"{tmp_name}_") as tmp_dir:
        cfg_path = Path(tmp_dir) / "grid.yaml"
        _write_grid_yaml(cfg_path, artifact_root, strategy_cfg)
        return run_layer1_controlled_grid(cfg_path)


def test_layer1_smoke_passes_reference_close_to_signal_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[np.ndarray | None] = []

    def _validate(signals: SignalMatrix, n_bars: int, *, reference_close=None) -> None:
        seen.append(reference_close)
        real_validate_signal_matrix(signals, n_bars, reference_close=reference_close)

    monkeypatch.setattr(runner, "validate_signal_matrix", _validate)
    _run_smoke(
        monkeypatch,
        "pytest_smoke_reference_close",
        _strategy_cfg("short_only"),
        _signals({0: int(Side.SHORT)}),
        simulate=lambda b, intent, spec: _accepted_result(intent.side),
    )
    assert seen and seen[0] is not None


def test_layer1_grid_passes_reference_close_to_signal_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[np.ndarray | None] = []

    def _validate(signals: SignalMatrix, n_bars: int, *, reference_close=None) -> None:
        seen.append(reference_close)
        real_validate_signal_matrix(signals, n_bars, reference_close=reference_close)

    monkeypatch.setattr(runner, "validate_signal_matrix", _validate)
    _run_grid(
        monkeypatch,
        "pytest_grid_reference_close",
        _strategy_cfg("short_only"),
        _signals({0: int(Side.SHORT)}),
        simulate=lambda b, intent, spec: _accepted_result(intent.side),
    )
    assert seen and seen[0] is not None


def test_layer1_smoke_derives_allowed_sides_from_signal_side_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[tuple[int | Side, ...]] = []

    def _adapter(signals: SignalMatrix, **kwargs: Any) -> SignalAdapterResult:
        seen.append(kwargs["allowed_sides"])
        return real_build_trade_intents(signals, **kwargs)

    monkeypatch.setattr(runner, "build_trade_intents_from_signals", _adapter)
    _run_smoke(
        monkeypatch,
        "pytest_smoke_allowed_sides",
        _strategy_cfg("short_only"),
        _signals({0: int(Side.SHORT)}),
        simulate=lambda b, intent, spec: _accepted_result(intent.side),
    )
    assert seen == [allowed_sides_for_mode("short_only")]


def test_layer1_grid_derives_allowed_sides_from_signal_side_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[tuple[int | Side, ...]] = []

    def _adapter(signals: SignalMatrix, **kwargs: Any) -> SignalAdapterResult:
        seen.append(kwargs["allowed_sides"])
        return real_build_trade_intents(signals, **kwargs)

    monkeypatch.setattr(runner, "build_trade_intents_from_signals", _adapter)
    _run_grid(
        monkeypatch,
        "pytest_grid_allowed_sides",
        _strategy_cfg("short_only"),
        _signals({0: int(Side.SHORT)}),
        simulate=lambda b, intent, spec: _accepted_result(intent.side),
    )
    assert seen == [allowed_sides_for_mode("short_only")]


def test_layer1_short_only_strategy_builds_short_intents_when_side_mode_short_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _run_smoke(
        monkeypatch,
        "pytest_short_only_intents",
        _strategy_cfg("short_only"),
        _signals({0: int(Side.SHORT)}),
        simulate=lambda b, intent, spec: _accepted_result(intent.side),
    )
    assert result.signal_entries == 1
    assert result.valid_intents == 1
    assert result.executed_results == 1


def test_layer1_both_strategy_builds_long_and_short_intents_when_side_mode_both(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_sides: list[int] = []

    def _simulate(bars, intent, spec):  # noqa: ANN001, ARG001
        seen_sides.append(intent.side)
        return _accepted_result(intent.side)

    result = _run_smoke(
        monkeypatch,
        "pytest_both_intents",
        _strategy_cfg("both"),
        _signals({0: int(Side.LONG), 1: int(Side.SHORT)}),
        simulate=_simulate,
    )
    assert result.valid_intents == 2
    assert seen_sides == [int(Side.LONG), int(Side.SHORT)]


def test_layer1_long_only_strategy_skips_short_signals_as_side_not_allowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _run_smoke(
        monkeypatch,
        "pytest_long_only_skips_short",
        _strategy_cfg("long_only"),
        _signals({0: int(Side.SHORT)}),
        simulate=lambda b, intent, spec: _accepted_result(intent.side),
    )
    assert result.signal_entries == 1
    assert result.valid_intents == 0
    assert result.skip_counts["invalid_signal"] == 1


def test_layer1_short_intent_reaches_execution_and_is_rejected_when_allow_short_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_sides: list[int] = []

    def _simulate(bars, intent, spec):  # noqa: ANN001, ARG001
        seen_sides.append(intent.side)
        assert spec.allow_short is False
        return TradeResult.rejected(
            reject_reason=int(RejectReason.SHORT_NOT_ALLOWED),
            candidate_id=intent.candidate_id,
            signal_bar=intent.signal_bar,
            side=intent.side,
            qty=float(intent.qty),
        )

    result = _run_smoke(
        monkeypatch,
        "pytest_short_rejected_by_execution",
        _strategy_cfg("short_only"),
        _signals({0: int(Side.SHORT)}),
        simulate=_simulate,
    )
    assert seen_sides == [int(Side.SHORT)]
    assert result.valid_intents == 1
    assert result.metrics.rejected_trades == 1
    assert result.metrics.reject_reason_counts == {"SHORT_NOT_ALLOWED": 1}


def test_layer1_short_intent_reaches_execution_and_can_be_accepted_when_allow_short_true(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_sides: list[int] = []

    def _short_spec(path: Path | str):  # noqa: ANN001
        raw = load_yaml(repo_root() / "configs" / "execution" / "intraday_default.yaml")
        raw["allow_short"] = True
        return runner.ExecutionSpec.from_config(raw)

    def _simulate(bars, intent, spec):  # noqa: ANN001, ARG001
        seen_sides.append(intent.side)
        assert spec.allow_short is True
        return _accepted_result(intent.side)

    monkeypatch.setattr(runner, "load_execution_spec", _short_spec)
    result = _run_smoke(
        monkeypatch,
        "pytest_short_accepted_by_execution",
        _strategy_cfg("short_only"),
        _signals({0: int(Side.SHORT)}),
        simulate=_simulate,
    )
    assert seen_sides == [int(Side.SHORT)]
    assert result.valid_intents == 1
    assert result.metrics.accepted_trades == 1


def test_current10_layer1_outputs_unchanged_or_behaviorally_equivalent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _run_smoke(
        monkeypatch,
        "pytest_current10_default_long_only",
        _strategy_cfg(None),
        _signals({0: int(Side.LONG)}),
        simulate=lambda b, intent, spec: _accepted_result(intent.side),
    )
    assert runner._allowed_sides_from_strategy_cfg(_strategy_cfg(None)) == (int(Side.LONG),)
    assert result.signal_entries == 1
    assert result.valid_intents == 1
    assert result.metrics.accepted_trades == 1
