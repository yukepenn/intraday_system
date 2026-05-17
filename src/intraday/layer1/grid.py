"""Layer1 grid resolver.

Pure config logic for controlled parameter grids (Phase 6b).

Rules (from configs/strategies/grids/*):
  base config -> fixed overrides -> per-combo grid overrides
  fixed/grid key overlap raises ValueError
  list values within base configs remain leaf values; the expander only treats
  top-level grid keys as cartesian axes.
  Dotted keys (e.g. "risk.target_r") are merged deep-style.
"""

from __future__ import annotations

import copy
import itertools
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intraday.core.config import load_yaml
from intraday.core.errors import ConfigError
from intraday.core.hashing import hash_config, stable_json_dumps
from intraday.core.paths import repo_root

__all__ = [
    "ResolvedGridCombo",
    "expand_grid",
    "load_grid_document",
    "normalize_override_mapping",
    "reconstruct_resolved_config_for_combo",
    "resolve_grid_combos",
    "resolve_grid_document",
]


@dataclass(frozen=True)
class ResolvedGridCombo:
    """One fully-resolved strategy config from a grid document."""

    combo_id: str
    overrides: dict[str, Any]
    fixed_overrides: dict[str, Any]
    grid_overrides: dict[str, Any]
    resolved_config: dict[str, Any]
    params_json: str
    config_hash: str


def load_grid_document(path: Path | str) -> dict[str, Any]:
    """Load a strategy grid YAML document (runtime)."""
    return load_yaml(path)


def normalize_override_mapping(mapping: Mapping[str, Any]) -> dict[tuple[str, ...], Any]:
    """Normalize a dotted-key override mapping into tuples of path segments.

    Example:
        {"risk.target_r": 1.0, "signal.entry_start_minute": 60}
        -> {("risk", "target_r"): 1.0, ("signal", "entry_start_minute"): 60}

    Nested dicts are flattened; lists are kept as leaf values.
    """
    result: dict[tuple[str, ...], Any] = {}

    def _walk(prefix: tuple[str, ...], value: Any) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                if not isinstance(k, str):
                    raise TypeError(f"override keys must be strings, got {type(k)!r}")
                if "." in k:
                    parts = tuple(p for p in k.split(".") if p)
                    _walk(prefix + parts, v)
                else:
                    _walk(prefix + (k,), v)
        else:
            if prefix in result:
                raise ValueError(f"duplicate override key: {'.'.join(prefix)}")
            result[prefix] = value

    if mapping is None:
        return result
    for key, val in mapping.items():
        if not isinstance(key, str):
            raise TypeError(f"override keys must be strings, got {type(key)!r}")
        parts = tuple(p for p in key.split(".") if p)
        _walk(parts, val)
    return result


def _paths_to_nested(path_values: Mapping[tuple[str, ...], Any]) -> dict[str, Any]:
    """Build a nested dict from dotted-path keys."""
    root: dict[str, Any] = {}
    for path, val in path_values.items():
        cursor: dict[str, Any] = root
        for segment in path[:-1]:
            nxt = cursor.get(segment)
            if not isinstance(nxt, dict):
                nxt = {}
                cursor[segment] = nxt
            cursor = nxt
        cursor[path[-1]] = copy.deepcopy(val)
    return root


