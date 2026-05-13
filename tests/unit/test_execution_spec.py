"""ExecutionSpec validation and YAML load."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from intraday.core.config import load_yaml
from intraday.core.errors import ConfigError
from intraday.execution.spec import ExecutionSpec, load_execution_spec

REPO = Path(__file__).resolve().parents[2]
DEFAULT_YAML = REPO / "configs" / "execution" / "intraday_default.yaml"


def test_default_yaml_loads() -> None:
    spec = load_execution_spec(DEFAULT_YAML)
    assert spec.entry_timing == "next_open"
    assert spec.same_bar_policy == "stop_first"
    assert spec.semantics_version == "execution_v1"


def test_from_config_validates_same_bar_policy() -> None:
    raw = load_yaml(DEFAULT_YAML)
    bad = copy.deepcopy(raw)
    bad["same_bar_policy"] = "both_first"
    with pytest.raises(ConfigError, match="same_bar_policy"):
        ExecutionSpec.from_config(bad)


def test_from_config_validates_entry_timing() -> None:
    raw = load_yaml(DEFAULT_YAML)
    bad = copy.deepcopy(raw)
    bad["entry_timing"] = "this_bar"
    with pytest.raises(ConfigError, match="entry_timing"):
        ExecutionSpec.from_config(bad)


def test_negative_slippage_raises() -> None:
    raw = load_yaml(DEFAULT_YAML)
    bad = copy.deepcopy(raw)
    bad["slippage_per_share"] = -0.01
    with pytest.raises(ConfigError, match="slippage"):
        ExecutionSpec.from_config(bad)


def test_negative_commission_raises() -> None:
    raw = load_yaml(DEFAULT_YAML)
    bad = copy.deepcopy(raw)
    bad["commission_per_trade"] = -1.0
    with pytest.raises(ConfigError, match="commission"):
        ExecutionSpec.from_config(bad)


def test_negative_min_risk_raises() -> None:
    raw = load_yaml(DEFAULT_YAML)
    bad = copy.deepcopy(raw)
    bad["min_risk_per_share"] = -0.01
    with pytest.raises(ConfigError, match="min_risk"):
        ExecutionSpec.from_config(bad)


def test_eod_minute_bounds() -> None:
    raw = load_yaml(DEFAULT_YAML)
    bad = copy.deepcopy(raw)
    bad["eod_exit_minute"] = 390
    with pytest.raises(ConfigError, match="eod_exit_minute"):
        ExecutionSpec.from_config(bad)


def test_max_hold_default_zero_raises() -> None:
    raw = load_yaml(DEFAULT_YAML)
    bad = copy.deepcopy(raw)
    bad["max_hold_bars_default"] = 0
    with pytest.raises(ConfigError, match="max_hold_bars_default"):
        ExecutionSpec.from_config(bad)


def test_to_dict_roundtrip_keys() -> None:
    spec = load_execution_spec(DEFAULT_YAML)
    d = spec.to_dict()
    assert d["entry_timing"] == "next_open"
    spec2 = ExecutionSpec.from_config(d)
    assert spec2 == spec


def test_allow_short_string_false() -> None:
    raw = load_yaml(DEFAULT_YAML)
    mod = copy.deepcopy(raw)
    mod["allow_short"] = "false"
    spec = ExecutionSpec.from_config(mod)
    assert spec.allow_short is False
