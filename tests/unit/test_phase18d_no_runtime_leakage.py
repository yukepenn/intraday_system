"""Phase18D guardrails: no runtime promotion or heavy artifact leakage."""

from __future__ import annotations

import csv
from pathlib import Path

ARTIFACT_DIR = Path("artifacts/current10_refined_readiness_phase18d")

FORBIDDEN_SUFFIXES = {".parquet", ".npy", ".npz", ".memmap", ".log"}
FORBIDDEN_PATH_PARTS = {
    "data/raw",
    "data/curated",
    "data/cache",
    "configs/candidates",
    "configs/layer2",
    "configs/layer3",
    "wfo",
    "live",
    "paper",
    "top_runs",
    "trade_records",
    "equity",
}


def _artifact_files() -> list[Path]:
    return [path for path in ARTIFACT_DIR.rglob("*") if path.is_file()]


def test_phase18d_artifact_directory_contains_only_csv_and_md() -> None:
    assert _artifact_files()
    assert {path.suffix for path in _artifact_files()} <= {".csv", ".md"}
    assert not any(path.suffix in FORBIDDEN_SUFFIXES for path in _artifact_files())


def test_phase18d_source_map_has_no_runtime_candidate_or_layer_leakage() -> None:
    with (ARTIFACT_DIR / "SOURCE_MAP.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    forbidden = []
    for row in rows:
        file_path = row["file_path"].replace("\\", "/")
        if any(part in file_path for part in FORBIDDEN_PATH_PARTS):
            forbidden.append(file_path)
        if Path(file_path).suffix in FORBIDDEN_SUFFIXES:
            forbidden.append(file_path)
    assert forbidden == []


def test_phase18d_validation_records_forbidden_commands_as_not_run() -> None:
    with (ARTIFACT_DIR / "validation_results.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    command_status = {row["command"]: row["status"] for row in rows}
    assert command_status["python -m intraday.cli.main layer1 grid ..."] == "not_run"
    assert command_status["python -m intraday.cli.main layer1 select-dry-run ..."] == "not_run"
    assert command_status["Layer2 / Layer3 / WFO / live / paper commands"] == "not_run"


def test_phase18d_layer1_inspect_rows_are_not_actual_grid_runs() -> None:
    with (ARTIFACT_DIR / "v2_layer1_grid_inspect_summary.csv").open(
        newline="", encoding="utf-8"
    ) as f:
        rows = list(csv.DictReader(f))

    assert rows
    assert {row["actual_grid_run"] for row in rows} == {"false"}
