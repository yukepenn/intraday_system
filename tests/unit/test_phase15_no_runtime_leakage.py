from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_phase15_created_no_runtime_layer1_configs() -> None:
    layer1_configs = ROOT / "configs" / "layer1"
    phase15_yaml = [
        path
        for path in layer1_configs.rglob("*.yaml")
        if "phase15" in path.as_posix().lower()
        or "result_review" in path.as_posix().lower()
        or "focused_diagnostic" in path.as_posix().lower()
    ]
    assert phase15_yaml == []


def test_phase15_created_no_candidate_yaml() -> None:
    candidate_root = ROOT / "configs" / "candidates"
    assert list(candidate_root.rglob("*.yaml")) == []
    assert list(candidate_root.rglob("*.yml")) == []


def test_phase15_created_no_layer2_wfo_or_live_configs() -> None:
    for rel in ("configs/layer2", "configs/layer3", "configs/wfo", "configs/live", "configs/paper"):
        root = ROOT / rel
        if root.exists():
            assert list(root.rglob("*.yaml")) == []
            assert list(root.rglob("*.yml")) == []


def test_phase15_artifacts_are_review_only() -> None:
    phase15 = ROOT / "artifacts" / "layer1_strategy_library_result_review_phase15"
    assert phase15.is_dir()
    assert list(phase15.rglob("*.parquet")) == []
    assert list(phase15.rglob("*.npy")) == []
    assert list(phase15.rglob("*.npz")) == []
    assert not any(
        "trade" in path.name.lower() and path.suffix == ".csv" for path in phase15.rglob("*")
    )
