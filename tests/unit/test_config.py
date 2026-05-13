"""config.py unit tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from intraday.core.config import load_yaml, require_keys, write_yaml
from intraday.core.errors import ConfigError


def test_load_yaml_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "x.yaml"
    payload = {"strategy": "pa", "version": "v1", "fields": [1, 2, 3], "nested": {"a": 1}}
    write_yaml(p, payload)
    loaded = load_yaml(p)
    assert loaded == payload


def test_load_yaml_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_yaml(tmp_path / "absent.yaml")


def test_load_yaml_non_mapping_raises(tmp_path: Path) -> None:
    p = tmp_path / "x.yaml"
    p.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_yaml(p)


def test_require_keys_passes_when_present() -> None:
    require_keys({"a": 1, "b": 2}, ("a", "b"))


def test_require_keys_raises_on_missing() -> None:
    with pytest.raises(ConfigError) as exc:
        require_keys({"a": 1}, ("a", "b", "c"), where="my_config")
    assert "my_config" in str(exc.value)
    assert "b" in str(exc.value)
    assert "c" in str(exc.value)
