"""Shared helpers for Phase19 Brooks PA strategies."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix, SignalMatrix
from intraday.core.errors import ConfigError
from intraday.core.types import Side
from intraday.strategies.config_validation import (
    _as_float,
    _as_int,
    parse_bool_like,
    validate_optional_nonnegative_float,
    validate_optional_positive_float,
    validate_optional_positive_int,
    validate_side_mode_allowed,
)
from intraday.strategies.contracts import (
    SIDE_MODE_BOTH,
    SIDE_MODE_LONG_ONLY,
    SIDE_MODE_SHORT_ONLY,
    SIGNAL_CONTRACT_VERSION,
    allowed_sides_for_mode,
    clip_finite,
    compute_signal_hash,
    require_feature_columns,
    validate_signal_matrix,
)

BROOKS_SIDE_MODES: tuple[str, ...] = (
    SIDE_MODE_LONG_ONLY,
    SIDE_MODE_SHORT_ONLY,
    SIDE_MODE_BOTH,
)


def brooks_bool(signal_config: Mapping[str, Any], key: str, default: bool) -> bool:
    """Strict boolean coercion for Brooks strategy runtime config reads.

    Mirrors the validation-time semantics of ``parse_bool_like`` so that
    ``"false"`` / ``"true"`` / ``0`` / ``1`` cannot diverge between validation
    and runtime. Raises ``ConfigError`` on invalid values.
    """
    return parse_bool_like(signal_config.get(key, default), f"signal.{key}")


def validate_brooks_strategy_config(
    config: Mapping[str, Any],
    *,
    strategy_name: str,
    required_feature_set: str | tuple[str, ...],
    allowed_stop_modes: tuple[str, ...] = ("signal_extreme",),
) -> None:
    """Validate config fields shared by Phase19B side-aware Brooks strategies."""
    if config.get("strategy") != strategy_name:
        raise ConfigError(f"strategy must be {strategy_name}, got {config.get('strategy')!r}")
    if "family" in config and config["family"] != "pa":
        raise ConfigError("family must be pa when present")

    allowed_feature_sets = (
        (required_feature_set,) if isinstance(required_feature_set, str) else required_feature_set
    )
    rfs = config.get("required_feature_set")
    if rfs not in (None, *allowed_feature_sets):
        joined = " or ".join(allowed_feature_sets)
        raise ConfigError(f"required_feature_set must be {joined}")

    sig = config.get("signal")
    if not isinstance(sig, Mapping):
        raise ConfigError("signal section required")
    validate_side_mode_allowed(sig, allowed=BROOKS_SIDE_MODES)

    es = _as_int(sig.get("entry_start_minute"), "signal.entry_start_minute")
    ee = _as_int(sig.get("entry_end_minute"), "signal.entry_end_minute")
    if not (0 <= es < ee <= 389):
        raise ConfigError("entry window must satisfy 0 <= entry_start < entry_end <= 389")

    for key in (
        "pullback_max_depth_atr",
        "tr_score_min",
        "min_range_width_atr",
        "bo_score_min",
        "tight_score_min",
        "broad_score_min",
        "initial_move_min_atr",
        "zone_fraction",
    ):
        validate_optional_nonnegative_float(sig, key, f"signal.{key}")
    for key in (
        "range_window",
        "tr_window",
        "fail_back_inside_bars",
        "breakout_window",
        "pullback_max_bars",
    ):
        validate_optional_positive_int(sig, key, f"signal.{key}")
    for key in (
        "require_second_entry",
        "require_signal_bar",
        "require_failed_breakout",
        "require_reversal_bar",
        "require_prior_strong_breakout",
        "require_always_in_with_side",
        "require_micro_channel",
        "block_late_trend",
        "block_strong_bo_followthrough",
    ):
        if key in sig:
            parse_bool_like(sig[key], f"signal.{key}")

    risk = config.get("risk")
    if not isinstance(risk, Mapping):
        raise ConfigError("risk section required")
    stop_mode = str(risk.get("stop_mode", "signal_extreme"))
    if stop_mode not in allowed_stop_modes:
        raise ConfigError(f"risk.stop_mode invalid: {stop_mode!r}")
    if risk.get("target_mode", "fixed_r") != "fixed_r":
        raise ConfigError("risk.target_mode must be fixed_r")
    validate_optional_positive_float(risk, "target_r", "risk.target_r")
    if _as_float(risk.get("target_r"), "risk.target_r") <= 0:
        raise ConfigError("risk.target_r must be > 0")
    if (
        "max_trades_per_day" in risk
        and _as_int(risk["max_trades_per_day"], "risk.max_trades_per_day") <= 0
    ):
        raise ConfigError("risk.max_trades_per_day must be > 0")
    if (
        "min_risk_per_share" in risk
        and _as_float(risk["min_risk_per_share"], "risk.min_risk_per_share") < 0
    ):
        raise ConfigError("risk.min_risk_per_share must be >= 0")

    backtest = config.get("backtest")
    if isinstance(backtest, Mapping):
        if "quantity" in backtest and _as_float(backtest["quantity"], "backtest.quantity") <= 0:
            raise ConfigError("backtest.quantity must be > 0")
        if "eod_exit_minute" in backtest:
            eod = _as_int(backtest["eod_exit_minute"], "backtest.eod_exit_minute")
            if not (0 <= eod <= 389):
                raise ConfigError("backtest.eod_exit_minute must be in 0..389")
        if (
            "max_hold_minutes" in backtest
            and _as_int(backtest["max_hold_minutes"], "backtest.max_hold_minutes") <= 0
        ):
            raise ConfigError("backtest.max_hold_minutes must be > 0")


def brooks_allowed_sides(signal_config: Mapping[str, Any]) -> tuple[int, ...]:
    """Return allowed sides for a validated Brooks side mode."""
    mode = validate_side_mode_allowed(signal_config, allowed=BROOKS_SIDE_MODES)
    return allowed_sides_for_mode(mode)


def require_brooks_feature_columns(
    features: FeatureMatrix,
    required: tuple[str, ...],
    *,
    strategy_name: str,
) -> None:
    require_feature_columns(features.columns, required, strategy_name=strategy_name)


def in_entry_window(bars: BarMatrix, signal_config: Mapping[str, Any]) -> np.ndarray:
    minute = bars.minute.astype(np.int32, copy=False)
    return (minute >= int(signal_config["entry_start_minute"])) & (
        minute <= int(signal_config["entry_end_minute"])
    )


def previous_same_session_bool(condition: np.ndarray, session_id: np.ndarray) -> np.ndarray:
    out = np.zeros(condition.shape[0], dtype=bool)
    out[1:] = (session_id[1:] == session_id[:-1]) & condition[:-1]
    return out


def prior_condition_within(
    condition: np.ndarray,
    session_id: np.ndarray,
    max_bars: int,
) -> np.ndarray:
    out = np.zeros(condition.shape[0], dtype=bool)
    last_seen = -1
    current_session: int | None = None
    for i in range(condition.shape[0]):
        sid = int(session_id[i])
        if current_session is None or sid != current_session:
            current_session = sid
            last_seen = -1
        if last_seen >= 0 and i - last_seen <= max_bars:
            out[i] = True
        if bool(condition[i]):
            last_seen = i
    return out


def long_short_stops(
    bars: BarMatrix,
    features: FeatureMatrix,
    *,
    stop_mode: str,
    range_window: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Resolve raw long/short stops without computing entry or target prices."""
    if stop_mode == "range_third" and range_window is not None:
        return (
            features.column(f"pa_tr_lower_third_{range_window}").astype(np.float64, copy=True),
            features.column(f"pa_tr_upper_third_{range_window}").astype(np.float64, copy=True),
        )
    if stop_mode == "range_extreme" and range_window is not None:
        return (
            features.column(f"pa_tr_low_{range_window}").astype(np.float64, copy=True),
            features.column(f"pa_tr_high_{range_window}").astype(np.float64, copy=True),
        )
    return (
        bars.low.astype(np.float64, copy=True),
        bars.high.astype(np.float64, copy=True),
    )


