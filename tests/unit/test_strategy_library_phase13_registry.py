"""Phase 13 strategy registry and contract guards."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from intraday.core.paths import repo_root
from intraday.strategies.registry import (
    clear_strategy_registry,
    list_strategies,
    register_builtin_strategies,
)

PHASE13_STRATEGIES = (
    "pa_buy_sell_close_trend",
    "orb_continuation",
    "orb_retest_continuation",
    "failed_orb",
    "gap_acceptance_failure",
    "vwap_trend_pullback",
    "vwap_reclaim_reject",
    "prior_day_level_trap",
    "cci_extreme_snapback",
    "stochastic_oversold_cross",
)

FORBIDDEN_IMPORT_FRAGMENTS = (
    "intraday.execution",
    "intraday.backtest",
    "pandas",
    "parquet",
    "QT",
)


@pytest.fixture(autouse=True)
def _registry() -> None:
    clear_strategy_registry()
    register_builtin_strategies()
    yield
    clear_strategy_registry()


def test_registry_lists_ten_strategies() -> None:
    names = list_strategies()
    for s in PHASE13_STRATEGIES:
        assert s in names
    assert len(names) >= 10


def test_strategy_modules_forbidden_imports() -> None:
    root = repo_root() / "src/intraday/strategies"
    modules = [
        p
        for p in root.rglob("*.py")
        if p.name != "__init__.py" and "pa/buy_sell_close_trend" not in str(p).replace("\\", "/")
    ]
    new_modules = [
        p
        for p in modules
        if any(
            part in p.parts
            for part in ("orb", "gap", "vwap", "levels", "cci", "stochastic", "common.py")
        )
    ]
    for path in new_modules:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    _assert_clean_import(alias.name, path)
            elif isinstance(node, ast.ImportFrom) and node.module:
                _assert_clean_import(node.module, path)


def _assert_clean_import(module: str, path: Path) -> None:
    for frag in FORBIDDEN_IMPORT_FRAGMENTS:
        if frag in module:
            raise AssertionError(f"{path} imports forbidden module {module!r}")


def test_candidates_dir_has_no_runtime_yaml() -> None:
    cand = repo_root() / "configs/candidates"
    yamls = [p for p in cand.rglob("*.yaml") if p.name.lower() != "readme.md"]
    assert yamls == []
