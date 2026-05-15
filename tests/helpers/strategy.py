"""Synthetic helpers for strategy unit tests."""

from __future__ import annotations

import numpy as np
from intraday.core.arrays import FeatureMatrix


def make_feature_matrix_with_columns(
    n_bars: int,
    columns: dict[str, np.ndarray | float],
    *,
    feature_hash: str = "synthetic_features",
) -> FeatureMatrix:
    """Build a FeatureMatrix from column name -> 1-D array or scalar broadcast."""
    if n_bars <= 0:
        raise ValueError("n_bars must be positive")
    names = list(columns.keys())
    values = np.full((n_bars, len(names)), np.nan, dtype=np.float64)
    col_map: dict[str, int] = {}
    for j, name in enumerate(names):
        col_map[name] = j
        raw = columns[name]
        if np.isscalar(raw):
            values[:, j] = float(raw)  # type: ignore[arg-type]
        else:
            arr = np.asarray(raw, dtype=np.float64)
            if arr.shape == (1,) and n_bars > 1:
                arr = np.full(n_bars, arr[0], dtype=np.float64)
            if arr.shape != (n_bars,):
                raise ValueError(f"column {name!r} length {arr.shape} != n_bars {n_bars}")
            values[:, j] = arr
    return FeatureMatrix(values=values, columns=col_map, feature_hash=feature_hash)
