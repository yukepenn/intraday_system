"""Phase16B artifact schema checks."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path("artifacts/layer1_10_strategy_rational_expanded_grid_phase16b")


EXPECTED_COLUMNS = {
    "SOURCE_MAP.csv": [
        "file_path",
        "purpose",
        "required_for_review",
        "generated_or_source",
        "local_only_dependency",
        "notes",
    ],
    "chatgpt_key_tables.csv": ["section", "item", "metric", "value", "interpretation"],
    "validation_results.csv": ["command", "status", "exit_code", "notes"],
    "phase16b_run_manifest.csv": [
        "run_id",
        "strategy",
        "symbol",
        "window",
        "config_path",
        "previous_phase16_status",
        "phase16b_action",
        "phase16b_run_status",
        "elapsed_seconds",
        "output_artifact_root",
        "notes",
    ],
    "remaining_grid_run_summary.csv": [
        "strategy",
        "window",
        "combo_count",
        "attempted",
        "completed",
        "blocked",
        "reason_if_blocked",
        "notes",
    ],
    "artifact_schema_validation.csv": [
        "artifact_path",
        "artifact_type",
        "parse_ok",
        "expected_columns_ok",
        "row_count",
        "issue",
        "notes",
    ],
}


def test_phase16b_required_csv_artifacts_parse() -> None:
    for name, expected in EXPECTED_COLUMNS.items():
        path = ROOT / name
        assert path.is_file(), name
        with path.open(encoding="utf-8", newline="") as fh:
            rdr = csv.DictReader(fh)
            assert rdr.fieldnames is not None
            for col in expected:
                assert col in rdr.fieldnames
            assert list(rdr), name


def test_phase16b_manifest_completed_all_configs() -> None:
    with (ROOT / "phase16b_run_manifest.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 20
    assert {row["phase16b_run_status"] for row in rows} == {"pass"}
    assert sum(int(row["phase16b_run_status"] == "pass") for row in rows) == 20
