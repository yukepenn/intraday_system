"""VWAP trend pullback strategy tests."""

from intraday.strategies.vwap.trend_pullback import validate_vwap_trend_pullback_config

from tests.helpers import strategy_phase13 as sp13
from tests.helpers.strategy_phase13 import load_base_config


def test_base_yaml_validates() -> None:
    validate_vwap_trend_pullback_config(load_base_config("vwap_trend_pullback"))


def test_rejects_short_side() -> None:
    sp13.test_rejects_short_side(validate_vwap_trend_pullback_config, "vwap_trend_pullback")
