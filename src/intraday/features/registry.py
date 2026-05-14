"""Feature registry: named ``FeatureDef`` kernels."""

from __future__ import annotations

from intraday.core.errors import ConfigError
from intraday.core.registry import Registry
from intraday.features.base import FeatureDef

FEATURE_REGISTRY: Registry[FeatureDef] = Registry("feature")

_BUILTIN_REGISTERED = False


def register_feature(defn: FeatureDef) -> None:
    """Register a feature group (duplicate name raises)."""
    try:
        FEATURE_REGISTRY.register(defn.name, defn)
    except KeyError as exc:
        raise ConfigError(str(exc)) from exc


def get_feature(name: str) -> FeatureDef:
    try:
        return FEATURE_REGISTRY.get(name)
    except KeyError as exc:
        raise ConfigError(f"unknown feature group: {name!r}") from exc


def list_features() -> list[str]:
    return FEATURE_REGISTRY.names()


def clear_feature_registry() -> None:
    """Clear all registrations (tests)."""
    global _BUILTIN_REGISTERED
    FEATURE_REGISTRY.clear()
    _BUILTIN_REGISTERED = False


def register_builtin_features() -> None:
    """Register built-in Phase 4 kernels (idempotent)."""
    global _BUILTIN_REGISTERED
    if _BUILTIN_REGISTERED:
        return

    from intraday.features.kernels import orb as orb_k
    from intraday.features.kernels import price_action as pa_k
    from intraday.features.kernels import regime as reg_k
    from intraday.features.kernels import volatility as vol_k
    from intraday.features.kernels import volume as volu_k
    from intraday.features.kernels import vwap as vwap_k

    register_feature(
        FeatureDef(
            name="vwap",
            version="v1",
            required_inputs=("open", "high", "low", "close", "volume", "session_id"),
            outputs=("vwap", "vwap_dist", "vwap_dist_pct", "vwap_side"),
            compute_reference=vwap_k.compute_vwap_group,
        )
    )
    register_feature(
        FeatureDef(
            name="orb",
            version="v1",
            required_inputs=("open", "high", "low", "close", "minute", "session_id"),
            outputs=("orb_high", "orb_low", "orb_mid", "orb_range"),
            compute_reference=orb_k.compute_orb_group,
        )
    )
    register_feature(
        FeatureDef(
            name="volatility",
            version="v1",
            required_inputs=("open", "high", "low", "close", "session_id"),
            outputs=("bar_range", "true_range", "atr_like", "range_mean"),
            compute_reference=vol_k.compute_volatility_group,
        )
    )
    register_feature(
        FeatureDef(
            name="price_action",
            version="v1",
            required_inputs=("open", "high", "low", "close", "session_id"),
            outputs=(
                "body_pct",
                "upper_wick_pct",
                "lower_wick_pct",
                "rolling_high",
                "rolling_low",
                "close_position_in_range",
            ),
            compute_reference=pa_k.compute_price_action_group,
        )
    )
    register_feature(
        FeatureDef(
            name="volume",
            version="v1",
            required_inputs=("volume", "session_id"),
            outputs=("volume_mean", "rel_volume"),
            compute_reference=volu_k.compute_volume_group,
        )
    )
    register_feature(
        FeatureDef(
            name="regime",
            version="v1",
            required_inputs=("close", "session_id"),
            outputs=("close_vs_rolling_mean", "trend_slope_like"),
            compute_reference=reg_k.compute_regime_group,
        )
    )
    _BUILTIN_REGISTERED = True
