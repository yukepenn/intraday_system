"""Feature config resolution, validation, and deterministic hashing."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any

from intraday.core.config import load_yaml
from intraday.core.errors import ConfigError
from intraday.core.hashing import hash_config

# Bumped when feature semantics or hashing envelope change.
FEATURE_ENGINE_SEMANTIC_VERSION = "feature_engine_mvp_v1"

LEGACY_GROUP_ORDER: tuple[str, ...] = (
    "vwap",
    "orb",
    "volatility",
    "price_action",
    "volume",
    "regime",
)

OPTIONAL_GROUP_ORDER: tuple[str, ...] = ("levels", "indicators")

BROOKS_GROUP_ORDER: tuple[str, ...] = (
    "pa_brooks_bar_core",
    "pa_brooks_regime_core",
    "pa_brooks_swing_core",
    "pa_brooks_range_core",
)

CANONICAL_GROUP_ORDER: tuple[str, ...] = (
    LEGACY_GROUP_ORDER + OPTIONAL_GROUP_ORDER + BROOKS_GROUP_ORDER
)

ALLOWED_OUTPUTS: dict[str, frozenset[str]] = {
    "vwap": frozenset({"vwap", "vwap_dist", "vwap_dist_pct", "vwap_side", "vwap_slope_5"}),
    "orb": frozenset({"orb_high", "orb_low", "orb_mid", "orb_range", "orb_width_pct"}),
    "volatility": frozenset({"bar_range", "true_range", "atr_like", "range_mean"}),
    "price_action": frozenset(
        {
            "body_pct",
            "upper_wick_pct",
            "lower_wick_pct",
            "rolling_high",
            "rolling_low",
            "close_position_in_range",
        }
    ),
    "volume": frozenset({"volume_mean", "rel_volume"}),
    "regime": frozenset({"close_vs_rolling_mean", "trend_slope_like"}),
    "levels": frozenset(
        {
            "prior_session_open",
            "prior_session_high",
            "prior_session_low",
            "prior_session_close",
            "open_gap_pct",
            "dist_to_prior_high_pct",
            "dist_to_prior_low_pct",
            "dist_to_prior_close_pct",
        }
    ),
    "indicators": frozenset({"cci", "stoch_k", "stoch_d"}),
    "pa_brooks_bar_core": frozenset(
        {
            "strong_bull_close",
            "strong_bear_close",
            "weak_bull_close",
            "weak_bear_close",
            "bull_signal_bar",
            "bear_signal_bar",
            "failed_bull_signal_bar",
            "failed_bear_signal_bar",
            "bull_micro_channel",
            "bear_micro_channel",
        }
    ),
    "pa_brooks_regime_core": frozenset(
        {
            "pa_always_in_side",
            "pa_strong_bull_bo_score",
            "pa_strong_bear_bo_score",
            "pa_tight_bull_channel_score",
            "pa_tight_bear_channel_score",
            "pa_broad_bull_channel_score",
            "pa_broad_bear_channel_score",
            "pa_trading_range_score",
            "pa_late_trend_score",
        }
    ),
    "pa_brooks_swing_core": frozenset(
        {
            "pa_leg_direction",
            "pa_pullback_bar_count",
            "pa_pullback_depth_atr",
            "pa_two_leg_pullback_down",
            "pa_two_leg_pullback_up",
            "pa_second_entry_buy_proxy",
            "pa_second_entry_sell_proxy",
        }
    ),
    "pa_brooks_range_core": frozenset(
        {
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
        }
    ),
}


def load_feature_config(path: Path | str) -> dict[str, Any]:
    """Load a feature YAML file (root must be a mapping)."""
    return load_yaml(path)


def _as_bool(v: Any, *, field: str) -> bool:
    if isinstance(v, bool):
        return v
    raise ConfigError(f"{field} must be a bool, got {type(v).__name__}")


def _positive_ints(seq: Any, *, field: str) -> list[int]:
    if seq is None:
        return []
    if isinstance(seq, int | float):
        seq = [seq]
    if not isinstance(seq, Sequence) or isinstance(seq, str | bytes):
        raise ConfigError(f"{field} must be a list of positive integers")
    out: list[int] = []
    for x in seq:
        xi = int(x)
        if xi <= 0:
            raise ConfigError(f"{field} must contain positive integers, got {xi!r}")
        out.append(xi)
    return out


def resolve_feature_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a JSON-serializable resolved config (used for hashing)."""
    if "feature_set_id" not in config:
        raise ConfigError("feature config missing required key: 'feature_set_id'")
    if "version" not in config:
        raise ConfigError("feature config missing required key: 'version'")
    if "features" not in config:
        raise ConfigError("feature config missing required key: 'features'")

    fsid = str(config["feature_set_id"])
    ver = str(config["version"])
    feats_raw = config["features"]
    if not isinstance(feats_raw, dict):
        raise ConfigError("'features' must be a mapping")

    engine = dict(config.get("engine") or {})
    engine.setdefault("mode", "reference")
    engine.setdefault("session_reset", True)
    engine.setdefault("dtype", "float64")
    if str(engine.get("mode")) != "reference":
        raise ConfigError("Phase 4 only supports engine.mode == 'reference'")
    if not _as_bool(engine.get("session_reset", True), field="engine.session_reset"):
        raise ConfigError("Phase 4 requires engine.session_reset == true")
    if str(engine.get("dtype")) != "float64":
        raise ConfigError("Phase 4 requires engine.dtype == 'float64'")

    resolved_features: dict[str, Any] = {}
    for group in LEGACY_GROUP_ORDER:
        if group not in feats_raw:
            resolved_features[group] = {"enabled": False}
            continue
        block = feats_raw[group]
        if not isinstance(block, dict):
            raise ConfigError(f"features.{group} must be a mapping")
        if not _as_bool(block.get("enabled", False), field=f"features.{group}.enabled"):
            resolved_features[group] = {"enabled": False}
            continue

        allowed = ALLOWED_OUTPUTS[group]
        outs = block.get("outputs")
        if not isinstance(outs, list) or not outs:
            raise ConfigError(f"features.{group}.outputs must be a non-empty list")
        outs_s = [str(o) for o in outs]
        if len(set(outs_s)) != len(outs_s):
            raise ConfigError(f"features.{group}.outputs contains duplicates: {outs_s!r}")
        unknown = [o for o in outs_s if o not in allowed]
        if unknown:
            raise ConfigError(f"features.{group}.outputs unknown: {unknown!r}")

        gcfg: dict[str, Any] = {"enabled": True, "outputs": outs_s}

        if group == "vwap":
            price = str(block.get("price", "hlc3"))
            if price not in ("hlc3", "close"):
                raise ConfigError(f"features.vwap.price unsupported: {price!r}")
            gcfg["price"] = price

        if group == "orb":
            if block.get("open_minutes") is None:
                raise ConfigError("features.orb.open_minutes is required when orb is enabled")
            gcfg["open_minutes"] = _positive_ints(
                block.get("open_minutes"), field="features.orb.open_minutes"
            )
            if not gcfg["open_minutes"]:
                raise ConfigError("features.orb.open_minutes must be non-empty when orb is enabled")

        if group == "volatility":
            gcfg["atr_like_windows"] = _positive_ints(
                block.get("atr_like_windows"), field="features.volatility.atr_like_windows"
            )
            gcfg["range_windows"] = _positive_ints(
                block.get("range_windows"), field="features.volatility.range_windows"
            )
            if "atr_like" in outs_s and not gcfg["atr_like_windows"]:
                raise ConfigError("atr_like outputs require features.volatility.atr_like_windows")
            if "range_mean" in outs_s and not gcfg["range_windows"]:
                raise ConfigError("range_mean outputs require features.volatility.range_windows")

        if group == "price_action":
            gcfg["rolling_windows"] = _positive_ints(
                block.get("rolling_windows"), field="features.price_action.rolling_windows"
            )
            need = [o for o in outs_s if o in ("rolling_high", "rolling_low")]
            if need and not gcfg["rolling_windows"]:
                raise ConfigError(f"{need} require features.price_action.rolling_windows")

        if group == "volume":
            gcfg["rolling_windows"] = _positive_ints(
                block.get("rolling_windows"), field="features.volume.rolling_windows"
            )
            if not gcfg["rolling_windows"]:
                raise ConfigError("volume group requires features.volume.rolling_windows")

        if group == "regime":
            gcfg["windows"] = _positive_ints(block.get("windows"), field="features.regime.windows")
            if not gcfg["windows"]:
                raise ConfigError("regime group requires features.regime.windows")

        resolved_features[group] = gcfg

    for group in OPTIONAL_GROUP_ORDER:
        if group not in feats_raw:
            continue
        block = feats_raw[group]
        if not isinstance(block, dict):
            raise ConfigError(f"features.{group} must be a mapping")
        if not _as_bool(block.get("enabled", False), field=f"features.{group}.enabled"):
            continue

        allowed = ALLOWED_OUTPUTS[group]
        outs = block.get("outputs")
        if not isinstance(outs, list) or not outs:
            raise ConfigError(f"features.{group}.outputs must be a non-empty list")
        outs_s = [str(o) for o in outs]
        if len(set(outs_s)) != len(outs_s):
            raise ConfigError(f"features.{group}.outputs contains duplicates: {outs_s!r}")
        unknown = [o for o in outs_s if o not in allowed]
        if unknown:
            raise ConfigError(f"features.{group}.outputs unknown: {unknown!r}")

        gcfg = {"enabled": True, "outputs": outs_s}
        if group == "indicators":
            gcfg["cci_windows"] = _positive_ints(
                block.get("cci_windows"), field="features.indicators.cci_windows"
            )
            gcfg["stochastic_windows"] = _positive_ints(
                block.get("stochastic_windows"),
                field="features.indicators.stochastic_windows",
            )
            gcfg["stochastic_smooth_windows"] = _positive_ints(
                block.get("stochastic_smooth_windows"),
                field="features.indicators.stochastic_smooth_windows",
            )
            if "cci" in outs_s and not gcfg["cci_windows"]:
                raise ConfigError("cci outputs require features.indicators.cci_windows")
            if ("stoch_k" in outs_s or "stoch_d" in outs_s) and not gcfg["stochastic_windows"]:
                raise ConfigError(
                    "stochastic outputs require features.indicators.stochastic_windows"
                )
            if "stoch_d" in outs_s and not gcfg["stochastic_smooth_windows"]:
                raise ConfigError(
                    "stoch_d outputs require features.indicators.stochastic_smooth_windows"
                )
        resolved_features[group] = gcfg

    for group in BROOKS_GROUP_ORDER:
        if group not in feats_raw:
            continue
        block = feats_raw[group]
        if not isinstance(block, dict):
            raise ConfigError(f"features.{group} must be a mapping")
        if not _as_bool(block.get("enabled", False), field=f"features.{group}.enabled"):
            continue

        allowed = ALLOWED_OUTPUTS[group]
        outs = block.get("outputs")
        if not isinstance(outs, list) or not outs:
            raise ConfigError(f"features.{group}.outputs must be a non-empty list")
        outs_s = [str(o) for o in outs]
        if len(set(outs_s)) != len(outs_s):
            raise ConfigError(f"features.{group}.outputs contains duplicates: {outs_s!r}")
        unknown = [o for o in outs_s if o not in allowed]
        if unknown:
            raise ConfigError(f"features.{group}.outputs unknown: {unknown!r}")

        gcfg = {"enabled": True, "outputs": outs_s}
        if group == "pa_brooks_bar_core":
            gcfg["micro_channel_lengths"] = _positive_ints(
                block.get("micro_channel_lengths", [3]),
                field="features.pa_brooks_bar_core.micro_channel_lengths",
            )
            gcfg["signal_window"] = int(block.get("signal_window", 5))
            if gcfg["signal_window"] <= 0:
                raise ConfigError("features.pa_brooks_bar_core.signal_window must be > 0")
            gcfg["min_signal_body_pct"] = float(block.get("min_signal_body_pct", 0.5))
        elif group == "pa_brooks_regime_core":
            gcfg["windows"] = _positive_ints(
                block.get("windows"), field="features.pa_brooks_regime_core.windows"
            )
            if not gcfg["windows"]:
                raise ConfigError("pa_brooks_regime_core requires windows")
        elif group == "pa_brooks_swing_core":
            gcfg["swing_window"] = int(block.get("swing_window", 5))
            if gcfg["swing_window"] <= 1:
                raise ConfigError("features.pa_brooks_swing_core.swing_window must be > 1")
            gcfg["atr_window"] = int(block.get("atr_window", 20))
            if gcfg["atr_window"] <= 0:
                raise ConfigError("features.pa_brooks_swing_core.atr_window must be > 0")
        elif group == "pa_brooks_range_core":
            gcfg["range_windows"] = _positive_ints(
                block.get("range_windows"), field="features.pa_brooks_range_core.range_windows"
            )
            if not gcfg["range_windows"]:
                raise ConfigError("pa_brooks_range_core requires range_windows")
            gcfg["atr_window"] = int(block.get("atr_window", 20))
            if gcfg["atr_window"] <= 0:
                raise ConfigError("features.pa_brooks_range_core.atr_window must be > 0")
            gcfg["back_inside_bars"] = int(block.get("back_inside_bars", 3))
            if gcfg["back_inside_bars"] <= 0:
                raise ConfigError("features.pa_brooks_range_core.back_inside_bars must be > 0")
        resolved_features[group] = gcfg

    for key in feats_raw:
        if key not in CANONICAL_GROUP_ORDER:
            raise ConfigError(f"unknown feature group: {key!r}")

    out: dict[str, Any] = {
        "feature_set_id": fsid,
        "version": ver,
        "engine": engine,
        "features": resolved_features,
    }
    if "description" in config:
        out["description"] = str(config["description"])
    return out


