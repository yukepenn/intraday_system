"""Phase18C missing-feature fail-closed checks for v2 optional branches."""

from __future__ import annotations

import pytest
from intraday.core.errors import ConfigError

from tests.unit.test_phase18c_strategy_v2_branches import (
    _bars,
    _cfg,
    _gap_cols,
    _generate,
    _indicator_cols,
    _level_cols,
    _orb_cols,
    _pa_cols,
    _vwap_cols,
)


@pytest.mark.parametrize(
    ("strategy", "cfg_update", "missing_column", "cols"),
    (
        (
            "pa_buy_sell_close_trend",
            {"signal": {"min_rel_volume_20": 1.5}},
            "rel_volume_20",
            _pa_cols,
        ),
        ("pa_buy_sell_close_trend", {"risk": {"stop_mode": "vwap_atr_buffer"}}, "vwap", _pa_cols),
        ("orb_continuation", {"signal": {"orb_open_minutes": 3}}, "orb_high_3", _orb_cols),
        (
            "gap_acceptance_failure",
            {"signal": {"require_close_above_vwap": True}},
            "vwap",
            _gap_cols,
        ),
        (
            "vwap_trend_pullback",
            {"signal": {"min_rel_volume_20": 1.5}},
            "rel_volume_20",
            _vwap_cols,
        ),
        (
            "prior_day_level_trap",
            {"signal": {"require_close_above_vwap": True}},
            "vwap",
            _level_cols,
        ),
        (
            "cci_extreme_snapback",
            {"signal": {"require_vwap_slope_positive": True}},
            "vwap_slope_5",
            _indicator_cols,
        ),
        (
            "stochastic_oversold_cross",
            {"signal": {"require_vwap_slope_positive": True}},
            "vwap_slope_5",
            _indicator_cols,
        ),
    ),
)
def test_phase18c_missing_optional_feature_columns_fail_closed(
    strategy: str,
    cfg_update: dict,
    missing_column: str,
    cols,
) -> None:
    bars = _bars()
    cfg = _cfg(strategy)
    for section, updates in cfg_update.items():
        cfg[section].update(updates)
    feature_cols = cols(bars.n_bars)
    feature_cols.pop(missing_column, None)

    with pytest.raises(ConfigError):
        _generate(strategy, cfg, bars, feature_cols)
