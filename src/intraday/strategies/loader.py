"""Strategy config loader."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from intraday.core.config import load_yaml
from intraday.strategies.config_validation import validate_strategy_config_for_name
from intraday.strategies.registry import get_strategy, register_builtin_strategies


def load_strategy_config(path: Path | str) -> dict[str, Any]:
    """Load a strategy base config YAML."""
    return load_yaml(path)


def load_strategy_metadata(path: Path | str) -> dict[str, Any]:
    """Load strategy metadata YAML (audit/review; not runtime truth)."""
    return load_yaml(path)


def load_strategy_grid(path: Path | str) -> dict[str, Any]:
    """Load a strategy grid skeleton YAML."""
    return load_yaml(path)


def resolve_strategy_config(config_or_path: Path | str | Mapping[str, Any]) -> dict[str, Any]:
    """Return a strategy config dict from a path or mapping."""
    if isinstance(config_or_path, Mapping):
        return dict(config_or_path)
    return load_strategy_config(config_or_path)


def validate_strategy_config(strategy_name: str, config: Mapping[str, Any]) -> None:
    """Validate strategy config via registry StrategyDef."""
    register_builtin_strategies()
    defn = get_strategy(strategy_name)
    validate_strategy_config_for_name(strategy_name, config, defn=defn)
