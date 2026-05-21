"""Adapt :class:`SignalMatrix` rows to :class:`TradeIntent` (no execution / PnL)."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from intraday.core.arrays import SignalMatrix
from intraday.core.types import Side
from intraday.execution.intent import TradeIntent


@dataclass(frozen=True)
class SignalAdapterResult:
    intents: tuple[TradeIntent, ...]
    total_entries: int
    valid_intents: int
    skipped_invalid: int
    skip_reasons: dict[str, int]


def build_trade_intents_from_signals(
    signals: SignalMatrix,
    *,
    qty: float,
    max_hold_bars: int,
    candidate_id: int = 1,
    allowed_sides: tuple[int | Side, ...] = (Side.LONG,),
) -> SignalAdapterResult:
    """One entry row -> one intent; invalid rows increment ``skip_reasons``."""
    entry = np.asarray(signals.entry, dtype=bool)
    side = np.asarray(signals.side)
    stop = np.asarray(signals.stop, dtype=np.float64)
    target_r = np.asarray(signals.target_r, dtype=np.float64)
    score = np.asarray(signals.score, dtype=np.float64)
    setup_code = np.asarray(signals.setup_code)

    total_entries = int(np.sum(entry))
    skip_reasons: dict[str, int] = {}
    intents: list[TradeIntent] = []
    allowed_side_ints = {int(s) for s in allowed_sides}

    def bump(reason: str) -> None:
        skip_reasons[reason] = skip_reasons.get(reason, 0) + 1

    if not math.isfinite(qty) or qty <= 0:
        for _ in np.flatnonzero(entry):
            bump("qty_non_positive")
        skipped = total_entries
        return SignalAdapterResult(
            intents=tuple(),
            total_entries=total_entries,
            valid_intents=0,
            skipped_invalid=skipped,
            skip_reasons=skip_reasons,
        )

    if max_hold_bars < 0:
        for _ in range(total_entries):
            bump("max_hold_negative")
        return SignalAdapterResult(
            intents=tuple(),
            total_entries=total_entries,
            valid_intents=0,
            skipped_invalid=total_entries,
            skip_reasons=skip_reasons,
        )

    for i in np.flatnonzero(entry):
        si = int(side[i])
        if si not in (int(Side.LONG), int(Side.SHORT)):
            bump("invalid_side")
            continue
        if si not in allowed_side_ints:
            bump("side_not_allowed")
            continue
        if not math.isfinite(float(stop[i])):
            bump("nonfinite_stop")
            continue
        tr = float(target_r[i])
        if not math.isfinite(tr) or tr <= 0:
            bump("invalid_target_r")
            continue

        intents.append(
            TradeIntent(
                candidate_id=int(candidate_id),
                signal_bar=int(i),
                side=si,
                qty=float(qty),
                raw_stop_price=float(stop[i]),
                target_r=tr,
                max_hold_bars=int(max_hold_bars),
                score=float(score[i]),
                setup_code=int(setup_code[i]),
            )
        )

    valid = len(intents)
    skipped = total_entries - valid
    return SignalAdapterResult(
        intents=tuple(intents),
        total_entries=total_entries,
        valid_intents=valid,
        skipped_invalid=skipped,
        skip_reasons=skip_reasons,
    )


def signal_matrix_to_intents(
    signals: SignalMatrix,
    *,
    qty: float,
    max_hold_bars: int,
    candidate_id: int = 1,
    allowed_sides: tuple[int | Side, ...] = (Side.LONG,),
) -> SignalAdapterResult:
    """Alias for :func:`build_trade_intents_from_signals`."""
    return build_trade_intents_from_signals(
        signals,
        qty=qty,
        max_hold_bars=max_hold_bars,
        candidate_id=candidate_id,
        allowed_sides=allowed_sides,
    )
