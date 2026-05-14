"""Minimal generic Registry.

Used by features.registry and strategies.registry to register typed objects by name.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    """Name -> object registry with simple typed semantics."""

    def __init__(self, kind: str) -> None:
        self._kind = kind
        self._items: dict[str, T] = {}

    @property
    def kind(self) -> str:
        return self._kind

    def register(self, name: str, item: T, *, overwrite: bool = False) -> T:
        if not name:
            raise ValueError(f"empty name for {self._kind} registration")
        if name in self._items and not overwrite:
            raise KeyError(f"{self._kind} {name!r} already registered")
        self._items[name] = item
        return item

    def get(self, name: str) -> T:
        if name not in self._items:
            raise KeyError(f"{self._kind} {name!r} not registered")
        return self._items[name]

    def has(self, name: str) -> bool:
        return name in self._items

    def names(self) -> list[str]:
        return sorted(self._items.keys())

    def __iter__(self) -> Iterator[tuple[str, T]]:
        for name in sorted(self._items.keys()):
            yield name, self._items[name]

    def __len__(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        """Remove all registrations (primarily for tests)."""
        self._items.clear()
