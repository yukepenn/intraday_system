"""Imports of core packages must succeed."""

from __future__ import annotations

import importlib


def test_import_root() -> None:
    import intraday

    assert hasattr(intraday, "__version__")
    assert isinstance(intraday.__version__, str)


def test_import_core_modules() -> None:
    for name in (
        "intraday.core",
        "intraday.core.types",
        "intraday.core.arrays",
        "intraday.core.hashing",
        "intraday.core.config",
        "intraday.core.paths",
        "intraday.core.errors",
        "intraday.core.constants",
        "intraday.core.registry",
    ):
        importlib.import_module(name)


def test_import_subsystem_packages() -> None:
    for name in (
        "intraday.data",
        "intraday.data.catalog",
        "intraday.data.schema",
        "intraday.data.loader",
        "intraday.data.normalize",
        "intraday.data.validate",
        "intraday.features",
        "intraday.features.base",
        "intraday.features.registry",
        "intraday.strategies",
        "intraday.strategies.base",
        "intraday.execution",
        "intraday.execution.spec",
        "intraday.execution.intent",
        "intraday.execution.records",
        "intraday.execution.reference",
        "intraday.execution.fast",
        "intraday.management",
        "intraday.management.modes",
        "intraday.backtest",
        "intraday.layer1",
        "intraday.layer1.grid",
        "intraday.layer2",
        "intraday.layer3",
        "intraday.portfolio",
        "intraday.reports",
        "intraday.research",
        "intraday.cli",
        "intraday.cli.main",
        "intraday.utils",
    ):
        importlib.import_module(name)
