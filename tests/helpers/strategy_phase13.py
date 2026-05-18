"""Shared helpers for Phase 13 strategy unit tests."""

from __future__ import annotations

import copy

import numpy as np
import pytest
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.strategies.contracts import validate_signal_matrix
from intraday.strategies.loader import load_strategy_config

from tests.helpers.bars import make_bar_matrix
from tests.helpers.strategy import make_feature_matrix_with_columns


def load_base_config(strategy_name: str) -> dict:
    path = repo_root() / f"configs/strategies/base/{strategy_name}.yaml"
    return load_strategy_config(path)


def assert_signal_matrix_valid(sig, n: int) -> None:
    validate_signal_matrix(sig, n)


def assert_non_entry_convention(sig) -> None:
    non = ~sig.entry
    if non.any():
        assert (sig.side[non] == 0).all()
        assert np.isnan(sig.stop[non]).all()
        assert np.isnan(sig.target_r[non]).all()
        assert np.isnan(sig.score[non]).all()
        assert (sig.setup_code[non] == 0).all()


def assert_entry_stop_target(sig, bars) -> None:
    if not sig.entry.any():
        return
    idx = int(np.flatnonzero(sig.entry)[0])
    assert sig.side[idx] == 1
    assert np.isfinite(sig.stop[idx])
    assert sig.stop[idx] < bars.close[idx]
    assert sig.target_r[idx] > 0
    assert np.isfinite(sig.score[idx])


def signals_unchanged_up_to(a, b, k: int) -> None:
    for name in ("entry", "side", "stop", "target_r", "score", "setup_code"):
        x = getattr(a, name)[: k + 1]
        y = getattr(b, name)[: k + 1]
        if name == "entry":
            assert np.array_equal(x.astype(bool), y.astype(bool))
        elif name in ("side", "setup_code"):
            assert np.array_equal(x, y)
        else:
            assert np.allclose(x, y, equal_nan=True)


def test_base_yaml_validates(generate_fn, validate_fn, strategy_name: str) -> None:
    cfg = load_base_config(strategy_name)
    validate_fn(cfg)


def test_rejects_short_side(validate_fn, strategy_name: str) -> None:
    cfg = load_base_config(strategy_name)
    cfg = copy.deepcopy(cfg)
    cfg["signal"]["side"] = "short"
    with pytest.raises(ConfigError):
        validate_fn(cfg)


def test_missing_column_raises(generate_fn, validate_fn, strategy_name: str, cols: dict) -> None:
    cfg = load_base_config(strategy_name)
    validate_fn(cfg)
    bars = make_bar_matrix([100.0], [101.0], [99.0], [100.0], minute=[120])
    feats = make_feature_matrix_with_columns(1, cols, feature_hash="fh")
    with pytest.raises(ConfigError):
        generate_fn(bars, feats, cfg)
