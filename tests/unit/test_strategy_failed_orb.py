"""Failed ORB strategy tests."""

from intraday.strategies.orb.failed_orb import validate_failed_orb_config

from tests.helpers import strategy_phase13 as sp13
from tests.helpers.strategy_phase13 import load_base_config


def test_base_yaml_validates() -> None:
    validate_failed_orb_config(load_base_config("failed_orb"))


def test_rejects_short_side() -> None:
    sp13.test_rejects_short_side(validate_failed_orb_config, "failed_orb")
