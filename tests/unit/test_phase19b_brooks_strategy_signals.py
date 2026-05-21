"""Synthetic signal tests for Phase19B Brooks PA strategies."""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest
from intraday.core.config import load_yaml
from intraday.core.types import Side
from intraday.strategies.registry import get_strategy, register_builtin_strategies

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns

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


def _bars():
    return make_bar_matrix(
        [100, 101, 102, 103, 104, 105],
        [101, 102, 103, 104, 105, 106],
        [99, 100, 101, 102, 103, 104],
        [100.5, 101.5, 102.5, 103.5, 104.5, 105.5],
        minute=[0, 1, 2, 3, 4, 5],
    )


def _cfg(strategy: str, side_mode: str = "both") -> dict:
    cfg = copy.deepcopy(
        load_yaml(REPO / "configs" / "strategies" / "base" / "phase19" / f"{strategy}.yaml")
    )
    cfg["signal"]["side_mode"] = side_mode
    cfg["signal"]["entry_start_minute"] = 0
    cfg["signal"]["entry_end_minute"] = 5
    if strategy == "pa_failed_breakout_trap":
        cfg["signal"]["fail_back_inside_bars"] = 1
    return cfg


def _zeros() -> np.ndarray:
    return np.zeros(6, dtype=np.float64)


def _base_cols() -> dict[str, np.ndarray | float]:
    cols: dict[str, np.ndarray | float] = {
        "pa_always_in_side": [0, 1, 1, -1, -1, 0],
        "pa_pullback_bar_count": 2,
        "pa_pullback_depth_atr": 0.4,
        "pa_two_leg_pullback_down": [0, 1, 0, 0, 0, 0],
        "pa_two_leg_pullback_up": [0, 0, 0, 1, 0, 0],
        "pa_second_entry_buy_proxy": [0, 1, 0, 0, 0, 0],
        "pa_second_entry_sell_proxy": [0, 0, 0, 1, 0, 0],
        "bull_signal_bar": [0, 1, 0, 0, 1, 0],
        "bear_signal_bar": [0, 0, 0, 1, 0, 0],
        "strong_bull_close": [0, 1, 0, 0, 1, 0],
        "strong_bear_close": [0, 0, 0, 1, 0, 0],
        "pa_trading_range_score_20": 0.2,
        "pa_strong_bull_bo_score_20": [0.8, 0.1, 0.1, 0.1, 0.1, 0.1],
        "pa_strong_bear_bo_score_20": [0.1, 0.1, 0.8, 0.1, 0.1, 0.1],
        "pa_tight_bull_channel_score_20": [0, 0.8, 0, 0, 0, 0],
        "pa_tight_bear_channel_score_20": [0, 0, 0, 0.8, 0, 0],
        "pa_broad_bull_channel_score_20": [0, 0.6, 0, 0, 0, 0],
        "pa_broad_bear_channel_score_20": [0, 0, 0, 0.6, 0, 0],
        "pa_late_trend_score_20": 0.1,
        "bull_micro_channel_3": [0, 1, 0, 0, 0, 0],
        "bear_micro_channel_3": [0, 0, 0, 1, 0, 0],
    }
    for w in (30, 60, 90):
        cols[f"pa_tr_width_atr_{w}"] = 1.2
        cols[f"pa_close_in_lower_third_{w}"] = [0, 1, 0, 0, 0, 0]
        cols[f"pa_close_in_upper_third_{w}"] = [0, 0, 0, 1, 0, 0]
        cols[f"pa_range_breakout_down_{w}"] = [1, 0, 0, 0, 0, 0]
        cols[f"pa_range_breakout_up_{w}"] = [0, 0, 1, 0, 0, 0]
        cols[f"pa_close_back_inside_range_{w}"] = [0, 1, 0, 1, 0, 0]
        cols[f"pa_tr_lower_third_{w}"] = 100.0
        cols[f"pa_tr_upper_third_{w}"] = 105.0
        cols[f"pa_tr_low_{w}"] = 99.0
        cols[f"pa_tr_high_{w}"] = 106.0
    return cols


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_phase19b_strategy_generates_long_and_short(strategy: str) -> None:
    register_builtin_strategies()
    bars = _bars()
    features = make_feature_matrix_with_columns(6, _base_cols())
    signals = get_strategy(strategy).generate_reference(bars, features, _cfg(strategy))

    assert int(Side.LONG) in set(signals.side[signals.entry])
    assert int(Side.SHORT) in set(signals.side[signals.entry])
    assert np.all(signals.stop[signals.side == int(Side.LONG)] < bars.close[signals.side == 1])
    assert np.all(signals.stop[signals.side == int(Side.SHORT)] > bars.close[signals.side == -1])
    assert np.all(np.isfinite(signals.score[signals.entry]))
    assert np.all(signals.target_r[signals.entry] > 0)
    assert np.all(signals.setup_code[signals.entry] != 0)


@pytest.mark.parametrize(
    ("side_mode", "forbidden_side"),
    (("long_only", int(Side.SHORT)), ("short_only", int(Side.LONG))),
)
@pytest.mark.parametrize("strategy", STRATEGIES)
def test_phase19b_strategy_side_mode_filters(
    strategy: str, side_mode: str, forbidden_side: int
) -> None:
    register_builtin_strategies()
    signals = get_strategy(strategy).generate_reference(
        _bars(),
        make_feature_matrix_with_columns(6, _base_cols()),
        _cfg(strategy, side_mode),
    )
    assert forbidden_side not in set(signals.side[signals.entry])


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_phase19b_strategy_signal_hash_deterministic(strategy: str) -> None:
    register_builtin_strategies()
    bars = _bars()
    features = make_feature_matrix_with_columns(6, _base_cols())
    s1 = get_strategy(strategy).generate_reference(bars, features, _cfg(strategy))
    s2 = get_strategy(strategy).generate_reference(bars, features, _cfg(strategy))
    assert s1.signal_hash == s2.signal_hash
