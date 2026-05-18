"""ORB continuation strategy tests."""

from __future__ import annotations

import numpy as np
import pytest
from intraday.core.errors import ConfigError
from intraday.strategies.orb.continuation import (
    SETUP_CODE,
    generate_orb_continuation_signals,
    validate_orb_continuation_config,
)

from tests.helpers import strategy_phase13 as sp13
from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns
from tests.helpers.strategy_phase13 import load_base_config


def _feat(n: int, **kw) -> dict:
    base = {
        "orb_high_15": np.full(n, 99.0),
        "orb_low_15": np.full(n, 97.0),
        "orb_mid_15": np.full(n, 98.0),
        "orb_range_15": np.full(n, 2.0),
        "orb_width_pct_15": np.full(n, 0.02),
        "vwap": np.full(n, 98.0),
        "vwap_slope_5": np.full(n, 0.05),
        "atr_like_20": np.full(n, 1.0),
    }
    base.update(kw)
    return base


def test_base_yaml_validates() -> None:
    validate_orb_continuation_config(load_base_config("orb_continuation"))


def test_rejects_short_side() -> None:
    sp13.test_rejects_short_side(validate_orb_continuation_config, "orb_continuation")


def test_synthetic_entry() -> None:
    cfg = load_base_config("orb_continuation")
    bars = make_bar_matrix([100.0], [102.0], [98.0], [101.0], minute=[30])
    feats = make_feature_matrix_with_columns(1, _feat(1, orb_high_15=np.array([100.5])))
    sig = generate_orb_continuation_signals(bars, feats, cfg)
    assert sig.entry.any()
    assert sig.setup_code[0] == SETUP_CODE
    sp13.assert_signal_matrix_valid(sig, 1)
    sp13.assert_entry_stop_target(sig, bars)


def test_missing_column_raises() -> None:
    cfg = load_base_config("orb_continuation")
    bars = make_bar_matrix([100.0], [101.0], [99.0], [100.0], minute=[30])
    with pytest.raises(ConfigError):
        generate_orb_continuation_signals(
            bars, make_feature_matrix_with_columns(1, {"vwap": np.array([1.0])}), cfg
        )


def test_no_lookahead() -> None:
    cfg = load_base_config("orb_continuation")
    n = 5
    bars = make_bar_matrix(
        [100.0] * n, [102.0] * n, [98.0] * n, [101.0] * n, minute=[20, 21, 22, 23, 24]
    )
    feats = make_feature_matrix_with_columns(n, _feat(n, orb_high_15=np.full(n, 100.0)))
    s0 = generate_orb_continuation_signals(bars, feats, cfg)
    f2 = make_feature_matrix_with_columns(
        n,
        _feat(n, orb_high_15=np.concatenate([feats.column("orb_high_15")[:3], [200.0, 200.0]])),
        feature_hash=feats.feature_hash,
    )
    s1 = generate_orb_continuation_signals(bars, f2, cfg)
    sp13.signals_unchanged_up_to(s0, s1, 2)


def test_non_entry_convention() -> None:
    cfg = load_base_config("orb_continuation")
    bars = make_bar_matrix([100.0], [101.0], [99.0], [98.0], minute=[30])
    feats = make_feature_matrix_with_columns(1, _feat(1))
    sig = generate_orb_continuation_signals(bars, feats, cfg)
    sp13.assert_non_entry_convention(sig)
