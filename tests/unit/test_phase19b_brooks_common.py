"""Phase19B Brooks common helper tests."""

from __future__ import annotations

import numpy as np
import pytest
from intraday.core.errors import ConfigError
from intraday.core.types import Side
from intraday.strategies.pa.brooks_common import (
    brooks_allowed_sides,
    build_brooks_signal_matrix,
    deterministic_score,
)

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns


def _cfg(side_mode: str = "both") -> dict:
    return {
        "strategy": "unit_brooks",
        "version": "strategy_v1",
        "signal_contract_version": "signal_v1",
        "signal": {"side_mode": side_mode},
        "risk": {"target_r": 1.2},
    }


def test_brooks_allowed_sides_modes() -> None:
    assert brooks_allowed_sides({"side_mode": "long_only"}) == (int(Side.LONG),)
    assert brooks_allowed_sides({"side_mode": "short_only"}) == (int(Side.SHORT),)
    assert brooks_allowed_sides({"side_mode": "both"}) == (int(Side.LONG), int(Side.SHORT))
    with pytest.raises(ConfigError):
        brooks_allowed_sides({"side_mode": "bad"})


def test_build_brooks_signal_matrix_conventions() -> None:
    bars = make_bar_matrix(
        [100, 101, 102],
        [101, 102, 103],
        [99, 100, 101],
        [100.5, 101.5, 102.5],
    )
    features = make_feature_matrix_with_columns(3, {"x": [1, 2, 3]})
    signals = build_brooks_signal_matrix(
        bars=bars,
        features=features,
        config=_cfg(),
        strategy_name="unit_brooks",
        long_entry=np.array([False, True, False]),
        short_entry=np.array([False, False, True]),
        long_stop=bars.low,
        short_stop=bars.high,
        long_score=np.array([np.nan, 0.7, np.nan]),
        short_score=np.array([np.nan, np.nan, 0.8]),
        setup_code_long=7101,
        setup_code_short=7201,
    )
    assert signals.side.tolist() == [0, int(Side.LONG), int(Side.SHORT)]
    assert np.isnan(signals.stop[0])
    assert signals.stop[1] < bars.close[1]
    assert signals.stop[2] > bars.close[2]
    assert np.all(signals.target_r[signals.entry] > 0)
    assert np.all(np.isfinite(signals.score[signals.entry]))
    assert np.all(signals.setup_code[signals.entry] != 0)


def test_build_brooks_signal_matrix_honors_side_mode() -> None:
    bars = make_bar_matrix([100, 101], [101, 102], [99, 100], [100.5, 101.5])
    features = make_feature_matrix_with_columns(2, {"x": [1, 2]})
    signals = build_brooks_signal_matrix(
        bars=bars,
        features=features,
        config=_cfg("short_only"),
        strategy_name="unit_brooks",
        long_entry=np.array([True, False]),
        short_entry=np.array([False, True]),
        long_stop=bars.low,
        short_stop=bars.high,
        long_score=np.array([0.7, np.nan]),
        short_score=np.array([np.nan, 0.8]),
        setup_code_long=7101,
        setup_code_short=7201,
    )
    assert signals.side.tolist() == [0, int(Side.SHORT)]


def test_deterministic_score_requires_finite_terms() -> None:
    score = deterministic_score(np.array([1.0, np.nan]), np.array([0.5, 1.0]))
    assert np.isfinite(score[0])
    assert np.isnan(score[1])
