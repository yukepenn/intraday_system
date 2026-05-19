"""Phase18B v2 feature-config coverage."""

from __future__ import annotations

from pathlib import Path

from intraday.core.paths import repo_root
from intraday.features.specs import (
    collect_all_column_names,
    load_feature_config,
    resolve_feature_config,
)

PHASE18B_FEATURE_CONFIGS = (
    "configs/features/opening_core_v2.yaml",
    "configs/features/vwap_level_core_v2.yaml",
    "configs/features/gap_level_core_v2.yaml",
    "configs/features/indicator_core_v2.yaml",
    "configs/features/pa_core_v2.yaml",
)

FORBIDDEN_LABEL_TOKENS = ("pnl", "profit", "target_hit", "stop_hit", "winner", "outcome")


def test_phase18b_feature_configs_resolve_and_have_columns() -> None:
    root = repo_root()
    for rel in PHASE18B_FEATURE_CONFIGS:
        cfg = load_feature_config(root / rel)
        resolved = resolve_feature_config(cfg)
        columns = collect_all_column_names(resolved)
        assert cfg["version"] == "feature_set_v2"
        assert columns
        lowered = " ".join(columns).lower()
        assert not any(token in lowered for token in FORBIDDEN_LABEL_TOKENS)


def test_opening_core_v2_supports_registered_orb_windows() -> None:
    cfg = load_feature_config(Path(repo_root()) / "configs/features/opening_core_v2.yaml")
    columns = collect_all_column_names(resolve_feature_config(cfg))
    for minutes in (5, 10, 15, 20):
        assert f"orb_high_{minutes}" in columns
        assert f"orb_low_{minutes}" in columns
        assert f"orb_width_pct_{minutes}" in columns


def test_phase18b_v2_configs_use_session_reset_reference_engine() -> None:
    for rel in PHASE18B_FEATURE_CONFIGS:
        resolved = resolve_feature_config(load_feature_config(repo_root() / rel))
        assert resolved["engine"]["mode"] == "reference"
        assert resolved["engine"]["session_reset"] is True
        assert resolved["engine"]["dtype"] == "float64"
