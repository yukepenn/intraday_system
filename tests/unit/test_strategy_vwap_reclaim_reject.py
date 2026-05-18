"""VWAP reclaim strategy tests."""

from intraday.strategies.vwap.reclaim_reject import validate_vwap_reclaim_reject_config

from tests.helpers import strategy_phase13 as sp13
from tests.helpers.strategy_phase13 import load_base_config


def test_base_yaml_validates() -> None:
    validate_vwap_reclaim_reject_config(load_base_config("vwap_reclaim_reject"))


def test_rejects_short_side() -> None:
    sp13.test_rejects_short_side(validate_vwap_reclaim_reject_config, "vwap_reclaim_reject")
