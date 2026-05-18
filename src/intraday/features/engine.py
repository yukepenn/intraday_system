"""FeatureMatrix engine: BarMatrix + resolved config → FeatureMatrix."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

import numpy as np

from intraday.core.arrays import BarMatrix, FeatureMatrix
from intraday.core.errors import ConfigError, IntradaySystemError
from intraday.features.registry import get_feature, register_builtin_features
from intraday.features.specs import (
    CANONICAL_GROUP_ORDER,
    collect_all_column_names,
    expand_column_names,
    hash_feature_config,
    resolve_feature_config,
)


def _sanitize_values(values: np.ndarray) -> np.ndarray:
    out = values.astype(np.float64, copy=True)
    out[np.isinf(out)] = np.nan
    return out


def build_feature_matrix(
    bars: BarMatrix,
    feature_config: Mapping[str, Any],
    *,
    store: Any | None = None,
    use_cache: bool = True,
    mode: Literal["reference", "fast"] = "reference",
) -> FeatureMatrix:
    """Build a ``FeatureMatrix`` from bars and YAML-resolved feature config.

    Phase 4: ``mode`` must be ``\"reference\"``. Fast kernels are not implemented.
    """
    if mode == "fast":
        raise IntradaySystemError(
            "build_feature_matrix: mode='fast' is not implemented in Phase 4; use mode='reference'."
        )
    if mode != "reference":
        raise IntradaySystemError(f"build_feature_matrix: unsupported mode {mode!r}")

    if bars.n_bars <= 0:
        raise ConfigError("build_feature_matrix requires BarMatrix.n_bars > 0")

    resolved = resolve_feature_config(feature_config)
    feature_hash = hash_feature_config(resolved)
    column_names = collect_all_column_names(resolved)

    if use_cache and store is not None:
        cached = store.get(bars.data_hash, feature_hash)
        if cached is not None:
            if cached.n_bars != bars.n_bars:
                raise IntradaySystemError(
                    "FeatureStore cache hit row count mismatch vs bars (corrupt cache)."
                )
            if cached.feature_hash != feature_hash:
                raise IntradaySystemError(
                    "FeatureStore cache hit feature_hash mismatch (corrupt cache)."
                )
            return cached

    register_builtin_features()

    blocks: dict[str, np.ndarray] = {}
    for group in CANONICAL_GROUP_ORDER:
        if group not in resolved["features"]:
            continue
        gcfg = resolved["features"][group]
        if not gcfg.get("enabled"):
            continue
        defn = get_feature(group)
        raw = defn.compute_reference(bars, gcfg)
        for col in expand_column_names(group, gcfg):
            if col not in raw:
                raise IntradaySystemError(
                    f"feature kernel {group!r} did not produce column {col!r}; got {sorted(raw)!r}"
                )
            arr = raw[col]
            if arr.shape != (bars.n_bars,):
                raise IntradaySystemError(
                    f"feature column {col!r} expected shape ({bars.n_bars},), got {arr.shape!r}"
                )
            blocks[col] = arr

    if not column_names:
        raise ConfigError("no enabled feature outputs in config")

    stacked = np.column_stack([blocks[c] for c in column_names])
    values = _sanitize_values(stacked)
    columns = {name: i for i, name in enumerate(column_names)}
    matrix = FeatureMatrix(values=values, columns=columns, feature_hash=feature_hash)

    if use_cache and store is not None:
        store.put(bars.data_hash, feature_hash, matrix)

    return matrix
