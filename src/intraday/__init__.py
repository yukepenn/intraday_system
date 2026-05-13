"""intraday_system — array-first intraday research engine.

Strategies produce signals.
Execution produces trades and PnL.
Layer1 produces candidates.
Layer2 selects between candidates.
Layer3 validates frozen systems.
"""

from __future__ import annotations

__version__ = "0.1.0a0"

__all__ = ["__version__"]
