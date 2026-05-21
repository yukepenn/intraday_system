"""Phase19 polish: current-10 long-only behavior-equivalence policy.

Raw ``signal_hash`` identity is intentionally not asserted across
``signal.side`` -> ``signal.side_mode`` key migration because the hash includes
the resolved config identity. Compatibility here means validation succeeds and
SignalMatrix behavior is equivalent on representative fixtures.
"""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest
from intraday.core.config import load_yaml
from intraday.strategies.loader import validate_strategy_config
from intraday.strategies.registry import get_strategy, register_builtin_strategies

from tests.unit.test_current10_short_signal_generation import (
    CURRENT10_CASES,
    Current10Case,
    case_ids,
)

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


def _base(strategy: str) -> dict:
    return load_yaml(REPO / "configs" / "strategies" / "base" / f"{strategy}.yaml")


@pytest.fixture(scope="module", autouse=True)
def _register() -> None:
    register_builtin_strategies()


@pytest.mark.parametrize("strategy", CURRENT10)
def test_canonical_base_config_validates_unchanged(strategy: str) -> None:
    cfg = _base(strategy)
    validate_strategy_config(strategy, cfg)


@pytest.mark.parametrize("strategy", CURRENT10)
def test_side_mode_long_only_and_legacy_side_both_validate(strategy: str) -> None:
    cfg_new = copy.deepcopy(_base(strategy))
    cfg_new["signal"].pop("side", None)
    cfg_new["signal"]["side_mode"] = "long_only"
    validate_strategy_config(strategy, cfg_new)

    cfg_legacy = copy.deepcopy(_base(strategy))
    cfg_legacy["signal"].pop("side_mode", None)
    cfg_legacy["signal"]["side"] = "long_only"
    validate_strategy_config(strategy, cfg_legacy)

    cfg_missing = copy.deepcopy(_base(strategy))
    cfg_missing["signal"].pop("side", None)
    cfg_missing["signal"].pop("side_mode", None)
    validate_strategy_config(strategy, cfg_missing)


def _assert_signal_arrays_equal(a, b) -> None:
    assert np.array_equal(a.entry, b.entry)
    assert np.array_equal(a.side, b.side)
    assert np.allclose(a.stop, b.stop, equal_nan=True)
    assert np.allclose(a.target_r, b.target_r, equal_nan=True)
    assert np.allclose(a.score, b.score, equal_nan=True)
    assert np.array_equal(a.setup_code, b.setup_code)


@pytest.mark.parametrize("case", CURRENT10_CASES, ids=case_ids)
def test_missing_side_mode_and_legacy_side_match_long_only_behavior(
    case: Current10Case,
) -> None:
    bars, feats = case.fixture_factory()

    canonical = case.config_factory(side_mode="long_only")
    legacy = copy.deepcopy(canonical)
    legacy["signal"].pop("side_mode", None)
    legacy["signal"]["side"] = "long_only"
    missing = copy.deepcopy(canonical)
    missing["signal"].pop("side_mode", None)
    missing["signal"].pop("side", None)

    s_canonical = get_strategy(case.strategy).generate_reference(bars, feats, canonical)
    s_legacy = get_strategy(case.strategy).generate_reference(bars, feats, legacy)
    s_missing = get_strategy(case.strategy).generate_reference(bars, feats, missing)

    _assert_signal_arrays_equal(s_canonical, s_legacy)
    _assert_signal_arrays_equal(s_canonical, s_missing)
    # The raw hashes may differ across key spellings because config identity is
    # part of compute_signal_hash; behavior equivalence is the compatibility bar.
