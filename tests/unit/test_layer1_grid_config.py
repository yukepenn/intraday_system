"""Controlled grid Layer1 YAML loader tests."""

from __future__ import annotations

import pytest
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.layer1.config import (
    load_layer1_controlled_grid_config,
    validate_layer1_controlled_grid_config,
)


def test_repo_controlled_grid_loads() -> None:
    path = repo_root() / "configs/layer1/controlled_pa_qqq_2024h1.yaml"
    cfg = load_layer1_controlled_grid_config(path)
    validate_layer1_controlled_grid_config(cfg)
    assert cfg.execution_mode == "reference"
    assert not cfg.grid_allow_prefix_slicing


def test_prefix_slicing_true_rejected() -> None:
    root = repo_root()
    art = root / "artifacts" / "layer1_pa_controlled_grid_phase6b" / "_pytest_cfg_prefix"
    art.mkdir(parents=True, exist_ok=True)
    rel_out = (art / "out").relative_to(root).as_posix()
    p = art / "bad.yaml"
    p.write_text(
        f"""
run_id: X
description: d
symbol: QQQ
start: 2024-01-01
end: 2024-01-02
data:
  data_root: data/curated/bars_1m_rth
feature:
  config: configs/features/pa_core_v1.yaml
  use_cache: false
strategy:
  name: pa_buy_sell_close_trend
  base_config: configs/strategies/base/pa_buy_sell_close_trend.yaml
  grid: configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml
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
  allow_prefix_slicing: true
  require_no_fixed_grid_overlap: true
output:
  artifact_root: {rel_out}
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        load_layer1_controlled_grid_config(p)


def test_max_combos_guard() -> None:
    root = repo_root()
    art = root / "artifacts" / "layer1_pa_controlled_grid_phase6b" / "_pytest_cfg_max"
    art.mkdir(parents=True, exist_ok=True)
    rel_out = (art / "out").relative_to(root).as_posix()
    p = art / "mc.yaml"
    p.write_text(
        f"""
run_id: X
description: d
symbol: QQQ
start: 2024-01-01
end: 2024-01-02
data:
  data_root: data/curated/bars_1m_rth
feature:
  config: configs/features/pa_core_v1.yaml
  use_cache: false
strategy:
  name: pa_buy_sell_close_trend
  base_config: configs/strategies/base/pa_buy_sell_close_trend.yaml
  grid: configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml
execution:
  config: configs/execution/intraday_default.yaml
  mode: reference
backtest:
  max_trades_per_session: 1
  skip_while_trade_open: true
  count_rejected_intents: true
  save_row_level_trades: false
grid:
  max_combos: 8
  allow_prefix_slicing: false
  require_no_fixed_grid_overlap: true
output:
  artifact_root: {rel_out}
""",
        encoding="utf-8",
    )
    cfg = load_layer1_controlled_grid_config(p)
    with pytest.raises(ConfigError) as exc:
        validate_layer1_controlled_grid_config(cfg)
    assert "combos" in str(exc.value).lower()


def test_missing_grid_path() -> None:
    root = repo_root()
    art = root / "artifacts" / "layer1_pa_controlled_grid_phase6b" / "_pytest_cfg_missing"
    art.mkdir(parents=True, exist_ok=True)
    rel_out = (art / "out").relative_to(root).as_posix()
    p = art / "mg.yaml"
    p.write_text(
        f"""
run_id: X
description: d
symbol: QQQ
start: 2024-01-01
end: 2024-01-02
data:
  data_root: data/curated/bars_1m_rth
feature:
  config: configs/features/pa_core_v1.yaml
  use_cache: false
strategy:
  name: pa_buy_sell_close_trend
  base_config: configs/strategies/base/pa_buy_sell_close_trend.yaml
  grid: configs/strategies/grids/does_not_exist_grid.yaml
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
    cfg = load_layer1_controlled_grid_config(p)
    with pytest.raises(ConfigError):
        validate_layer1_controlled_grid_config(cfg)
