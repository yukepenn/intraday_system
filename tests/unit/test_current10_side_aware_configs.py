"""Phase19 immediate fix: current-10 side_mode config validation tests."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from intraday.core.config import load_yaml
from intraday.core.errors import ConfigError
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


@pytest.mark.parametrize("strategy", CURRENT10)
@pytest.mark.parametrize("side_mode", ("long_only", "short_only", "both"))
def test_current10_accepts_all_side_modes_via_side_mode_field(
    strategy: str, side_mode: str
) -> None:
    cfg = copy.deepcopy(_base_config(strategy))
    cfg["signal"].pop("side", None)
    cfg["signal"]["side_mode"] = side_mode
    validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize("strategy", CURRENT10)
def test_current10_accepts_legacy_side_long_only(strategy: str) -> None:
    cfg = copy.deepcopy(_base_config(strategy))
    cfg["signal"].pop("side_mode", None)
    cfg["signal"]["side"] = "long_only"
    validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize("strategy", CURRENT10)
def test_current10_missing_side_mode_validates_as_long_only(strategy: str) -> None:
    cfg = copy.deepcopy(_base_config(strategy))
    cfg["signal"].pop("side_mode", None)
    cfg["signal"].pop("side", None)
    validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize("strategy", CURRENT10)
def test_current10_rejects_unknown_side_mode(strategy: str) -> None:
    cfg = copy.deepcopy(_base_config(strategy))
    cfg["signal"].pop("side", None)
    cfg["signal"]["side_mode"] = "not_a_side"
    with pytest.raises(ConfigError):
        validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize("strategy", CURRENT10)
def test_current10_canonical_configs_use_side_mode(strategy: str) -> None:
    cfg = _base_config(strategy)
    # Phase19 immediate fix: canonical base configs migrate to side_mode.
    assert cfg["signal"].get("side_mode") == "long_only"
