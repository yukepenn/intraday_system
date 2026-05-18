"""Layer1 selection dry-run artifact writer tests."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from intraday.cli.layer1_cmds import validate_selection_dry_run_output_root
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.layer1.selection import run_layer1_candidate_selection_dry_run
from intraday.layer1.selection_reports import write_layer1_candidate_selection_dry_run_artifacts

BASE = "configs/strategies/base/pa_buy_sell_close_trend.yaml"
GRID = "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml"
SWEEP = "artifacts/layer1_pa_grid_review_phase6c/sweep_results_review.csv"


def test_output_root_under_artifacts_accepted() -> None:
    root = repo_root()
    resolved = validate_selection_dry_run_output_root(
        "artifacts/layer1_pa_candidate_selection_dry_run_phase7b",
        root=root,
    )
    assert resolved.is_relative_to(root / "artifacts")


@pytest.mark.parametrize(
    "output_root",
    [
        "/tmp/out",
        "C:\\temp\\out",
        "\\\\server\\share\\out",
        "configs/candidates/l1_pa_controlled_v1/out",
        "artifacts/../configs/candidates/x",
        ".",
        "",
        "   ",
    ],
)
def test_output_root_rejected(output_root: str) -> None:
    with pytest.raises(ConfigError):
        validate_selection_dry_run_output_root(output_root, root=repo_root())


def test_write_dry_run_artifacts(tmp_path: Path) -> None:
    root = repo_root()
    result = run_layer1_candidate_selection_dry_run(
        sweep_results_path=root / SWEEP,
        base_config_path=root / BASE,
        grid_config_path=root / GRID,
    )
    write_layer1_candidate_selection_dry_run_artifacts(result, tmp_path)

    results_csv = tmp_path / "dry_run_selection_results.csv"
    assert results_csv.is_file()
    with results_csv.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == result.row_count
    assert all(r["promotion_allowed_now"] == "false" for r in rows)
    for r in rows:
        json.loads(r["reject_reasons_json"])
        json.loads(r["warning_flags_json"])
    text = results_csv.read_text(encoding="utf-8")
    assert "D:\\" not in text
    assert "OneDrive" not in text

    write_layer1_candidate_selection_dry_run_artifacts(result, tmp_path)
    assert results_csv.read_text(encoding="utf-8") == text

    candidates = root / "configs" / "candidates"
    yaml_files = list(candidates.rglob("*.yaml")) + list(candidates.rglob("*.yml"))
    assert yaml_files == []


def _malformed_metric_sweep_row(
    combo_id: str, *, total_r: str, profit_factor_r: str
) -> dict[str, object]:
    root = repo_root()
    from intraday.layer1.grid import load_grid_document, resolve_grid_combos

    doc = load_grid_document(root / GRID)
    combos = {c.combo_id: c for c in resolve_grid_combos(doc)}
    combo = combos[combo_id]
    return {
        "run_id": "MALFORMED_METRICS",
        "combo_id": combo_id,
        "config_hash": combo.config_hash,
        "params_json": combo.params_json,
        "signal_entries": 100,
        "accepted_trades": 120,
        "rejected_trades": 0,
        "total_r": total_r,
        "avg_r": 0.05,
        "median_r": 0.1,
        "win_rate": 0.52,
        "profit_factor_r": profit_factor_r,
        "max_drawdown_r": 5.0,
        "skip_reason_counts_json": "{}",
        "exit_reason_counts_json": "{}",
        "reject_reason_counts_json": "{}",
        "adapter_skip_reasons_json": "{}",
        "feature_hash": "x",
        "signal_hash": "y",
        "execution_mode": "reference",
    }


def test_write_dry_run_artifacts_malformed_metrics_do_not_abort(tmp_path: Path) -> None:
    import csv as csv_mod

    from intraday.layer1.selection import run_layer1_candidate_selection_dry_run

    root = repo_root()
    sweep_path = tmp_path / "malformed_sweep.csv"
    rows = [
        _malformed_metric_sweep_row("combo_0001", total_r="not_a_number", profit_factor_r="1.1"),
        _malformed_metric_sweep_row("combo_0002", total_r="nan", profit_factor_r="inf"),
    ]
    fieldnames = list(rows[0].keys())
    with sweep_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv_mod.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    result = run_layer1_candidate_selection_dry_run(
        sweep_results_path=sweep_path,
        base_config_path=root / BASE,
        grid_config_path=root / GRID,
    )
    out = tmp_path / "dry_run_out"
    write_layer1_candidate_selection_dry_run_artifacts(result, out)

    md_text = (out / "dry_run_selection_results.md").read_text(encoding="utf-8")
    assert "invalid" in md_text
    assert (out / "dry_run_selection_results.csv").is_file()
