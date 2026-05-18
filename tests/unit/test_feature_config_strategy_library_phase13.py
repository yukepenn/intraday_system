"""Phase 13 feature config resolution and hash stability."""

from __future__ import annotations

from intraday.core.paths import repo_root
from intraday.features.specs import (
    collect_all_column_names,
    hash_feature_config,
    load_feature_config,
    resolve_feature_config,
)

PA_HASH_PINNED = "facb93387b6460a7f79bfd08a23b71560539d284f5ca2f0e1b565cb224a15498"
ORB_HASH_PINNED = "e3c3df12cb5a2bdd787d5a5deaeada374d9b0787d7c0b993a309eb5bfc03d27d"


def test_pa_core_v1_hash_stable_pinned() -> None:
    raw = load_feature_config(repo_root() / "configs/features/pa_core_v1.yaml")
    h = hash_feature_config(resolve_feature_config(raw))
    assert h == PA_HASH_PINNED


def test_orb_core_v1_hash_stable_pinned() -> None:
    raw = load_feature_config(repo_root() / "configs/features/orb_core_v1.yaml")
    h = hash_feature_config(resolve_feature_config(raw))
    assert h == ORB_HASH_PINNED


def test_new_feature_configs_resolve() -> None:
    names = (
        "opening_core_v1",
        "gap_level_core_v1",
        "vwap_level_core_v1",
        "indicator_core_v1",
        "strategy_library_core_v1",
    )
    for name in names:
        raw = load_feature_config(repo_root() / f"configs/features/{name}.yaml")
        resolved = resolve_feature_config(raw)
        cols = collect_all_column_names(resolved)
        assert cols
        assert len(cols) == len(set(cols))
