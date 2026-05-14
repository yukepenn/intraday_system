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

CANONICAL_GROUP_ORDER: tuple[str, ...] = (
    "vwap",
    "orb",
    "volatility",
    "price_action",
    "volume",
    "regime",
)

ALLOWED_OUTPUTS: dict[str, frozenset[str]] = {
    "vwap": frozenset({"vwap", "vwap_dist", "vwap_dist_pct", "vwap_side"}),
    "orb": frozenset({"orb_high", "orb_low", "orb_mid", "orb_range"}),
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
    for group in CANONICAL_GROUP_ORDER:
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
