"""Repository structure smoke test."""

from __future__ import annotations

from intraday.core.paths import repo_root

REQUIRED_DIRS: tuple[str, ...] = (
    "docs",
    "configs",
    "configs/data",
    "configs/execution",
    "configs/features",
    "configs/strategies/base",
    "configs/strategies/grids",
    "configs/strategies/metadata",
    "configs/candidates",
    "configs/layer1",
    "configs/layer2",
    "configs/layer3",
    "configs/reports",
    "data",
    "data/raw",
    "data/curated",
    "data/cache",
    "artifacts",
    "artifacts/bootstrap/phase0_1a",
    "src/intraday",
    "src/intraday/core",
    "src/intraday/data",
    "src/intraday/features",
    "src/intraday/strategies",
    "src/intraday/execution",
    "src/intraday/management",
    "src/intraday/backtest",
    "src/intraday/layer1",
    "src/intraday/layer2",
    "src/intraday/layer3",
    "src/intraday/portfolio",
    "src/intraday/reports",
    "src/intraday/research",
    "src/intraday/cli",
    "src/intraday/utils",
    "tests",
    "tests/unit",
    "tests/smoke",
    ".github/workflows",
)


REQUIRED_FILES: tuple[str, ...] = (
    "pyproject.toml",
    "README.md",
    "Makefile",
    ".gitignore",
    ".gitattributes",
    "PROJECT_STATUS.md",
    "PROGRESS.md",
    "CHANGES.md",
    "NEXT_HANDOFF.md",
    "docs/ARCHITECTURE.md",
    "docs/PROJECT_STRUCTURE.md",
    "docs/DATA_CONTRACT.md",
    "docs/CONFIG_CONTRACT.md",
    "docs/CACHE_CONTRACT.md",
    "docs/EXECUTION_CONTRACT.md",
    "docs/LAYER_FLOW.md",
    "docs/PHASE_PLAN.md",
    "docs/QT_REFERENCE_POLICY.md",
    "docs/DEVELOPMENT_WORKFLOW.md",
    "docs/DESIGN_BASELINE.md",
    "configs/data/data_roots.yaml",
    "configs/data/ibkr_qqq_1m.yaml",
    "configs/data/symbols.yaml",
    "configs/data/sessions_us_equity.yaml",
    "configs/execution/intraday_default.yaml",
    "configs/features/pa_core_v1.yaml",
    "configs/features/gap_core_v1.yaml",
    "configs/features/cci_core_v1.yaml",
    "configs/reports/default_report.yaml",
    "src/intraday/__init__.py",
    ".github/workflows/ci.yml",
)


def test_required_directories_exist() -> None:
    root = repo_root()
    missing = [d for d in REQUIRED_DIRS if not (root / d).exists()]
    assert not missing, f"missing directories: {missing}"


def test_required_files_exist() -> None:
    root = repo_root()
    missing = [f for f in REQUIRED_FILES if not (root / f).exists()]
    assert not missing, f"missing files: {missing}"
