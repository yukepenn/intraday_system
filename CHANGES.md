# CHANGES

Curated changelog. Follows the spirit of [Keep a Changelog](https://keepachangelog.com/) with project-specific decision/phase entries.

## [Unreleased] – 2026-05-13

### Phase 3 — Fast execution skeleton + parity

- Feat(execution): add `simulate_trade_path_fast` and Numba `_simulate_trade_path_fast_kernel` (post-entry scan parity vs reference; shared `materialize_trade`).
- Feat(execution): add `parity.py` (`compare_trade_results`, `assert_trade_results_equal`) and export fast + parity from `execution` package.
- Feat(types): add `RejectReason.INVALID_MARKET_DATA`; finite checks on `TradeIntent` qty/target_r/stop; finite entry open in `materialize_trade`; finite OHLC/raw-exit guards in reference path.
- Test: `tests/parity/test_execution_fast_parity.py`, `tests/unit/test_execution_fast_contract.py`, hardening tests in execution unit tests.
- Docs: `EXECUTION_CONTRACT.md`, `PHASE_PLAN.md`, README/PROJECT_STATUS/NEXT_HANDOFF; Ruff format on a few pre-existing files for green `ruff format --check`.
- Chore(artifacts): add `artifacts/execution_fast_phase3/` Phase 3 review bundle.

### Phase 2 — Reference execution engine

- Feat(execution): implement `materialize_trade`, `MaterializedTrade`, and `simulate_trade_path_reference` (intrabar stop/target, same-bar policy, EOD before max-hold, session roll + truncated fallback, entry/exit slippage, commission, gross/net PnL, R-multiple).
- Feat(execution): harden `ExecutionSpec` (`validate`, `from_config`, `load_execution_spec`, `to_dict`) and `TradeResult.rejected` / `accepted_trade` helpers; `TradeIntent.validate_shape`.
- Feat(execution): cost helpers `apply_entry_slippage`, `apply_exit_slippage`, `compute_*`; retain `apply_slippage` as entry alias.
- Feat(types): add `RejectReason.INVALID_INTENT` for malformed intents.
- Fix(schema): replace misleading `RAW_REQUIRED_COLUMNS` timestamp implication with `RAW_REQUIRED_OHLCV_COLUMNS` + documented alias.
- Docs: rewrite `EXECUTION_CONTRACT.md` for Phase 2 semantics; update `PHASE_PLAN`, `LAYER_FLOW`, `README`, status handoff files.
- Chore(data): refresh `data/**/README.md` for local-only parquet + timestamp column names.
- Test: add `tests/helpers/bars.py`, `tests/unit/test_execution_*.py`, `tests/smoke/test_execution_reference_smoke.py` (synthetic only).
- Chore(artifacts): add `artifacts/execution_reference_phase2/` Phase 2 review bundle.

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

- Batch `simulate_trade_paths_fast`, feature kernels, strategy logic.
- Layer1/Layer2/Layer3 runners, candidate YAML generation, router/validator, management overlays in execution.
- No raw/curated parquet or cache files committed.

### Decision

- `FAST_EXECUTION_PARITY_COMPLETE`
- Recommended next step: `IMPLEMENT_FEATURE_ENGINE_MVP`
