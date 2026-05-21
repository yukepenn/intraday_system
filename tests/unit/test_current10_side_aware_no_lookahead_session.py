"""Phase19 immediate fix: short-branch no-lookahead and session-boundary tests."""

from __future__ import annotations

import numpy as np
from intraday.strategies.contracts import SIGNAL_CONTRACT_VERSION
from intraday.strategies.pa.buy_sell_close_trend import (
    generate_pa_buy_sell_close_trend_signals,
)

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns


def _pa_short_cfg() -> dict:
    return {
        "strategy": "pa_buy_sell_close_trend",
        "version": "strategy_v1",
        "signal_contract_version": SIGNAL_CONTRACT_VERSION,
        "signal": {
            "side_mode": "short_only",
            "entry_start_minute": 60,
            "entry_end_minute": 300,
            "body_pct_min": 0.5,
            "close_position_min": 0.5,
            "trend_slope_min": 0.0,
            "close_vs_mean_min": 0.0,
            "require_vwap_side": False,
        },
        "risk": {
            "stop_mode": "signal_low",
            "target_mode": "fixed_r",
            "target_r": 1.35,
            "atr_buffer_mult": 0.35,
        },
    }


def _bear_feats(n: int, **overrides) -> dict:
    base = {
        "body_pct": np.full(n, 0.8),
        "close_position_in_range": np.full(n, 0.1),
        "trend_slope_like_20": np.full(n, -1.0),
        "close_vs_rolling_mean_20": np.full(n, -0.5),
        "vwap_side": np.full(n, -1.0),
        "atr_like_20": np.full(n, 1.0),
        "rolling_low_20": np.full(n, 95.0),
        "rolling_high_20": np.full(n, 110.0),
        "bar_range": np.full(n, 5.0),
    }
    base.update(overrides)
    return base


def _signals_unchanged_up_to(a, b, k: int) -> None:
    for name in ("entry", "side", "stop", "target_r", "score", "setup_code"):
        x = getattr(a, name)[: k + 1]
        y = getattr(b, name)[: k + 1]
        if name == "entry":
            assert np.array_equal(x.astype(bool), y.astype(bool))
        elif name in ("side", "setup_code"):
            assert np.array_equal(x, y)
        else:
            assert np.allclose(x, y, equal_nan=True)


def test_short_branch_no_lookahead_future_body_pct() -> None:
    n = 6
    k = 2
    bars = make_bar_matrix([100.0] * n, [105.0] * n, [100.0] * n, [100.0] * n, minute=[120] * n)
    feats0 = make_feature_matrix_with_columns(n, _bear_feats(n), feature_hash="fh_t0")
    s0 = generate_pa_buy_sell_close_trend_signals(bars, feats0, _pa_short_cfg())

    body = _bear_feats(n)["body_pct"].copy()
    body[k + 1 :] = 0.01  # perturb future bars only
    feats1 = make_feature_matrix_with_columns(
        n, _bear_feats(n, body_pct=body), feature_hash="fh_t0"
    )
    s1 = generate_pa_buy_sell_close_trend_signals(bars, feats1, _pa_short_cfg())
    _signals_unchanged_up_to(s0, s1, k)


def test_short_branch_session_boundary_does_not_leak_state() -> None:
    """Session change between bars must reset short-branch state."""
    n = 6
    # First three bars in session 0, last three in session 1, all valid entry times.
    bars = make_bar_matrix(
        [100.0] * n,
        [105.0] * n,
        [100.0] * n,
        [100.0] * n,
        session_id=[0, 0, 0, 1, 1, 1],
        minute=[120, 121, 122, 60, 61, 62],
    )
    feats = make_feature_matrix_with_columns(n, _bear_feats(n), feature_hash="fh_sess")
    s = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_short_cfg())
    # Should still emit short entries in BOTH sessions (state did not leak).
    # max_trades_per_day is not set in this config -> no thinning, so multiple
    # entries can occur within a session.
    sess0_entries = int(s.entry[bars.session_id == 0].sum())
    sess1_entries = int(s.entry[bars.session_id == 1].sum())
    assert sess0_entries > 0
    assert sess1_entries > 0
    # Sides must be -1 wherever entry fires.
    assert (s.side[s.entry] == -1).all()
