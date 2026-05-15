"""Tests for Layer1 grid report writers."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from intraday.core.paths import repo_root
from intraday.layer1.reports import write_layer1_grid_artifacts
from intraday.layer1.result import Layer1GridResult, Layer1GridRow


def _row(
    *,
    combo_id: str,
    params: str,
    total_r: float,
    acc: int,
    pfr: float = 0.0,
) -> Layer1GridRow:
    return Layer1GridRow(
        run_id="GRID_R",
        combo_id=combo_id,
        config_hash="h" + combo_id,
        params_json=params,
        signal_entries=1,
        valid_intents=1,
        executed_results=1,
        accepted_trades=acc,
        rejected_trades=0,
        total_r=total_r,
        avg_r=total_r if acc else 0.0,
        median_r=total_r if acc else 0.0,
        win_rate=1.0 if acc else 0.0,
        profit_factor_r=pfr,
        max_drawdown_r=0.0,
        avg_bars_held=1.0 if acc else 0.0,
        exit_reason_counts_json="{}",
        reject_reason_counts_json="{}",
        skip_reason_counts_json=json.dumps({"invalid_signal": 0}, sort_keys=True),
        adapter_skip_reasons_json="{}",
        feature_hash="fh",
        signal_hash="sh",
        execution_mode="reference",
    )


def test_grid_artifact_writes_and_sweep_rows(tmp_path: Path) -> None:
    rows = (
        _row(combo_id="combo_0001", params='{"a":1}', total_r=2.0, acc=1, pfr=2.0),
        _row(combo_id="combo_0002", params='{"a":2}', total_r=1.0, acc=1, pfr=1.0),
        _row(combo_id="combo_0003", params='{"a":3}', total_r=0.0, acc=0, pfr=0.0),
    )
    res = Layer1GridResult(
        run_id="GRID_R",
        symbol="QQQ",
        start="2024-01-01",
        end="2024-01-02",
        combo_count=3,
        rows=rows,
        feature_hash="fh",
        execution_mode="reference",
    )
    write_layer1_grid_artifacts(res, tmp_path)

    sweep_p = tmp_path / "sweep_results.csv"
    assert sweep_p.is_file()
    with sweep_p.open(encoding="utf-8") as fh:
        rdr = list(csv.DictReader(fh))
    assert len(rdr) == 3
    for row in rdr:
        json.loads(row["params_json"])
    raw = sweep_p.read_text(encoding="utf-8")
    assert ":\\\\" not in raw  # no Windows absolute-style paths in cell text

    top = tmp_path / "top_rows_by_total_r.csv"
    with top.open(encoding="utf-8") as fh:
        trows = list(csv.DictReader(fh))
    assert trows[0]["combo_id"] == "combo_0001"
    assert trows[1]["combo_id"] == "combo_0002"


def test_grid_reports_use_repo_paths_independent(tmp_path: Path) -> None:
    """Reports receive an explicit output dir; content has no repo-root leakage."""
    row = _row(combo_id="combo_0001", params="{}", total_r=0.0, acc=0)
    res = Layer1GridResult(
        run_id="X",
        symbol="Q",
        start="2024-01-01",
        end="2024-01-02",
        combo_count=1,
        rows=(row,),
        feature_hash="f",
        execution_mode="reference",
    )
    write_layer1_grid_artifacts(res, tmp_path)
    root = str(repo_root())
    for p in tmp_path.glob("*.csv"):
        assert root not in p.read_text(encoding="utf-8")
