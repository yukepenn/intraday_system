"""StrategyDef dataclass."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyDef:
    """Definition of one strategy.

    ``generate_reference`` is the truth path. ``generate_fast`` (optional) is
    the parity-tested Numba path. ``validate_config`` is a config-schema check.
    """

    name: str
    family: str
    version: str
    required_feature_set: str
    signal_contract_version: str
    generate_reference: Callable
    generate_fast: Callable | None = None
    validate_config: Callable | None = None
