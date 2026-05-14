"""CLI commands for the Phase 4 feature engine."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from intraday.core.paths import repo_root
from intraday.data.loader import load_bars_from_curated
from intraday.features.engine import build_feature_matrix
from intraday.features.registry import list_features, register_builtin_features
from intraday.features.specs import (
    collect_all_column_names,
    hash_feature_config,
    load_feature_config,
    resolve_feature_config,
)


def cmd_features_list() -> int:
    register_builtin_features()
    names = list_features()
    print(json.dumps({"builtin_groups": names}, indent=2))
    return 0


def cmd_features_inspect(*, config: str) -> int:
    root = repo_root()
    path = Path(config)
    if not path.is_absolute():
        path = root / path
    raw = load_feature_config(path)
    resolved = resolve_feature_config(raw)
    cols = collect_all_column_names(resolved)
    fh = hash_feature_config(resolved)
    enabled = [g for g, c in resolved["features"].items() if c.get("enabled")]
    print(
        json.dumps(
            {
                "feature_set_id": resolved["feature_set_id"],
                "version": resolved["version"],
                "enabled_groups": enabled,
                "expected_column_count": len(cols),
                "feature_hash": fh,
                "columns": cols,
            },
            indent=2,
        )
    )
    return 0


def cmd_features_build(
    *,
    config: str,
    symbol: str,
    start: str,
    end: str,
    data_root: str,
    no_cache: bool,
    cache_root: str | None,
) -> int:
    root = repo_root()
    cfg_path = Path(config)
    if not cfg_path.is_absolute():
        cfg_path = root / cfg_path
    raw = load_feature_config(cfg_path)
    resolve_feature_config(raw)

    droot = Path(data_root)
    if not droot.is_absolute():
        droot = root / droot

    bars = load_bars_from_curated(
        symbol,
        start,
        end,
        data_root=str(droot),
        base=root,
    )
    store = None
    if not no_cache:
        from intraday.features.store import FeatureStore

        cr = Path(cache_root) if cache_root else root / "data/cache/features"
        if not cr.is_absolute():
            cr = root / cr
        store = FeatureStore(root=cr)

    matrix = build_feature_matrix(
        bars,
        raw,
        store=store,
        use_cache=not no_cache,
        mode="reference",
    )

    nan_counts: dict[str, int] = {}
    for name, j in matrix.columns.items():
        col = matrix.values[:, j]
        nan_counts[name] = int(np.isnan(col).sum())

    out = {
        "rows": matrix.n_bars,
        "columns": matrix.n_columns,
        "feature_hash": matrix.feature_hash,
        "first_ts_ns": int(bars.ts_ns[0]) if bars.n_bars else None,
        "last_ts_ns": int(bars.ts_ns[-1]) if bars.n_bars else None,
        "nan_counts": nan_counts,
        "cache_used": not no_cache and store is not None,
    }
    print(json.dumps(out, indent=2))
    return 0
