"""Phase19 design guardrails: no runtime promotion or heavy artifact leakage.

Originally a design-only test. Phase19B legitimately implemented strategies
11-17 runtime files; the design-phase "must-not-exist" guards on those files
have been intentionally retired in the Phase19 Immediate Fix. The remaining
guardrails enforce that the Phase19 design artifact bundle did not leak
runtime/candidate/heavy/binary files and that diagnostic strategies 18-20
remain deferred.
"""

from __future__ import annotations

import csv
from pathlib import Path

ARTIFACT_DIR = Path("artifacts/phase19_brooks_pa_design")

FORBIDDEN_SUFFIXES = {".parquet", ".npy", ".npz", ".memmap", ".log"}
FORBIDDEN_PATH_PARTS = {
    "data/raw",
    "data/curated",
    "data/cache",
    "configs/candidates",
    "configs/layer2",
    "configs/layer3",
    "configs/wfo",
    "configs/live",
    "configs/paper",
    "wfo",
    "live",
    "paper",
    "top_runs",
    "trade_records",
    "equity",
}

PHASE19_DIAGNOSTIC_STRATEGIES_STILL_DEFERRED = {
    "src/intraday/strategies/pa/mtr_reversal_diagnostic.py",
    "src/intraday/strategies/pa/wedge_reversal_diagnostic.py",
    "src/intraday/strategies/pa/climax_reversal_diagnostic.py",
    "configs/features/pa_brooks_opening_v1.yaml",
    "configs/features/pa_brooks_reversal_v1.yaml",
    "configs/features/pa_brooks_magnet_v1.yaml",
}


def _artifact_files() -> list[Path]:
    return [path for path in ARTIFACT_DIR.rglob("*") if path.is_file()]


def test_phase19_artifact_directory_contains_only_csv_and_md() -> None:
    files = _artifact_files()
    assert files
    suffixes = {path.suffix for path in files}
    assert suffixes <= {".csv", ".md"}, f"unexpected suffixes: {suffixes - {'.csv', '.md'}}"
    assert not any(path.suffix in FORBIDDEN_SUFFIXES for path in files)


def test_phase19_source_map_has_no_runtime_candidate_or_layer_leakage() -> None:
    with (ARTIFACT_DIR / "SOURCE_MAP.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    forbidden = []
    for row in rows:
        file_path = row["file_path"].replace("\\", "/")
        if any(part in file_path for part in FORBIDDEN_PATH_PARTS):
            forbidden.append(file_path)
        if Path(file_path).suffix in FORBIDDEN_SUFFIXES:
            forbidden.append(file_path)
    assert forbidden == [], f"forbidden entries in SOURCE_MAP.csv: {forbidden}"


def test_phase19_diagnostic_strategies_18_to_20_still_deferred() -> None:
    """Phase19B implemented 11-17. Diagnostic strategies 18-20 and Brooks
    opening/reversal/magnet feature kernels remain deferred."""

    leaked = [hint for hint in PHASE19_DIAGNOSTIC_STRATEGIES_STILL_DEFERRED if Path(hint).exists()]
    assert leaked == [], (
        "Diagnostic strategies 18-20 and Brooks opening/reversal/magnet feature "
        f"kernels must remain deferred. Leaked: {leaked}"
    )


def test_phase19_validation_records_forbidden_commands_as_not_run() -> None:
    with (ARTIFACT_DIR / "validation_results.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    command_status = {row["command"]: row["status"] for row in rows}
    assert command_status["python -m intraday.cli.main layer1 grid ..."] == "not_run"
    assert command_status["python -m intraday.cli.main layer1 select-dry-run ..."] == "not_run"
    assert command_status["Layer2 / Layer3 / WFO / live / paper commands"] == "not_run"


def test_phase19_file_plan_source_edit_targets_exist() -> None:
    """``source-edit`` rows reference EXISTING files that an implementation
    phase will edit; those must already exist today.

    NOTE: the historical "must not yet exist" guard on ``source``/``config``
    rows was retired in the Phase19 Immediate Fix because Phase19B has
    legitimately implemented strategies 11-17.
    """

    with (ARTIFACT_DIR / "phase19_file_plan.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    edit_rows = [row for row in rows if row["file_type"] == "source-edit"]
    missing_targets = [
        row["future_file_path"] for row in edit_rows if not Path(row["future_file_path"]).exists()
    ]
    assert missing_targets == [], (
        "Phase19 source-edit rows must point at existing files. "
        f"Missing edit targets: {missing_targets}"
    )


def test_phase19_chatgpt_key_tables_confirm_no_runtime_writes() -> None:
    with (ARTIFACT_DIR / "chatgpt_key_tables.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    metrics = {row["metric"]: row["value"] for row in rows}
    for metric in (
        "implementation_code_written",
        "runtime_configs_created",
        "candidate_yaml_created",
        "select_dry_run_run",
        "layer2_created",
        "wfo_run",
        "live_paper_run",
        "economic_claims_made",
        "phase19_strategy_source_files_added",
        "phase19_feature_kernels_added",
        "signal_adapter_modified",
        "execution_modified",
        "current10_strategies_modified",
        "qt_runtime_dependency",
    ):
        assert metrics[metric] == "false", f"metric {metric!r} must be 'false' in Phase19 design"
    assert metrics["actual_layer1_grid_runs"] == "0"
