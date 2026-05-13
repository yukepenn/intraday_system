"""Feature registry (skeleton)."""

from __future__ import annotations

from intraday.core.registry import Registry
from intraday.features.base import FeatureDef

FEATURE_REGISTRY: Registry[FeatureDef] = Registry("feature")
