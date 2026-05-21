"""Phase19A no-runtime-leakage guardrails.

NOTE: Phase19B legitimately created strategies 11-17 runtime files (per the
Phase19 plan). The two design-only guardrails that asserted those files must
NOT exist have been intentionally retired in the Phase19 Immediate Fix; the
remaining guardrails enforce that no candidate/Layer2/Layer3/WFO/live/paper
configs or heavy run outputs leaked through Phase19A.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Strategies 18-20 (diagnostic) must remain deferred until an explicit later phase.
DEFERRED_DIAGNOSTIC_STRATEGY_FILES = (
    "mtr_reversal_diagnostic.py",
    "wedge_reversal_diagnostic.py",
    "climax_reversal_diagnostic.py",
)


def test_phase19a_diagnostic_strategies_18_to_20_still_deferred() -> None:
    """Phase19B implemented 11-17. Strategies 18-20 remain deferred."""
    strategy_dir = REPO / "src" / "intraday" / "strategies" / "pa"
    leaked = [name for name in DEFERRED_DIAGNOSTIC_STRATEGY_FILES if (strategy_dir / name).exists()]
    assert leaked == [], (
        "Strategies 18-20 (diagnostic) must remain deferred per Phase19 plan. " f"Leaked: {leaked}"
    )


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
