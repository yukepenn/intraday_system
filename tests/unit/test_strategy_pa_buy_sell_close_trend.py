"""PA buy_sell_close_trend signal logic and no-lookahead tests."""

from __future__ import annotations

import copy

import numpy as np
import pytest
from intraday.strategies.contracts import SIGNAL_CONTRACT_VERSION
from intraday.strategies.pa.buy_sell_close_trend import (
    SETUP_CODE_LONG,
    generate_pa_buy_sell_close_trend_signals,
)

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns


def _pa_config(**signal_overrides: object) -> dict:
    sig = {
        "side": "long_only",
        "entry_start_minute": 60,
        "entry_end_minute": 300,
        "body_pct_min": 0.5,
        "close_position_min": 0.5,
        "trend_slope_min": 0.0,
        "close_vs_mean_min": 0.0,
        "require_vwap_side": False,
    }
    sig.update(signal_overrides)
    return {
        "strategy": "pa_buy_sell_close_trend",
        "version": "strategy_v1",
        "signal_contract_version": SIGNAL_CONTRACT_VERSION,
        "signal": sig,
        "risk": {
            "stop_mode": "signal_low",
            "target_mode": "fixed_r",
            "target_r": 1.35,
            "atr_buffer_mult": 0.35,
        },
    }


def _feature_dict(n: int, **overrides: np.ndarray | float) -> dict[str, np.ndarray | float]:
    base: dict[str, np.ndarray | float] = {
        "body_pct": np.full(n, 0.8),
        "close_position_in_range": np.full(n, 0.9),
        "trend_slope_like_20": np.full(n, 1.0),
        "close_vs_rolling_mean_20": np.full(n, 0.5),
        "vwap_side": np.full(n, 1.0),
        "atr_like_20": np.full(n, 1.0),
        "rolling_low_20": np.full(n, 90.0),
        "bar_range": np.full(n, 2.0),
    }
    for key, val in overrides.items():
        if isinstance(val, np.ndarray) and val.shape == (1,) and n > 1:
            base[key] = np.full(n, float(val[0]))
        else:
            base[key] = val
    return base


def _bars_and_features(
    n: int | None = None,
    *,
    minute: list[int] | None = None,
    close: float = 100.0,
    low: float = 95.0,
    feat_overrides: dict | None = None,
):
    if minute is None:
        n = n or 5
        minute = [120] * n
    else:
        n = len(minute)
    close_l = [close] * n
    low_l = [low] * n
    bars = make_bar_matrix(close_l, close_l, low_l, close_l, minute=minute)
    feats = make_feature_matrix_with_columns(
        n, _feature_dict(n, **(feat_overrides or {})), feature_hash="fh_test"
    )
    return bars, feats


def _signals_unchanged_up_to(
    a,
    b,
    k: int,
) -> None:
    """Compare signal arrays for indices <= k (NaN-safe)."""
    for name in ("entry", "side", "stop", "target_r", "score", "setup_code"):
        x = getattr(a, name)[: k + 1]
        y = getattr(b, name)[: k + 1]
        if name == "entry":
            assert np.array_equal(x.astype(bool), y.astype(bool))
        elif name in ("side", "setup_code"):
            assert np.array_equal(x, y)
        else:
            assert np.allclose(x, y, equal_nan=True)


def test_entry_when_all_thresholds_pass() -> None:
    bars, feats = _bars_and_features()
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config())
    assert sig.entry.any()
    idx = int(np.flatnonzero(sig.entry)[0])
    assert sig.side[idx] == 1
    assert sig.setup_code[idx] == SETUP_CODE_LONG
    assert sig.target_r[idx] == pytest.approx(1.35)
    assert np.isfinite(sig.score[idx])


def test_no_entry_before_entry_start() -> None:
    bars, feats = _bars_and_features(minute=[30])
    sig = generate_pa_buy_sell_close_trend_signals(
        bars, feats, _pa_config(entry_start_minute=60, entry_end_minute=300)
    )
    assert not sig.entry.any()


