# Phase 14 ? PHASE14_PREFLIGHT_AND_LAYER1_STRATEGY_LIBRARY_SMALL_GRID_DIAGNOSTIC

## Summary

- Phase name: `PHASE14_PREFLIGHT_AND_LAYER1_STRATEGY_LIBRARY_SMALL_GRID_DIAGNOSTIC`
- Branch: `main`
- Pre-task HEAD: `dbaeb3d96f32585d04ed9450affa0751b1a974e9`
- Previous Cursor task commit reviewed by Codex: `0762f9197f7a08037d8cd6f9ff0ecca3cd9d5d5e`
- HEAD at start: Codex review commit `dbaeb3d96f32585d04ed9450affa0751b1a974e9`; Phase 13 task commit is the reviewed parent target `0762f9197f7a08037d8cd6f9ff0ecca3cd9d5d5e`.
- Final commit hash: recorded in final Cursor response after commit.
- Decision label: `LAYER1_STRATEGY_LIBRARY_SMALL_GRID_DIAGNOSTIC_COMPLETE`
- Recommended next step: `REVIEW_LAYER1_STRATEGY_LIBRARY_SMALL_GRID_RESULTS`

## Phase 13 Repairs

Repaired 7 malformed CSV audit artifacts in place with `csv.DictWriter`:

- `artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/SOURCE_MAP.csv` ? Rewrote in place with csv.DictWriter and preserved existing row content.
- `artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/chatgpt_key_tables.csv` ? Rewrote in place with csv.DictWriter and preserved existing row content.
- `artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/validation_results.csv` ? Rewrote in place with csv.DictWriter and preserved existing row content.
- `artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/strategy_inventory.csv` ? Rewrote in place with csv.DictWriter and preserved existing row content.
- `artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/feature_requirements_matrix.csv` ? Rewrote in place with csv.DictWriter and preserved existing row content.
- `artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/config_inventory.csv` ? Rewrote in place with csv.DictWriter and preserved existing row content.
- `artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/phase14_readiness_matrix.csv` ? Rewrote in place with csv.DictWriter and preserved existing row content.

## Data Availability

| Window | Status | Rows | Notes |
| --- | --- | ---: | --- |
| `qqq_2024h1` | `PASS` / `PASS` | 48360 | 124 full sessions; no warnings.  |
| `qqq_2024h2` | `PASS_WITH_WARNINGS` / `PASS` | 49380 | Optional exact-repeat sanity diagnostic ran with existing H2 data; not confirmation/promotion. missing_minute_slots_total=540 |

## Layer1 Configs

- Created 20 Layer1 controlled-grid diagnostic configs under `configs/layer1/phase14_strategy_library_small_grid/`.
- H1 primary: 10 configs, all `grid-inspect` PASS.
- H2 exact-repeat sanity: 10 configs, all `grid-inspect` PASS.
- Combo counts: PA 16; all other strategy grids 24; no prefix slicing.

## H1 Diagnostic Summary

| Strategy | Combos | Signals | Accepted | Rejected | Health |
| --- | ---: | ---: | ---: | ---: | --- |
| `pa_buy_sell_close_trend` | 16/16 | 56524 | 1908 | 0 | `CLEAN_PLUMBING` |
| `orb_continuation` | 24/24 | 1848 | 1840 | 8 | `CLEAN_PLUMBING` |
| `orb_retest_continuation` | 24/24 | 1728 | 1716 | 12 | `CLEAN_PLUMBING` |
| `failed_orb` | 24/24 | 1284 | 1254 | 30 | `CLEAN_PLUMBING` |
| `gap_acceptance_failure` | 24/24 | 176 | 176 | 0 | `CLEAN_PLUMBING` |
| `vwap_trend_pullback` | 24/24 | 2730 | 2730 | 0 | `CLEAN_PLUMBING` |
| `vwap_reclaim_reject` | 24/24 | 2304 | 2296 | 8 | `CLEAN_PLUMBING` |
| `prior_day_level_trap` | 24/24 | 606 | 602 | 4 | `CLEAN_PLUMBING` |
| `cci_extreme_snapback` | 24/24 | 2964 | 2954 | 10 | `CLEAN_PLUMBING` |
| `stochastic_oversold_cross` | 24/24 | 2802 | 2784 | 18 | `CLEAN_PLUMBING` |

## H2 Exact-Repeat Sanity Summary

| Strategy | Combos | Signals | Accepted | Rejected | Health |
| --- | ---: | ---: | ---: | ---: | --- |
| `pa_buy_sell_close_trend` | 16/16 | 58316 | 1916 | 0 | `CLEAN_PLUMBING` |
| `orb_continuation` | 24/24 | 2052 | 2052 | 0 | `CLEAN_PLUMBING` |
| `orb_retest_continuation` | 24/24 | 1860 | 1860 | 0 | `CLEAN_PLUMBING` |
| `failed_orb` | 24/24 | 1452 | 1431 | 21 | `CLEAN_PLUMBING` |
| `gap_acceptance_failure` | 24/24 | 132 | 130 | 2 | `CLEAN_PLUMBING` |
| `vwap_trend_pullback` | 24/24 | 2544 | 2536 | 8 | `CLEAN_PLUMBING` |
| `vwap_reclaim_reject` | 24/24 | 2040 | 2040 | 0 | `CLEAN_PLUMBING` |
| `prior_day_level_trap` | 24/24 | 462 | 458 | 4 | `CLEAN_PLUMBING` |
| `cci_extreme_snapback` | 24/24 | 3066 | 3050 | 16 | `CLEAN_PLUMBING` |
| `stochastic_oversold_cross` | 24/24 | 2802 | 2790 | 12 | `CLEAN_PLUMBING` |

## Validation Commands

- `python -m compileall src tests`: PASS
- `python -m pytest -q`: PASS (`445 passed`)
- `python -m pytest -q tests/smoke`: PASS (`25 passed`)
- CLI doctor/structure/features/strategies inspections: PASS
- Data validate/load H1: PASS
- Data validate/load H2: PASS_WITH_WARNINGS for validation (`missing_minute_slots_total=540`), load PASS
- Layer1 grid-inspect: PASS for 20/20 configs
- Layer1 grid: PASS for 10/10 H1 and 10/10 H2 configs
- `python -m ruff check .`: FAIL_UNRELATED_EXISTING after Phase14 test lint fixes; remaining findings are pre-existing `scripts/generate_phase7_dry_run.py` and `scripts/validate_repo.py`.
- `python -m ruff format --check .`: FAIL_UNRELATED_EXISTING on pre-existing `scripts/generate_phase7_dry_run.py`.

Full command ledger: `validation_results.csv`.

## Artifact Schema

`artifact_schema_validation.csv` validates all required Phase 14 CSVs and repaired Phase 13 CSVs with `csv.DictReader`. No character-split headers remain.

## Non-Goals Preserved

No candidate YAML, no candidate promotion, no select-dry-run, no Layer2, no Layer3, no WFO, no live/paper, no execution truth changes, no strategy retuning from results, no QT runtime dependency, and CSV/MD artifacts remain audit-only.

## Known Limitations

- QQQ-only diagnostic windows.
- Tiny controlled grids only; not broad research.
- H2 was an exact-repeat sanity diagnostic because local data exists; it is not confirmation or promotion evidence.
- Performance metrics are diagnostic facts only; top rows are not candidates.
- Ruff full-repo lint still has unrelated pre-existing script findings recorded in `validation_results.csv`.
