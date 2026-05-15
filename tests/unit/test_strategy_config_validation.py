"""Strategy config validation tests."""

from __future__ import annotations

import copy

import pytest
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.strategies.config_validation import validate_pa_buy_sell_close_trend_config
from intraday.strategies.loader import load_strategy_config


def _base() -> dict:
    return copy.deepcopy(
        load_strategy_config(repo_root() / "configs/strategies/base/pa_buy_sell_close_trend.yaml")
    )


def test_valid_base_passes() -> None:
    validate_pa_buy_sell_close_trend_config(_base())


def test_invalid_entry_window() -> None:
    cfg = _base()
    cfg["signal"]["entry_start_minute"] = 300
    cfg["signal"]["entry_end_minute"] = 60
    with pytest.raises(ConfigError):
        validate_pa_buy_sell_close_trend_config(cfg)


def test_invalid_stop_mode() -> None:
    cfg = _base()
    cfg["risk"]["stop_mode"] = "bogus"
    with pytest.raises(ConfigError):
        validate_pa_buy_sell_close_trend_config(cfg)


def test_invalid_target_r() -> None:
    cfg = _base()
    cfg["risk"]["target_r"] = 0
    with pytest.raises(ConfigError):
        validate_pa_buy_sell_close_trend_config(cfg)


def test_invalid_close_position() -> None:
    cfg = _base()
    cfg["signal"]["close_position_min"] = 1.5
    with pytest.raises(ConfigError):
        validate_pa_buy_sell_close_trend_config(cfg)
