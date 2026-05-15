"""Synthetic Layer1 smoke runner tests (mocked bars / features / signals)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
from intraday.core.arrays import FeatureMatrix, SignalMatrix
from intraday.core.paths import repo_root
from intraday.core.types import ExitReason, Side
from intraday.execution.records import TradeResult
from intraday.layer1.runner import run_layer1_smoke

from tests.helpers.bars import make_bar_matrix


def _signal_matrix(n: int, entry_bars: list[int], *, sh: str = "h") -> SignalMatrix:
    entry = np.zeros(n, dtype=bool)
    side = np.zeros(n, dtype=np.int8)
    stop = np.full(n, np.nan, dtype=np.float64)
    target_r = np.full(n, np.nan, dtype=np.float64)
    score = np.full(n, np.nan, dtype=np.float64)
    setup = np.zeros(n, dtype=np.int16)
    for i in entry_bars:
        entry[i] = True
        side[i] = int(Side.LONG)
        stop[i] = 50.0
        target_r[i] = 1.0
        score[i] = 1.0
        setup[i] = 1001
    return SignalMatrix(entry, side, stop, target_r, score, setup, sh)


def _write_smoke_yaml(artifact_dir: Path, cfg_path: Path, *, max_trades: int = 1) -> None:
    root = repo_root()
    rel = artifact_dir.relative_to(root).as_posix()
    text = f"""
run_id: UNIT_LAYER1
description: unit
symbol: QQQ
asset: equity
timeframe: 1m
start: 2024-01-01
end: 2024-01-03
data:
  data_root: data/curated/bars_1m_rth
feature:
  config: configs/features/pa_core_v1.yaml
  use_cache: false
strategy:
  name: pa_buy_sell_close_trend
  config: configs/strategies/base/pa_buy_sell_close_trend.yaml
execution:
  config: configs/execution/intraday_default.yaml
  mode: reference
backtest:
  max_trades_per_session: {max_trades}
  skip_while_trade_open: true
  count_rejected_intents: true
  save_row_level_trades: false
output:
  artifact_root: {rel}
