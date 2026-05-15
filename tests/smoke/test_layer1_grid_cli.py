"""Smoke tests for Layer1 grid CLI."""

from __future__ import annotations

import pytest

pytest.importorskip("typer")

from intraday.cli.main import app  # noqa: E402
from typer.testing import CliRunner  # noqa: E402


def test_layer1_grid_help() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["layer1", "grid", "--help"])
    assert res.exit_code == 0


def test_layer1_grid_inspect_help() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["layer1", "grid-inspect", "--help"])
    assert res.exit_code == 0


def test_layer1_grid_inspect_repo_config() -> None:
    runner = CliRunner()
    cfg = "configs/layer1/controlled_pa_qqq_2024h1.yaml"
    res = runner.invoke(app, ["layer1", "grid-inspect", "--config", cfg])
    assert res.exit_code == 0
    assert "combo_count" in res.stdout
    assert "16" in res.stdout
