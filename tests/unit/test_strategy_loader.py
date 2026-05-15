"""Strategy loader tests."""

from __future__ import annotations

import pytest
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.strategies.loader import (
    load_strategy_config,
    load_strategy_grid,
    load_strategy_metadata,
    resolve_strategy_config,
    validate_strategy_config,
)


def test_pa_base_config_loads_and_validates() -> None:
    root = repo_root()
    cfg = load_strategy_config(root / "configs/strategies/base/pa_buy_sell_close_trend.yaml")
    assert cfg["strategy"] == "pa_buy_sell_close_trend"
    validate_strategy_config("pa_buy_sell_close_trend", cfg)


def test_pa_metadata_loads() -> None:
    root = repo_root()
    meta = load_strategy_metadata(root / "configs/strategies/metadata/pa_buy_sell_close_trend.yaml")
    assert meta["setup_codes"][1001] == "PA_BUY_SELL_CLOSE_TREND_LONG"


def test_pa_grid_loads() -> None:
    root = repo_root()
    grid = load_strategy_grid(
        root / "configs/strategies/grids/pa_buy_sell_close_trend_focused.yaml"
    )
    assert grid["strategy"] == "pa_buy_sell_close_trend"
    assert "grid" in grid


def test_resolve_strategy_config_from_dict() -> None:
    d = {"strategy": "pa_buy_sell_close_trend", "signal": {"side": "long_only"}}
    assert resolve_strategy_config(d)["strategy"] == "pa_buy_sell_close_trend"


def test_invalid_side_rejected() -> None:
    root = repo_root()
    cfg = load_strategy_config(root / "configs/strategies/base/pa_buy_sell_close_trend.yaml")
    cfg = dict(cfg)
    cfg["signal"] = dict(cfg["signal"])
    cfg["signal"]["side"] = "short_only"
    with pytest.raises(ConfigError):
        validate_strategy_config("pa_buy_sell_close_trend", cfg)
