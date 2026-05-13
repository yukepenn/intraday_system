"""Management modes and ManagementPlan (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class ScaleOutRule:
    trigger_r: float
    exit_fraction: float


@dataclass(frozen=True)
class TrailingRule:
    activate_after_r: float
    trail_distance_r: float


@dataclass(frozen=True)
class NoFollowThroughRule:
    check_after_bars: int
    min_favorable_r: float
    exit_fraction: float


@dataclass(frozen=True)
class ManagementPlan:
    mode: Literal["fixed_r", "scaleout_trail", "scaleout", "trailing", "no_followthrough"]
    scale_outs: tuple[ScaleOutRule, ...] = field(default_factory=tuple)
    trailing: TrailingRule | None = None
    no_followthrough: NoFollowThroughRule | None = None
