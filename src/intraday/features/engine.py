"""Feature engine entrypoints (skeleton)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from intraday.core.arrays import BarMatrix, FeatureMatrix
from intraday.core.errors import IntradaySystemError


def build_feature_matrix(
    bars: BarMatrix,
    feature_config: Mapping[str, Any],
    *,
    store: object | None = None,
    mode: Literal["reference", "fast"] = "fast",
) -> FeatureMatrix:
    """Build a FeatureMatrix. NOT YET IMPLEMENTED (Phase 4)."""
    raise IntradaySystemError("build_feature_matrix is not implemented yet (Phase 4).")
