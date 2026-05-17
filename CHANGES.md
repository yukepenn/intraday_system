# CHANGES

Curated changelog. Follows the spirit of [Keep a Changelog](https://keepachangelog.com/) with project-specific decision/phase entries.

## [Unreleased] – 2026-05-17

### Phase 7 — Layer1 PA candidate selection design

- Feat(layer1): `reconstruct_resolved_config_for_combo`; `evaluate_selection_gates` (`PA_L1_SELECTION_DESIGN_V1`, `promotion_allowed_now=false`).
- Docs: `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`; `configs/candidates/l1_pa_controlled_v1/README.md`; candidate root README refresh.
- Chore(artifacts): `artifacts/layer1_pa_candidate_selection_design_phase7/` — doctrine, gates, dry-run tables, sample schema (SAMPLE ONLY), review bundle.
- Test: `test_layer1_candidate_selection_design.py`, `test_layer1_selection_gates.py`; grid reconstruction tests.
- Validation: `pytest` **340 passed**; Ruff; CLI smoke + `layer1 grid-inspect`.

### Phase 6d — PA logic / controlled-grid diagnostics (pre–selection design)

- Docs/artifacts: `artifacts/pa_logic_grid_review_phase6d/` Phase 6d review bundle (parameter-axis diagnostics, exit/skip review, readiness label, serialization audit proposals, GitHub-renderable bundle).
- Status: PROJECT_STATUS/NEXT_HANDOFF/README/PHASE_PLAN/LAYER1_CONTRACT aligned to Phase **6d** completion and **candidate selection design next** (`DESIGN_LAYER1_PA_CANDIDATE_SELECTION`).
- Validation: `compileall`; `pytest` **324 passed**; `ruff format/check`; CLI (`doctor`, `validate structure`, `layer1 grid-inspect`).

### Phase 6c — Layer1 PA grid results review

- Fix(paths): `is_absolute_path_like` for cross-platform absolute / drive / UNC detection; Layer1 smoke + controlled-grid loaders reject non-repo-relative `output.artifact_root` on Linux CI.
- Test: `tests/unit/test_core_paths.py`; parametrized `artifact_root` cases for smoke + grid loaders.
- Chore(artifacts): `artifacts/layer1_pa_grid_review_phase6c/` — `sweep_results_review.csv`, summaries, distributions, `CHATGPT_REVIEW_BUNDLE.md`, validation tables.
- Docs: `CONFIG_CONTRACT`, `LAYER1_CONTRACT`, `PHASE_PLAN`, README, status handoff.
- `pytest` **324** at handoff.

### Phase 6b — Layer1 PA controlled grid

- Feat(layer1): `ResolvedGridCombo`, `resolve_grid_combos`, `run_layer1_controlled_grid`, `Layer1GridResult` / `Layer1GridRow`, `load_layer1_controlled_grid_config` + validation (16-combo cap, no prefix slicing).
- Feat(layer1): `write_layer1_grid_artifacts` (`sweep_results.csv`, summaries, distributions, top rows).
- Feat(cli): `layer1 grid`, `layer1 grid-inspect`.
- Feat(grid): `configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml`, `configs/layer1/controlled_pa_qqq_2024h1.yaml`.
- Fix(metrics): `summarize_trade_results(..., count_rejected_in_metrics=...)` + smoke/grid skip keys `execution_rejected_included` / `execution_rejected_excluded`.
- Docs: `LAYER1_CONTRACT`, `BACKTEST_CONTRACT`, `LAYER_FLOW`, `PHASE_PLAN`, `ARCHITECTURE`, README/status.
- Test: `test_layer1_grid*`, `test_layer1_grid_cli`; `pytest` **303** at handoff.
- Chore(artifacts): `artifacts/layer1_pa_controlled_grid_phase6b/*` review bundle; gitignore `local_run/` + `_pytest_*` under that tree.

### Phase 6 — Layer1 PA smoke run

- Feat(layer1): `run_layer1_smoke`, smoke YAML loader/validation (`configs/layer1/smoke_pa_qqq_2024h1.yaml`), session scan (max trades / skip while open), `Layer1SmokeResult`.
- Feat(backtest): `signal_adapter` (`SignalAdapterResult`), `summarize_trade_results` / `BacktestMetrics` (TradeResult-only aggregates).
- Feat(execution): `merge_execution_spec_with_strategy` for strategy `backtest`/`risk` overrides.
- Feat(cli): `layer1 run`, `layer1 inspect`.
- Fix(strategies): `parse_bool_like` for `require_vwap_side`; validate `signal.score_mode` (`simple_pa_v1` only for Phase 6).
- Docs: `LAYER1_CONTRACT.md`, `BACKTEST_CONTRACT.md`; updates to `LAYER_FLOW`, `PHASE_PLAN`, `ARCHITECTURE`, README/status handoff.
- Test: `test_signal_adapter`, `test_backtest_metrics`, `test_layer1_*`, `test_execution_spec_merge`, `test_layer1_cli`; `pytest` **286** at handoff.
- Chore(artifacts): `artifacts/layer1_pa_smoke_phase6/` review bundle; gitignore `local_run` + `_pytest_runner*` under that tree.
- Chore(validate): `cli/main.py` structure check includes new contracts + smoke YAML.

### Phase 5 — PA strategy signal MVP

- Feat(strategies): `pa_buy_sell_close_trend` signal generator (`BarMatrix` + `FeatureMatrix` → `SignalMatrix`; no parquet/execution/PnL).
- Feat(strategies): registry, loader, PA config validation, deterministic `signal_hash`.
- Feat(cli): `strategies list`, `strategies inspect`, `strategies generate-smoke`.
- Feat(config): PA base/metadata/grid YAML under `configs/strategies/`.
- Docs: `STRATEGY_CONTRACT.md`; updates to `LAYER_FLOW`, `PHASE_PLAN`, `ARCHITECTURE`, README/status handoff.
- Test: `tests/unit/test_strategy_*.py`, `tests/smoke/test_strategy_cli.py`, `tests/helpers/strategy.py`.
- Chore(artifacts): `artifacts/strategy_pa_phase5/` Phase 5 review bundle.

### Phase 4 — Feature engine MVP

- Feat(features): `build_feature_matrix` (reference mode only), `resolve_feature_config`, `hash_feature_config`, canonical column ordering, `inf` → `nan` sanitize.
- Feat(features): reference kernels — VWAP, ORB, volatility/true range, price action, volume, regime (`kernels/session_ops.py`).
- Feat(features): `FeatureStore` (`data_hash` / `feature_hash` directory layout) + cache get/put validation.
- Feat(cli): `features list`, `features inspect`, `features build` (Typer).
- Feat(config): finalize `configs/features/pa_core_v1.yaml` (22 PA-core market-fact columns).
- Feat(core): `Registry.clear()` for test isolation.
- Docs: `FEATURE_CONTRACT.md`; updates to `CACHE_CONTRACT`, `LAYER_FLOW`, `PHASE_PLAN`, `ARCHITECTURE`, README/PROJECT_STATUS/NEXT_HANDOFF.
- Test: `tests/unit/test_feature_*.py`, `tests/unit/test_features_*.py`, `tests/smoke/test_feature_cli.py`.
- Chore(artifacts): `artifacts/feature_engine_phase4/` Phase 4 review tables + bundle.

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

- Broad parameter sweeps / WFO / live-paper; candidate YAML promotion; GAP/CCI strategies; Layer2 router; Layer3 validation; management overlays in execution; portfolio sizing.

### Decision — Phase 6d (latest)

- `PA_GRID_REVIEW_COMPLETE_READY_FOR_SELECTION_DESIGN`
- Recommended singular next procedural step (authoring/design only): **`DESIGN_LAYER1_PA_CANDIDATE_SELECTION`**

### Earlier historical anchors (prior phases)

| Phase tag | Meaning |
| --- | --- |
| `LAYER1_PA_GRID_RESULTS_REVIEW_COMPLETE` | Phase **6c** CI + sanitized grid bundle merge milestone |
| `LAYER1_PA_CONTROLLED_GRID_COMPLETE` | Phase **6b** grid infrastructure milestone |
| `LAYER1_PA_SMOKE_COMPLETE` | Phase **6** smoke plumbing milestone |

Legacy directional note retained for archaeology only: **`IMPLEMENT_LAYER1_PA_CONTROLLED_GRID`** already satisfied upstream of Phase **6b–6d**.
