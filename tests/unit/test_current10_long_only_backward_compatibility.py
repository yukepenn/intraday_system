"""Phase19 immediate fix: ensure current-10 long-only behavior is unchanged.

Compares signal hashes for ``side_mode=long_only`` against the equivalent
legacy ``side=long_only`` and ``no side_mode`` configurations across all
current-10 base configs.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from intraday.core.config import load_yaml
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


def _base(strategy: str) -> dict:
    return load_yaml(REPO / "configs" / "strategies" / "base" / f"{strategy}.yaml")


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
