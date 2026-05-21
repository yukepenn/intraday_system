"""Phase19 immediate fix: current-10 short-side signal generation tests.

Verifies that, on synthetic fixtures crafted to satisfy short-side conditions:
- ``side_mode=long_only`` emits no short entries.
- ``side_mode=short_only`` emits no long entries.
- short entries carry the approved short setup code with side=-1 and
  ``stop > close``; non-entry rows remain flat/NaN/zero.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest
from intraday.strategies.contracts import SIGNAL_CONTRACT_VERSION
from intraday.strategies.pa.buy_sell_close_trend import (
    SETUP_CODE_LONG as PA_LONG,
)
from intraday.strategies.pa.buy_sell_close_trend import (
    SETUP_CODE_SHORT as PA_SHORT,
)
from intraday.strategies.pa.buy_sell_close_trend import (
    generate_pa_buy_sell_close_trend_signals,
)

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns


def _pa_short_config(**overrides: Any) -> dict:
    sig = {
        "side_mode": "short_only",
        "entry_start_minute": 60,
        "entry_end_minute": 300,
        "body_pct_min": 0.5,
        "close_position_min": 0.5,
        "trend_slope_min": 0.0,
        "close_vs_mean_min": 0.0,
        "require_vwap_side": False,
    }
    sig.update(overrides)
    return {
        "strategy": "pa_buy_sell_close_trend",
        "version": "strategy_v1",
        "signal_contract_version": SIGNAL_CONTRACT_VERSION,
        "signal": sig,
        "risk": {
            "stop_mode": "signal_low",  # mapped to signal_high for shorts
            "target_mode": "fixed_r",
            "target_r": 1.35,
            "atr_buffer_mult": 0.35,
        },
    }


def _short_fixture(n: int = 4):
    bars = make_bar_matrix(
        [100.0] * n,
        [105.0] * n,  # bar high above close for short stop
        [100.0] * n,  # bar low at close (bearish bar)
        [100.0] * n,
        minute=[120] * n,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "body_pct": np.full(n, 0.8),
            "close_position_in_range": np.full(n, 0.1),  # 1 - cp = 0.9
            "trend_slope_like_20": np.full(n, -1.0),  # bearish
            "close_vs_rolling_mean_20": np.full(n, -0.5),  # below mean
            "vwap_side": np.full(n, -1.0),  # below VWAP
            "atr_like_20": np.full(n, 1.0),
            "rolling_low_20": np.full(n, 95.0),
            "rolling_high_20": np.full(n, 110.0),
            "bar_range": np.full(n, 5.0),
        },
        feature_hash="fh_short",
    )
    return bars, feats


def test_short_only_emits_short_with_approved_setup_code() -> None:
    bars, feats = _short_fixture()
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_short_config())
    assert sig.entry.any(), "expected short entries on bearish synthetic fixture"
    idx = int(np.flatnonzero(sig.entry)[0])
    assert sig.side[idx] == -1
    assert sig.setup_code[idx] == PA_SHORT
    assert sig.stop[idx] > bars.close[idx]
    assert sig.target_r[idx] == pytest.approx(1.35)
    assert np.isfinite(sig.score[idx])


def test_long_only_emits_no_short_on_bearish_fixture() -> None:
    bars, feats = _short_fixture()
    cfg = _pa_short_config(side_mode="long_only")
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, cfg)
    assert not sig.entry.any() or (sig.side[sig.entry] == 1).all()
    assert not (sig.side == -1).any()


def test_short_only_emits_no_long_on_bearish_fixture() -> None:
    bars, feats = _short_fixture()
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_short_config())
    assert not (sig.side == 1).any()


def test_both_mode_can_emit_long_on_bullish_fixture() -> None:
    # Use bullish fixture from baseline long-only tests.
    n = 4
    bars = make_bar_matrix(
        [100.0] * n,
        [100.0] * n,
        [95.0] * n,
        [100.0] * n,
        minute=[120] * n,
    )
    feats = make_feature_matrix_with_columns(
        n,
        {
            "body_pct": np.full(n, 0.8),
            "close_position_in_range": np.full(n, 0.9),
            "trend_slope_like_20": np.full(n, 1.0),
            "close_vs_rolling_mean_20": np.full(n, 0.5),
            "vwap_side": np.full(n, 1.0),
            "atr_like_20": np.full(n, 1.0),
            "rolling_low_20": np.full(n, 90.0),
            "rolling_high_20": np.full(n, 110.0),
            "bar_range": np.full(n, 5.0),
        },
        feature_hash="fh_bull",
    )
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_short_config(side_mode="both"))
    assert sig.entry.any()
    idx = int(np.flatnonzero(sig.entry)[0])
    assert sig.side[idx] == 1
    assert sig.setup_code[idx] == PA_LONG


def test_short_non_entry_convention() -> None:
    bars, feats = _short_fixture(n=4)
    # Entry window 60..300 but minute 30 is outside.
    bars = make_bar_matrix(
        [100.0] * 4, [105.0] * 4, [100.0] * 4, [100.0] * 4, minute=[30, 30, 30, 30]
    )
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_short_config())
    assert sig.side[0] == 0
    assert np.isnan(sig.stop[0])
    assert np.isnan(sig.target_r[0])
    assert np.isnan(sig.score[0])
    assert sig.setup_code[0] == 0
