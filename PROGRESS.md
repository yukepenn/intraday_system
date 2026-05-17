# PROGRESS

Chronological log of meaningful progress milestones.

- [2026-05-17] Phase 7 Layer1 PA candidate-selection design (`DESIGN_LAYER1_PA_CANDIDATE_SELECTION`) — `docs/LAYER1_CANDIDATE_SELECTION_CONTRACT.md`; `reconstruct_resolved_config_for_combo` + `evaluate_selection_gates` (`PA_L1_SELECTION_DESIGN_V1`); dry-run on Phase **6c** sweep (**7** hold / **9** reject); sample schema artifacts-only; `configs/candidates/l1_pa_controlled_v1/README.md` only; **340** `pytest`; decision **`LAYER1_PA_CANDIDATE_SELECTION_DESIGN_COMPLETE`**; next **`IMPLEMENT_LAYER1_PA_CANDIDATE_SELECTION_DRY_RUN`**.
- [2026-05-15] Phase 6d PA logic/grid diagnostics (`REVIEW_PA_LOGIC_OR_GRID`) — revalidated Phase **6c** sweep artifacts (**16**/16 combos), wrote axis/interaction diagnostics + readiness label `READY_TO_DESIGN_SELECTION`; serialization uplift noted before eventual YAML promotion; `artifacts/pa_logic_grid_review_phase6d/` bundle + doc/status alignment; validation **324** `pytest`; decision **`PA_GRID_REVIEW_COMPLETE_READY_FOR_SELECTION_DESIGN`**; next procedural step **`DESIGN_LAYER1_PA_CANDIDATE_SELECTION`**.
- [2026-05-15] Phase 6c Layer1 PA grid review — `is_absolute_path_like` + Layer1 `artifact_root` validation (Linux CI fix for `C:/tmp/abs`); tests `test_core_paths` + extended Layer1 loader tests; local QQQ 2024H1 curated grid **16/16** combos; `artifacts/layer1_pa_grid_review_phase6c/` review bundle; **324** `pytest`; decision `LAYER1_PA_GRID_RESULTS_REVIEW_COMPLETE`; next `REVIEW_PA_LOGIC_OR_GRID`.
- [2026-05-15] Phase 6b Layer1 PA controlled grid — explicit 16-combo PA grid YAML (`configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml`) + `configs/layer1/controlled_pa_qqq_2024h1.yaml`; `resolve_grid_combos` / `ResolvedGridCombo`; `run_layer1_controlled_grid` + shared `layer1_scan_trade_intents`; grid artifact writer; `layer1 grid` / `grid-inspect`; `count_rejected_in_metrics` flag + skip diagnostics; docs/status refresh; `artifacts/layer1_pa_controlled_grid_phase6b/` bundle; **303** `pytest`; local QQQ grid skipped (no curated parquet in workspace).
- [2026-05-15] Phase 6 Layer1 PA smoke — smoke YAML (`configs/layer1/`), `load_layer1_smoke_config` / validate, `merge_execution_spec_with_strategy`, `backtest/signal_adapter.py` → `TradeIntent`, `backtest/metrics.py` (`summarize_trade_results`), `run_layer1_smoke` + `Layer1SmokeResult`, `layer1` CLI (`run`/`inspect`), docs `LAYER1_CONTRACT` + `BACKTEST_CONTRACT`, PA preflight `parse_bool_like` + `score_mode`; unit + smoke tests; `artifacts/layer1_pa_smoke_phase6/` review bundle; local QQQ 2024H1 smoke executed (124 session-capped trades).
- [2026-05-15] Phase 5 PA strategy signal MVP — `SignalMatrix` contract + validation, strategy registry/loader/config validation, `pa_buy_sell_close_trend` signal generator (long-only, `pa_core_v1` features), PA base/metadata/grid YAML, `strategies` CLI (`list`/`inspect`/`generate-smoke`), synthetic + no-lookahead tests, `artifacts/strategy_pa_phase5/` review bundle.
- [2026-05-13] Phase 4 feature engine MVP — `resolve_feature_config` / `hash_feature_config`, builtin registry + reference kernels (VWAP, ORB, volatility, price action, volume, regime), `build_feature_matrix` + `FeatureStore`, `features` CLI (`list`/`inspect`/`build`), `docs/FEATURE_CONTRACT.md`, finalized `configs/features/pa_core_v1.yaml` (22 columns), unit + smoke tests (no-lookahead / session-reset), local QQQ 2024H1 feature smoke; `artifacts/feature_engine_phase4/` review bundle; status/docs/README refresh.
- [2026-05-13] Phase 3 fast execution + parity — finite guards on intents and required OHLC (`INVALID_MARKET_DATA`), `simulate_trade_path_fast` + Numba `_simulate_trade_path_fast_kernel` (shared `materialize_trade`), `parity.py` helpers, `tests/parity/test_execution_fast_parity.py` + `tests/unit/test_execution_fast_contract.py`, execution package exports; docs (`EXECUTION_CONTRACT`, `PHASE_PLAN`), README/status; `artifacts/execution_fast_phase3/` review bundle; optional QQQ data smoke unchanged.
- [2026-05-13] Phase 2 reference execution — `ExecutionSpec` validation + YAML load, `TradeIntent`/`TradeResult` contracts, `materialize_trade`, `simulate_trade_path_reference` (next-open, session guard, slippage, stop/target/EOD/max-hold, same-bar policy, costs, R-multiple), synthetic `BarMatrix` test helpers, execution unit/smoke tests; data README + raw schema constant clarification; docs/contracts/status handoff refresh; `artifacts/execution_reference_phase2/` review bundle.
- [2026-05-13] Phase 1B data foundation hardening — raw timestamp contract (`ts_ny`/`ts_utc`/… + YAML `raw_timestamp.column`), exact `session_date` window filtering, safe partial-month **write** guard, BarMatrix `session_id` recomputation, stronger validation invariants, `data timestamp-audit` / `data session-coverage`, inventory CSV path sanitization, doc/status sync, Phase 1B review artifacts.
- [2026-05-13] Phase 1 data foundation — raw schema/timestamp config, guarded raw canonicalization, IBKR→curated RTH normalization, BarMatrix loader, validation reports, expanded `data` CLI, and tests (synthetic + local QQQ 2024H1 smoke).
- [2026-05-12] Bootstrap intraday_system architecture skeleton (Phase 0/1A):
  - Initialized Git repo on `main`, remote `https://github.com/yukepenn/intraday_system.git`.
  - Added `pyproject.toml`, `Makefile`, `.gitignore`, `.gitattributes`, `README.md`.
  - Added doc suite under `docs/`: ARCHITECTURE, PROJECT_STRUCTURE, DATA_CONTRACT,
    CONFIG_CONTRACT, CACHE_CONTRACT, EXECUTION_CONTRACT, LAYER_FLOW, PHASE_PLAN,
    QT_REFERENCE_POLICY, DEVELOPMENT_WORKFLOW, DESIGN_BASELINE.
  - Added `configs/` skeleton (data, execution, features, strategies, candidates,
    layer1, layer2, layer3, reports).
  - Implemented `src/intraday/core/` (types, arrays, hashing, config, paths,
    errors, registry, constants).
  - Implemented `src/intraday/data/catalog.py` (parquet inventory + layout audit)
    and skeletons for `loader.py`, `normalize.py`, `validate.py`, `sessions.py`, `calendar.py`.
  - Added subsystem skeletons (features, strategies, execution, management,
    backtest, layer1 [with real `grid.py`], layer2, layer3, portfolio, reports,
    research, utils).
  - Implemented CLI with `--help`, `doctor`, `validate structure`,
    `data inventory` (Typer + argparse fallback).
  - Added unit tests (hashing, config, arrays, catalog, layer1.grid) and smoke
    tests (import, CLI help/doctor/validate, repo structure).
  - Generated raw data inventory: 104 parquet files locally, 34.3 MiB total,
    100% `legacy_qt_like`, 100% `safe_normal_git`.
  - Documented data canonicalization deferral to Phase 1.
  - Added CI workflow (`.github/workflows/ci.yml`).
  - Decision: `BOOTSTRAP_PHASE0_1A_COMPLETE` (next: `IMPLEMENT_DATA_FOUNDATION_BARMATRIX_NORMALIZATION`).
