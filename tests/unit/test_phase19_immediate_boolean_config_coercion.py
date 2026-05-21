"""Phase19 immediate-fix boolean config coercion tests.

Validates that strategy runtime boolean reads agree with validation-time
``parse_bool_like`` semantics, and that no strategy runtime still uses
``bool(sig.get(...))`` / ``bool(config.get(...))`` patterns (which silently
coerce strings like ``"false"`` to ``True``).
"""

from __future__ import annotations

import copy
import re
from pathlib import Path

import numpy as np
import pytest
from intraday.core.config import load_yaml
from intraday.core.errors import ConfigError
from intraday.core.types import Side
from intraday.strategies.pa.brooks_common import brooks_bool
from intraday.strategies.registry import get_strategy, register_builtin_strategies

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns

REPO = Path(__file__).resolve().parents[2]

PHASE19B_STRATEGIES = (
    "pa_second_entry_pullback",
    "pa_trading_range_bls_hs",
    "pa_failed_breakout_trap",
    "pa_opening_reversal_sr",
    "pa_breakout_pullback_continuation",
    "pa_tight_channel_pullback",
    "pa_broad_channel_zone",
)


# --- brooks_bool semantics -------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (True, True),
        (False, False),
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("1", True),
        ("0", False),
        ("yes", True),
        ("no", False),
        (1, True),
        (0, False),
    ),
)
def test_brooks_bool_strict_semantics(value: object, expected: bool) -> None:
    assert brooks_bool({"flag": value}, "flag", False) is expected
    assert brooks_bool({"flag": value}, "flag", True) is expected


def test_brooks_bool_default_when_missing() -> None:
    assert brooks_bool({}, "flag", True) is True
    assert brooks_bool({}, "flag", False) is False


def test_brooks_bool_rejects_invalid_string() -> None:
    with pytest.raises(ConfigError):
        brooks_bool({"flag": "definitely_not_a_bool"}, "flag", False)


def test_brooks_bool_rejects_non_zero_one_int() -> None:
    with pytest.raises(ConfigError):
        brooks_bool({"flag": 2}, "flag", False)


# --- static scan -----------------------------------------------------------


def test_no_strategy_runtime_uses_bool_sig_get() -> None:
    """Strategy source must not coerce booleans via ``bool(sig.get(...))``."""
    src_root = REPO / "src" / "intraday" / "strategies"
    pattern = re.compile(r"bool\(\s*sig\.get\(|bool\(\s*config\.get\(")
    offenders: list[str] = []
    for path in src_root.rglob("*.py"):
        if "setup_codes.py" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        if pattern.search(text):
            offenders.append(str(path))
    assert offenders == [], (
        "found bool(sig.get(...)) / bool(config.get(...)) patterns; "
        f"use brooks_bool / parse_bool_like instead: {offenders}"
    )


# --- runtime-vs-validation parity -----------------------------------------


def _bars():
    return make_bar_matrix(
        [100, 101, 102, 103, 104, 105],
        [101, 102, 103, 104, 105, 106],
        [99, 100, 101, 102, 103, 104],
        [100.5, 101.5, 102.5, 103.5, 104.5, 105.5],
        minute=[0, 1, 2, 3, 4, 5],
    )


def _phase19b_features():
    cols: dict[str, np.ndarray | float] = {
        "pa_always_in_side": [0, 1, 1, -1, -1, 0],
        "pa_pullback_bar_count": 2,
        "pa_pullback_depth_atr": 0.4,
        "pa_two_leg_pullback_down": [0, 1, 0, 0, 0, 0],
        "pa_two_leg_pullback_up": [0, 0, 0, 1, 0, 0],
        "pa_second_entry_buy_proxy": [0, 1, 0, 0, 0, 0],
        "pa_second_entry_sell_proxy": [0, 0, 0, 1, 0, 0],
        "bull_signal_bar": [0, 1, 0, 0, 1, 0],
        "bear_signal_bar": [0, 0, 0, 1, 0, 0],
        "strong_bull_close": [0, 1, 0, 0, 1, 0],
        "strong_bear_close": [0, 0, 0, 1, 0, 0],
        "pa_trading_range_score_20": 0.2,
        "pa_strong_bull_bo_score_20": [0.8, 0.1, 0.1, 0.1, 0.1, 0.1],
        "pa_strong_bear_bo_score_20": [0.1, 0.1, 0.8, 0.1, 0.1, 0.1],
        "pa_tight_bull_channel_score_20": [0, 0.8, 0, 0, 0, 0],
        "pa_tight_bear_channel_score_20": [0, 0, 0, 0.8, 0, 0],
        "pa_broad_bull_channel_score_20": [0, 0.6, 0, 0, 0, 0],
        "pa_broad_bear_channel_score_20": [0, 0, 0, 0.6, 0, 0],
        "pa_late_trend_score_20": 0.1,
        "bull_micro_channel_3": [0, 1, 0, 0, 0, 0],
        "bear_micro_channel_3": [0, 0, 0, 1, 0, 0],
    }
    for w in (30, 60, 90):
        cols[f"pa_tr_width_atr_{w}"] = 1.2
        cols[f"pa_close_in_lower_third_{w}"] = [0, 1, 0, 0, 0, 0]
        cols[f"pa_close_in_upper_third_{w}"] = [0, 0, 0, 1, 0, 0]
        cols[f"pa_range_breakout_down_{w}"] = [1, 0, 0, 0, 0, 0]
        cols[f"pa_range_breakout_up_{w}"] = [0, 0, 1, 0, 0, 0]
        cols[f"pa_close_back_inside_range_{w}"] = [0, 1, 0, 1, 0, 0]
        cols[f"pa_tr_lower_third_{w}"] = 100.0
        cols[f"pa_tr_upper_third_{w}"] = 105.0
        cols[f"pa_tr_low_{w}"] = 99.0
        cols[f"pa_tr_high_{w}"] = 106.0
    return make_feature_matrix_with_columns(6, cols)


