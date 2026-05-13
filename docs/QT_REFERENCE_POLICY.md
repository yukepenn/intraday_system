# QT_REFERENCE_POLICY — intraday_system

How `QT/` (the legacy research archive) relates to this repo.

## 1. QT is read-only reference

`QT/` lives outside this repo at **`<qt-reference-root>`** (local-only on your machine). It contains years of strategy/feature research and Layer1/Layer2/Layer3 vocabulary.

`intraday_system/` is the clean final system. It is independent of QT at runtime.

## 2. What we copy from QT

- Strategy logic ideas (PA, GAP, CCI, VWAP, ORB).
- Feature concepts (VWAP regime, ORB high/low, ATR-like, swing windows, trend score inputs).
- Strategy YAML field shapes.
- Layer1/Layer2/Layer3 vocabulary.
- The execution-backed-truth principle.
- Candidate YAML concept.
- Artifact validation discipline.

## 3. What we DO NOT copy

- The legacy archive folder structure.
- Old Numba PnL as active truth (we re-derive reference truth).
- Research CSV/MD as runtime config (configs are YAML-only here).
- Hard-coded absolute drive assumptions.
- Multiple competing engines.
- Compressed one-line modules.
- Broad scripts without central config.

## 4. Operational rules

- Do **not** add `QT/` to `sys.path`.
- Do **not** `import QT.*` from this repo.
- Do **not** depend on QT artifacts at runtime.
- It is acceptable to **read** QT files during research and reproduce logic in this repo, with attribution in commit messages or doc comments.
- It is acceptable to add **regression tests** in `tests/regression/` that compare this repo's output against numbers exported from QT for a fixed window.

## 5. QT becomes

- Reference source.
- Not architecture source.
- Not runtime dependency.

## 6. If a QT file is critical

If a QT script encodes critical strategy logic and we want to reproduce it, the workflow is:

1. Read it as reference (no copy/paste of full file).
2. Re-implement cleanly in `src/intraday/strategies/<family>/<name>.py`.
3. Encode parameters in `configs/strategies/base/<name>.yaml`.
4. Add regression test in `tests/regression/test_qt_<family>_signal_reference.py` that runs a small window and compares signal/trade counts within tolerance.

## 7. Reverse direction

`intraday_system/` never writes back into `QT/`. Outputs land under `data/curated/`, `data/cache/`, `artifacts/`, or `configs/candidates/` — all inside this repo.
