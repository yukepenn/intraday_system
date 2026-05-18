"""CCI extreme snapback strategy tests."""

from intraday.strategies.cci.extreme_snapback import validate_cci_extreme_snapback_config

from tests.helpers import strategy_phase13 as sp13
from tests.helpers.strategy_phase13 import load_base_config


def test_base_yaml_validates() -> None:
    validate_cci_extreme_snapback_config(load_base_config("cci_extreme_snapback"))


def test_rejects_short_side() -> None:
    sp13.test_rejects_short_side(validate_cci_extreme_snapback_config, "cci_extreme_snapback")
