"""FeatureDef dataclass."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureDef:
    """Definition of one named feature kernel.

    ``compute_reference`` is the truth path. ``compute_fast`` (optional) is the
    parity-tested Numba path.
    """

    name: str
    version: str
    required_inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    compute_reference: Callable
    compute_fast: Callable | None = None
