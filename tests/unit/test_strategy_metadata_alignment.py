"""Phase19 immediate fix: metadata <-> StrategyDef <-> setup-code registry alignment."""

from __future__ import annotations

from pathlib import Path

import pytest
from intraday.core.config import load_yaml
from intraday.strategies.registry import get_strategy, list_strategies, register_builtin_strategies
from intraday.strategies.setup_codes import SETUP_CODES

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

PHASE19_CORE = (
    "pa_second_entry_pullback",
    "pa_trading_range_bls_hs",
    "pa_failed_breakout_trap",
    "pa_opening_reversal_sr",
    "pa_breakout_pullback_continuation",
    "pa_tight_channel_pullback",
    "pa_broad_channel_zone",
)


def _metadata_path(strategy: str) -> Path:
    if strategy in PHASE19_CORE:
        return REPO / "configs" / "strategies" / "metadata" / "phase19" / f"{strategy}.yaml"
    return REPO / "configs" / "strategies" / "metadata" / f"{strategy}.yaml"


@pytest.fixture(scope="module", autouse=True)
def _registry():
    register_builtin_strategies()


@pytest.mark.parametrize("strategy", CURRENT10 + PHASE19_CORE)
def test_strategydef_setup_codes_match_registry(strategy: str) -> None:
    defn = get_strategy(strategy)
    spec = SETUP_CODES[strategy]
    assert defn.setup_code_long == spec.long_code
    assert defn.setup_code_short == spec.short_code


@pytest.mark.parametrize("strategy", CURRENT10 + PHASE19_CORE)
def test_metadata_setup_codes_match_registry(strategy: str) -> None:
    meta = load_yaml(_metadata_path(strategy))
    spec = SETUP_CODES[strategy]
    codes = meta["setup_codes"]
    assert int(codes["long"]) == spec.long_code
    assert int(codes["short"]) == spec.short_code


@pytest.mark.parametrize("strategy", CURRENT10 + PHASE19_CORE)
def test_metadata_diagnostic_flags_separated(strategy: str) -> None:
    meta = load_yaml(_metadata_path(strategy))
    # All current implemented strategies are core (not diagnostic_only).
    assert meta.get("core_or_diagnostic") == "core"
    assert meta.get("diagnostic_only") is False
    # Phase19 immediate fix: grid_inspect_only is a separate, looser guardrail.
    assert meta.get("grid_inspect_only") in (True, False)


@pytest.mark.parametrize("strategy", CURRENT10 + PHASE19_CORE)
def test_strategydef_exposes_required_feature_columns(strategy: str) -> None:
    defn = get_strategy(strategy)
    assert (
        defn.required_feature_columns
    ), f"{strategy} must expose non-empty required_feature_columns via StrategyDef"


@pytest.mark.parametrize("strategy", CURRENT10 + PHASE19_CORE)
def test_strategydef_allowed_side_modes_includes_long_only(strategy: str) -> None:
    defn = get_strategy(strategy)
    assert "long_only" in defn.allowed_side_modes
    assert defn.default_side_mode == "long_only"


def test_no_unknown_strategies_in_registry() -> None:
    names = set(list_strategies())
    # All registered strategies must have setup-code entries; no orphans.
    missing = sorted(n for n in names if n not in SETUP_CODES)
    assert missing == [], f"registered strategies without setup-code registry entry: {missing}"
