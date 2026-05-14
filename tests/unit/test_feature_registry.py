"""Feature registry behavior."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pytest
from intraday.core.arrays import BarMatrix
from intraday.core.errors import ConfigError
from intraday.features.base import FeatureDef
from intraday.features.registry import (
    clear_feature_registry,
    get_feature,
    list_features,
    register_builtin_features,
    register_feature,
)


def _noop_bars(bars: BarMatrix, cfg: Mapping) -> dict[str, np.ndarray]:
    return {"x": np.zeros(bars.n_bars, dtype=np.float64)}


@pytest.fixture(autouse=True)
def _reset_registry() -> None:
    clear_feature_registry()
    yield
    clear_feature_registry()


def test_register_and_get() -> None:
    register_feature(
        FeatureDef(
            name="dummy",
            version="v0",
            required_inputs=(),
            outputs=("x",),
            compute_reference=_noop_bars,
        )
    )
    d = get_feature("dummy")
    assert d.name == "dummy"


def test_duplicate_registration_raises() -> None:
    d = FeatureDef(
        name="dup",
        version="v0",
        required_inputs=(),
        outputs=("x",),
        compute_reference=_noop_bars,
    )
    register_feature(d)
    with pytest.raises(ConfigError, match="already registered"):
        register_feature(d)


def test_unknown_feature_raises() -> None:
    register_builtin_features()
    with pytest.raises(ConfigError, match="unknown"):
        get_feature("not_a_real_group")


def test_list_features_includes_builtins() -> None:
    register_builtin_features()
    names = list_features()
    assert "vwap" in names
    assert "orb" in names
    assert sorted(names) == names
