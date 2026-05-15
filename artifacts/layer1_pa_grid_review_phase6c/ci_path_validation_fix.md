# CI path validation fix (Phase 6c)

## Summary

Added `intraday.core.paths.is_absolute_path_like()` and used it for `output.artifact_root` in `load_layer1_smoke_config` and `load_layer1_controlled_grid_config` so Linux CI rejects Windows drive, drive-relative, POSIX absolute, and UNC-style paths consistently.

## Semantics

- Rejects POSIX absolute (`/tmp/abs`), Windows absolute (`C:/tmp/abs`, `D:\TradingData\x`), drive-relative (`C:tmp\...`), and UNC prefixes after normalizing `/` → `\` (leading `\\`).
- Accepts repo-relative paths with `/` or `\`.

## Implementation

- `src/intraday/core/paths.py` — `is_absolute_path_like`
- `src/intraday/layer1/config.py` — artifact_root checks

## Tests

- `tests/unit/test_core_paths.py` — direct unit tests
- `tests/unit/test_layer1_config.py` — smoke loader parametrized cases + relative acceptance
- `tests/unit/test_layer1_grid_config.py` — controlled grid loader mirror tests
