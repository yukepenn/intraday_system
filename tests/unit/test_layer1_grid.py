"""layer1.grid unit tests."""

from __future__ import annotations

import json

import pytest
from intraday.core.paths import repo_root
from intraday.layer1.grid import (
    expand_grid,
    grid_document_combo_count,
    load_grid_document,
    normalize_override_mapping,
    resolve_grid_combos,
    resolve_grid_document,
)


def test_normalize_dotted_keys() -> None:
    out = normalize_override_mapping({"risk.target_r": 1.0, "signal.entry_start_minute": 60})
    assert out == {("risk", "target_r"): 1.0, ("signal", "entry_start_minute"): 60}


def test_normalize_nested_dicts() -> None:
    out = normalize_override_mapping({"risk": {"target_r": 1.0, "stop_mode": "atr_buffer"}})
    assert out == {("risk", "target_r"): 1.0, ("risk", "stop_mode"): "atr_buffer"}


def test_normalize_preserves_list_leaves() -> None:
    out = normalize_override_mapping({"features.vol_windows": [5, 15, 30]})
    assert out == {("features", "vol_windows"): [5, 15, 30]}


def test_expand_grid_empty_returns_single_empty_combo() -> None:
    combos = expand_grid({})
    assert combos == [{}]


def test_expand_grid_cartesian_size() -> None:
    grid = {"risk.target_r": [1.0, 1.5], "signal.entry_start_minute": [60, 90, 120]}
    combos = expand_grid(grid)
    assert len(combos) == 2 * 3


def test_resolve_fixed_only() -> None:
    base = {"strategy": "pa", "risk": {"target_r": 1.0, "max_trades_per_day": 1}}
    out = list(resolve_grid_document(base, {"risk.max_trades_per_day": 2}, None))
    assert len(out) == 1
    assert out[0]["risk"]["max_trades_per_day"] == 2
    assert out[0]["risk"]["target_r"] == 1.0  # unchanged


def test_resolve_grid_only() -> None:
    base = {"strategy": "pa", "risk": {"target_r": 1.0}}
    out = list(resolve_grid_document(base, None, {"risk.target_r": [1.0, 1.5, 2.0]}))
    assert len(out) == 3
    targets = sorted(c["risk"]["target_r"] for c in out)
    assert targets == [1.0, 1.5, 2.0]


def test_resolve_fixed_and_grid() -> None:
    base = {
        "strategy": "pa",
        "risk": {"target_r": 1.0, "max_trades_per_day": 1},
        "backtest": {"max_hold_minutes": 30},
    }
    out = list(
        resolve_grid_document(
            base,
            {"risk.max_trades_per_day": 2},
            {"risk.target_r": [1.0, 1.5], "backtest.max_hold_minutes": [40, 60]},
        )
    )
    assert len(out) == 2 * 2
    for cfg in out:
        assert cfg["risk"]["max_trades_per_day"] == 2
        assert cfg["risk"]["target_r"] in (1.0, 1.5)
        assert cfg["backtest"]["max_hold_minutes"] in (40, 60)


def test_resolve_overlap_raises() -> None:
    base = {"risk": {"target_r": 1.0}}
    with pytest.raises(ValueError) as exc:
        list(
            resolve_grid_document(
                base,
                {"risk.target_r": 1.0},
                {"risk.target_r": [1.0, 1.5]},
            )
        )
    assert "risk.target_r" in str(exc.value)


def test_list_values_remain_leaves() -> None:
    base = {"features": {"vol_windows": [5, 15, 30]}}
    out = list(
        resolve_grid_document(
            base,
            {"features.vol_windows": [10, 20, 40]},
            None,
        )
    )
    assert len(out) == 1
    assert out[0]["features"]["vol_windows"] == [10, 20, 40]


def test_controlled_small_yaml_combo_count() -> None:
    path = repo_root() / "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml"
    doc = load_grid_document(path)
    assert grid_document_combo_count(doc) == 16


def test_resolve_grid_combos_controlled_small() -> None:
    path = repo_root() / "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml"
    doc = load_grid_document(path)
    combos = resolve_grid_combos(doc)
    assert len(combos) == 16
    assert combos[0].combo_id == "combo_0001"
    assert combos[-1].combo_id == "combo_0016"
    assert combos[0].config_hash != combos[1].config_hash
    params = json.loads(combos[0].params_json)
    assert "signal" in params
    assert isinstance(params["signal"]["require_vwap_side"], bool)
    assert isinstance(params["signal"]["body_pct_min"], float)


def test_resolve_grid_combos_hash_stable() -> None:
    path = repo_root() / "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml"
    doc = load_grid_document(path)
    h1 = [c.config_hash for c in resolve_grid_combos(doc)]
    h2 = [c.config_hash for c in resolve_grid_combos(doc)]
    assert h1 == h2


def test_expand_grid_key_order_deterministic() -> None:
    g1 = {"a.x": [1, 2], "b.y": [3, 4]}
    g2 = {"b.y": [3, 4], "a.x": [1, 2]}
    c1 = expand_grid(g1)
    c2 = expand_grid(g2)
    assert len(c1) == len(c2) == 4
    assert c1 != c2
