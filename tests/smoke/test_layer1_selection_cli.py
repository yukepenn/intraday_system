"""Smoke tests for Layer1 select-dry-run CLI."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from intraday.core.paths import repo_root


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    root = repo_root()
    return subprocess.run(
        [sys.executable, "-m", "intraday.cli.main", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def test_select_dry_run_help() -> None:
    proc = _run_cli("layer1", "select-dry-run", "--help")
    assert proc.returncode == 0
    assert "sweep-results" in proc.stdout


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
    out = tmp_path / "out"
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
        str(out),
    )
    assert proc.returncode == 0, proc.stderr
    assert "promotion_allowed_now=false" in proc.stdout
    assert (out / "dry_run_selection_results.csv").is_file()
    candidates = root / "configs" / "candidates"
    assert list(candidates.rglob("*.yaml")) == []
