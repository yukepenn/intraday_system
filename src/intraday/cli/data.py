"""Data subcommand implementations.

Currently the canonical command implementations live in ``cli.main``; this module
re-exports them for future expansion (ingest, normalize, validate).
"""

from __future__ import annotations

from intraday.cli.main import cmd_data_inventory

__all__ = ["cmd_data_inventory"]
