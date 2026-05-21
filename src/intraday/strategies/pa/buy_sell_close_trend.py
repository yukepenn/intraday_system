"""PA buy-sell-close trend continuation with side-aware short retrofit."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.core.errors import ConfigError
from intraday.strategies.base import StrategyDef
from intraday.strategies.common import (
    build_side_aware_signal_matrix,
    compute_long_stop,
    compute_short_stop,
    previous_same_session,
)
from intraday.strategies.config_validation import (
    CURRENT10_SIDE_MODES,
    parse_bool_like,
    validate_pa_buy_sell_close_trend_config,
)
from intraday.strategies.contracts import (
    SIDE_MODE_LONG_ONLY,
    SIGNAL_CONTRACT_VERSION,
    clip_finite,
    normalize_side_mode,
    require_feature_columns,
)
from intraday.strategies.setup_codes import get_setup_codes

STRATEGY_NAME = "pa_buy_sell_close_trend"
_SPEC = get_setup_codes(STRATEGY_NAME)
SETUP_CODE_LONG = _SPEC.long_code
SETUP_CODE_SHORT = _SPEC.short_code

PA_REQUIRED_FEATURE_COLUMNS: tuple[str, ...] = (
    "body_pct",
    "close_position_in_range",
    "trend_slope_like_20",
    "close_vs_rolling_mean_20",
    "vwap_side",
    "atr_like_20",
    "rolling_low_20",
    "bar_range",
)

PA_OPTIONAL_FEATURE_COLUMNS: dict[str, tuple[str, ...]] = {
    "max_vwap_dist_pct": ("vwap_dist_pct",),
    "min_rel_volume_20": ("rel_volume_20",),
    "require_close_above_vwap": ("vwap",),
    "require_above_rolling_high_20": ("rolling_high_20",),
    "range_mean_mult": ("range_mean_20",),
    "vwap_atr_buffer": ("vwap",),
    "short": ("rolling_high_20",),
}

_LONG_STOP_MODES = (
    "signal_low",
    "rolling_low",
    "rolling_low_20",
    "atr_buffer",
    "vwap_atr_buffer",
)

_SHORT_STOP_MODE_MAP: dict[str, str] = {
    "signal_low": "signal_high",
    "rolling_low": "rolling_high_20",
    "rolling_low_20": "rolling_high_20",
    "atr_buffer": "atr_buffer",
    "vwap_atr_buffer": "vwap_atr_buffer",
}


def _short_stop_mode(sig: Mapping[str, Any], long_mode: str) -> str:
    candidate = sig.get("short_stop_mode")
    if candidate is None:
        return _SHORT_STOP_MODE_MAP.get(long_mode, "signal_high")
    return str(candidate)


def _simple_pa_v1_long_score(
    body_pct: np.ndarray,
    close_pos: np.ndarray,
    trend_slope: np.ndarray,
    close_vs_mean: np.ndarray,
    atr: np.ndarray,
    vwap_side: np.ndarray,
) -> np.ndarray:
    trend_term = clip_finite(trend_slope / atr, -2.0, 2.0)
    mean_term = clip_finite(close_vs_mean / atr, -2.0, 2.0)
    vwap_bonus = np.where(vwap_side > 0, 0.10, 0.0)
    return body_pct + 0.25 * close_pos + 0.25 * trend_term + 0.25 * mean_term + vwap_bonus


def _simple_pa_v1_short_score(
    body_pct: np.ndarray,
    close_pos: np.ndarray,
    trend_slope: np.ndarray,
    close_vs_mean: np.ndarray,
    atr: np.ndarray,
    vwap_side: np.ndarray,
) -> np.ndarray:
    # Mirror long-side score: invert signed terms and use 1 - close_pos so the
    # score grows when bearish conditions strengthen.
    trend_term = clip_finite(-trend_slope / atr, -2.0, 2.0)
    mean_term = clip_finite(-close_vs_mean / atr, -2.0, 2.0)
    vwap_bonus = np.where(vwap_side < 0, 0.10, 0.0)
    return body_pct + 0.25 * (1.0 - close_pos) + 0.25 * trend_term + 0.25 * mean_term + vwap_bonus


def generate_pa_buy_sell_close_trend_signals(
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
) -> SignalMatrix:
    """Generate side-aware PA trend signals from BarMatrix + FeatureMatrix."""
    validate_pa_buy_sell_close_trend_config(config)
    score_mode = str(config["signal"].get("score_mode", "simple_pa_v1"))
    if score_mode != "simple_pa_v1":
        raise ConfigError(f"unsupported signal.score_mode for {STRATEGY_NAME}: {score_mode!r}")

    sig = config["signal"]
    risk = config["risk"]
    side_mode = normalize_side_mode(sig)
    short_enabled = side_mode != SIDE_MODE_LONG_ONLY
    optional_cols: list[str] = []
    if "max_vwap_dist_pct" in sig:
        optional_cols.extend(PA_OPTIONAL_FEATURE_COLUMNS["max_vwap_dist_pct"])
    if "min_rel_volume_20" in sig:
        optional_cols.extend(PA_OPTIONAL_FEATURE_COLUMNS["min_rel_volume_20"])
    if parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    ):
        optional_cols.extend(PA_OPTIONAL_FEATURE_COLUMNS["require_close_above_vwap"])
    if parse_bool_like(
        sig.get("require_above_rolling_high_20", False),
        "signal.require_above_rolling_high_20",
    ):
        optional_cols.extend(PA_OPTIONAL_FEATURE_COLUMNS["require_above_rolling_high_20"])
    if "min_range_mean_mult" in sig or "max_range_mean_mult" in sig:
        optional_cols.extend(PA_OPTIONAL_FEATURE_COLUMNS["range_mean_mult"])
    long_stop_mode = str(risk.get("stop_mode", "signal_low"))
    if long_stop_mode == "vwap_atr_buffer":
        optional_cols.extend(PA_OPTIONAL_FEATURE_COLUMNS["vwap_atr_buffer"])
    if short_enabled:
        optional_cols.extend(PA_OPTIONAL_FEATURE_COLUMNS["short"])
        short_stop_mode = _short_stop_mode(sig, long_stop_mode)
        if short_stop_mode in ("vwap_atr_buffer",):
            optional_cols.append("vwap")
    require_feature_columns(
        features.columns,
        (*PA_REQUIRED_FEATURE_COLUMNS, *tuple(dict.fromkeys(optional_cols))),
        strategy_name=STRATEGY_NAME,
    )

    es = int(sig["entry_start_minute"])
    ee = int(sig["entry_end_minute"])
    body_min = float(sig.get("body_pct_min", 0))
    cp_min = float(sig.get("close_position_min", 0))
    trend_min = float(sig.get("trend_slope_min", 0))
    cv_min = float(sig.get("close_vs_mean_min", 0))
    req_vwap = parse_bool_like(sig.get("require_vwap_side", False), "signal.require_vwap_side")
    req_close_above_vwap = parse_bool_like(
        sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap"
    )
    req_breakout = parse_bool_like(
        sig.get("require_above_rolling_high_20", False),
        "signal.require_above_rolling_high_20",
    )
    target_r_val = float(risk["target_r"])
    atr_mult = float(risk.get("atr_buffer_mult", 0.35))

    body_pct = features.column("body_pct")
    close_pos = features.column("close_position_in_range")
    trend_slope = features.column("trend_slope_like_20")
    close_vs_mean = features.column("close_vs_rolling_mean_20")
    vwap_side = features.column("vwap_side")
    atr = features.column("atr_like_20")
    close = bars.close

    minute = bars.minute.astype(np.int32, copy=False)
    in_window = (minute >= es) & (minute <= ee)

    finite_req = (
        np.isfinite(body_pct)
        & np.isfinite(close_pos)
        & np.isfinite(trend_slope)
        & np.isfinite(close_vs_mean)
        & np.isfinite(vwap_side)
        & np.isfinite(atr)
        & (atr > 0)
    )

    long_cand = (
        in_window
        & finite_req
        & (body_pct >= body_min)
        & (close_pos >= cp_min)
        & (trend_slope >= trend_min)
        & (close_vs_mean >= cv_min)
    )
    if req_vwap:
        long_cand &= vwap_side > 0
    if req_close_above_vwap:
        long_cand &= close > features.column("vwap")
    if "max_vwap_dist_pct" in sig:
        long_cand &= np.abs(features.column("vwap_dist_pct")) <= float(sig["max_vwap_dist_pct"])
    if "min_rel_volume_20" in sig:
        long_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])
    if req_breakout:
        prior_rolling_high = previous_same_session(
            features.column("rolling_high_20"), bars.session_id
        )
        long_cand &= close > prior_rolling_high
    if "min_range_mean_mult" in sig:
        long_cand &= features.column("bar_range") >= float(
            sig["min_range_mean_mult"]
        ) * features.column("range_mean_20")
    if "max_range_mean_mult" in sig:
        long_cand &= features.column("bar_range") <= float(
            sig["max_range_mean_mult"]
        ) * features.column("range_mean_20")

    short_cand = np.zeros_like(long_cand, dtype=bool)
    if short_enabled:
        # Mirror the long-side filters: invert signed thresholds, flip
        # close_position semantics, and require bearish optional filters when set.
        short_cand = (
            in_window
            & finite_req
            & (body_pct >= body_min)
            & ((1.0 - close_pos) >= cp_min)
            & (trend_slope <= -trend_min)
            & (close_vs_mean <= -cv_min)
        )
        if req_vwap:
            short_cand &= vwap_side < 0
        if req_close_above_vwap:
            short_cand &= close < features.column("vwap")
        if "max_vwap_dist_pct" in sig:
            short_cand &= np.abs(features.column("vwap_dist_pct")) <= float(
                sig["max_vwap_dist_pct"]
            )
        if "min_rel_volume_20" in sig:
            short_cand &= features.column("rel_volume_20") >= float(sig["min_rel_volume_20"])
        if req_breakout:
            prior_rolling_low = previous_same_session(
                features.column("rolling_low_20"), bars.session_id
            )
            short_cand &= close < prior_rolling_low
        if "min_range_mean_mult" in sig:
            short_cand &= features.column("bar_range") >= float(
                sig["min_range_mean_mult"]
            ) * features.column("range_mean_20")
        if "max_range_mean_mult" in sig:
            short_cand &= features.column("bar_range") <= float(
                sig["max_range_mean_mult"]
            ) * features.column("range_mean_20")

    vwap_arr = features.column("vwap") if "vwap" in features.columns else None
    long_stop = compute_long_stop(
        bars,
        features,
        long_stop_mode,
        atr_mult=atr_mult,
        vwap=vwap_arr,
    )
    long_score = _simple_pa_v1_long_score(
        body_pct, close_pos, trend_slope, close_vs_mean, atr, vwap_side
    )
    if short_enabled:
        short_stop = compute_short_stop(
            bars,
            features,
            _short_stop_mode(sig, long_stop_mode),
            atr_mult=atr_mult,
            vwap=vwap_arr,
        )
        short_score = _simple_pa_v1_short_score(
            body_pct, close_pos, trend_slope, close_vs_mean, atr, vwap_side
        )
    else:
        short_stop = np.full(bars.n_bars, np.nan, dtype=np.float64)
        short_score = np.full(bars.n_bars, np.nan, dtype=np.float64)

    max_trades = int(risk["max_trades_per_day"]) if "max_trades_per_day" in risk else None
    return build_side_aware_signal_matrix(
        bars=bars,
        features=features,
        config=dict(config),
        strategy_name=STRATEGY_NAME,
        long_entry=long_cand,
        short_entry=short_cand,
        long_stop=long_stop,
        short_stop=short_stop,
        long_score=long_score,
        short_score=short_score,
        target_r_val=target_r_val,
        setup_code_long=SETUP_CODE_LONG,
        setup_code_short=SETUP_CODE_SHORT,
        side_mode=side_mode,
        max_trades_per_day=max_trades,
    )


PA_BUY_SELL_CLOSE_TREND_DEF = StrategyDef(
    name=STRATEGY_NAME,
    family="pa",
    version="strategy_v1",
    required_feature_set="pa_core_v1",
    signal_contract_version=SIGNAL_CONTRACT_VERSION,
    generate_reference=generate_pa_buy_sell_close_trend_signals,
    validate_config=validate_pa_buy_sell_close_trend_config,
    setup_code_long=SETUP_CODE_LONG,
    setup_code_short=SETUP_CODE_SHORT,
    allowed_side_modes=CURRENT10_SIDE_MODES,
    default_side_mode=SIDE_MODE_LONG_ONLY,
    required_feature_columns=PA_REQUIRED_FEATURE_COLUMNS,
)
