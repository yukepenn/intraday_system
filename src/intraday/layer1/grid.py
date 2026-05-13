"""Layer1 grid resolver.

Pure config logic. Central to the build plan, so it is implemented now (Phase 0/1A)
and unit-tested in tests/unit/test_layer1_grid.py.

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
from typing import Any

__all__ = [
    "expand_grid",
    "normalize_override_mapping",
    "resolve_grid_document",
]


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
    """
    if not grid:
        return [{}]
    axes: list[tuple[tuple[str, ...], list[Any]]] = []
    for key, values in grid.items():
        if not isinstance(key, str):
            raise TypeError(f"grid keys must be strings, got {type(key)!r}")
        if not isinstance(values, list):
            raise TypeError(
                f"grid axis values must be a list, got {type(values)!r} for {key!r}"
            )
        if not values:
            raise ValueError(f"grid axis {key!r} has empty value list")
        path = tuple(p for p in key.split(".") if p)
        axes.append((path, values))

    combos: list[dict[tuple[str, ...], Any]] = []
    for product in itertools.product(*(vals for _, vals in axes)):
        combo: dict[tuple[str, ...], Any] = {}
        for (path, _), val in zip(axes, product, strict=False):
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
        raise ValueError(
            f"fixed/grid key overlap is forbidden: {names!r}"
        )


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
