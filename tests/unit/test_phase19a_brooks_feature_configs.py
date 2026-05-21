"""Phase19A Brooks Slice F1 feature config tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from intraday.core.config import load_yaml
from intraday.features.engine import build_feature_matrix
from intraday.features.specs import collect_all_column_names, resolve_feature_config

from tests.helpers.bars import make_bar_matrix

REPO = Path(__file__).resolve().parents[2]
CORE_CONFIG = REPO / "configs" / "features" / "pa_brooks_core_v1.yaml"
RANGE_CONFIG = REPO / "configs" / "features" / "pa_brooks_range_v1.yaml"
FORBIDDEN_LABEL_FRAGMENTS = (
    "should_buy",
    "should_short",
    "winner",
    "pnl",
    "target_price",
    "fill",
    "realized_r",
)


def _bars(n: int = 120):
    open_ = [100.0 + i * 0.05 for i in range(n)]
    close = [x + (0.2 if i % 3 else -0.1) for i, x in enumerate(open_)]
    high = [max(o, c) + 0.4 for o, c in zip(open_, close, strict=True)]
    low = [min(o, c) - 0.4 for o, c in zip(open_, close, strict=True)]
    return make_bar_matrix(open_, high, low, close, minute=list(range(n)))


def test_brooks_feature_configs_load_with_unique_columns() -> None:
    for path in (CORE_CONFIG, RANGE_CONFIG):
        resolved = resolve_feature_config(load_yaml(path))
        columns = collect_all_column_names(resolved)
        assert columns
        assert len(columns) == len(set(columns))


def test_brooks_core_required_slice_f1_columns_exist() -> None:
    matrix = build_feature_matrix(_bars(), load_yaml(CORE_CONFIG), use_cache=False)
    expected = {
        "strong_bull_close",
        "strong_bear_close",
        "bull_signal_bar",
        "bear_signal_bar",
        "bull_micro_channel_3",
        "bear_micro_channel_3",
        "pa_always_in_side",
        "pa_strong_bull_bo_score_20",
        "pa_strong_bear_bo_score_20",
        "pa_tight_bull_channel_score_20",
        "pa_tight_bear_channel_score_20",
        "pa_broad_bull_channel_score_20",
        "pa_broad_bear_channel_score_20",
        "pa_trading_range_score_20",
        "pa_late_trend_score_20",
        "pa_leg_direction",
        "pa_pullback_bar_count",
        "pa_pullback_depth_atr",
        "pa_two_leg_pullback_down",
        "pa_two_leg_pullback_up",
        "pa_second_entry_buy_proxy",
        "pa_second_entry_sell_proxy",
    }
    assert expected <= set(matrix.columns)


def test_brooks_range_required_slice_f1_columns_exist() -> None:
    matrix = build_feature_matrix(_bars(), load_yaml(RANGE_CONFIG), use_cache=False)
    expected = {
        f"{base}_{window}"
        for window in (30, 60, 90)
        for base in (
            "pa_tr_high",
            "pa_tr_low",
            "pa_tr_mid",
            "pa_tr_upper_third",
            "pa_tr_lower_third",
            "pa_tr_width_atr",
            "pa_close_in_lower_third",
            "pa_close_in_upper_third",
            "pa_range_breakout_up",
            "pa_range_breakout_down",
            "pa_close_back_inside_range",
        )
    }
    assert expected <= set(matrix.columns)


def test_brooks_feature_columns_do_not_encode_strategy_or_outcomes() -> None:
    for path in (CORE_CONFIG, RANGE_CONFIG):
        resolved = resolve_feature_config(load_yaml(path))
        for column in collect_all_column_names(resolved):
            lowered = column.lower()
            assert not any(fragment in lowered for fragment in FORBIDDEN_LABEL_FRAGMENTS)


def test_brooks_feature_outputs_sanitize_inf_and_have_warmup_nan() -> None:
    matrix = build_feature_matrix(_bars(), load_yaml(RANGE_CONFIG), use_cache=False)
    assert not np.isinf(matrix.values).any()
    assert np.isnan(matrix.column("pa_tr_high_30")[:30]).all()
    assert np.isfinite(matrix.column("pa_tr_high_30")[30:]).any()
