"""Phase19A no-runtime-leakage guardrails."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

FORBIDDEN_STRATEGY_FILES = (
    "second_entry_pullback.py",
    "trading_range_bls_hs.py",
    "failed_breakout_trap.py",
    "opening_reversal_sr.py",
    "breakout_pullback_continuation.py",
    "tight_channel_pullback.py",
    "broad_channel_zone.py",
    "mtr_reversal_diagnostic.py",
    "wedge_reversal_diagnostic.py",
    "climax_reversal_diagnostic.py",
)


def test_phase19a_did_not_create_strategies_11_to_20_source_files() -> None:
    strategy_dir = REPO / "src" / "intraday" / "strategies" / "pa"
    leaked = [name for name in FORBIDDEN_STRATEGY_FILES if (strategy_dir / name).exists()]
    assert leaked == []


def test_phase19a_did_not_create_phase19_strategy_runtime_yamls() -> None:
    forbidden_dirs = (
        REPO / "configs" / "strategies" / "base" / "phase19",
        REPO / "configs" / "strategies" / "grids" / "phase19",
        REPO / "configs" / "strategies" / "metadata" / "phase19",
        REPO / "configs" / "layer1" / "phase19_brooks_pa_grid_inspect",
    )
    leaked = [str(path.relative_to(REPO)) for path in forbidden_dirs if path.exists()]
    assert leaked == []


def test_phase19a_did_not_create_candidate_layer2_layer3_wfo_live_or_paper_configs() -> None:
    forbidden = []
    for rel in (
        "configs/candidates",
        "configs/layer2",
        "configs/layer3",
        "configs/wfo",
        "configs/live",
        "configs/paper",
    ):
        root = REPO / rel
        forbidden.extend(path for path in root.rglob("*.yaml") if path.is_file())
    assert forbidden == []


def test_phase19a_did_not_create_actual_layer1_grid_outputs_or_heavy_artifacts() -> None:
    artifact_dir = REPO / "artifacts" / "phase19a_side_support_brooks_feature_foundation"
    assert artifact_dir.exists()
    forbidden_suffixes = {".parquet", ".npy", ".npz", ".memmap", ".log"}
    leaked = [
        str(path.relative_to(REPO))
        for path in artifact_dir.rglob("*")
        if path.is_file()
        and (path.suffix in forbidden_suffixes or "runs" in path.parts or "top_runs" in path.parts)
    ]
    assert leaked == []
