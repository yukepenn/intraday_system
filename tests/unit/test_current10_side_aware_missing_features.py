"""Phase19 polish: all current-10 short branches fail closed on missing features."""

from __future__ import annotations

import pytest
from intraday.core.errors import ConfigError
from intraday.strategies.registry import get_strategy, register_builtin_strategies

from tests.helpers.strategy import make_feature_matrix_with_columns
from tests.unit.test_current10_short_signal_generation import (
    CURRENT10_CASES,
    Current10Case,
    case_ids,
)


@pytest.fixture(scope="module", autouse=True)
def _register() -> None:
    register_builtin_strategies()


@pytest.mark.parametrize("case", CURRENT10_CASES, ids=case_ids)
def test_current10_short_branch_missing_required_feature_raises_config_error(
    case: Current10Case,
) -> None:
    bars, feats = case.fixture_factory()
    columns = {
        name: feats.values[:, idx].copy()
        for name, idx in feats.columns.items()
        if name != case.missing_column
    }
    missing = make_feature_matrix_with_columns(
        bars.n_bars,
        columns,
        feature_hash=f"{feats.feature_hash}_missing_{case.missing_column}",
    )
    cfg = case.config_factory(side_mode="short_only")
    with pytest.raises(ConfigError):
        get_strategy(case.strategy).generate_reference(bars, missing, cfg)


def test_pa_long_only_does_not_require_short_specific_rolling_high() -> None:
    """Default long_only does not require the PA short-only rolling_high_20 column."""
    pa_case = CURRENT10_CASES[0]
    bars, feats = pa_case.fixture_factory()
    columns = {
        name: feats.values[:, idx].copy()
        for name, idx in feats.columns.items()
        if name != "rolling_high_20"
    }
    missing = make_feature_matrix_with_columns(bars.n_bars, columns, feature_hash="fh_pa_long")
    cfg = pa_case.config_factory(side_mode="long_only")
    get_strategy(pa_case.strategy).generate_reference(bars, missing, cfg)
