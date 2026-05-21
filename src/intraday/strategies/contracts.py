"""Strategy output contract (SignalMatrix semantics)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from intraday.core.arrays import SignalMatrix
from intraday.core.errors import ConfigError
from intraday.core.hashing import hash_config
from intraday.core.types import Side

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
SHORT_SIDE: int = -1
SIDE_MODE_LONG_ONLY: str = "long_only"
SIDE_MODE_SHORT_ONLY: str = "short_only"
SIDE_MODE_BOTH: str = "both"
VALID_SIDE_MODES: frozenset[str] = frozenset(
    {SIDE_MODE_LONG_ONLY, SIDE_MODE_SHORT_ONLY, SIDE_MODE_BOTH}
)


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


def normalize_side_mode(signal_config: Mapping[str, Any], *, where: str = "signal") -> str:
    """Return the side mode while preserving legacy ``signal.side`` compatibility."""
    raw_side_mode = signal_config.get("side_mode")
    raw_legacy_side = signal_config.get("side")

    if raw_side_mode is None:
        raw_side_mode = raw_legacy_side if raw_legacy_side is not None else SIDE_MODE_LONG_ONLY

    mode = str(raw_side_mode)
    if mode not in VALID_SIDE_MODES:
        raise ConfigError(
            f"{where}.side_mode must be one of {sorted(VALID_SIDE_MODES)}, got {mode!r}"
        )

    if raw_legacy_side is not None:
        legacy = str(raw_legacy_side)
        if legacy not in VALID_SIDE_MODES:
            raise ConfigError(
                f"{where}.side must be one of {sorted(VALID_SIDE_MODES)}, got {legacy!r}"
            )
        if legacy != mode:
            raise ConfigError(f"{where}.side={legacy!r} conflicts with side_mode={mode!r}")

    return mode


def allowed_sides_for_mode(side_mode: str) -> tuple[int, ...]:
    """Map a validated side mode to allowed ``Side`` integer values."""
    if side_mode == SIDE_MODE_LONG_ONLY:
        return (int(Side.LONG),)
    if side_mode == SIDE_MODE_SHORT_ONLY:
        return (int(Side.SHORT),)
    if side_mode == SIDE_MODE_BOTH:
        return (int(Side.LONG), int(Side.SHORT))
    raise ConfigError(f"unknown side_mode: {side_mode!r}")


def validate_signal_matrix(
    signals: SignalMatrix,
    n_bars: int,
    *,
    reference_close: np.ndarray | None = None,
) -> None:
    """Validate SignalMatrix shape and entry/non-entry conventions."""
    if signals.n_bars != n_bars:
        raise ValueError(f"SignalMatrix n_bars={signals.n_bars} != expected {n_bars}")
    if reference_close is not None:
        if not isinstance(reference_close, np.ndarray):
            raise TypeError("reference_close must be a numpy ndarray")
        if reference_close.shape != (n_bars,):
            raise ValueError(
                f"reference_close shape {reference_close.shape!r} != expected ({n_bars},)"
            )

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

    entry_side = side[entry]
    if not np.all((entry_side == LONG_SIDE) | (entry_side == SHORT_SIDE)):
        raise ValueError("entry bars must have side in {+1, -1}")
    if not np.all(np.isfinite(stop[entry])):
        raise ValueError("entry bars must have finite stop")
    if not np.all(np.isfinite(target_r[entry]) & (target_r[entry] > 0)):
        raise ValueError("entry bars must have finite target_r > 0")
    if not np.all(np.isfinite(score[entry])):
        raise ValueError("entry bars must have finite score")
    if not np.all(setup_code[entry] != 0):
        raise ValueError("entry bars must have non-zero setup_code")

    if reference_close is not None:
        close = np.asarray(reference_close, dtype=np.float64)
        long_entry = entry & (side == LONG_SIDE)
        short_entry = entry & (side == SHORT_SIDE)
        if long_entry.any() and not np.all(stop[long_entry] < close[long_entry]):
            raise ValueError("long entry bars must have stop below reference close")
        if short_entry.any() and not np.all(stop[short_entry] > close[short_entry]):
            raise ValueError("short entry bars must have stop above reference close")


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
