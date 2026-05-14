"""Local-only FeatureStore (npz + JSON sidecars)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from intraday.core.arrays import FeatureMatrix
from intraday.core.errors import IntradaySystemError
from intraday.features.specs import FEATURE_ENGINE_SEMANTIC_VERSION


class FeatureStore:
    """File-backed feature cache under ``root`` (default ``data/cache/features``).

    Layout::

        {root}/data_hash={data_hash}/feature_hash={feature_hash}/
            matrix.npz      # array ``values`` (float64, shape N x K)
            columns.json    # ordered column names [name0, name1, ...]
            meta.json       # hashes, shapes, engine version

    Cache is not runtime truth; entries may be deleted and rebuilt.
    """

    def __init__(self, root: Path | str = Path("data/cache/features")) -> None:
        self.root = Path(root)

    def _entry_dir(self, data_hash: str, feature_hash: str) -> Path:
        return self.root / f"data_hash={data_hash}" / f"feature_hash={feature_hash}"

    def get(self, data_hash: str, feature_hash: str) -> FeatureMatrix | None:
        base = self._entry_dir(data_hash, feature_hash)
        meta_path = base / "meta.json"
        vals_path = base / "matrix.npz"
        cols_path = base / "columns.json"
        if not meta_path.is_file() or not vals_path.is_file() or not cols_path.is_file():
            return None

        try:
            meta: dict[str, Any] = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise IntradaySystemError(
                f"FeatureStore corrupt meta.json (invalid JSON): {base}"
            ) from exc

        if meta.get("data_hash") != data_hash or meta.get("feature_hash") != feature_hash:
            raise IntradaySystemError(f"FeatureStore meta hash mismatch (corrupt): {base}")

        try:
            cols: list[str] = json.loads(cols_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise IntradaySystemError(f"FeatureStore corrupt columns.json: {base}") from exc

        with np.load(vals_path) as loaded:
            if "values" not in loaded:
                raise IntradaySystemError(f"FeatureStore matrix.npz missing 'values': {base}")
            values = np.asarray(loaded["values"], dtype=np.float64)

        n_bars = int(meta.get("n_bars", -1))
        n_cols = int(meta.get("n_columns", -1))
        if n_bars < 0 or n_cols < 0:
            raise IntradaySystemError(f"FeatureStore meta missing shape fields: {base}")
        if values.shape != (n_bars, n_cols):
            raise IntradaySystemError(
                f"FeatureStore values shape {values.shape} != meta ({n_bars}, {n_cols}): {base}"
            )
        if len(cols) != n_cols:
            raise IntradaySystemError(
                f"FeatureStore columns.json length {len(cols)} != n_columns {n_cols}: {base}"
            )

        colmap = {name: i for i, name in enumerate(cols)}
        if len(colmap) != len(cols):
            raise IntradaySystemError(
                f"FeatureStore duplicate column names in columns.json: {base}"
            )

        fh = str(meta.get("feature_hash", ""))
        if fh != feature_hash:
            raise IntradaySystemError("FeatureStore matrix feature_hash meta mismatch")

        return FeatureMatrix(values=values, columns=colmap, feature_hash=fh)

    def put(self, data_hash: str, feature_hash: str, matrix: FeatureMatrix) -> Path:
        if matrix.feature_hash != feature_hash:
            raise IntradaySystemError(
                "FeatureStore.put: matrix.feature_hash does not match argument"
            )
        base = self._entry_dir(data_hash, feature_hash)
        base.mkdir(parents=True, exist_ok=True)

        n_bars, n_cols = matrix.values.shape
        ordered_names: list[str | None] = [None] * n_cols
        for name, idx in matrix.columns.items():
            if idx < 0 or idx >= n_cols:
                raise IntradaySystemError("FeatureStore.put: invalid column index map")
            ordered_names[idx] = name
        if any(x is None for x in ordered_names):
            raise IntradaySystemError("FeatureStore.put: columns map is not contiguous 0..K-1")
        names_out = [str(x) for x in ordered_names]

        meta = {
            "kind": "feature_matrix",
            "data_hash": data_hash,
            "feature_hash": feature_hash,
            "n_bars": n_bars,
            "n_columns": n_cols,
            "feature_engine_semantic_version": FEATURE_ENGINE_SEMANTIC_VERSION,
            "dtype": "float64",
        }

        parent = base.parent
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=str(parent), prefix=".feature_put_") as td:
            tdp = Path(td)
            np.savez_compressed(
                tdp / "matrix.npz", values=matrix.values.astype(np.float64, copy=False)
            )
            (tdp / "columns.json").write_text(
                json.dumps(names_out, separators=(",", ":"), ensure_ascii=False),
                encoding="utf-8",
            )
            (tdp / "meta.json").write_text(
                json.dumps(meta, separators=(",", ":"), ensure_ascii=False),
                encoding="utf-8",
            )
            for name in ("matrix.npz", "columns.json", "meta.json"):
                src = tdp / name
                dst = base / name
                dst.unlink(missing_ok=True)
                src.replace(dst)

        return base
