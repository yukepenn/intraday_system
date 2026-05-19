"""Phase18B guardrails: no promotion/runtime leakage and no-lookahead helpers."""

from __future__ import annotations

import numpy as np
from intraday.core.paths import repo_root
from intraday.strategies.common import bars_since_prior_condition, prior_condition_within_bars


def test_bars_since_prior_condition_excludes_current_bar_and_resets_session() -> None:
    condition = np.array([False, True, False, True, False, True, False], dtype=bool)
    session_id = np.array([1, 1, 1, 1, 2, 2, 2], dtype=np.int32)
    age = bars_since_prior_condition(condition, session_id)
    assert age.tolist() == [-1, -1, 1, 2, -1, -1, 1]


def test_prior_condition_within_bars_uses_prior_only() -> None:
    condition = np.array([False, True, False, False, True], dtype=bool)
    session_id = np.ones(5, dtype=np.int32)
    recent = prior_condition_within_bars(condition, session_id, max_bars=2)
    assert recent.tolist() == [False, False, True, True, False]


def test_phase18b_does_not_create_candidate_or_layer2_runtime_configs() -> None:
    root = repo_root()
    phase18b_paths = [
        p.relative_to(root).as_posix()
        for p in root.rglob("*phase18b*")
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
    assert not any(
        any(token in path.lower() for token in forbidden_tokens) for path in phase18b_paths
    )
