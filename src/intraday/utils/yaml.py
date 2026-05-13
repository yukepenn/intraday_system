"""YAML helpers (thin re-exports from core.config)."""

from __future__ import annotations

from intraday.core.config import load_yaml, write_yaml

__all__ = ["load_yaml", "write_yaml"]
