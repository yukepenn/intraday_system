"""Prior-day level trap strategy tests."""

from intraday.strategies.levels.prior_day_level_trap import validate_prior_day_level_trap_config

from tests.helpers import strategy_phase13 as sp13
from tests.helpers.strategy_phase13 import load_base_config


def test_base_yaml_validates() -> None:
    validate_prior_day_level_trap_config(load_base_config("prior_day_level_trap"))


def test_rejects_short_side() -> None:
    sp13.test_rejects_short_side(validate_prior_day_level_trap_config, "prior_day_level_trap")
