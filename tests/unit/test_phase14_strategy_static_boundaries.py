"""Static strategy-layer boundary checks for Phase 14."""

from __future__ import annotations

import ast
from pathlib import Path

from intraday.core.paths import repo_root

FORBIDDEN_IMPORT_PREFIXES = (
    "intraday.execution",
    "intraday.backtest",
    "pyarrow",
    "pandas",
    "QT",
)
FORBIDDEN_STRING_FRAGMENTS = (
    ".parquet",
    "read_parquet",
    "scan_parquet",
    "sys.path",
    "D:/",
    "D:\\",
    "C:/",
    "C:\\",
    "QT/",
    "QT\\",
)


def _strategy_modules() -> list[Path]:
    root = repo_root() / "src/intraday/strategies"
    return [p for p in root.rglob("*.py") if p.name != "__init__.py"]


def test_strategy_modules_do_not_cross_runtime_boundaries() -> None:
    for path in _strategy_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    _assert_import_allowed(alias.name, path)
            elif isinstance(node, ast.ImportFrom) and node.module:
                _assert_import_allowed(node.module, path)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                _assert_string_allowed(node.value, path)


def _assert_import_allowed(module: str, path: Path) -> None:
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        if module == prefix or module.startswith(f"{prefix}."):
            raise AssertionError(f"{path} imports forbidden module {module!r}")


def _assert_string_allowed(value: str, path: Path) -> None:
    for fragment in FORBIDDEN_STRING_FRAGMENTS:
        if fragment in value:
            raise AssertionError(f"{path} contains forbidden boundary fragment {fragment!r}")
