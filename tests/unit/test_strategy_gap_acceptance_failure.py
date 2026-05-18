"""Gap acceptance failure strategy tests."""

from intraday.strategies.gap.acceptance_failure import validate_gap_acceptance_failure_config

from tests.helpers import strategy_phase13 as sp13
from tests.helpers.strategy_phase13 import load_base_config


def test_base_yaml_validates() -> None:
    validate_gap_acceptance_failure_config(load_base_config("gap_acceptance_failure"))


def test_rejects_short_side() -> None:
    sp13.test_rejects_short_side(validate_gap_acceptance_failure_config, "gap_acceptance_failure")
