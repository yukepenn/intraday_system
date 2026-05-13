"""CandidateSpec dataclass (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CandidateSpec:
    """Frozen Layer1 candidate (schema ``layer1_candidate_v1``).

    Phase 0/1A defines the type. Phase 6 populates fields from sweep results
    and writes candidate YAMLs.
    """

    schema_version: str = "layer1_candidate_v1"
    candidate_id: str = ""
    strategy: str = ""
    family: str = ""
    symbol: str = ""
    asset: str = ""
    timeframe: str = ""
    side: str = "long_only"
    candidate_rank: int = 0

    config: dict[str, Any] = field(default_factory=dict)
    execution: dict[str, Any] = field(default_factory=dict)
    source: dict[str, Any] = field(default_factory=dict)
    hashes: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    selection: dict[str, Any] = field(default_factory=dict)
