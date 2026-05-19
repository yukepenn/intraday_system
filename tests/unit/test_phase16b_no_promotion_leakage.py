"""Phase16B guardrails: repair/rerun only, no promotion leakage."""

from __future__ import annotations

from pathlib import Path

ROOT = Path("artifacts/layer1_10_strategy_rational_expanded_grid_phase16b")


def test_phase16b_guardrails_forbid_promotion_paths() -> None:
    text = (ROOT / "non_promotion_guardrails.md").read_text(encoding="utf-8")

    required = [
        "No candidate YAML",
        "No promotion",
        "No select-dry-run",
        "No Layer2",
        "No Layer3",
        "No WFO",
        "No live/paper",
        "No strategy retuning",
        "No feature semantic changes",
        "No execution truth changes",
        "No prefix slicing",
        "No post-result grid shrinking",
    ]
    for phrase in required:
        assert phrase in text


def test_phase16b_did_not_create_runtime_candidate_yaml() -> None:
    candidate_yamls = [
        p for p in Path("configs/candidates").rglob("*.yaml") if p.name.upper() != "README.YAML"
    ]

    assert candidate_yamls == []
