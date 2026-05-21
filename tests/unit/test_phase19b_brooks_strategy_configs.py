"""Phase19B Brooks strategy config validation tests."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from intraday.core.config import load_yaml
from intraday.core.errors import ConfigError
from intraday.strategies.loader import validate_strategy_config

REPO = Path(__file__).resolve().parents[2]

STRATEGIES = (
    "pa_second_entry_pullback",
    "pa_trading_range_bls_hs",
    "pa_failed_breakout_trap",
    "pa_opening_reversal_sr",
    "pa_breakout_pullback_continuation",
    "pa_tight_channel_pullback",
    "pa_broad_channel_zone",
)


def _cfg(strategy: str) -> dict:
    return load_yaml(REPO / "configs" / "strategies" / "base" / "phase19" / f"{strategy}.yaml")


@pytest.mark.parametrize("strategy", STRATEGIES)
@pytest.mark.parametrize("side_mode", ("long_only", "short_only", "both"))
def test_phase19b_configs_accept_supported_side_modes(strategy: str, side_mode: str) -> None:
    cfg = _cfg(strategy)
    cfg["signal"]["side_mode"] = side_mode
    validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_phase19b_configs_reject_invalid_side_mode(strategy: str) -> None:
    cfg = _cfg(strategy)
    cfg["signal"]["side_mode"] = "sideways"
    with pytest.raises(ConfigError):
        validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_phase19b_configs_reject_target_price_modes(strategy: str) -> None:
    cfg = copy.deepcopy(_cfg(strategy))
    cfg["risk"]["target_mode"] = "range_mid"
    with pytest.raises(ConfigError, match="fixed_r"):
        validate_strategy_config(strategy, cfg)