def test_no_entry_after_entry_end() -> None:
    bars, feats = _bars_and_features(minute=[350])
    sig = generate_pa_buy_sell_close_trend_signals(
        bars, feats, _pa_config(entry_start_minute=60, entry_end_minute=300)
    )
    assert not sig.entry.any()


def test_body_threshold_blocks() -> None:
    bars, feats = _bars_and_features(feat_overrides={"body_pct": np.array([0.2])})
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config(body_pct_min=0.5))
    assert not sig.entry.any()


def test_close_position_threshold_blocks() -> None:
    bars, feats = _bars_and_features(feat_overrides={"close_position_in_range": np.array([0.2])})
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config(close_position_min=0.5))
    assert not sig.entry.any()


def test_trend_slope_threshold_blocks() -> None:
    bars, feats = _bars_and_features(feat_overrides={"trend_slope_like_20": np.array([-1.0])})
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config(trend_slope_min=0.0))
    assert not sig.entry.any()


def test_close_vs_mean_threshold_blocks() -> None:
    bars, feats = _bars_and_features(feat_overrides={"close_vs_rolling_mean_20": np.array([-2.0])})
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config(close_vs_mean_min=0.0))
    assert not sig.entry.any()


def test_require_vwap_side_blocks() -> None:
    bars, feats = _bars_and_features(feat_overrides={"vwap_side": np.array([0.0])})
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config(require_vwap_side=True))
    assert not sig.entry.any()


def test_stop_mode_signal_low() -> None:
    bars, feats = _bars_and_features(low=92.0)
    cfg = _pa_config()
    cfg["risk"]["stop_mode"] = "signal_low"
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, cfg)
    idx = int(np.flatnonzero(sig.entry)[0])
    assert sig.stop[idx] == pytest.approx(92.0)


def test_stop_mode_rolling_low() -> None:
    bars, feats = _bars_and_features(feat_overrides={"rolling_low_20": np.array([88.0])})
    cfg = _pa_config()
    cfg["risk"]["stop_mode"] = "rolling_low"
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, cfg)
    idx = int(np.flatnonzero(sig.entry)[0])
    assert sig.stop[idx] == pytest.approx(88.0)


def test_stop_mode_atr_buffer() -> None:
    bars, feats = _bars_and_features(feat_overrides={"atr_like_20": np.array([2.0])})
    cfg = _pa_config()
    cfg["risk"]["stop_mode"] = "atr_buffer"
    cfg["risk"]["atr_buffer_mult"] = 0.5
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, cfg)
    idx = int(np.flatnonzero(sig.entry)[0])
    assert sig.stop[idx] == pytest.approx(100.0 - 0.5 * 2.0)


def test_invalid_stop_suppresses_entry() -> None:
    bars, feats = _bars_and_features(low=101.0)
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config())
    assert not sig.entry.any()


def test_non_entry_convention() -> None:
    bars, feats = _bars_and_features(minute=[30])
    sig = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config())
    assert sig.side[0] == 0
    assert np.isnan(sig.stop[0])
    assert np.isnan(sig.target_r[0])
    assert np.isnan(sig.score[0])
    assert sig.setup_code[0] == 0


def test_signal_hash_stable_and_changes() -> None:
    bars, feats = _bars_and_features()
    cfg = _pa_config()
    s1 = generate_pa_buy_sell_close_trend_signals(bars, feats, cfg)
    s2 = generate_pa_buy_sell_close_trend_signals(bars, feats, cfg)
    assert s1.signal_hash == s2.signal_hash
    cfg2 = copy.deepcopy(cfg)
    cfg2["risk"]["target_r"] = 2.0
    s3 = generate_pa_buy_sell_close_trend_signals(bars, feats, cfg2)
    assert s1.signal_hash != s3.signal_hash


