"""Logging helpers (skeleton)."""

from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a project-scoped logger."""
    logger = logging.getLogger(name if name.startswith("intraday") else f"intraday.{name}")
    return logger
