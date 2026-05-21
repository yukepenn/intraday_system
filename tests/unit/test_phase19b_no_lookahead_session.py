"""Phase19B synthetic no-lookahead/session tests."""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest
from intraday.core.config import load_yaml
from intraday.strategies.registry import get_strategy, register_builtin_strategies

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns
from tests.unit.test_phase19b_brooks_strategy_signals import _base_cols

REPO = Path(__file__).resolve().parents[2]

STRATEGIES = (
    "pa_second_entry_pullback",
    "pa_trading_range_bls_hs",
    "pa_failed_breakout_trap",
    "pa_opening_reversal_sr",
    "pa_breakout_pullback_continuation",
    "pa_tight_channel_pullback",
    "pa_broad_channel_zone",
)


def _cfg(strategy: str) -> dict:
    cfg = load_yaml(REPO / "configs" / "strategies" / "base" / "phase19" / f"{strategy}.yaml")
    cfg["signal"]["side_mode"] = "both"
    cfg["signal"]["entry_start_minute"] = 0
    cfg["signal"]["entry_end_minute"] = 5
    return cfg


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_phase19b_future_feature_perturbation_does_not_change_prior_signal(strategy: str) -> None:
    register_builtin_strategies()
    bars = make_bar_matrix(
        [100, 101, 102, 103, 104, 105],
        [101, 102, 103, 104, 105, 106],
        [99, 100, 101, 102, 103, 104],
        [100.5, 101.5, 102.5, 103.5, 104.5, 105.5],
    )
    cols = _base_cols()
    base = get_strategy(strategy).generate_reference(
        bars, make_feature_matrix_with_columns(6, cols), _cfg(strategy)
    )
    perturbed = copy.deepcopy(cols)
    for key, value in list(perturbed.items()):
        if not np.isscalar(value):
            arr = np.asarray(value, dtype=np.float64).copy()
            arr[-1] = 999.0
            perturbed[key] = arr
    changed = get_strategy(strategy).generate_reference(
        bars, make_feature_matrix_with_columns(6, perturbed), _cfg(strategy)
    )
    assert np.array_equal(base.entry[:-1], changed.entry[:-1])
    assert np.array_equal(base.side[:-1], changed.side[:-1])


def test_phase19b_prior_condition_helper_resets_by_session() -> None:
    from intraday.strategies.pa.brooks_common import prior_condition_within

    condition = np.array([True, False, False, False], dtype=bool)
    session_id = np.array([0, 0, 1, 1], dtype=np.int32)
    assert prior_condition_within(condition, session_id, 3).tolist() == [
        False,
        True,
        False,
        False,
    ]
