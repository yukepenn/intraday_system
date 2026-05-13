"""FeatureStore (skeleton)."""

from __future__ import annotations

from intraday.core.arrays import FeatureMatrix


class FeatureStore:
    """Skeleton FeatureStore. Phase 4 will implement file-backed get/put."""

    def get(self, data_hash: str, feature_hash: str) -> FeatureMatrix | None:
        return None

    def put(self, data_hash: str, feature_hash: str, matrix: FeatureMatrix) -> None:
        return None
