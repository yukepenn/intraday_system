"""CLI surface smoke tests."""

from __future__ import annotations

import subprocess
import sys


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "intraday.cli.main", *args],
        capture_output=True,
        text=True,
    )


def test_cli_help() -> None:
    res = _run(["--help"])
    assert res.returncode == 0, (res.stdout, res.stderr)
    combined = (res.stdout + res.stderr).lower()
    assert "intraday" in combined


def test_cli_doctor() -> None:
    res = _run(["doctor"])
    assert res.returncode == 0, (res.stdout, res.stderr)
    assert "doctor" in res.stdout.lower()


def test_cli_validate_structure() -> None:
    res = _run(["validate", "structure"])
    assert res.returncode == 0, (res.stdout, res.stderr)
    assert "structure" in res.stdout.lower()
