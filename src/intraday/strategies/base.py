"""StrategyDef dataclass."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from intraday.strategies.contracts import SIDE_MODE_LONG_ONLY


@dataclass(frozen=True)
class StrategyDef:
    """Definition of one strategy.

    ``generate_reference`` is the truth path. ``generate_fast`` (optional) is
    the parity-tested Numba path. ``validate_config`` is a config-schema check.

    The optional ``setup_code_long`` / ``setup_code_short`` / ``allowed_side_modes``
    / ``default_side_mode`` / ``required_feature_columns`` fields make
    StrategyDef the authoritative inspect-time metadata source so that the CLI
    ``strategies inspect`` command does not have to rely on per-strategy
    hard-coded constants.
    """

    name: str
    family: str
    version: str
    required_feature_set: str
    signal_contract_version: str
    generate_reference: Callable
    generate_fast: Callable | None = None
    validate_config: Callable | None = None
    setup_code_long: int | None = None
    setup_code_short: int | None = None
    allowed_side_modes: tuple[str, ...] = (SIDE_MODE_LONG_ONLY,)
    default_side_mode: str = SIDE_MODE_LONG_ONLY
    required_feature_columns: tuple[str, ...] = ()
