"""Smoke tests for Layer1 select-dry-run CLI."""

from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

import pytest
from intraday.core.paths import repo_root

pytest.importorskip("typer")

from intraday.cli.main import app  # noqa: E402
from typer.testing import CliRunner  # noqa: E402

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    root = repo_root()
    return subprocess.run(
        [sys.executable, "-m", "intraday.cli.main", *args],
        cwd=root,
        capture_output=True,
        text=True,
        env={
            **dict(__import__("os").environ),
            "NO_COLOR": "1",
            "TERM": "dumb",
            "COLUMNS": "120",
        },
    )


def test_select_dry_run_help() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["layer1", "select-dry-run", "--help"])
    assert res.exit_code == 0, (res.stdout, res.stderr)
    combined = _strip_ansi(res.stdout).lower()
    for token in ("sweep-results", "base-config", "grid-config", "output-root"):
        assert token in combined, f"missing {token!r} in help: {combined[:500]!r}"

    proc = _run_cli("layer1", "select-dry-run", "--help")
    assert proc.returncode == 0, proc.stderr
    proc_text = _strip_ansi(proc.stdout + proc.stderr).lower()
    for token in ("sweep-results", "base-config", "grid-config", "output-root"):
        assert token in proc_text, f"missing {token!r} in subprocess help"


def test_select_dry_run_synthetic(tmp_path: Path) -> None:
    root = repo_root()
    from intraday.layer1.grid import load_grid_document, resolve_grid_combos

    doc = load_grid_document(
        root / "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml"
    )
    combo = resolve_grid_combos(doc)[2]
    sweep = tmp_path / "sweep.csv"
    fieldnames = [
        "run_id",
        "combo_id",
        "config_hash",
        "params_json",
        "accepted_trades",
        "rejected_trades",
        "total_r",
        "profit_factor_r",
        "max_drawdown_r",
        "win_rate",
        "signal_entries",
        "skip_reason_counts_json",
    ]
    with sweep.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerow(
            {
                "run_id": "CLI_TEST",
                "combo_id": combo.combo_id,
                "config_hash": combo.config_hash,
                "params_json": combo.params_json,
                "accepted_trades": 124,
                "rejected_trades": 0,
                "total_r": 6.5,
                "profit_factor_r": 1.14,
                "max_drawdown_r": 5.7,
                "win_rate": 0.52,
                "signal_entries": 4380,
                "skip_reason_counts_json": "{}",
            }
        )
    out = root / "artifacts" / "_pytest_layer1_selection_cli" / "out"
    if out.exists():
        for child in out.iterdir():
            if child.is_file():
                child.unlink()
    proc = _run_cli(
        "layer1",
        "select-dry-run",
        "--sweep-results",
        str(sweep),
        "--base-config",
        "configs/strategies/base/pa_buy_sell_close_trend.yaml",
        "--grid-config",
        "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml",
        "--output-root",
        "artifacts/_pytest_layer1_selection_cli/out",
    )
    assert proc.returncode == 0, proc.stderr
    assert "promotion_allowed_now=false" in proc.stdout
    assert (out / "dry_run_selection_results.csv").is_file()
    candidates = root / "configs" / "candidates"
    assert list(candidates.rglob("*.yaml")) == []


def test_select_dry_run_rejects_absolute_output_root(tmp_path: Path) -> None:
    sweep = tmp_path / "sweep.csv"
    sweep.write_text("run_id,combo_id\n", encoding="utf-8")
    proc = _run_cli(
        "layer1",
        "select-dry-run",
        "--sweep-results",
        str(sweep),
        "--base-config",
        "configs/strategies/base/pa_buy_sell_close_trend.yaml",
        "--grid-config",
        "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml",
        "--output-root",
        "/tmp/out",
    )
    combined = (proc.stdout + proc.stderr).lower()
    assert proc.returncode != 0 or "artifacts" in combined
    assert "artifacts" in combined


def test_select_dry_run_rejects_candidates_output_root(tmp_path: Path) -> None:
    sweep = tmp_path / "sweep.csv"
    sweep.write_text("run_id,combo_id\n", encoding="utf-8")
    proc = _run_cli(
        "layer1",
        "select-dry-run",
        "--sweep-results",
        str(sweep),
        "--base-config",
        "configs/strategies/base/pa_buy_sell_close_trend.yaml",
        "--grid-config",
        "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml",
        "--output-root",
        "configs/candidates/l1_pa_controlled_v1/out",
    )
    combined = (proc.stdout + proc.stderr).lower()
    assert proc.returncode != 0 or "configs/candidates" in combined
    assert "configs/candidates" in combined
