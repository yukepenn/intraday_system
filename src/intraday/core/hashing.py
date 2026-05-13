"""Deterministic hashing utilities for cache keys.

All hashes are SHA-256, sorted-key JSON for dicts, and stable across platforms.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


def stable_json_dumps(obj: Any) -> str:
    """Return a canonical JSON dump of ``obj`` (sorted keys, no whitespace)."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=_default_encoder,
    )


def _default_encoder(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, set | frozenset):
        return sorted(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    raise TypeError(f"unsupported type for stable_json_dumps: {type(value)!r}")


def hash_config(config: Mapping[str, Any] | Any) -> str:
    """Hash a config-like object deterministically.

    Accepts any JSON-serializable value (typically a Mapping). Returns hex SHA-256.
    """
    payload = stable_json_dumps(config)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def hash_file(path: Path | str, *, chunk_size: int = 1 << 20) -> str:
    """Hash the full byte contents of a file (SHA-256, hex)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def hash_paths_manifest(
    paths: Iterable[Path | str],
    *,
    base: Path | str | None = None,
    include_mtime: bool = True,
) -> str:
    """Hash a manifest of file metadata: (relpath, size_bytes [, mtime_ns]).

    This is far faster than hashing every byte and is appropriate for the
    ``data_hash`` cache-seed. For audit-grade integrity, use ``hash_file`` per file.
    """
    base_path = Path(base).resolve() if base is not None else None
    entries: list[tuple[str, int, int]] = []
    for p in paths:
        pp = Path(p).resolve()
        rel = pp.as_posix()
        if base_path is not None:
            try:
                rel = pp.relative_to(base_path).as_posix()
            except ValueError:
                pass
        stat = pp.stat()
        mtime_ns = int(stat.st_mtime_ns) if include_mtime else 0
        entries.append((rel, int(stat.st_size), mtime_ns))
    entries.sort()
    payload = stable_json_dumps(entries)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
