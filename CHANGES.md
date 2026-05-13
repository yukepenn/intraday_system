# CHANGES

Curated changelog. Follows the spirit of [Keep a Changelog](https://keepachangelog.com/) with project-specific decision/phase entries.

## [Unreleased] – 2026-05-13

### Phase 1B — Data foundation repair and handoff hardening

- Fix(data): accepted raw timestamp names (`ts_ny`, `ts_utc`, `timestamp`, `date`, `datetime`) with YAML `raw_timestamp.column`; schema inspection validates configured column or accepted temporal columns.
- Fix(data): normalization applies exact **NY `session_date`** window filter after RTH; **`write` blocked** unless the requested `[start, end]` spans full calendar months (prevents truncating canonical monthly partitions).
- Fix(data): `load_bars_from_curated` **recomputes** dense monotone `session_id` from sorted `session_date` over the loaded window (ignores file-local curated ranks for runtime semantics).
- Fix(data): `validate_bar_matrix` enforces session-start `minute == 0` and consistent `session_date` on `session_id` jumps.
- Feat(cli): `data timestamp-audit` and `data session-coverage` write reviewable CSV/MD artifacts.
- Fix(data): raw inventory CSV/MD writes sanitize `resolved_path` / root to `<repo-root>/...` when possible.
- Feat(cli): `data normalize` JSON prints repo-relative `output_paths` where possible.
- Docs: sync README / PROJECT_STATUS / PHASE_PLAN / DATA_CONTRACT / dataset YAML comments for Phase 1B reality.
- Test: expand coverage for schema, normalize windowing + write guard, loader session_id, validation edge cases.
- Chore(artifacts): add `artifacts/data_foundation_phase1b/` review bundle outputs.

### Phase 1 — Data foundation (Layer 0)

- Feat(data): raw catalog/inventory, schema inspection, timestamp audit helpers, raw canonicalization (dry-run default), IBKR→curated RTH normalization, curated BarMatrix loader, `DataValidationReport`.
- Feat(cli): `data inspect`, `data canonicalize-raw`, `data normalize`, `data validate-curated`, `data load-bars`, `data inventory`.
- Docs: DATA_CONTRACT updates for observed IBKR columns; QT reference policy placeholders.

### Phase 0/1A — Bootstrap

- Feat(repo): repository skeleton, core utilities, CLI skeleton, CI, initial tests and docs.

### Intentionally NOT included (still)

- Reference execution simulator, Numba fast path, feature kernels, strategy logic.
- Layer1/Layer2/Layer3 runners, candidate YAML generation, router/validator.
- No raw/curated parquet or cache files committed.

### Decision

- `DATA_FOUNDATION_PHASE1B_COMPLETE`
- Recommended next step: `IMPLEMENT_REFERENCE_EXECUTION_ENGINE`