def deterministic_score(*terms: np.ndarray) -> np.ndarray:
    """Small finite score combiner for signal quality, not economics."""
    if not terms:
        raise ValueError("at least one score term required")
    out = np.zeros_like(terms[0], dtype=np.float64)
    valid = np.ones_like(terms[0], dtype=bool)
    for term in terms:
        arr = np.asarray(term, dtype=np.float64)
        valid &= np.isfinite(arr)
        out += np.nan_to_num(arr, nan=0.0)
    out = out / float(len(terms))
    out[~valid] = np.nan
    return clip_finite(out, -5.0, 5.0)


def build_brooks_signal_matrix(
    *,
    bars: BarMatrix,
    features: FeatureMatrix,
    config: Mapping[str, Any],
    strategy_name: str,
    long_entry: np.ndarray,
    short_entry: np.ndarray,
    long_stop: np.ndarray,
    short_stop: np.ndarray,
    long_score: np.ndarray,
    short_score: np.ndarray,
    setup_code_long: int,
    setup_code_short: int,
) -> SignalMatrix:
    """Build a side-aware SignalMatrix with strict entry/non-entry conventions."""
    n = bars.n_bars
    allowed = set(brooks_allowed_sides(config["signal"]))
    long_enabled = int(Side.LONG) in allowed
    short_enabled = int(Side.SHORT) in allowed

    long_entry = np.asarray(long_entry, dtype=bool) & long_enabled
    short_entry = np.asarray(short_entry, dtype=bool) & short_enabled

    close = bars.close.astype(np.float64, copy=False)
    long_entry &= np.isfinite(long_stop) & (long_stop < close) & np.isfinite(long_score)
    short_entry &= np.isfinite(short_stop) & (short_stop > close) & np.isfinite(short_score)
    short_entry &= ~long_entry

    entry = long_entry | short_entry
    side = np.zeros(n, dtype=np.int8)
    stop = np.full(n, np.nan, dtype=np.float64)
    target_r = np.full(n, np.nan, dtype=np.float64)
    score = np.full(n, np.nan, dtype=np.float64)
    setup_code = np.zeros(n, dtype=np.int16)

    target = float(config["risk"]["target_r"])
    if long_entry.any():
        side[long_entry] = int(Side.LONG)
        stop[long_entry] = long_stop[long_entry]
        target_r[long_entry] = target
        score[long_entry] = long_score[long_entry]
        setup_code[long_entry] = int(setup_code_long)
    if short_entry.any():
        side[short_entry] = int(Side.SHORT)
        stop[short_entry] = short_stop[short_entry]
        target_r[short_entry] = target
        score[short_entry] = short_score[short_entry]
        setup_code[short_entry] = int(setup_code_short)

    signal_hash = compute_signal_hash(
        strategy_name=strategy_name,
        strategy_version=str(config.get("version", "strategy_v1")),
        signal_contract_version=str(config.get("signal_contract_version", SIGNAL_CONTRACT_VERSION)),
        config=dict(config),
        feature_hash=features.feature_hash,
    )
    out = SignalMatrix(
        entry=entry.astype(np.bool_),
        side=side,
        stop=stop,
        target_r=target_r,
        score=score,
        setup_code=setup_code,
        signal_hash=signal_hash,
    )
    validate_signal_matrix(out, n, reference_close=bars.close)
    return out
