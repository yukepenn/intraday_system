"""Validation subcommand implementations.

Currently the canonical command implementations live in ``cli.main``; this module
re-exports them for future expansion (parity, candidates, artifacts).
"""

from __future__ import annotations

from intraday.cli.main import cmd_validate_structure

__all__ = ["cmd_validate_structure"]
