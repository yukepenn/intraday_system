"""hashing.py unit tests."""

from __future__ import annotations

from intraday.core.hashing import hash_config, stable_json_dumps


def test_hash_config_stable_under_key_ordering() -> None:
    a = {"b": 1, "a": 2, "c": {"y": 3, "x": 4}}
    b = {"a": 2, "c": {"x": 4, "y": 3}, "b": 1}
    assert hash_config(a) == hash_config(b)


def test_hash_config_changes_on_value_change() -> None:
    a = {"x": 1, "y": "abc"}
    b = {"x": 1, "y": "abd"}
    assert hash_config(a) != hash_config(b)


def test_hash_config_changes_on_key_add() -> None:
    a = {"x": 1}
    b = {"x": 1, "y": None}
    assert hash_config(a) != hash_config(b)


def test_stable_json_dumps_sorts_keys() -> None:
    text = stable_json_dumps({"b": 1, "a": 2})
    assert text == '{"a":2,"b":1}'


def test_stable_json_dumps_handles_nested_lists() -> None:
    text = stable_json_dumps({"x": [1, 2, 3], "y": ["b", "a"]})
    assert text == '{"x":[1,2,3],"y":["b","a"]}'
