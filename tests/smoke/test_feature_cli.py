"""Smoke tests for feature CLI (Typer path)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys

import pytest
from intraday.core.paths import repo_root

_HAS_TYPER = importlib.util.find_spec("typer") is not None


@pytest.mark.skipif(not _HAS_TYPER, reason="Typer not installed")
def test_features_list_json() -> None:
    root = repo_root()
    out = subprocess.check_output(
        [sys.executable, "-m", "intraday.cli.main", "features", "list"],
        cwd=str(root),
        text=True,
    )
    data = json.loads(out)
    assert "vwap" in data["builtin_groups"]


@pytest.mark.skipif(not _HAS_TYPER, reason="Typer not installed")
def test_features_inspect_pa_core() -> None:
    root = repo_root()
    out = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "intraday.cli.main",
            "features",
            "inspect",
            "--config",
            "configs/features/pa_core_v1.yaml",
        ],
        cwd=str(root),
        text=True,
    )
    data = json.loads(out)
    assert data["feature_set_id"] == "pa_core_v1"
    assert data["expected_column_count"] == len(data["columns"])
    assert len(data["feature_hash"]) == 64
