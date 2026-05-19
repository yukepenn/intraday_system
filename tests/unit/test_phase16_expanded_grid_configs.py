"""Phase16 rational expanded grid config inventory tests."""

from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from intraday.core.paths import is_absolute_path_like, repo_root
from intraday.layer1.config import (
    MAX_EXPANDED_GRID_COMBOS,
    load_layer1_controlled_grid_config,
    validate_layer1_controlled_grid_config,
)
from intraday.layer1.grid import grid_document_combo_count, load_grid_document

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
WINDOWS = ("qqq_2024h1", "qqq_2024h2")
PHASE16_ARTIFACT_ROOT = "artifacts/layer1_10_strategy_rational_expanded_grid_phase16"
FORBIDDEN_KEYS = {
    "candidate",
    "candidates",
    "candidate_root",
    "selection",
    "promotion",
    "layer2",
    "layer3",
    "wfo",
    "live",
    "paper",
}


def _walk_keys(obj: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            keys.add(str(key))
            keys.update(_walk_keys(value))
    elif isinstance(obj, list):
        for item in obj:
            keys.update(_walk_keys(item))
    return keys


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_phase16_expanded_grids_exist_are_bounded_and_documented() -> None:
    root = repo_root()
    rationale_rows = _read_csv(
        root
        / "artifacts/layer1_10_strategy_rational_expanded_grid_phase16"
        / "expanded_grid_axis_rationale.csv"
    )
    documented_axes = {(row["strategy"], row["axis"]) for row in rationale_rows}
    count_rows = {
        row["strategy"]: row
        for row in _read_csv(
            root
            / "artifacts/layer1_10_strategy_rational_expanded_grid_phase16"
            / "per_strategy_combo_count.csv"
        )
    }

    for strategy in STRATEGIES:
        rel = Path(f"configs/strategies/grids/expanded_phase16/{strategy}_rational_expanded.yaml")
        path = root / rel
        assert path.is_file(), rel
        doc = load_grid_document(path)
        assert doc["strategy"] == strategy
        assert doc.get("diagnostic_only") is True
        assert not (_walk_keys(doc) & FORBIDDEN_KEYS)

        combo_count = grid_document_combo_count(doc)
        assert 0 < combo_count <= MAX_EXPANDED_GRID_COMBOS
        assert int(doc["combo_count"]) == combo_count
        assert int(count_rows[strategy]["combo_count"]) == combo_count
        if combo_count > 1500:
            assert count_rows[strategy]["justification_if_large"]

        grid = doc["grid"]
        assert isinstance(grid, Mapping)
        for axis in grid:
            assert (strategy, str(axis)) in documented_axes


def test_phase16_layer1_configs_exist_validate_and_stay_diagnostic() -> None:
    root = repo_root()
    for window in WINDOWS:
        for strategy in STRATEGIES:
            rel = Path(
                f"configs/layer1/phase16_10_strategy_rational_expanded_grid/{window}_{strategy}.yaml"
            )
            path = root / rel
            assert path.is_file(), rel
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            assert isinstance(raw, Mapping)
            assert not (set(raw.keys()) & FORBIDDEN_KEYS)
            assert not (_walk_keys(raw) & {"candidate_root", "promotion_allowed_now"})

            cfg = load_layer1_controlled_grid_config(path)
            validate_layer1_controlled_grid_config(cfg)
            assert cfg.execution_mode == "reference"
            assert not cfg.save_row_level_trades
            assert not cfg.grid_allow_prefix_slicing
            assert cfg.artifact_root.startswith(PHASE16_ARTIFACT_ROOT)

            for rel_path in (
                cfg.feature_config,
                cfg.strategy_base_config,
                cfg.strategy_grid_path,
                cfg.execution_config,
                cfg.artifact_root,
            ):
                assert not is_absolute_path_like(rel_path), rel_path

            grid_doc = load_grid_document(root / cfg.strategy_grid_path)
            combo_count = grid_document_combo_count(grid_doc)
            assert combo_count > 24
            assert combo_count <= MAX_EXPANDED_GRID_COMBOS
            assert cfg.grid_max_combos == combo_count
