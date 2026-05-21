"""Phase19B grid skeleton and Layer1 grid-inspect config tests."""

from __future__ import annotations

from pathlib import Path

from intraday.core.config import load_yaml
from intraday.layer1.config import (
    load_layer1_controlled_grid_config,
    validate_layer1_controlled_grid_config,
)
from intraday.layer1.grid import grid_document_combo_count, load_grid_document

REPO = Path(__file__).resolve().parents[2]

STRATEGIES = (
    "pa_second_entry_pullback",
    "pa_trading_range_bls_hs",
    "pa_failed_breakout_trap",
    "pa_opening_reversal_sr",
    "pa_breakout_pullback_continuation",
    "pa_tight_channel_pullback",
    "pa_broad_channel_zone",
)


def test_phase19b_grid_skeletons_are_bounded_and_diagnostic() -> None:
    for strategy in STRATEGIES:
        path = (
            REPO
            / "configs"
            / "strategies"
            / "grids"
            / "phase19"
            / f"{strategy}_controlled_small.yaml"
        )
        doc = load_grid_document(path)
        raw = load_yaml(path)
        assert raw["diagnostic_only"] is True
        assert raw["broad_sweep_allowed"] is False
        assert grid_document_combo_count(doc) <= 12
        assert raw["grid"]["signal.side_mode"] == ["long_only", "short_only", "both"]
        assert "risk.target_mode" not in raw["grid"]


def test_phase19b_layer1_grid_inspect_configs_parse() -> None:
    for strategy in STRATEGIES:
        path = REPO / "configs" / "layer1" / "phase19_brooks_pa_grid_inspect" / f"{strategy}.yaml"
        cfg = load_layer1_controlled_grid_config(path)
        validate_layer1_controlled_grid_config(cfg)
        raw = load_yaml(path)
        assert cfg.strategy_name == strategy
        assert raw["grid"]["max_combos"] == 12
