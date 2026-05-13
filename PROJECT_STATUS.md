# PROJECT_STATUS

## Current phase

**Phase 1 — Data foundation (BarMatrix + normalization) — implemented.**

## Decision

`DATA_FOUNDATION_BARMATRIX_COMPLETE` (local QQQ 2024H1 curated + validation + BarMatrix load verified).

## Recommended next step

`IMPLEMENT_REFERENCE_EXECUTION_ENGINE`

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Tests: `pytest` green (55) + `ruff check src tests` + `compileall`.
- Raw parquet: **local-only** (gitignored). QQQ months are **canonical** under `data/raw/ibkr/asset=equity/symbol=QQQ/...`; SPY remains **legacy_qt_like** until migrated.
- Curated parquet: **local-only** (gitignored). QQQ **2024-01..2024-06** written under `data/curated/bars_1m_rth/...` and validated.
- Full-history QQQ normalization (`--all-available`) not run in this session (optional follow-up).

See `NEXT_HANDOFF.md` and `artifacts/data_foundation_phase1/`.
