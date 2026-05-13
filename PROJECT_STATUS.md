# PROJECT_STATUS

## Current phase

**Phase 1B — Data foundation repair and handoff hardening** (this task).

## Decision

`DATA_FOUNDATION_PHASE1B_COMPLETE` (local QQQ 2024H1 curated validation + BarMatrix load + tests + artifacts refreshed).

## Recommended next step

`IMPLEMENT_REFERENCE_EXECUTION_ENGINE`

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Tests: `pytest` green (73) + `ruff format --check` + `ruff check` + `compileall`.
- Raw parquet: **local-only** (gitignored). QQQ months are **canonical** under `data/raw/ibkr/asset=equity/symbol=QQQ/...`; SPY may remain **legacy_qt_like** until migrated.
- Curated parquet: **local-only** (gitignored). QQQ **2024-01..2024-06** validated under `data/curated/bars_1m_rth/...`.
- BarMatrix `session_id` is **recomputed** over the loaded window (deterministic across months).

See `NEXT_HANDOFF.md` and `artifacts/data_foundation_phase1b/`.
