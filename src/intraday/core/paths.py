"""Repo path helpers.

The repo root is detected by walking up until a marker file (pyproject.toml) is
found. This is used by the CLI and tests; runtime modules should accept paths
explicitly rather than relying on auto-detection.
"""

from __future__ import annotations

from pathlib import Path

_REPO_MARKERS = ("pyproject.toml", ".git")


def repo_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` (or this file) until a repo marker is found."""
    here = (start or Path(__file__)).resolve()
    for candidate in [here, *here.parents]:
        if candidate.is_dir() and any((candidate / m).exists() for m in _REPO_MARKERS):
            return candidate
    raise RuntimeError(
        "Could not locate repo root (no pyproject.toml or .git found upward)."
    )


def relpath(path: Path | str, base: Path | None = None) -> str:
    """Return ``path`` as a POSIX-style relative path from ``base`` (repo root)."""
    base = (base or repo_root()).resolve()
    p = Path(path).resolve()
    try:
        return p.relative_to(base).as_posix()
    except ValueError:
        return p.as_posix()


def resolve(path: Path | str, base: Path | None = None) -> Path:
    """Resolve a path against repo root if it is relative; absolute paths pass through."""
    base = (base or repo_root()).resolve()
    p = Path(path)
    if p.is_absolute():
        return p.resolve()
    return (base / p).resolve()
