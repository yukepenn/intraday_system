"""Phase19B side_mode validation gate tests."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from intraday.core.config import load_yaml
from intraday.core.errors import ConfigError
from intraday.strategies.config_validation import validate_side_mode_allowed
from intraday.strategies.loader import validate_strategy_config

REPO = Path(__file__).resolve().parents[2]

CURRENT10 = (
    "pa_buy_sell_close_trend",
    "orb_continuation",
    "orb_retest_continuation",
    "failed_orb",
    "gap_acceptance_failure",
    "vwap_trend_pullback",
    "vwap_reclaim_reject",
    "prior_day_level_trap",
    "cci_extreme_snapback",
    "stochastic_oversold_cross",
)


def _base_config(strategy: str) -> dict:
    return load_yaml(REPO / "configs" / "strategies" / "base" / f"{strategy}.yaml")


def _phase18b_config(strategy: str) -> dict:
    return load_yaml(REPO / "configs" / "strategies" / "base" / "phase18b" / f"{strategy}_v2.yaml")


@pytest.mark.parametrize("strategy", CURRENT10)
@pytest.mark.parametrize("side_mode", ("long_only", "short_only", "both"))
def test_current10_accept_all_side_modes(strategy: str, side_mode: str) -> None:
    """Phase19 immediate fix: current-10 now accepts long_only, short_only, both."""
    cfg = copy.deepcopy(_base_config(strategy))
    cfg["signal"].pop("side", None)
    cfg["signal"]["side_mode"] = side_mode
    validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize("strategy", CURRENT10)
@pytest.mark.parametrize("side_mode", ("long_only", "short_only", "both"))
def test_current10_phase18b_accept_all_side_modes(strategy: str, side_mode: str) -> None:
    cfg = copy.deepcopy(_phase18b_config(strategy))
    cfg["signal"].pop("side", None)
    cfg["signal"]["side_mode"] = side_mode
    validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize("strategy", CURRENT10)
def test_current10_reject_unknown_side_mode(strategy: str) -> None:
    cfg = copy.deepcopy(_base_config(strategy))
    cfg["signal"].pop("side", None)
    cfg["signal"]["side_mode"] = "not_a_side"
    with pytest.raises(ConfigError, match="side_mode"):
        validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize("strategy", CURRENT10)
def test_current10_accept_missing_or_long_side_mode(strategy: str) -> None:
    cfg = copy.deepcopy(_base_config(strategy))
    cfg["signal"].pop("side", None)
    validate_strategy_config(strategy, cfg)

    cfg["signal"]["side_mode"] = "long_only"
    validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize("side_mode", ("long_only", "short_only", "both"))
def test_phase19_side_mode_helper_accepts_brooks_modes(side_mode: str) -> None:
    assert (
        validate_side_mode_allowed(
            {"side_mode": side_mode},
            allowed=("long_only", "short_only", "both"),
        )
        == side_mode
    )


def test_phase19_side_mode_helper_rejects_invalid_mode() -> None:
    with pytest.raises(ConfigError):
        validate_side_mode_allowed(
            {"side_mode": "not_a_side"},
            allowed=("long_only", "short_only", "both"),
        )