def _deep_merge_dicts(a: Mapping[str, Any], b: Mapping[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(dict(a))
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge_dicts(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def _apply_overrides(
    base: dict[str, Any],
    overrides: dict[tuple[str, ...], Any],
) -> dict[str, Any]:
    """Apply path-keyed overrides into a deep copy of ``base``."""
    out = copy.deepcopy(base)
    for path, value in overrides.items():
        cursor: dict[str, Any] = out
        for segment in path[:-1]:
            existing = cursor.get(segment)
            if not isinstance(existing, dict):
                existing = {}
                cursor[segment] = existing
            cursor = existing
        cursor[path[-1]] = copy.deepcopy(value)
    return out


def expand_grid(grid: Mapping[str, Any]) -> list[dict[tuple[str, ...], Any]]:
    """Expand a top-level grid mapping into a list of per-combo override dicts.

    Each key of ``grid`` is treated as a single axis whose value must be a list
    of leaf values. The cartesian product produces one combo per output entry.

    Empty grid returns ``[{}]`` (one combo: no axes).
    Key order follows the mapping iteration order (YAML insertion order).
    """
    if not grid:
        return [{}]
    axes: list[tuple[tuple[str, ...], list[Any]]] = []
    for key, values in grid.items():
        if not isinstance(key, str):
            raise TypeError(f"grid keys must be strings, got {type(key)!r}")
        if not isinstance(values, list):
            raise TypeError(f"grid axis values must be a list, got {type(values)!r} for {key!r}")
        if not values:
            raise ValueError(f"grid axis {key!r} has empty value list")
        path = tuple(p for p in key.split(".") if p)
        axes.append((path, values))

    combos: list[dict[tuple[str, ...], Any]] = []
    for product in itertools.product(*(vals for _, vals in axes)):
        combo: dict[tuple[str, ...], Any] = {}
        for (path, _), val in zip(axes, product, strict=True):
            combo[path] = val
        combos.append(combo)
    return combos


def _check_overlap(
    fixed_paths: set[tuple[str, ...]],
    grid_paths: set[tuple[str, ...]],
) -> None:
    overlap = sorted(fixed_paths & grid_paths)
    if overlap:
        names = [".".join(p) for p in overlap]
        raise ValueError(f"fixed/grid key overlap is forbidden: {names!r}")


def resolve_grid_document(
    base_config: Mapping[str, Any],
    fixed: Mapping[str, Any] | None,
    grid: Mapping[str, Any] | None,
) -> Iterator[dict[str, Any]]:
    """Yield fully-resolved configs for each combo.

    Order:
      1. start from a deep copy of ``base_config``;
      2. apply ``fixed`` overrides;
      3. apply combo overrides for each cartesian point of ``grid``.

    Raises ``ValueError`` if any key appears in both ``fixed`` and ``grid``.
    """
    fixed_overrides = normalize_override_mapping(fixed or {})
    combos = expand_grid(grid or {})
    grid_paths: set[tuple[str, ...]] = set()
    for combo in combos:
        grid_paths.update(combo.keys())
    _check_overlap(set(fixed_overrides.keys()), grid_paths)

    base_dict = dict(base_config)
    for combo in combos:
        merged = _apply_overrides(base_dict, fixed_overrides)
        merged = _apply_overrides(merged, combo)
        yield merged


def grid_document_combo_count(doc: Mapping[str, Any]) -> int:
    """Return the number of cartesian combos implied by ``doc['grid']``."""
    grid = doc.get("grid") or {}
    if not isinstance(grid, Mapping):
        raise TypeError("grid document 'grid' must be a mapping")
    return len(expand_grid(grid))


def resolve_grid_combos(
    doc: Mapping[str, Any],
    *,
    repo_base: Path | None = None,
) -> list[ResolvedGridCombo]:
    """Load base strategy config from ``doc['base_config']`` and expand grid combos.

    ``doc`` must include ``base_config`` (repo-relative path), optional ``fixed``,
    and optional ``grid`` mappings (grid axis lists).
    """
    root = repo_base or repo_root()
    base_rel = str(doc.get("base_config", "")).strip()
    if not base_rel:
        raise ValueError("grid document requires base_config")
    base_path = Path(base_rel)
    if not base_path.is_absolute():
        base_path = root / base_path
    base_raw = load_yaml(base_path)
    base_dict = dict(base_raw)

    fixed = doc.get("fixed") or {}
    grid = doc.get("grid") or {}
    if not isinstance(fixed, Mapping):
        raise TypeError("grid document 'fixed' must be a mapping when present")
    if not isinstance(grid, Mapping):
        raise TypeError("grid document 'grid' must be a mapping when present")

    fixed_overrides = normalize_override_mapping(fixed)
    combos = expand_grid(grid)
    grid_paths: set[tuple[str, ...]] = set()
    for combo in combos:
        grid_paths.update(combo.keys())
    _check_overlap(set(fixed_overrides.keys()), grid_paths)

    fixed_nested = _paths_to_nested(fixed_overrides)
    resolved: list[ResolvedGridCombo] = []
    for i, combo in enumerate(combos, start=1):
        grid_nested = _paths_to_nested(combo)
        merged_cfg = _apply_overrides(base_dict, fixed_overrides)
        merged_cfg = _apply_overrides(merged_cfg, combo)
        ov = _deep_merge_dicts(fixed_nested, grid_nested)
        params_json = stable_json_dumps(grid_nested)
        h = hash_config(merged_cfg)
        resolved.append(
            ResolvedGridCombo(
                combo_id=f"combo_{i:04d}",
                overrides=ov,
                fixed_overrides=copy.deepcopy(fixed_nested),
                grid_overrides=copy.deepcopy(grid_nested),
                resolved_config=merged_cfg,
                params_json=params_json,
                config_hash=h,
            )
        )
    return resolved


def reconstruct_resolved_config_for_combo(
    *,
    base_config_path: Path | str,
    grid_config_path: Path | str,
    combo_id: str,
    expected_config_hash: str | None = None,
    repo_base: Path | None = None,
) -> dict[str, Any]:
    """Reconstruct the full resolved strategy config for one grid combo.

    Loads ``base_config_path`` and ``grid_config_path``, resolves combos via
    ``resolve_grid_combos``, and returns the merged config (fixed + grid axes).

    When ``expected_config_hash`` is provided, raises ``ConfigError`` if
    ``hash_config(resolved)`` does not match.
    """
    root = repo_base or repo_root()
    base_path = Path(base_config_path)
    grid_path = Path(grid_config_path)
    if not base_path.is_absolute():
        base_path = root / base_path
    if not grid_path.is_absolute():
        grid_path = root / grid_path

    grid_doc = load_grid_document(grid_path)
    base_rel = str(grid_doc.get("base_config", "")).strip()
    if not base_rel:
        raise ConfigError("grid document requires base_config")
    expected_base = Path(base_rel)
    if not expected_base.is_absolute():
        expected_base = root / expected_base
    if base_path.resolve() != expected_base.resolve():
        raise ConfigError(
            f"base_config_path {base_path!s} does not match grid base_config {expected_base!s}"
        )

    combos = resolve_grid_combos(grid_doc, repo_base=root)
    match = [c for c in combos if c.combo_id == combo_id]
    if not match:
        known = ", ".join(c.combo_id for c in combos[:5])
        suffix = "..." if len(combos) > 5 else ""
        raise ConfigError(f"unknown combo_id {combo_id!r}; known include {known}{suffix}")
    resolved = match[0].resolved_config
    actual_hash = hash_config(resolved)
    if expected_config_hash is not None and actual_hash != expected_config_hash:
        raise ConfigError(
            f"config_hash mismatch for {combo_id!r}: "
            f"expected {expected_config_hash!r}, got {actual_hash!r}"
        )
    return resolved
