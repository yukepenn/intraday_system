"""Phase 14 Layer1 diagnostic config inventory tests."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from intraday.core.paths import is_absolute_path_like, repo_root
from intraday.layer1.config import (
    MAX_CONTROLLED_GRID_COMBOS,
    load_layer1_controlled_grid_config,
    validate_layer1_controlled_grid_config,
)
from intraday.layer1.grid import grid_document_combo_count, load_grid_document
from intraday.strategies.registry import (
    clear_strategy_registry,
    get_strategy,
    register_builtin_strategies,
)

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
FORBIDDEN_TOP_LEVEL = {
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


def test_phase14_configs_exist_validate_and_stay_diagnostic() -> None:
    root = repo_root()
    clear_strategy_registry()
    register_builtin_strategies()
    try:
        for window in WINDOWS:
            for strategy in STRATEGIES:
                rel = Path(
                    f"configs/layer1/phase14_strategy_library_small_grid/{window}_{strategy}.yaml"
                )
                path = root / rel
                assert path.is_file(), rel

                raw = yaml.safe_load(path.read_text(encoding="utf-8"))
                assert isinstance(raw, Mapping)
                assert not (set(raw.keys()) & FORBIDDEN_TOP_LEVEL)
                assert not (_walk_keys(raw) & {"candidate_root", "promotion_allowed_now"})

                cfg = load_layer1_controlled_grid_config(path)
                validate_layer1_controlled_grid_config(cfg)
                get_strategy(cfg.strategy_name)

                for rel_path in (
                    cfg.feature_config,
                    cfg.strategy_base_config,
                    cfg.strategy_grid_path,
                    cfg.execution_config,
                    cfg.artifact_root,
                ):
                    assert not is_absolute_path_like(rel_path), rel_path

                assert cfg.artifact_root.startswith(
                    "artifacts/layer1_strategy_library_small_grid_phase14/"
                )
                assert cfg.execution_mode == "reference"
                assert cfg.count_rejected_intents
                assert cfg.skip_while_trade_open
                assert not cfg.save_row_level_trades
                assert not cfg.grid_allow_prefix_slicing

                assert (root / cfg.feature_config).is_file()
                assert (root / cfg.strategy_base_config).is_file()
                assert (root / cfg.strategy_grid_path).is_file()

                grid_doc = load_grid_document(root / cfg.strategy_grid_path)
                combo_count = grid_document_combo_count(grid_doc)
                assert combo_count <= MAX_CONTROLLED_GRID_COMBOS
    finally:
        clear_strategy_registry()


def test_no_runtime_candidate_yaml_was_added() -> None:
    candidate_root = repo_root() / "configs/candidates"
    runtime_yamls = [p for p in candidate_root.rglob("*") if p.suffix.lower() in {".yaml", ".yml"}]
    assert runtime_yamls == []
