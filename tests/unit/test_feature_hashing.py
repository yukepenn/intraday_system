"""Deterministic feature hashing."""

from __future__ import annotations

import copy

from intraday.core.paths import repo_root
from intraday.features.specs import hash_feature_config, load_feature_config, resolve_feature_config


def test_hash_stable_under_features_key_reordering() -> None:
    path = repo_root() / "configs/features/pa_core_v1.yaml"
    raw = load_feature_config(path)
    r1 = resolve_feature_config(raw)
    h1 = hash_feature_config(r1)
    feats = copy.deepcopy(r1["features"])
    # reorder top-level feature groups in a new dict (different insertion order)
    keys = list(feats.keys())
    reordered = {k: feats[k] for k in reversed(keys)}
    r2 = copy.deepcopy(r1)
    r2["features"] = reordered
    assert hash_feature_config(r2) == h1


def test_hash_changes_when_config_changes() -> None:
    path = repo_root() / "configs/features/pa_core_v1.yaml"
    raw = load_feature_config(path)
    h1 = hash_feature_config(resolve_feature_config(raw))
    raw2 = copy.deepcopy(raw)
    raw2["feature_set_id"] = "other_id"
    h2 = hash_feature_config(resolve_feature_config(raw2))
    assert h1 != h2


def test_hash_changes_when_enabled_toggles() -> None:
    path = repo_root() / "configs/features/pa_core_v1.yaml"
    raw = load_feature_config(path)
    h1 = hash_feature_config(resolve_feature_config(raw))
    raw2 = copy.deepcopy(raw)
    raw2["features"]["vwap"]["enabled"] = False
    h2 = hash_feature_config(resolve_feature_config(raw2))
    assert h1 != h2
