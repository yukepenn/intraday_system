"""IO helpers (skeleton)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json(path: Path | str, data: Any, *, indent: int = 2) -> None:
    """Write JSON to ``path`` with consistent formatting."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=indent, sort_keys=True, ensure_ascii=False)
        fh.write("\n")


def read_json(path: Path | str) -> Any:
    """Read JSON from ``path``."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)
