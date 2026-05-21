"""Phase19B Brooks strategies fail closed on missing features."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from intraday.core.config import load_yaml
from intraday.core.errors import ConfigError
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

MISSING_COLUMN = {
    "pa_second_entry_pullback": "pa_always_in_side",
    "pa_trading_range_bls_hs": "pa_tr_width_atr_60",
    "pa_failed_breakout_trap": "pa_range_breakout_down_60",
    "pa_opening_reversal_sr": "pa_tr_width_atr_30",
    "pa_breakout_pullback_continuation": "pa_strong_bull_bo_score_20",
    "pa_tight_channel_pullback": "pa_tight_bull_channel_score_20",
    "pa_broad_channel_zone": "pa_broad_bull_channel_score_20",
}


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_phase19b_missing_required_feature_raises_config_error(strategy: str) -> None:
    register_builtin_strategies()
    cols = copy.deepcopy(_base_cols())
    cols.pop(MISSING_COLUMN[strategy])
    cfg = load_yaml(REPO / "configs" / "strategies" / "base" / "phase19" / f"{strategy}.yaml")
    cfg["signal"]["entry_start_minute"] = 0
    cfg["signal"]["entry_end_minute"] = 5
    bars = make_bar_matrix(
        [100, 101, 102, 103, 104, 105],
        [101, 102, 103, 104, 105, 106],
        [99, 100, 101, 102, 103, 104],
        [100.5, 101.5, 102.5, 103.5, 104.5, 105.5],
    )
    with pytest.raises(ConfigError, match="missing required feature columns"):
        get_strategy(strategy).generate_reference(
            bars,
            make_feature_matrix_with_columns(6, cols),
            cfg,
        )
