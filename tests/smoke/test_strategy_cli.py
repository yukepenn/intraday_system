"""Smoke tests for strategy CLI (Typer path)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys

import pytest
from intraday.core.paths import repo_root

_HAS_TYPER = importlib.util.find_spec("typer") is not None


@pytest.mark.skipif(not _HAS_TYPER, reason="Typer not installed")
def test_strategies_list_json() -> None:
    root = repo_root()
    out = subprocess.check_output(
        [sys.executable, "-m", "intraday.cli.main", "strategies", "list"],
        cwd=str(root),
        text=True,
    )
    data = json.loads(out)
    assert "pa_buy_sell_close_trend" in data["strategies"]


@pytest.mark.skipif(not _HAS_TYPER, reason="Typer not installed")
def test_strategies_inspect_pa() -> None:
    root = repo_root()
    out = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "intraday.cli.main",
            "strategies",
            "inspect",
            "--strategy",
            "pa_buy_sell_close_trend",
            "--config",
            "configs/strategies/base/pa_buy_sell_close_trend.yaml",
        ],
        cwd=str(root),
        text=True,
    )
    data = json.loads(out)
    assert data["strategy"] == "pa_buy_sell_close_trend"
    assert data["required_feature_set"] == "pa_core_v1"
    assert "body_pct" in data["required_feature_columns"]
