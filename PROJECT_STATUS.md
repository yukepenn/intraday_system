# PROJECT_STATUS

## Current phase

**Phase 0/1A — Bootstrap intraday_system architecture skeleton.**

## Decision

`BOOTSTRAP_PHASE0_1A_COMPLETE` (pending push verification).

## Recommended next step

`IMPLEMENT_DATA_FOUNDATION_BARMATRIX_NORMALIZATION` — i.e. Phase 1:

- Implement `data.normalize.normalize_raw_ibkr_to_curated` to write curated parquet under `data/curated/bars_1m_rth/...`.
- Implement `data.loader.load_bars_from_curated` to build `BarMatrix` from curated parquet.
- Implement `data.validate.validate_bar_data` for shape/duplicate/missing-minute checks.
- Decide whether to canonicalize raw layout (legacy_qt_like -> canonical) as part of Phase 1 or to keep the loader layout-aware.

## Snapshot

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Test status: smoke + unit tests passing (40/40 after status docs are added).
- Raw data: 104 parquet files locally, 34.3 MiB total, all `legacy_qt_like`, all `safe_normal_git`.
- Canonicalization of raw layout: **deferred** to Phase 1 (no bytes touched by Phase 0/1A).

See `NEXT_HANDOFF.md` for the full handoff and `docs/PHASE_PLAN.md` for the roadmap.
