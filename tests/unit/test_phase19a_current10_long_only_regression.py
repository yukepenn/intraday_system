"""Current-10 default long-only regression guard for Phase19A."""

from __future__ import annotations

from pathlib import Path

from intraday.core.config import load_yaml
from intraday.execution.spec import load_execution_spec
from intraday.strategies.contracts import SIDE_MODE_LONG_ONLY, normalize_side_mode

REPO = Path(__file__).resolve().parents[2]

CURRENT10_BASE_CONFIGS = (
    "pa_buy_sell_close_trend.yaml",
    "orb_continuation.yaml",
    "orb_retest_continuation.yaml",
    "failed_orb.yaml",
    "gap_acceptance_failure.yaml",
    "vwap_trend_pullback.yaml",
    "vwap_reclaim_reject.yaml",
    "prior_day_level_trap.yaml",
    "cci_extreme_snapback.yaml",
    "stochastic_oversold_cross.yaml",
)


def test_default_execution_config_remains_long_only() -> None:
    spec = load_execution_spec(REPO / "configs" / "execution" / "intraday_default.yaml")
    assert spec.allow_short is False


def test_current10_base_configs_remain_long_only() -> None:
    base = REPO / "configs" / "strategies" / "base"
    for name in CURRENT10_BASE_CONFIGS:
        cfg = load_yaml(base / name)
        assert normalize_side_mode(cfg["signal"]) == SIDE_MODE_LONG_ONLY


def test_current10_phase18b_configs_remain_long_only() -> None:
    base = REPO / "configs" / "strategies" / "base" / "phase18b"
    for name in CURRENT10_BASE_CONFIGS:
        cfg = load_yaml(base / name.replace(".yaml", "_v2.yaml"))
        assert normalize_side_mode(cfg["signal"]) == SIDE_MODE_LONG_ONLY
