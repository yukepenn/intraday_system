"""Strategy output contract (SignalMatrix semantics)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import SignalMatrix
from intraday.core.errors import ConfigError
from intraday.core.hashing import hash_config

REQUIRED_SIGNAL_COLUMNS: tuple[str, ...] = (
    "entry",
    "side",
    "stop",
    "target_r",
    "score",
    "setup_code",
)

SIGNAL_CONTRACT_VERSION: str = "signal_v1"

LONG_SIDE: int = 1


def compute_signal_hash(
    *,
    strategy_name: str,
    strategy_version: str,
    signal_contract_version: str,
    config: Mapping[str, Any],
    feature_hash: str,
) -> str:
    """Deterministic signal hash over strategy identity + config + features."""
    payload = {
        "strategy": strategy_name,
        "strategy_version": strategy_version,
        "signal_contract_version": signal_contract_version,
        "strategy_config_hash": hash_config(dict(config)),
        "feature_hash": feature_hash,
    }
    return hash_config(payload)


def validate_signal_matrix(signals: SignalMatrix, n_bars: int) -> None:
    """Validate SignalMatrix shape and entry/non-entry conventions."""
    if signals.n_bars != n_bars:
        raise ValueError(f"SignalMatrix n_bars={signals.n_bars} != expected {n_bars}")

    entry = np.asarray(signals.entry, dtype=bool)
    side = np.asarray(signals.side)
    stop = np.asarray(signals.stop, dtype=np.float64)
    target_r = np.asarray(signals.target_r, dtype=np.float64)
    score = np.asarray(signals.score, dtype=np.float64)
    setup_code = np.asarray(signals.setup_code)

    non_entry = ~entry
    if non_entry.any():
        if not np.all(side[non_entry] == 0):
            raise ValueError("non-entry bars must have side=0")
        if not np.all(np.isnan(stop[non_entry])):
            raise ValueError("non-entry bars must have stop=nan")
        if not np.all(np.isnan(target_r[non_entry])):
            raise ValueError("non-entry bars must have target_r=nan")
        if not np.all(np.isnan(score[non_entry])):
            raise ValueError("non-entry bars must have score=nan")
        if not np.all(setup_code[non_entry] == 0):
            raise ValueError("non-entry bars must have setup_code=0")

    if not entry.any():
        return

    if not np.all(side[entry] == LONG_SIDE):
        raise ValueError("entry bars must have side=+1 (long-only Phase 5)")
    if not np.all(np.isfinite(stop[entry])):
        raise ValueError("entry bars must have finite stop")
    if not np.all(np.isfinite(target_r[entry]) & (target_r[entry] > 0)):
        raise ValueError("entry bars must have finite target_r > 0")
    if not np.all(np.isfinite(score[entry])):
        raise ValueError("entry bars must have finite score")
    if not np.all(setup_code[entry] != 0):
        raise ValueError("entry bars must have non-zero setup_code")


def require_feature_columns(
    features_columns: Mapping[str, int],
    required: tuple[str, ...],
    *,
    strategy_name: str,
) -> None:
    """Raise if any required feature column is missing."""
    missing = [c for c in required if c not in features_columns]
    if missing:
        raise ConfigError(
            f"strategy {strategy_name!r} missing required feature columns: {missing!r}"
        )


def clip_finite(arr: np.ndarray, lo: float, hi: float) -> np.ndarray:
    out = np.clip(arr, lo, hi)
    out[~np.isfinite(arr)] = np.nan
    return out
