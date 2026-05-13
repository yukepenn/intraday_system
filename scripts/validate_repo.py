"""Thin wrapper: ``python scripts/validate_repo.py`` runs structure validation.

Equivalent to ``python -m intraday.cli.main validate structure``.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the in-tree src/ layout is importable without an install.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from intraday.cli.main import cmd_validate_structure  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(cmd_validate_structure())
