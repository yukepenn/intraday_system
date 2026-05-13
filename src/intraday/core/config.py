"""YAML config helpers.

Configs are runtime truth. These helpers do minimal validation. Pydantic-based
schemas live next to the consumers that own them.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import yaml

from intraday.core.errors import ConfigError


def load_yaml(path: Path | str) -> dict[str, Any]:
    """Load a YAML file and return a dict (rejects non-dict roots)."""
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"config file not found: {p}")
    with open(p, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"YAML root must be a mapping, got {type(data).__name__}: {p}")
    return data


def write_yaml(path: Path | str, data: Mapping[str, Any], *, sort_keys: bool = False) -> None:
    """Write ``data`` as YAML to ``path`` (creates parents)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(
            dict(data),
            fh,
            sort_keys=sort_keys,
            default_flow_style=False,
            allow_unicode=True,
        )


def require_keys(
    config: Mapping[str, Any],
    keys: Iterable[str],
    *,
    where: str = "config",
) -> None:
    """Raise ConfigError if any of ``keys`` is missing from ``config``."""
    missing = [k for k in keys if k not in config]
    if missing:
        raise ConfigError(f"missing required keys in {where}: {missing!r}")


def resolve_path(value: str | Path, base: Path | str | None = None) -> Path:
    """Resolve a config path against ``base`` if it's relative; absolute paths pass through."""
    p = Path(value)
    if p.is_absolute():
        return p
    if base is None:
        return p
    return Path(base) / p
