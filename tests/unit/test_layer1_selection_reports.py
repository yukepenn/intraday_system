"""Layer1 selection dry-run artifact writer tests."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from intraday.core.paths import repo_root
from intraday.layer1.selection import run_layer1_candidate_selection_dry_run
from intraday.layer1.selection_reports import write_layer1_candidate_selection_dry_run_artifacts

BASE = "configs/strategies/base/pa_buy_sell_close_trend.yaml"
GRID = "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml"
SWEEP = "artifacts/layer1_pa_grid_review_phase6c/sweep_results_review.csv"


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
