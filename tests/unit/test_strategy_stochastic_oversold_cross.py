"""Stochastic oversold cross strategy tests."""

from intraday.strategies.stochastic.oversold_cross import validate_stochastic_oversold_cross_config

from tests.helpers import strategy_phase13 as sp13
from tests.helpers.strategy_phase13 import load_base_config


def test_base_yaml_validates() -> None:
    validate_stochastic_oversold_cross_config(load_base_config("stochastic_oversold_cross"))


def test_rejects_short_side() -> None:
    sp13.test_rejects_short_side(
        validate_stochastic_oversold_cross_config, "stochastic_oversold_cross"
    )
