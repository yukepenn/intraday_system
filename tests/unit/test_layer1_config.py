"""Layer1 smoke YAML loader tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.layer1.config import load_layer1_smoke_config, validate_layer1_smoke_config


def test_repo_smoke_config_loads_and_validates() -> None:
    path = repo_root() / "configs/layer1/smoke_pa_qqq_2024h1.yaml"
    cfg = load_layer1_smoke_config(path)
    validate_layer1_smoke_config(cfg)
    assert cfg.execution_mode == "reference"
    assert cfg.max_trades_per_session == 1
    assert not cfg.save_row_level_trades


def test_invalid_execution_mode(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text(
        """
run_id: X
symbol: QQQ
start: 2024-01-01
end: 2024-01-02
data: { data_root: data/curated/bars_1m_rth }
feature: { config: configs/features/pa_core_v1.yaml, use_cache: false }
strategy: { name: pa_buy_sell_close_trend, config: configs/strategies/base/pa_buy_sell_close_trend.yaml }
execution: { config: configs/execution/intraday_default.yaml, mode: bogus }
backtest:
  max_trades_per_session: 1
  skip_while_trade_open: true
  count_rejected_intents: true
  save_row_level_trades: false
output: { artifact_root: artifacts/layer1_pa_smoke_phase6/local_run }
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        load_layer1_smoke_config(p)


@pytest.mark.parametrize(
    "artifact_root",
    (
        "C:/tmp/abs",
        r"D:\TradingData\x",
        r"\\server\share\x",
        "/tmp/abs",
        r"C:tmp\relative_to_current_dir_on_drive",
    ),
)
def test_absolute_artifact_root_rejected(tmp_path: Path, artifact_root: str) -> None:
    p = tmp_path / "bad2.yaml"
    p.write_text(
        f"""
run_id: X
symbol: QQQ
start: 2024-01-01
end: 2024-01-02
data: {{ data_root: data/curated/bars_1m_rth }}
feature: {{ config: configs/features/pa_core_v1.yaml, use_cache: false }}
strategy: {{ name: pa_buy_sell_close_trend, config: configs/strategies/base/pa_buy_sell_close_trend.yaml }}
execution: {{ config: configs/execution/intraday_default.yaml, mode: reference }}
backtest:
  max_trades_per_session: 1
  skip_while_trade_open: true
  count_rejected_intents: true
  save_row_level_trades: false
output: {{ artifact_root: {json.dumps(artifact_root)} }}
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        load_layer1_smoke_config(p)


@pytest.mark.parametrize(
    "artifact_root",
    ("artifacts/layer1_pa_smoke_phase6/local_run", r"artifacts\layer1_pa_smoke_phase6\local_run"),
)
def test_relative_artifact_roots_accepted(tmp_path: Path, artifact_root: str) -> None:
    p = tmp_path / "ok.yaml"
    p.write_text(
        f"""
run_id: X
symbol: QQQ
start: 2024-01-01
end: 2024-01-02
data: {{ data_root: data/curated/bars_1m_rth }}
feature: {{ config: configs/features/pa_core_v1.yaml, use_cache: false }}
strategy: {{ name: pa_buy_sell_close_trend, config: configs/strategies/base/pa_buy_sell_close_trend.yaml }}
execution: {{ config: configs/execution/intraday_default.yaml, mode: reference }}
backtest:
  max_trades_per_session: 1
  skip_while_trade_open: true
  count_rejected_intents: true
  save_row_level_trades: false
output: {{ artifact_root: {json.dumps(artifact_root)} }}
""",
        encoding="utf-8",
    )
    cfg = load_layer1_smoke_config(p)
    assert cfg.artifact_root == artifact_root
