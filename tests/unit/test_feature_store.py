"""FeatureStore get/put."""

from __future__ import annotations

import numpy as np
import pytest
from intraday.core.arrays import FeatureMatrix
from intraday.core.errors import IntradaySystemError
from intraday.features.store import FeatureStore


def test_put_get_roundtrip(tmp_path) -> None:
    root = tmp_path / "f"
    store = FeatureStore(root=root)
    v = np.array([[1.0, 2.0], [3.0, np.nan]], dtype=np.float64)
    m = FeatureMatrix(values=v, columns={"a": 0, "b": 1}, feature_hash="abc")
    p = store.put("dh", "abc", m)
    assert p.is_dir()
    m2 = store.get("dh", "abc")
    assert m2 is not None
    np.testing.assert_array_equal(m.values, m2.values)
    assert m2.columns == m.columns
    assert m2.feature_hash == "abc"


def test_missing_returns_none(tmp_path) -> None:
    store = FeatureStore(root=tmp_path / "x")
    assert store.get("a", "b") is None


def test_corrupt_meta_raises(tmp_path) -> None:
    base = tmp_path / "c" / "data_hash=d" / "feature_hash=f"
    base.mkdir(parents=True)
    (base / "meta.json").write_text("{not json", encoding="utf-8")
    (base / "matrix.npz").write_bytes(b"x")
    (base / "columns.json").write_text("[]", encoding="utf-8")
    store = FeatureStore(root=tmp_path / "c")
    with pytest.raises(IntradaySystemError, match="corrupt"):
        store.get("d", "f")


def test_put_rejects_hash_mismatch(tmp_path) -> None:
    store = FeatureStore(root=tmp_path / "z")
    m = FeatureMatrix(
        values=np.zeros((1, 1), dtype=np.float64),
        columns={"a": 0},
        feature_hash="real",
    )
    with pytest.raises(IntradaySystemError, match="feature_hash"):
        store.put("d", "other", m)
