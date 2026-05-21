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

    from intraday.features.kernels import brooks as brooks_k
    from intraday.features.kernels import indicators as ind_k
    from intraday.features.kernels import levels as levels_k
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
            outputs=("vwap", "vwap_dist", "vwap_dist_pct", "vwap_side", "vwap_slope_5"),
            compute_reference=vwap_k.compute_vwap_group,
        )
    )
    register_feature(
        FeatureDef(
            name="orb",
            version="v1",
            required_inputs=("open", "high", "low", "close", "minute", "session_id"),
            outputs=("orb_high", "orb_low", "orb_mid", "orb_range", "orb_width_pct"),
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
    register_feature(
        FeatureDef(
            name="levels",
            version="v1",
            required_inputs=("open", "high", "low", "close", "session_id"),
            outputs=(
                "prior_session_open",
                "prior_session_high",
                "prior_session_low",
                "prior_session_close",
                "open_gap_pct",
                "dist_to_prior_high_pct",
                "dist_to_prior_low_pct",
                "dist_to_prior_close_pct",
            ),
            compute_reference=levels_k.compute_levels_group,
        )
    )
    register_feature(
        FeatureDef(
            name="indicators",
            version="v1",
            required_inputs=("high", "low", "close", "session_id"),
            outputs=("cci", "stoch_k", "stoch_d"),
            compute_reference=ind_k.compute_indicators_group,
        )
    )
    register_feature(
        FeatureDef(
            name="pa_brooks_bar_core",
            version="v1",
            required_inputs=("open", "high", "low", "close", "session_id"),
            outputs=(
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
            ),
            compute_reference=brooks_k.compute_pa_brooks_bar_core_group,
        )
    )
    register_feature(
        FeatureDef(
            name="pa_brooks_regime_core",
            version="v1",
            required_inputs=("high", "low", "close", "session_id"),
            outputs=(
                "pa_always_in_side",
                "pa_strong_bull_bo_score",
                "pa_strong_bear_bo_score",
                "pa_tight_bull_channel_score",
                "pa_tight_bear_channel_score",
                "pa_broad_bull_channel_score",
                "pa_broad_bear_channel_score",
                "pa_trading_range_score",
                "pa_late_trend_score",
            ),
            compute_reference=brooks_k.compute_pa_brooks_regime_core_group,
        )
    )
    register_feature(
        FeatureDef(
            name="pa_brooks_swing_core",
            version="v1",
            required_inputs=("high", "low", "close", "session_id"),
            outputs=(
                "pa_leg_direction",
                "pa_pullback_bar_count",
                "pa_pullback_depth_atr",
                "pa_two_leg_pullback_down",
                "pa_two_leg_pullback_up",
                "pa_second_entry_buy_proxy",
                "pa_second_entry_sell_proxy",
            ),
            compute_reference=brooks_k.compute_pa_brooks_swing_core_group,
        )
    )
    register_feature(
        FeatureDef(
            name="pa_brooks_range_core",
            version="v1",
            required_inputs=("high", "low", "close", "session_id"),
            outputs=(
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
            ),
            compute_reference=brooks_k.compute_pa_brooks_range_core_group,
        )
    )
    _BUILTIN_REGISTERED = True
