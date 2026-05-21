"""Phase19 immediate fix: current-10 missing-feature ConfigError tests for short branches."""

from __future__ import annotations

import numpy as np
import pytest
from intraday.core.errors import ConfigError
from intraday.strategies.contracts import SIGNAL_CONTRACT_VERSION
from intraday.strategies.pa.buy_sell_close_trend import (
    generate_pa_buy_sell_close_trend_signals,
)

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns


def _pa_cfg(side_mode: str = "short_only") -> dict:
    return {
        "strategy": "pa_buy_sell_close_trend",
        "version": "strategy_v1",
        "signal_contract_version": SIGNAL_CONTRACT_VERSION,
        "signal": {
            "side_mode": side_mode,
            "entry_start_minute": 60,
            "entry_end_minute": 300,
            "body_pct_min": 0.5,
            "close_position_min": 0.5,
            "trend_slope_min": 0.0,
            "close_vs_mean_min": 0.0,
            "require_vwap_side": False,
            "require_above_rolling_high_20": True,
        },
        "risk": {
            "stop_mode": "signal_low",
            "target_mode": "fixed_r",
            "target_r": 1.35,
            "atr_buffer_mult": 0.35,
        },
    }


def test_pa_short_branch_missing_rolling_high_raises_config_error() -> None:
    n = 4
    bars = make_bar_matrix([100.0] * n, [105.0] * n, [95.0] * n, [100.0] * n, minute=[120] * n)
    # Intentionally omit rolling_high_20 even though side_mode requires short
    # branch features.
    feats = make_feature_matrix_with_columns(
        n,
        {
            "body_pct": np.full(n, 0.8),
            "close_position_in_range": np.full(n, 0.5),
            "trend_slope_like_20": np.full(n, 0.5),
            "close_vs_rolling_mean_20": np.full(n, 0.5),
            "vwap_side": np.full(n, 1.0),
            "atr_like_20": np.full(n, 1.0),
            "rolling_low_20": np.full(n, 95.0),
            "bar_range": np.full(n, 2.0),
        },
        feature_hash="fh_missing",
    )
    with pytest.raises(ConfigError):
        generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_cfg("short_only"))


def test_pa_long_only_does_not_require_rolling_high() -> None:
    """Default long_only does not require rolling_high_20 (no short branch)."""
    n = 4
    bars = make_bar_matrix([100.0] * n, [100.0] * n, [95.0] * n, [100.0] * n, minute=[120] * n)
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
            "bar_range": np.full(n, 5.0),
        },
        feature_hash="fh_long_only",
    )
    cfg = _pa_cfg("long_only")
    cfg["signal"].pop("require_above_rolling_high_20", None)
    generate_pa_buy_sell_close_trend_signals(bars, feats, cfg)
