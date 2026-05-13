"""Fast (Numba-accelerated) execution path (skeleton).

The fast engine MUST parity-match the reference engine on every covered
scenario. Implementation lands in Phase 3 with parity tests from day one.
"""

from __future__ import annotations

import numpy as np

from intraday.core.errors import IntradaySystemError


def simulate_trade_paths_fast(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    session_id: np.ndarray,
    minute: np.ndarray,
    intents: np.ndarray,
    spec_array: np.ndarray,
    management_array: np.ndarray | None = None,
) -> np.ndarray:
    """Batch-simulate intents using packed NumPy arrays. NOT YET IMPLEMENTED (Phase 3).

    Output: structured array with shape (N_intents,) matching TradeResult fields.
    """
    raise IntradaySystemError(
        "simulate_trade_paths_fast is not implemented yet (Phase 3). "
        "Must parity-match simulate_trade_path_reference once implemented."
    )
