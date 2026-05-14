"""Feature config validation and FeatureMatrix invariants."""

from __future__ import annotations

import copy

import numpy as np
import pytest
from intraday.core.arrays import FeatureMatrix
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.features.specs import load_feature_config, resolve_feature_config


def test_pa_core_yaml_loads() -> None:
    path = repo_root() / "configs/features/pa_core_v1.yaml"
    raw = load_feature_config(path)
    resolved = resolve_feature_config(raw)
    assert resolved["feature_set_id"] == "pa_core_v1"
    assert resolved["features"]["vwap"]["enabled"] is True


def test_missing_top_level_keys() -> None:
    with pytest.raises(ConfigError):
        resolve_feature_config({"version": "x", "features": {}})
    with pytest.raises(ConfigError):
        resolve_feature_config({"feature_set_id": "a", "features": {}})
    with pytest.raises(ConfigError):
        resolve_feature_config({"feature_set_id": "a", "version": "v"})


def test_unknown_feature_group() -> None:
    raw = {
        "feature_set_id": "t",
        "version": "v1",
        "features": {"vwap": {"enabled": False}, "bogus": {"enabled": True, "outputs": ["x"]}},
    }
    with pytest.raises(ConfigError, match="unknown feature group"):
        resolve_feature_config(raw)


def test_duplicate_outputs_in_group() -> None:
    raw = {
        "feature_set_id": "t",
        "version": "v1",
        "features": {
            "vwap": {"enabled": True, "price": "hlc3", "outputs": ["vwap", "vwap"]},
        },
    }
    with pytest.raises(ConfigError, match="duplicates"):
        resolve_feature_config(raw)


def test_invalid_window() -> None:
    raw = {
        "feature_set_id": "t",
        "version": "v1",
        "features": {
            "volume": {"enabled": True, "rolling_windows": [0], "outputs": ["volume_mean"]},
        },
    }
    with pytest.raises(ConfigError):
        resolve_feature_config(raw)


def test_feature_matrix_contract_validates_columns() -> None:
    v = np.zeros((3, 2), dtype=np.float64)
    FeatureMatrix(values=v, columns={"a": 0, "b": 1}, feature_hash="x")
    with pytest.raises(ValueError):
        FeatureMatrix(values=v, columns={"a": 1, "b": 2}, feature_hash="x")  # not 0..K-1

    raw = copy.deepcopy(load_feature_config(repo_root() / "configs/features/pa_core_v1.yaml"))
    raw["engine"]["mode"] = "fast"
    with pytest.raises(ConfigError):
        resolve_feature_config(raw)
