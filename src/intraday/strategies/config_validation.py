"""Strategy config validation."""

from __future__ import annotations

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
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{field} must be numeric, got {value!r}") from exc


def _as_int(value: Any, field: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{field} must be int, got {value!r}") from exc


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

    if config.get("required_feature_set") not in (None, "pa_core_v1"):
        raise ConfigError("required_feature_set must be pa_core_v1")

    sig = config.get("signal")
    if not isinstance(sig, Mapping):
        raise ConfigError("signal section required")

    side = sig.get("side", "long_only")
    if side != "long_only":
        raise ConfigError(f"signal.side must be long_only, got {side!r}")

    es = _as_int(sig.get("entry_start_minute"), "signal.entry_start_minute")
    ee = _as_int(sig.get("entry_end_minute"), "signal.entry_end_minute")
    if not (0 <= es <= ee <= 389):
        raise ConfigError("entry window must satisfy 0 <= entry_start <= entry_end <= 389")

    body_min = _as_float(sig.get("body_pct_min", 0), "signal.body_pct_min")
    if body_min < 0:
        raise ConfigError("signal.body_pct_min must be >= 0")

    cp_min = _as_float(sig.get("close_position_min", 0), "signal.close_position_min")
    if not (0 <= cp_min <= 1):
        raise ConfigError("signal.close_position_min must be in [0, 1]")

    _as_float(sig.get("trend_slope_min", 0), "signal.trend_slope_min")
    _as_float(sig.get("close_vs_mean_min", 0), "signal.close_vs_mean_min")
    parse_bool_like(sig.get("require_vwap_side", False), "signal.require_vwap_side")

    score_mode = sig.get("score_mode", "simple_pa_v1")
    if score_mode != "simple_pa_v1":
        raise ConfigError(f"signal.score_mode must be simple_pa_v1 in Phase 6, got {score_mode!r}")

    risk = config.get("risk")
    if not isinstance(risk, Mapping):
        raise ConfigError("risk section required")

    stop_mode = risk.get("stop_mode", "signal_low")
    if stop_mode not in ("signal_low", "rolling_low", "atr_buffer"):
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


def validate_long_only_strategy_base(
    config: Mapping[str, Any],
    *,
    strategy_name: str,
    family: str,
    required_feature_set: str,
    allowed_stop_modes: tuple[str, ...],
) -> None:
    """Shared long-only MVP config checks for Phase 13 strategies."""
    if config.get("strategy") != strategy_name:
        raise ConfigError(f"strategy must be {strategy_name}, got {config.get('strategy')!r}")
    if "family" in config and config["family"] != family:
        raise ConfigError(f"family must be {family} when present")
    rfs = config.get("required_feature_set")
    if rfs not in (None, required_feature_set):
        raise ConfigError(f"required_feature_set must be {required_feature_set}")

    sig = config.get("signal")
    if not isinstance(sig, Mapping):
        raise ConfigError("signal section required")
    if sig.get("side", "long_only") != "long_only":
        raise ConfigError("signal.side must be long_only")

    es = _as_int(sig.get("entry_start_minute"), "signal.entry_start_minute")
    ee = _as_int(sig.get("entry_end_minute"), "signal.entry_end_minute")
    if not (0 <= es <= ee <= 389):
        raise ConfigError("entry window must satisfy 0 <= entry_start <= entry_end <= 389")

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