"""
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(text, encoding="utf-8")


@patch("intraday.layer1.runner.simulate_trade_path_reference")
@patch("intraday.layer1.runner.build_feature_matrix")
@patch("intraday.layer1.runner.load_bars_from_curated")
def test_max_trades_per_session_skips_second(mock_bars, mock_fm, mock_sim) -> None:
    root = repo_root()
    art = root / "artifacts" / "layer1_pa_smoke_phase6" / "_pytest_runner_max"
    cfgp = art / "smoke_unit.yaml"
    _write_smoke_yaml(art, cfgp, max_trades=1)

    bars = make_bar_matrix(
        [100.0] * 12,
        [101.0] * 12,
        [99.0] * 12,
        [100.0] * 12,
        session_id=[0] * 12,
        minute=list(range(12)),
    )
    mock_bars.return_value = bars
    fm = FeatureMatrix(
        values=np.zeros((bars.n_bars, 1)),
        columns={"x": 0},
        feature_hash="fh",
    )
    mock_fm.return_value = fm

    sigs = _signal_matrix(12, [0, 5])
    mock_defn = MagicMock()
    mock_defn.generate_reference = lambda b, f, c: sigs  # noqa: ARG005

    def _sim(b, intent, spec):  # noqa: ARG001
        return TradeResult.accepted_trade(
            candidate_id=1,
            signal_bar=intent.signal_bar,
            entry_bar=intent.signal_bar + 1,
            exit_bar=intent.signal_bar + 2,
            side=int(Side.LONG),
            qty=1.0,
            entry_price=100.0,
            stop_price=99.0,
            target_price=101.0,
            exit_price=101.0,
            gross_pnl=1.0,
            net_pnl=1.0,
            r_multiple=1.0,
            exit_reason=int(ExitReason.TARGET),
            bars_held=2,
        )

    mock_sim.side_effect = _sim

    with patch("intraday.layer1.runner.get_strategy", return_value=mock_defn):
        res = run_layer1_smoke(cfgp)

    assert res.metrics.accepted_trades == 1
    assert res.skip_counts["max_trades_per_session"] == 1
    assert res.executed_results == 1


@patch("intraday.layer1.runner.simulate_trade_path_reference")
@patch("intraday.layer1.runner.build_feature_matrix")
@patch("intraday.layer1.runner.load_bars_from_curated")
def test_trade_open_skip(mock_bars, mock_fm, mock_sim) -> None:
    root = repo_root()
    art = root / "artifacts" / "layer1_pa_smoke_phase6" / "_pytest_runner_skip"
    cfgp = art / "smoke_unit.yaml"
    _write_smoke_yaml(art, cfgp, max_trades=2)

    bars = make_bar_matrix(
        [100.0] * 12,
        [101.0] * 12,
        [99.0] * 12,
        [100.0] * 12,
        session_id=[0] * 12,
        minute=list(range(12)),
    )
    mock_bars.return_value = bars
    fm = FeatureMatrix(
        values=np.zeros((bars.n_bars, 1)),
        columns={"x": 0},
        feature_hash="fh",
    )
    mock_fm.return_value = fm
    sigs = _signal_matrix(12, [0, 2])
    mock_defn = MagicMock()
    mock_defn.generate_reference = lambda b, f, c: sigs  # noqa: ARG005

    def _sim(b, intent, spec):  # noqa: ARG001
        return TradeResult.accepted_trade(
            candidate_id=1,
            signal_bar=intent.signal_bar,
            entry_bar=intent.signal_bar + 1,
            exit_bar=8,
            side=int(Side.LONG),
            qty=1.0,
            entry_price=100.0,
            stop_price=99.0,
            target_price=101.0,
            exit_price=101.0,
            gross_pnl=1.0,
            net_pnl=1.0,
            r_multiple=1.0,
            exit_reason=int(ExitReason.TARGET),
            bars_held=3,
        )

    mock_sim.side_effect = _sim

    with patch("intraday.layer1.runner.get_strategy", return_value=mock_defn):
        res = run_layer1_smoke(cfgp)

    assert res.skip_counts["trade_open"] == 1
    assert res.executed_results == 1


@patch("intraday.layer1.runner.simulate_trade_path_reference")
@patch("intraday.layer1.runner.build_feature_matrix")
@patch("intraday.layer1.runner.load_bars_from_curated")
def test_execution_rejected_counts(mock_bars, mock_fm, mock_sim) -> None:
    root = repo_root()
    art = root / "artifacts" / "layer1_pa_smoke_phase6" / "_pytest_runner_rej"
    cfgp = art / "smoke_unit.yaml"
    _write_smoke_yaml(art, cfgp, max_trades=2)

    bars = make_bar_matrix(
        [100.0] * 8,
        [101.0] * 8,
        [99.0] * 8,
        [100.0] * 8,
        session_id=[0] * 8,
        minute=list(range(8)),
    )
    mock_bars.return_value = bars
    mock_fm.return_value = FeatureMatrix(
        values=np.zeros((bars.n_bars, 1)),
        columns={"x": 0},
        feature_hash="fh",
    )
    sigs = _signal_matrix(8, [0])
    mock_defn = MagicMock()
    mock_defn.generate_reference = lambda b, f, c: sigs  # noqa: ARG005

    mock_sim.return_value = TradeResult.rejected(
        reject_reason=7,
        candidate_id=1,
        signal_bar=0,
        side=int(Side.LONG),
        qty=1.0,
    )

    with patch("intraday.layer1.runner.get_strategy", return_value=mock_defn):
        res = run_layer1_smoke(cfgp)

    assert res.skip_counts["execution_rejected_included"] == 1
    assert res.metrics.rejected_trades == 1


@patch("intraday.layer1.runner.simulate_trade_path_reference")
@patch("intraday.layer1.runner.build_feature_matrix")
@patch("intraday.layer1.runner.load_bars_from_curated")
def test_execution_rejected_excluded_from_metrics(mock_bars, mock_fm, mock_sim) -> None:
    root = repo_root()
    art = root / "artifacts" / "layer1_pa_controlled_grid_phase6b" / "_pytest_runner_rej_excl"
    cfgp = art / "smoke_unit.yaml"
    art.mkdir(parents=True, exist_ok=True)
    rel = art.relative_to(root).as_posix()
    text = f"""
run_id: UNIT_LAYER1_REJ_EXCL
description: unit
symbol: QQQ
asset: equity
timeframe: 1m
start: 2024-01-01
end: 2024-01-03
data:
  data_root: data/curated/bars_1m_rth
feature:
  config: configs/features/pa_core_v1.yaml
  use_cache: false
strategy:
  name: pa_buy_sell_close_trend
  config: configs/strategies/base/pa_buy_sell_close_trend.yaml
execution:
  config: configs/execution/intraday_default.yaml
  mode: reference
backtest:
  max_trades_per_session: 2
  skip_while_trade_open: true
  count_rejected_intents: false
  save_row_level_trades: false
output:
  artifact_root: {rel}
"""
    cfgp.write_text(text, encoding="utf-8")

    bars = make_bar_matrix(
        [100.0] * 8,
        [101.0] * 8,
        [99.0] * 8,
        [100.0] * 8,
        session_id=[0] * 8,
        minute=list(range(8)),
    )
    mock_bars.return_value = bars
    mock_fm.return_value = FeatureMatrix(
        values=np.zeros((bars.n_bars, 1)),
        columns={"x": 0},
        feature_hash="fh",
    )
    sigs = _signal_matrix(8, [0])
    mock_defn = MagicMock()
    mock_defn.generate_reference = lambda b, f, c: sigs  # noqa: ARG005

    mock_sim.return_value = TradeResult.rejected(
        reject_reason=7,
        candidate_id=1,
        signal_bar=0,
        side=int(Side.LONG),
        qty=1.0,
    )

    with patch("intraday.layer1.runner.get_strategy", return_value=mock_defn):
        res = run_layer1_smoke(cfgp)

    assert res.skip_counts["execution_rejected_excluded"] == 1
    assert res.skip_counts["execution_rejected_included"] == 0
    assert res.metrics.rejected_trades == 0
    assert res.metrics.reject_reason_counts == {}
