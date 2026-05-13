"""Feature spec helpers (skeleton)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from intraday.core.hashing import hash_config


def feature_config_hash(feature_config: Mapping[str, Any]) -> str:
    """Stable hash of a feature config dict."""
    return hash_config(feature_config)
