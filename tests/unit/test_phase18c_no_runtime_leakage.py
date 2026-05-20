"""Phase18C no-runtime-leakage guardrails."""

from __future__ import annotations

import subprocess

from intraday.core.paths import repo_root

ARTIFACT_DIR = repo_root() / "artifacts/existing_10_strategy_refinement_repair_phase18c"


def test_phase18c_does_not_create_candidate_layer2_layer3_or_live_configs() -> None:
    root = repo_root()
    phase_paths = [
        p.relative_to(root).as_posix()
        for p in root.rglob("*phase18c*")
        if ".git" not in p.parts and "__pycache__" not in p.parts
    ]
    forbidden_tokens = (
        "configs/candidates/",
        "configs/layer2/",
        "configs/layer3/",
        "wfo",
        "live",
        "paper",
    )
    assert not any(any(token in path.lower() for token in forbidden_tokens) for path in phase_paths)


def test_phase18c_artifact_dir_contains_only_review_summaries() -> None:
    forbidden_suffixes = {".parquet", ".npy", ".npz", ".memmap", ".log"}
    forbidden_names = {"trades", "equity", "top_runs", "runs"}
    for path in ARTIFACT_DIR.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ARTIFACT_DIR).as_posix().lower()
        assert path.suffix.lower() not in forbidden_suffixes
        assert not any(token in rel for token in forbidden_names)


def test_phase18c_source_map_does_not_include_codex_review() -> None:
    source_map = (ARTIFACT_DIR / "SOURCE_MAP.csv").read_text(encoding="utf-8")
    assert "CODEX_REVIEW.md" not in source_map


def test_phase18c_codex_review_not_modified_in_worktree() -> None:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", "CODEX_REVIEW.md"],
        cwd=repo_root(),
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == ""
