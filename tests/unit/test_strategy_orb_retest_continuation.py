"""ORB retest continuation strategy tests."""

from intraday.strategies.orb.retest_continuation import (
    validate_orb_retest_continuation_config,
)

from tests.helpers import strategy_phase13 as sp13
from tests.helpers.strategy_phase13 import load_base_config


def test_base_yaml_validates() -> None:
    validate_orb_retest_continuation_config(load_base_config("orb_retest_continuation"))


def test_rejects_short_side() -> None:
    sp13.test_rejects_short_side(validate_orb_retest_continuation_config, "orb_retest_continuation")
