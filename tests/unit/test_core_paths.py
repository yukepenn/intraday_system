"""Tests for cross-platform path helpers."""

from __future__ import annotations

import pytest
from intraday.core.paths import is_absolute_path_like


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", False),
        ("artifacts/local_run", False),
        ("artifacts\\local_run", False),
        ("outputs/foo", False),
        ("/tmp/abs", True),
        ("C:/tmp/abs", True),
        (r"D:\TradingData\x", True),
        (r"\\server\share\x", True),
        (r"C:tmp\relative_to_drive", True),
    ],
)
def test_is_absolute_path_like(value: str, expected: bool) -> None:
    assert is_absolute_path_like(value) is expected
