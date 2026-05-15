# NEXT_HANDOFF

Last updated: **2026-05-15** (Phase 6b Layer1 PA controlled grid).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- **Implementation commit:** after this handoff, read `git log -1 --oneline` / `git rev-parse HEAD` on `main` for the exact SHA (not embedded here to avoid amend workflows).

## B. Task scope

Phase **6b**: **Layer1 PA controlled grid** — small explicit strategy grid YAML → resolved configs → same Phase 6 plumbing per combo → **one** `Layer1GridRow` / `sweep_results.csv` row per combo — **not** candidate factory, **not** broad research.

**In scope:** `ResolvedGridCombo` / `resolve_grid_combos`, `Layer1ControlledGridConfig`, `run_layer1_controlled_grid`, `write_layer1_grid_artifacts`, `layer1 grid` / `grid-inspect`, controlled grid + Layer1 YAMLs, `count_rejected_intents` Option A, docs updates, `artifacts/layer1_pa_controlled_grid_phase6b/`.

**Out of scope:** Candidate promotion, candidate YAMLs, GAP/CCI, Layer2/3, WFO, overlays, portfolio sizing, prefix-biased grid slicing, profitability claims.

## C. Preflight fixes

- `CHANGES.md` / `docs/PHASE_PLAN.md` — Phase 6b + next-step alignment.
- **`count_rejected_intents`:** `summarize_trade_results(..., count_rejected_in_metrics=...)`; smoke/grid `skip_counts` distinguish `execution_rejected_included` vs `execution_rejected_excluded`.

## D. Controlled-grid contract

- Infrastructure validation only; one PA family; **16** explicit combos in shipped grid YAML.
- No prefix slicing (`allow_prefix_slicing: false` enforced); hard max **24** combos in validator.

## E. Grid configs

- `configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml`
- `configs/layer1/controlled_pa_qqq_2024h1.yaml` (`run_id: L1_PA_QQQ_2024H1_CONTROLLED_GRID_V1`, `execution.mode: reference`)

## F. Grid resolver / hashing

- `load_grid_document`, `normalize_override_mapping`, `expand_grid`, `grid_document_combo_count`, `resolve_grid_combos`
- Merge: base → fixed → combo; overlap raises `ValueError`.
- `params_json` = canonical JSON of **grid-axis** nested dict; `config_hash` = `hash_config(resolved_config)`.

## G. Grid runner

- `run_layer1_controlled_grid` — bars + features **once**; per combo validate → signals → adapter → `layer1_scan_trade_intents` → metrics.

## H. Reports / artifacts

- `write_layer1_grid_artifacts`: `sweep_results.csv`, `controlled_grid_summary.*`, inventories, reason distributions, top-row CSVs (review only).

## I. Local QQQ controlled grid

- **Skipped** in workspace without curated parquet; procedure documented in `artifacts/layer1_pa_controlled_grid_phase6b/local_qqq_controlled_grid.*`.

## J. Tests / validation

- `python -m compileall -q src` — pass
- `pytest -q` — **303** passed
- Ruff format/check — pass
- CLI: `--help`, `doctor`, `validate structure`, `layer1 grid-inspect` on repo YAML — pass

## K. Explicit non-implemented items

- Candidate selection, candidate YAML promotion, broad PA grid, GAP/CCI, Layer2 router, Layer3 validation, management overlays, portfolio sizing, WFO, live/paper trading.

## L. Risks / blockers

- Grid discipline: keep YAML grids small/explicit; never use prefix slicing as research design.
- Local-only curated data: infra milestone does not require QQQ parquet if synthetic tests pass.

## M. Files changed (high level)

- `src/intraday/layer1/{grid.py,config.py,runner.py,reports.py,result.py,__init__.py}`
- `src/intraday/backtest/metrics.py`
- `src/intraday/cli/{main.py,layer1_cmds.py}`
- `configs/layer1/controlled_pa_qqq_2024h1.yaml`, `configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml`
- `docs/{LAYER1_CONTRACT,BACKTEST_CONTRACT,LAYER_FLOW,PHASE_PLAN,ARCHITECTURE}.md`
- `tests/unit/test_layer1_grid.py`, `test_layer1_{grid_config,grid_runner,grid_reports}.py`, `test_{backtest_metrics,layer1_runner}.py`, `tests/smoke/test_layer1_grid_cli.py`
- `artifacts/layer1_pa_controlled_grid_phase6b/*` (review tables; not `local_run/`)
- Status: `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `NEXT_HANDOFF.md`
- `.gitignore` (phase6b `local_run/`, `_pytest_*`)

## N. Artifact hygiene

- No raw/curated parquet, caches, npy/npz/memmap, or row-level trade dumps staged.
- `artifacts/layer1_pa_controlled_grid_phase6b/local_run/` gitignored.

## O. Decision

`LAYER1_PA_CONTROLLED_GRID_COMPLETE`

## P. Recommended next step

`REVIEW_LAYER1_PA_GRID_RESULTS`
