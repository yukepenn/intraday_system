"""Cache-key helpers for FeatureStore (skeleton)."""

from __future__ import annotations

from intraday.core.hashing import hash_config


def feature_cache_key(feature_config_hash: str, data_hash: str) -> str:
    """Combined cache key for FeatureStore."""
    return hash_config({"feature_config_hash": feature_config_hash, "data_hash": data_hash})
