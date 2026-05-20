"""Strategy config validation."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from intraday.core.config import require_keys
from intraday.core.errors import ConfigError
from intraday.strategies.base import StrategyDef


def parse_bool_like(value: Any, field: str) -> bool:
    """Strict boolean coercion (no ``bool(string)`` pitfalls)."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        s = value.strip().lower()
        if s in ("true", "1", "yes"):
            return True
        if s in ("false", "0", "no"):
            return False
    raise ConfigError(f"{field} must be a boolean-like value, got {value!r}")


def _as_float(value: Any, field: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{field} must be numeric, got {value!r}") from exc
    if not math.isfinite(out):
        raise ConfigError(f"{field} must be finite, got {value!r}")
    return out


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ConfigError(f"{field} must be int, got {value!r}")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{field} must be int, got {value!r}") from exc
    if not math.isfinite(out):
        raise ConfigError(f"{field} must be finite, got {value!r}")
    if not out.is_integer():
        raise ConfigError(f"{field} must be an integer value, got {value!r}")
    return int(out)


def validate_optional_finite_float(config: Mapping[str, Any], key: str, field: str) -> None:
    if key in config:
        _as_float(config[key], field)


def validate_optional_nonnegative_float(config: Mapping[str, Any], key: str, field: str) -> None:
    if key in config and _as_float(config[key], field) < 0:
        raise ConfigError(f"{field} must be >= 0")


def validate_optional_positive_float(config: Mapping[str, Any], key: str, field: str) -> None:
    if key in config and _as_float(config[key], field) <= 0:
        raise ConfigError(f"{field} must be > 0")


def validate_optional_probability(config: Mapping[str, Any], key: str, field: str) -> None:
    if key in config:
        val = _as_float(config[key], field)
        if not (0 <= val <= 1):
            raise ConfigError(f"{field} must be in [0, 1]")


def validate_optional_positive_int(config: Mapping[str, Any], key: str, field: str) -> None:
    if key in config and _as_int(config[key], field) <= 0:
        raise ConfigError(f"{field} must be > 0")


def validate_optional_nonnegative_int(config: Mapping[str, Any], key: str, field: str) -> None:
    if key in config and _as_int(config[key], field) < 0:
        raise ConfigError(f"{field} must be >= 0")


def validate_optional_ordered_pair(
    config: Mapping[str, Any],
    min_key: str,
    max_key: str,
    min_field: str,
    max_field: str,
) -> None:
    if min_key in config and max_key in config:
        min_val = _as_float(config[min_key], min_field)
        max_val = _as_float(config[max_key], max_field)
        if min_val > max_val:
            raise ConfigError(f"{min_field} must be <= {max_field}")


def validate_strategy_base(config: Mapping[str, Any]) -> None:
    """Minimal base-config shape check."""
    require_keys(config, ("strategy", "version"), where="strategy base config")


def validate_strategy_grid(config: Mapping[str, Any]) -> None:
    """Minimal grid-config shape check."""
    require_keys(config, ("strategy", "base_config"), where="strategy grid config")


def validate_pa_buy_sell_close_trend_config(config: Mapping[str, Any]) -> None:
    """Validate ``pa_buy_sell_close_trend`` runtime config."""
    strategy = config.get("strategy")
    if strategy != "pa_buy_sell_close_trend":
        raise ConfigError(f"strategy must be pa_buy_sell_close_trend, got {strategy!r}")

    if "family" in config and config["family"] != "pa":
        raise ConfigError("family must be pa when present")

    if config.get("required_feature_set") not in (None, "pa_core_v1", "pa_core_v2"):
        raise ConfigError("required_feature_set must be pa_core_v1 or pa_core_v2")

    sig = config.get("signal")
    if not isinstance(sig, Mapping):
        raise ConfigError("signal section required")

    side = sig.get("side", "long_only")
    if side != "long_only":
        raise ConfigError(f"signal.side must be long_only, got {side!r}")

    es = _as_int(sig.get("entry_start_minute"), "signal.entry_start_minute")
    ee = _as_int(sig.get("entry_end_minute"), "signal.entry_end_minute")
    if not (0 <= es < ee <= 389):
        raise ConfigError("entry window must satisfy 0 <= entry_start < entry_end <= 389")

    body_min = _as_float(sig.get("body_pct_min", 0), "signal.body_pct_min")
    if body_min < 0:
        raise ConfigError("signal.body_pct_min must be >= 0")

    cp_min = _as_float(sig.get("close_position_min", 0), "signal.close_position_min")
    if not (0 <= cp_min <= 1):
        raise ConfigError("signal.close_position_min must be in [0, 1]")

    _as_float(sig.get("trend_slope_min", 0), "signal.trend_slope_min")
    _as_float(sig.get("close_vs_mean_min", 0), "signal.close_vs_mean_min")
    parse_bool_like(sig.get("require_vwap_side", False), "signal.require_vwap_side")
    parse_bool_like(sig.get("require_close_above_vwap", False), "signal.require_close_above_vwap")
    parse_bool_like(
        sig.get("require_above_rolling_high_20", False),
        "signal.require_above_rolling_high_20",
    )
    validate_optional_nonnegative_float(sig, "max_vwap_dist_pct", "signal.max_vwap_dist_pct")
    validate_optional_positive_float(sig, "min_rel_volume_20", "signal.min_rel_volume_20")
    validate_optional_nonnegative_float(sig, "min_range_mean_mult", "signal.min_range_mean_mult")
    validate_optional_nonnegative_float(sig, "max_range_mean_mult", "signal.max_range_mean_mult")
    validate_optional_ordered_pair(
        sig,
        "min_range_mean_mult",
        "max_range_mean_mult",
        "signal.min_range_mean_mult",
        "signal.max_range_mean_mult",
    )

    score_mode = sig.get("score_mode", "simple_pa_v1")
    if score_mode != "simple_pa_v1":
        raise ConfigError(f"signal.score_mode must be simple_pa_v1 in Phase 6, got {score_mode!r}")

    risk = config.get("risk")
    if not isinstance(risk, Mapping):
        raise ConfigError("risk section required")

    stop_mode = risk.get("stop_mode", "signal_low")
    if stop_mode not in (
        "signal_low",
        "rolling_low",
        "rolling_low_20",
        "atr_buffer",
        "vwap_atr_buffer",
    ):
        raise ConfigError(f"risk.stop_mode invalid: {stop_mode!r}")

    if risk.get("target_mode", "fixed_r") != "fixed_r":
        raise ConfigError("risk.target_mode must be fixed_r")

    target_r = _as_float(risk.get("target_r"), "risk.target_r")
    if target_r <= 0:
        raise ConfigError("risk.target_r must be > 0")

    atr_mult = _as_float(risk.get("atr_buffer_mult", 0), "risk.atr_buffer_mult")
    if atr_mult < 0:
        raise ConfigError("risk.atr_buffer_mult must be >= 0")

    if "min_risk_per_share" in risk:
        if _as_float(risk["min_risk_per_share"], "risk.min_risk_per_share") < 0:
            raise ConfigError("risk.min_risk_per_share must be >= 0")

    if "max_trades_per_day" in risk:
        if _as_int(risk["max_trades_per_day"], "risk.max_trades_per_day") <= 0:
            raise ConfigError("risk.max_trades_per_day must be > 0")

    backtest = config.get("backtest")
    if isinstance(backtest, Mapping):
        if "quantity" in backtest:
            if _as_float(backtest["quantity"], "backtest.quantity") <= 0:
                raise ConfigError("backtest.quantity must be > 0")
        if "eod_exit_minute" in backtest:
            eod = _as_int(backtest["eod_exit_minute"], "backtest.eod_exit_minute")
            if not (0 <= eod <= 389):
                raise ConfigError("backtest.eod_exit_minute must be in 0..389")
        if "max_hold_minutes" in backtest:
            if _as_int(backtest["max_hold_minutes"], "backtest.max_hold_minutes") <= 0:
                raise ConfigError("backtest.max_hold_minutes must be > 0")


def validate_long_only_strategy_base(
    config: Mapping[str, Any],
    *,
    strategy_name: str,
    family: str,
    required_feature_set: str | tuple[str, ...],
    allowed_stop_modes: tuple[str, ...],
) -> None:
    """Shared long-only MVP config checks for Phase 13 strategies."""
    if config.get("strategy") != strategy_name:
        raise ConfigError(f"strategy must be {strategy_name}, got {config.get('strategy')!r}")
    if "family" in config and config["family"] != family:
        raise ConfigError(f"family must be {family} when present")
    rfs = config.get("required_feature_set")
    allowed_feature_sets = (
        (required_feature_set,) if isinstance(required_feature_set, str) else required_feature_set
    )
    if rfs not in (None, *allowed_feature_sets):
        joined = " or ".join(allowed_feature_sets)
        raise ConfigError(f"required_feature_set must be {joined}")

    sig = config.get("signal")
    if not isinstance(sig, Mapping):
        raise ConfigError("signal section required")
    if sig.get("side", "long_only") != "long_only":
        raise ConfigError("signal.side must be long_only")

    es = _as_int(sig.get("entry_start_minute"), "signal.entry_start_minute")
    ee = _as_int(sig.get("entry_end_minute"), "signal.entry_end_minute")
    if not (0 <= es < ee <= 389):
        raise ConfigError("entry window must satisfy 0 <= entry_start < entry_end <= 389")

    risk = config.get("risk")
    if not isinstance(risk, Mapping):
        raise ConfigError("risk section required")
    stop_mode = str(risk.get("stop_mode", "signal_low"))
    if stop_mode not in allowed_stop_modes:
        raise ConfigError(f"risk.stop_mode invalid: {stop_mode!r}")
    if risk.get("target_mode", "fixed_r") != "fixed_r":
        raise ConfigError("risk.target_mode must be fixed_r")
    target_r = _as_float(risk.get("target_r"), "risk.target_r")
    if target_r <= 0:
        raise ConfigError("risk.target_r must be > 0")
    atr_mult = _as_float(risk.get("atr_buffer_mult", 0), "risk.atr_buffer_mult")
    if atr_mult < 0:
        raise ConfigError("risk.atr_buffer_mult must be >= 0")
    if "max_trades_per_day" in risk:
        if _as_int(risk["max_trades_per_day"], "risk.max_trades_per_day") <= 0:
            raise ConfigError("risk.max_trades_per_day must be > 0")

    backtest = config.get("backtest")
    if isinstance(backtest, Mapping) and "eod_exit_minute" in backtest:
        eod = _as_int(backtest["eod_exit_minute"], "backtest.eod_exit_minute")
        if not (0 <= eod <= 389):
            raise ConfigError("backtest.eod_exit_minute must be in 0..389")
    if isinstance(backtest, Mapping) and "max_hold_minutes" in backtest:
        if _as_int(backtest["max_hold_minutes"], "backtest.max_hold_minutes") <= 0:
            raise ConfigError("backtest.max_hold_minutes must be > 0")


def validate_strategy_config_for_name(
    strategy_name: str,
    config: Mapping[str, Any],
    *,
    defn: StrategyDef | None = None,
) -> None:
    """Dispatch validation to strategy-specific or StrategyDef hook."""
    if defn is not None and defn.validate_config is not None:
        defn.validate_config(config)
        return
    if strategy_name == "pa_buy_sell_close_trend":
        validate_pa_buy_sell_close_trend_config(config)
        return
    raise ConfigError(f"no validator for strategy {strategy_name!r}")
