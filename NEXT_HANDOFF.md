# NEXT_HANDOFF

Last updated: **2026-05-13** (Phase 1 data foundation).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Baseline (pre-Phase1) bootstrap SHA on remote: `f29babb49164bc4fa4766c2d13dab5834d5a1ce9`
- Phase 1 commit: **use `git log -1 --oneline` after pulling** (this handoff is authored alongside the Phase 1 commit).
- Note: Windows may require `git config --global --add safe.directory <repo>` if Git reports “dubious ownership”.

## B. Task scope (Phase 1)

Implemented Layer 0 data foundation only:

- Robust raw catalog / inventory (`infer_raw_layout(..., layout_root=...)`, `resolved_path` in inventory rows).
- Raw parquet schema inspection (metadata-first).
- Timestamp sampling helper (`timestamp_audit.py`) + dataset YAML `raw_timestamp` block.
- Guarded raw canonicalization (dry-run default; `--write` applies moves; byte-preserving `shutil.move`).
- `normalize_raw_ibkr_to_curated` (Polars) → curated monthly parquet under `data/curated/bars_1m_rth/...`.
- `load_bars_from_curated` → `BarMatrix` + deterministic `data_hash`.
- `DataValidationReport` + `validate_curated_dataset`.
- Expanded `intraday.cli.main data ...` commands + smoke tests.

**Not implemented (still skeleton / out of scope)**:

- Strategy logic, feature kernels, execution simulator / PnL, Numba fast path.
- Layer1/Layer2/Layer3 runners, candidate YAML generation, router/validator.

## C. Data inventory

- Raw root: `data/raw/ibkr` (repo-relative).
- Latest CLI inventory artifact: `artifacts/data_foundation_phase1/raw_data_inventory_cli.csv` (+ `.md`).
- After QQQ canonicalization: **76** canonical parquet (QQQ), **28** legacy (`SPY` months still `legacy_qt_like`).
- Raw parquet remains **gitignored** and **not staged**.

## D. Raw schema audit

- Observed QQQ vendor columns (see `artifacts/data_foundation_phase1/raw_schema_inspect_stdout.json` from `data inspect`):
  - Timestamp columns: `ts_utc` (UTC tz-aware), `ts_ny` (America/New_York tz-aware)
  - OHLCV: `open/high/low/close/volume` (+ extras like `useRTH`, `barCount`, …)
- Dataset config uses `raw_timestamp.column: ts_ny` and `semantics: bar_start`.

## E. Timestamp semantics

- Vendor `ts_ny` is tz-aware US/Eastern; used as the primary normalization clock.
- Decision recorded in `configs/data/ibkr_qqq_1m.yaml`: **`bar_start`** (not `unknown`).
- Curated contract: `ts_utc` / `ts_local` are **bar START**; if raw were `bar_end`, normalization subtracts 1 minute in NY before minute indexing (implemented).

## F. Raw layout canonicalization

- `data canonicalize-raw --root data/raw/ibkr --symbol QQQ --write` completed successfully for **all QQQ months** (bytes moved; sources removed).
- `SPY` remains legacy until explicitly migrated (28 files).

## G. Curated normalization

- Curated root: `data/curated/bars_1m_rth` (repo-relative).
- Local run: QQQ **2024-01-01 .. 2024-06-30** written successfully (**48360** rows).
- Full `2020..2026` “all available” normalization was **not** executed in this session (optional).

## H. BarMatrix loader

- `data load-bars` for QQQ 2024H1 succeeds; `data_hash` example from local run: `b00d2b8cf0bc183bcbc792a75a3eea3a44c254bd656df672a267c3b39a40050d`.

## I. Data validation

- `data validate-curated` for QQQ 2024H1 returns **no errors** (124 sessions; all full 390-minute sessions in that window).

## J. CLI / tests

Commands (Typer):

- `python -m intraday.cli.main data inventory --root data/raw/ibkr --output artifacts/data_foundation_phase1/raw_data_inventory_cli.csv`
- `python -m intraday.cli.main data inspect --dataset configs/data/ibkr_qqq_1m.yaml --symbol QQQ`
- `python -m intraday.cli.main data canonicalize-raw --root data/raw/ibkr --symbol QQQ` (dry-run) / `--write`
- `python -m intraday.cli.main data normalize --dataset configs/data/ibkr_qqq_1m.yaml --symbol QQQ --start 2024-01-01 --end 2024-06-30` / `--write` / `--all-available`
- `python -m intraday.cli.main data validate-curated --symbol QQQ --start 2024-01-01 --end 2024-06-30 --data-root data/curated/bars_1m_rth`
- `python -m intraday.cli.main data load-bars --symbol QQQ --start 2024-01-01 --end 2024-06-30 --data-root data/curated/bars_1m_rth`

Tests: **55** passing (`pytest -q`). `ruff check src tests` clean. `python -m compileall -q src` clean.

## K. Explicit non-implemented items

Same as Section B “Not implemented”.

## L. Risks / blockers

- **Git safe.directory** may block automation on some Windows setups.
- **SPY raw layout** still legacy; normalization/catalog remain compatible.
- **DST / half-day nuance**: RTH window is clock-based (`09:30 <= t < 16:00` NY); holiday/early-close handling is “report via warnings”, not exchange-calendar perfect yet.

## M. Files changed (high level)

- `src/intraday/data/{catalog,inspect,canonicalize,normalize,loader,validate,timestamp_audit}.py`
- `src/intraday/cli/{main,data,data_cmds}.py`
- `configs/data/ibkr_qqq_1m.yaml`, `.gitignore`
- `docs/{DATA_CONTRACT,QT_REFERENCE_POLICY}.md`
- `tests/unit/*data*`, `tests/smoke/test_data_cli.py`
- `artifacts/data_foundation_phase1/*` (manifests/summaries; no parquet)

## N. Local-only artifacts

- Raw + curated parquet under `data/**` (ignored by git).
- Any machine-local paths in old bootstrap artifacts are called out in `artifacts/data_foundation_phase1/local_path_hygiene_audit.md`.

## O. Recommended next step

`IMPLEMENT_REFERENCE_EXECUTION_ENGINE`

---

## Decision label (Phase 1)

`DATA_FOUNDATION_BARMATRIX_COMPLETE`
