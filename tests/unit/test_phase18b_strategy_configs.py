"""Phase18B strategy v2 config validation and synthetic generation."""

from __future__ import annotations

import copy

import pytest
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.features.engine import build_feature_matrix
from intraday.features.specs import load_feature_config
from intraday.strategies.loader import load_strategy_config, validate_strategy_config
from intraday.strategies.registry import get_strategy, register_builtin_strategies

from tests.helpers.bars import make_bar_matrix

STRATEGIES = (
    "pa_buy_sell_close_trend",
    "orb_continuation",
    "orb_retest_continuation",
    "failed_orb",
    "gap_acceptance_failure",
    "vwap_trend_pullback",
    "vwap_reclaim_reject",
    "prior_day_level_trap",
    "cci_extreme_snapback",
    "stochastic_oversold_cross",
)

FEATURE_BY_STRATEGY = {
    "pa_buy_sell_close_trend": "configs/features/pa_core_v2.yaml",
    "orb_continuation": "configs/features/opening_core_v2.yaml",
    "orb_retest_continuation": "configs/features/opening_core_v2.yaml",
    "failed_orb": "configs/features/opening_core_v2.yaml",
    "gap_acceptance_failure": "configs/features/gap_level_core_v2.yaml",
    "vwap_trend_pullback": "configs/features/vwap_level_core_v2.yaml",
    "vwap_reclaim_reject": "configs/features/vwap_level_core_v2.yaml",
    "prior_day_level_trap": "configs/features/gap_level_core_v2.yaml",
    "cci_extreme_snapback": "configs/features/indicator_core_v2.yaml",
    "stochastic_oversold_cross": "configs/features/indicator_core_v2.yaml",
}


def _v2_config(strategy: str) -> dict:
    return load_strategy_config(
        repo_root() / f"configs/strategies/base/phase18b/{strategy}_v2.yaml"
    )


def _set_path(config: dict, dotted: str, value: object) -> dict:
    out = copy.deepcopy(config)
    cursor = out
    parts = dotted.split(".")
    for part in parts[:-1]:
        cursor = cursor[part]
    cursor[parts[-1]] = value
    return out


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_phase18b_v1_and_v2_strategy_configs_validate(strategy: str) -> None:
    validate_strategy_config(
        strategy, load_strategy_config(repo_root() / f"configs/strategies/base/{strategy}.yaml")
    )
    validate_strategy_config(strategy, _v2_config(strategy))


@pytest.mark.parametrize(
    ("strategy", "field", "bad_value"),
    (
        ("pa_buy_sell_close_trend", "signal.max_vwap_dist_pct", -0.01),
        ("orb_continuation", "signal.breakout_buffer_atr", -0.01),
        ("orb_retest_continuation", "signal.max_retest_depth_atr", -0.01),
        ("failed_orb", "signal.max_breach_depth_atr", -0.01),
        ("gap_acceptance_failure", "signal.reclaim_mode", "prior_high"),
        ("vwap_trend_pullback", "signal.max_close_vwap_dist_atr", -0.01),
        ("vwap_reclaim_reject", "signal.below_lookback_bars", 0),
        ("prior_day_level_trap", "signal.level_type", "bogus"),
        ("cci_extreme_snapback", "signal.max_vwap_dist_pct", -0.01),
        ("stochastic_oversold_cross", "signal.min_k_d_spread_after_cross", -0.01),
    ),
)
def test_phase18b_invalid_v2_parameters_reject(
    strategy: str, field: str, bad_value: object
) -> None:
    with pytest.raises(ConfigError):
        validate_strategy_config(strategy, _set_path(_v2_config(strategy), field, bad_value))


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_phase18b_v2_signal_generation_runs_on_generic_features(strategy: str) -> None:
    register_builtin_strategies()
    cfg = _v2_config(strategy)
    # Keep generation focused on feature/strategy compatibility, not entry frequency.
    cfg["signal"]["entry_start_minute"] = 1
    cfg["signal"]["entry_end_minute"] = 59
    n_per_session = 60
    n = n_per_session * 2
    open_ = [100.0 + 0.03 * i for i in range(n)]
    high = [x + 0.8 for x in open_]
    low = [x - 0.8 for x in open_]
    close = [x + 0.2 for x in open_]
    session_id = [0] * n_per_session + [1] * n_per_session
    session_date = [20240102] * n_per_session + [20240103] * n_per_session
    minute = list(range(n_per_session)) * 2
    volume = [1000.0 + (i % 7) * 10.0 for i in range(n)]
    bars = make_bar_matrix(
        open_,
        high,
        low,
        close,
        session_id=session_id,
        session_date=session_date,
        minute=minute,
        volume=volume,
    )
    features = build_feature_matrix(
        bars,
        load_feature_config(repo_root() / FEATURE_BY_STRATEGY[strategy]),
        use_cache=False,
    )
    defn = get_strategy(strategy)
    signals = defn.generate_reference(bars, features, cfg)
    assert signals.entry.shape == (n,)


def test_phase18b_entry_window_requires_strict_order() -> None:
    cfg = _v2_config("orb_continuation")
    cfg["signal"]["entry_start_minute"] = cfg["signal"]["entry_end_minute"]
    with pytest.raises(ConfigError):
        validate_strategy_config("orb_continuation", cfg)
