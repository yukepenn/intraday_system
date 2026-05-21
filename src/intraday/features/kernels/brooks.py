"""Brooks-style price-action market facts for Phase19 Slice F1."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix
from intraday.features.kernels.session_ops import (
    rolling_mean_session,
    session_start_indices,
    true_range_session,
)


def _safe_divide(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    out = np.full(num.shape, np.nan, dtype=np.float64)
    np.divide(num, den, out=out, where=den != 0.0)
    return out


def _clip01(x: np.ndarray) -> np.ndarray:
    out = np.clip(x, 0.0, 1.0)
    out[~np.isfinite(x)] = np.nan
    return out.astype(np.float64, copy=False)


def _prior_rolling_max(x: np.ndarray, starts: np.ndarray, window: int) -> np.ndarray:
    out = np.full(x.shape[0], np.nan, dtype=np.float64)
    for i in range(x.shape[0]):
        s0 = int(starts[i])
        hi = i
        lo = max(s0, i - window)
        if hi - lo < window:
            continue
        out[i] = float(np.max(x[lo:hi]))
    return out


def _prior_rolling_min(x: np.ndarray, starts: np.ndarray, window: int) -> np.ndarray:
    out = np.full(x.shape[0], np.nan, dtype=np.float64)
    for i in range(x.shape[0]):
        s0 = int(starts[i])
        hi = i
        lo = max(s0, i - window)
        if hi - lo < window:
            continue
        out[i] = float(np.min(x[lo:hi]))
    return out


def _micro_channel(
    open_: np.ndarray,
    close: np.ndarray,
    session_id: np.ndarray,
    length: int,
    *,
    bullish: bool,
) -> np.ndarray:
    out = np.full(close.shape[0], np.nan, dtype=np.float64)
    for i in range(close.shape[0]):
        start = i - length + 1
        if start < 0 or session_id[start] != session_id[i]:
            continue
        ok = True
        for j in range(start, i + 1):
            if bullish:
                ok = ok and close[j] > open_[j]
                if j > start:
                    ok = ok and close[j] >= close[j - 1]
            else:
                ok = ok and close[j] < open_[j]
                if j > start:
                    ok = ok and close[j] <= close[j - 1]
        out[i] = 1.0 if ok else 0.0
    return out


def _bool_to_float(x: np.ndarray) -> np.ndarray:
    return x.astype(np.float64, copy=False)


def compute_pa_brooks_bar_core_group(
    bars: BarMatrix,
    cfg: Mapping[str, Any],
) -> dict[str, np.ndarray]:
    """Bar-local Brooks PA facts plus session-contained micro channels."""
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    open_ = bars.open.astype(np.float64, copy=False)
    high = bars.high.astype(np.float64, copy=False)
    low = bars.low.astype(np.float64, copy=False)
    close = bars.close.astype(np.float64, copy=False)
    starts = session_start_indices(bars.session_id)

    bar_range = high - low
    close_pos = _safe_divide(close - low, bar_range)
    body_pct = _safe_divide(np.abs(close - open_), bar_range)
    upper_wick = high - np.maximum(open_, close)
    lower_wick = np.minimum(open_, close) - low
    upper_wick_pct = _safe_divide(upper_wick, bar_range)
    lower_wick_pct = _safe_divide(lower_wick, bar_range)

    strong_bull = (close > open_) & (close_pos >= 0.8) & np.isfinite(close_pos)
    strong_bear = (close < open_) & (close_pos <= 0.2) & np.isfinite(close_pos)
    weak_bull = (close > open_) & (upper_wick_pct > body_pct) & np.isfinite(upper_wick_pct)
    weak_bear = (close < open_) & (lower_wick_pct > body_pct) & np.isfinite(lower_wick_pct)

    signal_window = int(cfg.get("signal_window", 5))
    prior_low = _prior_rolling_min(low, starts, signal_window)
    prior_high = _prior_rolling_max(high, starts, signal_window)
    min_body = float(cfg.get("min_signal_body_pct", 0.5))
    bull_signal = strong_bull & (body_pct >= min_body) & (low <= prior_low)
    bear_signal = strong_bear & (body_pct >= min_body) & (high >= prior_high)

    out: dict[str, np.ndarray] = {}
    if "strong_bull_close" in outputs:
        out["strong_bull_close"] = _bool_to_float(strong_bull)
    if "strong_bear_close" in outputs:
        out["strong_bear_close"] = _bool_to_float(strong_bear)
    if "weak_bull_close" in outputs:
        out["weak_bull_close"] = _bool_to_float(weak_bull)
    if "weak_bear_close" in outputs:
        out["weak_bear_close"] = _bool_to_float(weak_bear)
    if "bull_signal_bar" in outputs:
        out["bull_signal_bar"] = _bool_to_float(bull_signal)
    if "bear_signal_bar" in outputs:
        out["bear_signal_bar"] = _bool_to_float(bear_signal)
    if "failed_bull_signal_bar" in outputs:
        failed = np.zeros(bars.n_bars, dtype=np.float64)
        failed[1:] = (bull_signal[:-1] & (close[1:] < low[:-1])).astype(np.float64)
        failed[bars.session_id != np.roll(bars.session_id, 1)] = 0.0
        out["failed_bull_signal_bar"] = failed
    if "failed_bear_signal_bar" in outputs:
        failed = np.zeros(bars.n_bars, dtype=np.float64)
        failed[1:] = (bear_signal[:-1] & (close[1:] > high[:-1])).astype(np.float64)
        failed[bars.session_id != np.roll(bars.session_id, 1)] = 0.0
        out["failed_bear_signal_bar"] = failed
    if "bull_micro_channel" in outputs:
        for length in cfg.get("micro_channel_lengths", [3]):
            out[f"bull_micro_channel_{int(length)}"] = _micro_channel(
                open_,
                close,
                bars.session_id,
                int(length),
                bullish=True,
            )
    if "bear_micro_channel" in outputs:
        for length in cfg.get("micro_channel_lengths", [3]):
            out[f"bear_micro_channel_{int(length)}"] = _micro_channel(
                open_,
                close,
                bars.session_id,
                int(length),
                bullish=False,
            )
    return out


def compute_pa_brooks_regime_core_group(
    bars: BarMatrix,
    cfg: Mapping[str, Any],
) -> dict[str, np.ndarray]:
    """Observable regime scores, not strategy decisions."""
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    high = bars.high.astype(np.float64, copy=False)
    low = bars.low.astype(np.float64, copy=False)
    close = bars.close.astype(np.float64, copy=False)
    starts = session_start_indices(bars.session_id)
    true_range = true_range_session(high, low, close, bars.session_id)
    out: dict[str, np.ndarray] = {}

    always_in_sum = np.zeros(bars.n_bars, dtype=np.float64)
    always_in_count = 0
    for window in [int(x) for x in cfg.get("windows", [])]:
        atr = rolling_mean_session(true_range, bars.session_id, starts, window)
        prior_high = _prior_rolling_max(high, starts, window)
        prior_low = _prior_rolling_min(low, starts, window)
        den = np.where(atr > 0.0, atr, np.nan)
        slope = np.full(bars.n_bars, np.nan, dtype=np.float64)
        for i in range(bars.n_bars):
            j = i - window
            if j >= int(starts[i]):
                slope[i] = (close[i] - close[j]) / float(window)
        slope_atr = slope / den
        bull_bo = _clip01((close - prior_high) / den)
        bear_bo = _clip01((prior_low - close) / den)
        trend_strength = _clip01(np.abs(slope_atr))
        trading_range = _clip01(1.0 - trend_strength)
        tight_bull = _clip01(slope_atr * 2.0)
        tight_bear = _clip01(-slope_atr * 2.0)
        broad_bull = _clip01(slope_atr)
        broad_bear = _clip01(-slope_atr)

        if "pa_strong_bull_bo_score" in outputs:
            out[f"pa_strong_bull_bo_score_{window}"] = bull_bo
        if "pa_strong_bear_bo_score" in outputs:
            out[f"pa_strong_bear_bo_score_{window}"] = bear_bo
        if "pa_tight_bull_channel_score" in outputs:
            out[f"pa_tight_bull_channel_score_{window}"] = tight_bull
        if "pa_tight_bear_channel_score" in outputs:
            out[f"pa_tight_bear_channel_score_{window}"] = tight_bear
        if "pa_broad_bull_channel_score" in outputs:
            out[f"pa_broad_bull_channel_score_{window}"] = broad_bull
        if "pa_broad_bear_channel_score" in outputs:
            out[f"pa_broad_bear_channel_score_{window}"] = broad_bear
        if "pa_trading_range_score" in outputs:
            out[f"pa_trading_range_score_{window}"] = trading_range
        if "pa_late_trend_score" in outputs:
            out[f"pa_late_trend_score_{window}"] = _clip01(
                trend_strength + np.maximum(bull_bo, bear_bo)
            )

        side = np.where(slope_atr > 0.05, 1.0, np.where(slope_atr < -0.05, -1.0, 0.0))
        side[~np.isfinite(slope_atr)] = np.nan
        always_in_sum += np.nan_to_num(side, nan=0.0)
        always_in_count += 1

    if "pa_always_in_side" in outputs:
        side = np.full(bars.n_bars, np.nan, dtype=np.float64)
        if always_in_count > 0:
            avg = always_in_sum / always_in_count
            side = np.where(avg > 0.0, 1.0, np.where(avg < 0.0, -1.0, 0.0))
        out["pa_always_in_side"] = side.astype(np.float64, copy=False)

    return out


def compute_pa_brooks_range_core_group(
    bars: BarMatrix,
    cfg: Mapping[str, Any],
) -> dict[str, np.ndarray]:
    """Prior-exclusive rolling trading-range facts."""
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    high = bars.high.astype(np.float64, copy=False)
    low = bars.low.astype(np.float64, copy=False)
    close = bars.close.astype(np.float64, copy=False)
    starts = session_start_indices(bars.session_id)
    true_range = true_range_session(high, low, close, bars.session_id)
    atr = rolling_mean_session(true_range, bars.session_id, starts, int(cfg.get("atr_window", 20)))
    back_inside_bars = int(cfg.get("back_inside_bars", 3))

    out: dict[str, np.ndarray] = {}
    for window in [int(x) for x in cfg.get("range_windows", [])]:
        tr_high = _prior_rolling_max(high, starts, window)
        tr_low = _prior_rolling_min(low, starts, window)
        tr_width = tr_high - tr_low
        tr_mid = (tr_high + tr_low) / 2.0
        lower_third = tr_low + tr_width / 3.0
        upper_third = tr_high - tr_width / 3.0
        width_atr = _safe_divide(tr_width, atr)
        lower = (close <= lower_third) & np.isfinite(lower_third)
        upper = (close >= upper_third) & np.isfinite(upper_third)
        breakout_up = (close > tr_high) & np.isfinite(tr_high)
        breakout_down = (close < tr_low) & np.isfinite(tr_low)
        inside = (close <= tr_high) & (close >= tr_low) & np.isfinite(tr_high) & np.isfinite(tr_low)
        back_inside = np.zeros(bars.n_bars, dtype=np.float64)
        for i in range(bars.n_bars):
            if not inside[i]:
                continue
            lo_i = max(int(starts[i]), i - back_inside_bars)
            if np.any(breakout_up[lo_i:i]) or np.any(breakout_down[lo_i:i]):
                back_inside[i] = 1.0

        values = {
            "pa_tr_high": tr_high,
            "pa_tr_low": tr_low,
            "pa_tr_mid": tr_mid,
            "pa_tr_upper_third": upper_third,
            "pa_tr_lower_third": lower_third,
            "pa_tr_width_atr": width_atr,
            "pa_close_in_lower_third": _bool_to_float(lower),
            "pa_close_in_upper_third": _bool_to_float(upper),
            "pa_range_breakout_up": _bool_to_float(breakout_up),
            "pa_range_breakout_down": _bool_to_float(breakout_down),
            "pa_close_back_inside_range": back_inside,
        }
        for name, arr in values.items():
            if name in outputs:
                out[f"{name}_{window}"] = arr.astype(np.float64, copy=False)

    return out


def compute_pa_brooks_swing_core_group(
    bars: BarMatrix,
    cfg: Mapping[str, Any],
) -> dict[str, np.ndarray]:
    """Lightweight prior-exclusive swing and second-entry proxies."""
    outputs = set(cfg.get("outputs") or ())
    if not outputs:
        return {}

    high = bars.high.astype(np.float64, copy=False)
    low = bars.low.astype(np.float64, copy=False)
    close = bars.close.astype(np.float64, copy=False)
    starts = session_start_indices(bars.session_id)
    window = int(cfg.get("swing_window", 5))
    atr_window = int(cfg.get("atr_window", 20))
    true_range = true_range_session(high, low, close, bars.session_id)
    atr = rolling_mean_session(true_range, bars.session_id, starts, atr_window)

    leg_direction = np.full(bars.n_bars, np.nan, dtype=np.float64)
    for i in range(bars.n_bars):
        j0 = i - window
        j1 = i - 1
        if j0 < int(starts[i]) or j1 < int(starts[i]):
            continue
        diff = close[j1] - close[j0]
        leg_direction[i] = 1.0 if diff > 0 else (-1.0 if diff < 0 else 0.0)

    pullback_count = np.zeros(bars.n_bars, dtype=np.float64)
    pullback_depth = np.full(bars.n_bars, np.nan, dtype=np.float64)
    two_leg_down = np.zeros(bars.n_bars, dtype=np.float64)
    two_leg_up = np.zeros(bars.n_bars, dtype=np.float64)
    second_buy = np.zeros(bars.n_bars, dtype=np.float64)
    second_sell = np.zeros(bars.n_bars, dtype=np.float64)

    for i in range(bars.n_bars):
        s0 = int(starts[i])
        if not np.isfinite(leg_direction[i]) or i <= s0:
            continue
        count = 0
        j = i
        if leg_direction[i] > 0:
            while j > s0 and close[j] < close[j - 1]:
                count += 1
                j -= 1
            if count > 0:
                depth = np.max(high[j : i + 1]) - close[i]
                pullback_depth[i] = depth / atr[i] if atr[i] > 0 else np.nan
            two_leg_down[i] = 1.0 if count >= 2 else 0.0
            if i > s0 and two_leg_down[i] and close[i] > high[i - 1]:
                second_buy[i] = 1.0
        elif leg_direction[i] < 0:
            while j > s0 and close[j] > close[j - 1]:
                count += 1
                j -= 1
            if count > 0:
                depth = close[i] - np.min(low[j : i + 1])
                pullback_depth[i] = depth / atr[i] if atr[i] > 0 else np.nan
            two_leg_up[i] = 1.0 if count >= 2 else 0.0
            if i > s0 and two_leg_up[i] and close[i] < low[i - 1]:
                second_sell[i] = 1.0
        pullback_count[i] = float(count)

    values = {
        "pa_leg_direction": leg_direction,
        "pa_pullback_bar_count": pullback_count,
        "pa_pullback_depth_atr": pullback_depth,
        "pa_two_leg_pullback_down": two_leg_down,
        "pa_two_leg_pullback_up": two_leg_up,
        "pa_second_entry_buy_proxy": second_buy,
        "pa_second_entry_sell_proxy": second_sell,
    }
    return {
        name: arr.astype(np.float64, copy=False) for name, arr in values.items() if name in outputs
    }
