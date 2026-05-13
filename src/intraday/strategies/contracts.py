"""Strategy output contract (skeleton).

A valid SignalMatrix must contain: entry, side, stop, target_r, score, setup_code.
Phase 5 will add a contract checker that runs against generated SignalMatrices.
"""

from __future__ import annotations

REQUIRED_SIGNAL_COLUMNS: tuple[str, ...] = (
    "entry",
    "side",
    "stop",
    "target_r",
    "score",
    "setup_code",
)

SIGNAL_CONTRACT_VERSION: str = "signal_v1"
