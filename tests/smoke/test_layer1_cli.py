"""Smoke tests for Layer1 CLI."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys

import pytest
from intraday.core.paths import repo_root

_HAS_TYPER = importlib.util.find_spec("typer") is not None


@pytest.mark.skipif(not _HAS_TYPER, reason="Typer not installed")
def test_layer1_help() -> None:
    root = repo_root()
    subprocess.check_call(
        [sys.executable, "-m", "intraday.cli.main", "layer1", "--help"],
        cwd=str(root),
    )


@pytest.mark.skipif(not _HAS_TYPER, reason="Typer not installed")
def test_layer1_inspect_repo_config() -> None:
    root = repo_root()
    out = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "intraday.cli.main",
            "layer1",
            "inspect",
            "--config",
            "configs/layer1/smoke_pa_qqq_2024h1.yaml",
        ],
        cwd=str(root),
        text=True,
    )
    data = json.loads(out)
    assert data["run_id"] == "L1_PA_QQQ_2024H1_SMOKE_V1"