def _phase19b_base_cfg(strategy: str) -> dict:
    cfg = copy.deepcopy(
        load_yaml(REPO / "configs" / "strategies" / "base" / "phase19" / f"{strategy}.yaml")
    )
    cfg["signal"]["side_mode"] = "both"
    cfg["signal"]["entry_start_minute"] = 0
    cfg["signal"]["entry_end_minute"] = 5
    if strategy == "pa_failed_breakout_trap":
        cfg["signal"]["fail_back_inside_bars"] = 1
    return cfg


@pytest.mark.parametrize("strategy", PHASE19B_STRATEGIES)
@pytest.mark.parametrize(
    ("falsy", "truthy"),
    (
        (False, True),
        ("false", "true"),
        (0, 1),
    ),
)
def test_phase19b_boolean_runtime_matches_validation(
    strategy: str, falsy: object, truthy: object
) -> None:
    register_builtin_strategies()
    bars = _bars()
    features = _phase19b_features()
    defn = get_strategy(strategy)

    cfg_false = _phase19b_base_cfg(strategy)
    cfg_true = _phase19b_base_cfg(strategy)
    bool_keys: list[str] = []
    for candidate in (
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
        if candidate in cfg_false["signal"]:
            bool_keys.append(candidate)
    if not bool_keys:
        pytest.skip(f"{strategy} exposes no boolean signal config flags")
    for key in bool_keys:
        cfg_false["signal"][key] = falsy
        cfg_true["signal"][key] = truthy

    sig_false = defn.generate_reference(bars, features, cfg_false)
    sig_true = defn.generate_reference(bars, features, cfg_true)
    # Different boolean interpretations must yield different signal hashes;
    # any "false"-string falsely coerced to True would otherwise alias to True.
    if falsy != truthy:
        assert (
            sig_false.signal_hash != sig_true.signal_hash
        ), f"{strategy} runtime boolean coercion did not honor {falsy!r} vs {truthy!r}"


@pytest.mark.parametrize("strategy", PHASE19B_STRATEGIES)
def test_phase19b_invalid_boolean_raises(strategy: str) -> None:
    register_builtin_strategies()
    cfg = _phase19b_base_cfg(strategy)
    bool_keys = [
        k
        for k in (
            "require_second_entry",
            "require_signal_bar",
            "require_failed_breakout",
            "require_reversal_bar",
            "require_always_in_with_side",
            "require_micro_channel",
        )
        if k in cfg["signal"]
    ]
    if not bool_keys:
        pytest.skip(f"{strategy} exposes no boolean signal config flags")
    cfg["signal"][bool_keys[0]] = "definitely_not_a_bool"
    defn = get_strategy(strategy)
    with pytest.raises(ConfigError):
        defn.generate_reference(_bars(), _phase19b_features(), cfg)


def test_invalid_boolean_at_validation_time_raises() -> None:
    """Sanity check: validation itself still rejects bad booleans."""
    register_builtin_strategies()
    from intraday.strategies.loader import validate_strategy_config

    cfg = _phase19b_base_cfg("pa_second_entry_pullback")
    cfg["signal"]["require_second_entry"] = "definitely_not_a_bool"
    with pytest.raises(ConfigError):
        validate_strategy_config("pa_second_entry_pullback", cfg)


def test_short_only_filters_long_entries_with_strict_booleans() -> None:
    """End-to-end sanity that side_mode filtering still functions."""
    register_builtin_strategies()
    cfg = _phase19b_base_cfg("pa_second_entry_pullback")
    cfg["signal"]["side_mode"] = "short_only"
    sig = get_strategy("pa_second_entry_pullback").generate_reference(
        _bars(), _phase19b_features(), cfg
    )
    assert int(Side.LONG) not in set(sig.side[sig.entry])