def test_no_lookahead_future_body_pct() -> None:
    n = 6
    k = 2
    bars, feats = _bars_and_features(n=n)
    s0 = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config())
    cols = feats.values.copy()
    cols[k + 1 :, feats.columns["body_pct"]] = 0.01
    feats2 = make_feature_matrix_with_columns(
        n,
        {name: cols[:, j] for name, j in feats.columns.items()},
        feature_hash=feats.feature_hash,
    )
    s1 = generate_pa_buy_sell_close_trend_signals(bars, feats2, _pa_config())
    _signals_unchanged_up_to(s0, s1, k)


def test_no_lookahead_future_trend_slope() -> None:
    n = 6
    k = 2
    bars, feats = _bars_and_features(n=n)
    s0 = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config())
    arr = feats.column("trend_slope_like_20").copy()
    arr[k + 1 :] = -99.0
    feats2 = make_feature_matrix_with_columns(
        n, _feature_dict(n, trend_slope_like_20=arr), feature_hash=feats.feature_hash
    )
    s1 = generate_pa_buy_sell_close_trend_signals(bars, feats2, _pa_config())
    _signals_unchanged_up_to(s0, s1, k)


def test_no_lookahead_future_rolling_low() -> None:
    n = 6
    k = 2
    bars, feats = _bars_and_features(n=n)
    cfg = _pa_config()
    cfg["risk"]["stop_mode"] = "rolling_low"
    s0 = generate_pa_buy_sell_close_trend_signals(bars, feats, cfg)
    arr = feats.column("rolling_low_20").copy()
    arr[k + 1 :] = 200.0
    feats2 = make_feature_matrix_with_columns(
        n, _feature_dict(n, rolling_low_20=arr), feature_hash=feats.feature_hash
    )
    s1 = generate_pa_buy_sell_close_trend_signals(bars, feats2, cfg)
    _signals_unchanged_up_to(s0, s1, k)


def test_no_lookahead_future_vwap_side() -> None:
    n = 6
    k = 2
    bars, feats = _bars_and_features(n=n)
    s0 = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config())
    arr = feats.column("vwap_side").copy()
    arr[k + 1 :] = -1.0
    feats2 = make_feature_matrix_with_columns(
        n, _feature_dict(n, vwap_side=arr), feature_hash=feats.feature_hash
    )
    s1 = generate_pa_buy_sell_close_trend_signals(bars, feats2, _pa_config())
    _signals_unchanged_up_to(s0, s1, k)


def test_no_lookahead_future_bar_close() -> None:
    n = 6
    k = 2
    bars, feats = _bars_and_features(n=n)
    cfg = _pa_config()
    cfg["risk"]["stop_mode"] = "atr_buffer"
    s0 = generate_pa_buy_sell_close_trend_signals(bars, feats, cfg)
    close = bars.close.copy()
    close[k + 1 :] = 200.0
    low = bars.low.copy()
    low[k + 1 :] = 50.0
    bars2 = make_bar_matrix(
        close.tolist(),
        bars.high.tolist(),
        low.tolist(),
        close.tolist(),
        minute=bars.minute.tolist(),
    )
    s1 = generate_pa_buy_sell_close_trend_signals(bars2, feats, cfg)
    _signals_unchanged_up_to(s0, s1, k)


def test_current_bar_feature_change_may_change_signal_at_t() -> None:
    """Signals at bar close may use current-bar features (execution enters next open)."""
    n = 4
    k = 2
    minute = [120, 120, 120, 120]
    bars, feats = _bars_and_features(n=n, minute=minute)
    s0 = generate_pa_buy_sell_close_trend_signals(bars, feats, _pa_config(body_pct_min=0.7))
    body = feats.column("body_pct").copy()
    body[k] = 0.95
    feats2 = make_feature_matrix_with_columns(
        n, _feature_dict(n, body_pct=body), feature_hash=feats.feature_hash
    )
    s1 = generate_pa_buy_sell_close_trend_signals(bars, feats2, _pa_config(body_pct_min=0.7))
    assert s0.entry[k] != s1.entry[k] or not np.allclose(s0.score[k], s1.score[k], equal_nan=True)