def expand_column_names(group: str, gcfg: Mapping[str, Any]) -> list[str]:
    """Deterministic output column names for an enabled feature group."""
    if not gcfg.get("enabled"):
        return []
    outputs: list[str] = list(gcfg["outputs"])
    names: list[str] = []

    if group == "vwap":
        for o in outputs:
            names.append(o)
        return names

    if group == "orb":
        for om in gcfg["open_minutes"]:
            suf = f"_{om}"
            for o in outputs:
                names.append(f"{o}{suf}")
        return names

    if group == "volatility":
        for o in outputs:
            if o == "bar_range":
                names.append("bar_range")
            elif o == "true_range":
                names.append("true_range")
            elif o == "atr_like":
                for w in gcfg["atr_like_windows"]:
                    names.append(f"atr_like_{w}")
            elif o == "range_mean":
                for w in gcfg["range_windows"]:
                    names.append(f"range_mean_{w}")
        return names

    if group == "price_action":
        for o in outputs:
            if o in ("body_pct", "upper_wick_pct", "lower_wick_pct", "close_position_in_range"):
                names.append(o)
            elif o == "rolling_high":
                for w in gcfg["rolling_windows"]:
                    names.append(f"rolling_high_{w}")
            elif o == "rolling_low":
                for w in gcfg["rolling_windows"]:
                    names.append(f"rolling_low_{w}")
        return names

    if group == "volume":
        for o in outputs:
            for w in gcfg["rolling_windows"]:
                names.append(f"{o}_{w}")
        return names

    if group == "regime":
        for o in outputs:
            for w in gcfg["windows"]:
                names.append(f"{o}_{w}")
        return names

    if group == "levels":
        for o in outputs:
            names.append(o)
        return names

    if group == "indicators":
        for o in outputs:
            if o == "cci":
                for w in gcfg["cci_windows"]:
                    names.append(f"cci_{w}")
            elif o == "stoch_k":
                for w in gcfg["stochastic_windows"]:
                    names.append(f"stoch_k_{w}")
            elif o == "stoch_d":
                for w in gcfg["stochastic_windows"]:
                    for sm in gcfg["stochastic_smooth_windows"]:
                        names.append(f"stoch_d_{w}_{sm}")
        return names

    if group == "pa_brooks_bar_core":
        for o in outputs:
            if o == "bull_micro_channel":
                for k in gcfg["micro_channel_lengths"]:
                    names.append(f"bull_micro_channel_{k}")
            elif o == "bear_micro_channel":
                for k in gcfg["micro_channel_lengths"]:
                    names.append(f"bear_micro_channel_{k}")
            else:
                names.append(o)
        return names

    if group == "pa_brooks_regime_core":
        for o in outputs:
            if o == "pa_always_in_side":
                names.append(o)
            else:
                for w in gcfg["windows"]:
                    names.append(f"{o}_{w}")
        return names

    if group == "pa_brooks_swing_core":
        for o in outputs:
            names.append(o)
        return names

    if group == "pa_brooks_range_core":
        for o in outputs:
            for w in gcfg["range_windows"]:
                names.append(f"{o}_{w}")
        return names

    raise ConfigError(f"expand_column_names: unknown group {group!r}")


def collect_all_column_names(resolved: Mapping[str, Any]) -> list[str]:
    feats = resolved["features"]
    ordered: list[str] = []
    seen: set[str] = set()
    for group in CANONICAL_GROUP_ORDER:
        if group not in feats:
            continue
        gcfg = feats[group]
        for c in expand_column_names(group, gcfg):
            if c in seen:
                raise ConfigError(f"duplicate feature column name: {c!r}")
            seen.add(c)
            ordered.append(c)
    return ordered


def hash_feature_config(resolved: Mapping[str, Any]) -> str:
    """Deterministic SHA-256 hex of resolved config + engine semantic version."""
    payload = {
        "feature_engine_semantic_version": FEATURE_ENGINE_SEMANTIC_VERSION,
        "resolved": deepcopy(dict(resolved)),
    }
    return hash_config(payload)


def feature_config_hash(feature_config: Mapping[str, Any]) -> str:
    """Stable hash of a feature config dict (resolved or raw after resolve)."""
    return hash_feature_config(resolve_feature_config(feature_config))
