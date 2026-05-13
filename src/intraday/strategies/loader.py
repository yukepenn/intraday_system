"""Strategy config loader (skeleton)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from intraday.core.config import load_yaml


def load_strategy_config(path: Path | str) -> dict[str, Any]:
    """Load a strategy base or grid YAML and return its dict."""
    return load_yaml(path)
