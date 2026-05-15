"""Synthetic controlled grid runner tests."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from intraday.core.arrays import FeatureMatrix, SignalMatrix
from intraday.core.paths import repo_root
from intraday.core.types import ExitReason, Side
from intraday.execution.records import TradeResult
from intraday.layer1.runner import run_layer1_controlled_grid

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


def _write_grid_fixtures() -> tuple[Path, Path]:
    root = repo_root()
    art = root / "artifacts" / "layer1_pa_controlled_grid_phase6b" / "_pytest_runner_grid2"
    art.mkdir(parents=True, exist_ok=True)
    grid_p = art / "two_combo.yaml"
    grid_p.write_text(
        """
strategy: pa_buy_sell_close_trend
base_config: configs/strategies/base/pa_buy_sell_close_trend.yaml
fixed: {}
grid:
  risk.target_r: [1.0, 1.35]
""".strip()
        + "\n",
        encoding="utf-8",
    )
    rel_grid = grid_p.relative_to(root).as_posix()
    rel_out = (art / "out").relative_to(root).as_posix()
    cfg_p = art / "layer1_grid_unit.yaml"
    cfg_p.write_text(
        f"""
run_id: UNIT_GRID2
description: unit grid
symbol: QQQ
start: 2024-01-01
end: 2024-01-03
data:
  data_root: data/curated/bars_1m_rth
feature:
  config: configs/features/pa_core_v1.yaml
  use_cache: false
strategy:
  name: pa_buy_sell_close_trend
  base_config: configs/strategies/base/pa_buy_sell_close_trend.yaml
  grid: {rel_grid}
execution:
  config: configs/execution/intraday_default.yaml
  mode: reference
backtest:
  max_trades_per_session: 1
  skip_while_trade_open: true
  count_rejected_intents: true
  save_row_level_trades: false
grid:
  max_combos: null
  allow_prefix_slicing: false
  require_no_fixed_grid_overlap: true
output:
  artifact_root: {rel_out}
""",
        encoding="utf-8",
    )
    return cfg_p, art


@patch("intraday.layer1.runner.simulate_trade_path_reference")
@patch("intraday.layer1.runner.build_feature_matrix")
@patch("intraday.layer1.runner.load_bars_from_curated")
def test_two_combo_grid_rows(mock_bars, mock_fm, mock_sim) -> None:
    cfg_p, _art = _write_grid_fixtures()
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
        feature_hash="fh_grid",
    )
    mock_fm.return_value = fm

    sigs = _signal_matrix(12, [1])
    mock_defn = MagicMock()
    mock_defn.generate_reference = lambda b, f, c: sigs  # noqa: ARG005

    seq = {"i": 0}
    rseq = [1.0, 1.35]

    def _sim(b, intent, spec):  # noqa: ARG001
        m = rseq[seq["i"]]
        seq["i"] += 1
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
            r_multiple=m,
            exit_reason=int(ExitReason.TARGET),
            bars_held=2,
        )

    mock_sim.side_effect = _sim

    with patch("intraday.layer1.runner.get_strategy", return_value=mock_defn):
        res = run_layer1_controlled_grid(cfg_p)

    assert res.combo_count == 2
    assert {r.combo_id for r in res.rows} == {"combo_0001", "combo_0002"}
    assert res.rows[0].config_hash != res.rows[1].config_hash
    rs_sorted = sorted(res.rows, key=lambda x: x.combo_id)
    assert rs_sorted[0].total_r == pytest.approx(1.0)
    assert rs_sorted[1].total_r == pytest.approx(1.35)
    assert mock_fm.call_count == 1


@patch("intraday.layer1.runner.simulate_trade_path_reference")
@patch("intraday.layer1.runner.build_feature_matrix")
@patch("intraday.layer1.runner.load_bars_from_curated")
def test_grid_skip_counts_per_combo(mock_bars, mock_fm, mock_sim) -> None:
    cfg_p, _ = _write_grid_fixtures()
    bars = make_bar_matrix(
        [100.0] * 12,
        [101.0] * 12,
        [99.0] * 12,
        [100.0] * 12,
        session_id=[0] * 12,
        minute=list(range(12)),
    )
    mock_bars.return_value = bars
    mock_fm.return_value = FeatureMatrix(
        values=np.zeros((bars.n_bars, 1)),
        columns={"x": 0},
        feature_hash="fh",
    )
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
        res = run_layer1_controlled_grid(cfg_p)

    for row in res.rows:
        skips = json.loads(row.skip_reason_counts_json)
        assert skips.get("max_trades_per_session", 0) == 1
