"""Phase 7 resolved-config reconstruction tests."""

from __future__ import annotations

import json

import pytest
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.layer1.grid import (
    load_grid_document,
    reconstruct_resolved_config_for_combo,
    resolve_grid_combos,
)
from intraday.strategies.config_validation import validate_pa_buy_sell_close_trend_config

BASE = "configs/strategies/base/pa_buy_sell_close_trend.yaml"
GRID = "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml"


def test_reconstruct_combo_0001_hash() -> None:
    doc = load_grid_document(repo_root() / GRID)
    combos = resolve_grid_combos(doc)
    expected = combos[0].config_hash
    resolved = reconstruct_resolved_config_for_combo(
        base_config_path=BASE,
        grid_config_path=GRID,
        combo_id="combo_0001",
        expected_config_hash=expected,
    )
    assert resolved["risk"]["stop_mode"] == "signal_low"
    validate_pa_buy_sell_close_trend_config(resolved)


def test_reconstruct_top_combo_0015_hash() -> None:
    doc = load_grid_document(repo_root() / GRID)
    combos = {c.combo_id: c for c in resolve_grid_combos(doc)}
    expected = combos["combo_0015"].config_hash
    resolved = reconstruct_resolved_config_for_combo(
        base_config_path=BASE,
        grid_config_path=GRID,
        combo_id="combo_0015",
        expected_config_hash=expected,
    )
    assert resolved["risk"]["stop_mode"] == "rolling_low"
    validate_pa_buy_sell_close_trend_config(resolved)


def test_reconstruct_wrong_hash_raises() -> None:
    with pytest.raises(ConfigError) as exc:
        reconstruct_resolved_config_for_combo(
            base_config_path=BASE,
            grid_config_path=GRID,
            combo_id="combo_0001",
            expected_config_hash="0" * 64,
        )
    assert "config_hash mismatch" in str(exc.value)


def test_reconstruct_unknown_combo_raises() -> None:
    with pytest.raises(ConfigError) as exc:
        reconstruct_resolved_config_for_combo(
            base_config_path=BASE,
            grid_config_path=GRID,
            combo_id="combo_9999",
        )
    assert "unknown combo_id" in str(exc.value)


def test_fixed_overrides_present_in_reconstructed_config() -> None:
    resolved = reconstruct_resolved_config_for_combo(
        base_config_path=BASE,
        grid_config_path=GRID,
        combo_id="combo_0003",
    )
    assert resolved["signal"]["entry_start_minute"] == 60
    assert resolved["signal"]["entry_end_minute"] == 300
    assert resolved["backtest"]["max_hold_minutes"] == 50
    assert resolved["risk"]["min_risk_per_share"] == 0.03


def test_params_json_alone_is_grid_deltas_only() -> None:
    doc = load_grid_document(repo_root() / GRID)
    combo = resolve_grid_combos(doc)[0]
    params = json.loads(combo.params_json)
    resolved = reconstruct_resolved_config_for_combo(
        base_config_path=BASE,
        grid_config_path=GRID,
        combo_id=combo.combo_id,
    )
    assert "entry_start_minute" not in params.get("signal", {})
    assert resolved["signal"]["entry_start_minute"] == 60
