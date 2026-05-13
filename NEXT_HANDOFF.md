# NEXT_HANDOFF

Last updated: **2026-05-13** (Phase 1B data foundation hardening).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- After this task’s commit: use `git log -1 --oneline` and `git rev-parse HEAD` for the authoritative SHA (pre-commit baseline was recorded in `artifacts/data_foundation_phase1b/baseline_inventory.*`).
- Windows: `git config --global --add safe.directory <repo>` if Git reports “dubious ownership”.

## B. Task scope

Phase **1B** only: Layer 0 **repair / hardening** — docs sync, Ruff readability, raw timestamp contract, normalization exact window + safe writes, BarMatrix `session_id` determinism, timestamp/session evidence CLI + artifacts, expanded tests, path hygiene in committed artifacts.

**Out of scope (unchanged):** reference execution, Numba fast path, feature kernels, strategy logic, Layer1/2/3, candidate YAML, portfolio sizing, PnL / R-multiple logic.

## C. Status/docs synchronization

- `README.md` — project status reflects Phase 0/1 complete, Phase 1B current, Phase 2 next.
- `PROJECT_STATUS.md` — Phase 1B + decision `DATA_FOUNDATION_PHASE1B_COMPLETE`.
- `PROGRESS.md` — chronological Phase 1B entry.
- `CHANGES.md` — Phase 1 + 1B summaries; latest decision is Phase 1B (not stale bootstrap-only).
- `docs/PHASE_PLAN.md` — Phase 0/1 complete; Phase 1B gate; Phase 1 acceptance no longer implies a cache round-trip.
- `docs/DATA_CONTRACT.md` — timestamp candidates, window filter, write guard, BarMatrix `session_id` semantics.
- `configs/data/ibkr_qqq_1m.yaml` — comments: local raw, canonical QQQ expected, legacy support, SPY note.

See `artifacts/data_foundation_phase1b/status_sync.*`.

## D. Formatting/readability

`python -m ruff format src tests` applied; `ruff format --check` and `ruff check src tests` pass.

See `artifacts/data_foundation_phase1b/formatting_readability.*`.

## E. Raw schema contract

- Accepted timestamp column **names**: `ts_ny`, `ts_utc`, `timestamp`, `date`, `datetime` (`intraday.data.schema.RAW_TIMESTAMP_ACCEPTED_COLUMNS`).
- Inspection requires Arrow **temporal** types; dataset `raw_timestamp.column` must exist and be accepted when provided.
- QQQ uses `raw_timestamp.column: ts_ny` (dataset YAML).
- OHLCV mapping remains YAML-driven with defaults `open/high/low/close/volume`.

See `artifacts/data_foundation_phase1b/schema_contract_repair.*` and `raw_schema_audit.*`.

## F. Normalization exact-window behavior

- After RTH + dedupe: filter `start_session_key <= session_date <= end_session_key` using NY `session_date` (from bar-start `ts_local`).
- `write=True` to canonical monthly curated paths: **raises `ConfigError`** unless `[start,end]` spans full calendar months (start = first-of-month, end = last day of end month). Dry-run (default without `--write`) still reports exact filtered rows for partial windows.

See `artifacts/data_foundation_phase1b/normalization_window_filtering.*` and `normalization_result.*`.

## G. BarMatrix session_id determinism

`load_bars_from_curated` drops curated file `session_id`, joins dense ranks from sorted unique `session_date` after load/filter/sort. `validate_bar_matrix` checks monotone `session_id`, `session_date` consistency on jumps, and `minute==0` at session starts.

See `artifacts/data_foundation_phase1b/session_id_determinism.*`.

## H. Timestamp/session audit

- CLI: `python -m intraday.cli.main data timestamp-audit --dataset configs/data/ibkr_qqq_1m.yaml --symbol QQQ --output-dir artifacts/data_foundation_phase1b`
- Artifacts: `timestamp_semantics_audit.csv` / `.md` (samples: earliest/latest/March/November/2024 month when present).
- Session coverage (2024H1): `session_coverage_summary.csv` / `.md`.

## I. Local QQQ 2024H1 validation

- Rows: **48360**
- Sessions: **124**
- Minute range: **0..389**
- `data validate-curated`: **no errors**
- `data load-bars` `data_hash`: `b00d2b8cf0bc183bcbc792a75a3eea3a44c254bd656df672a267c3b39a40050d`

See `curated_validation.*`, `barmatrix_load_smoke.*`.

## J. Tests / validation

- `python -m compileall -q src` — pass
- `pytest -q` — **73** passed
- Ruff format/check — pass
- CLI: `--help`, `doctor`, `validate structure` — pass
- Data CLI: inventory, inspect, normalize (dry-run), timestamp-audit, validate-curated, load-bars, session-coverage — pass locally with QQQ data

See `artifacts/data_foundation_phase1b/validation_results.*` and `commands_run.*`.

## K. Artifact hygiene

- No raw/curated parquet, cache, npy/npz/memmap, or forbidden paths **staged**.
- Inventory CSV/MD use `<repo-root>/...` for `resolved_path` when under repo base; CLI summaries avoid dumping absolute roots in JSON where updated.

See `artifacts/data_foundation_phase1b/local_path_hygiene.*`.

## L. Explicit non-implemented items

- Reference execution simulator, Numba fast path, feature kernels, strategy logic.
- Layer1 runner, candidate generation, Layer2 router, Layer3 validation, management modes, portfolio sizing, PnL / R-multiple logic.

## M. Risks / blockers

- **Git safe.directory** on some Windows setups.
- **SPY** may remain legacy raw layout until migrated.
- **Exchange calendar perfection** (early closes): session coverage flags `short_session` / `invalid` heuristically; not full calendar truth yet.

## N. Files changed (high level)

- `src/intraday/data/{schema,inspect,normalize,loader,validate,timestamp_audit,catalog}.py`
- `src/intraday/cli/{data_cmds,main,data}.py`
- `configs/data/ibkr_qqq_1m.yaml`
- `docs/{DATA_CONTRACT,PHASE_PLAN}.md`
- `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `NEXT_HANDOFF.md`
- `tests/unit/{test_raw_schema_inspection,test_data_normalize,test_data_loader,test_data_validate}.py`
- `artifacts/data_foundation_phase1b/*`

## O. Local-only artifacts

- Raw + curated parquet under `data/**` (gitignored).
- Local-only machine paths may still appear in **stdout** when running CLI outside sanitized JSON fields.

## P. Decision

`DATA_FOUNDATION_PHASE1B_COMPLETE`

## Q. Recommended next step

`IMPLEMENT_REFERENCE_EXECUTION_ENGINE`
