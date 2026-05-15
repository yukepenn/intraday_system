# NEXT_HANDOFF

Last updated: **2026-05-15** (Phase 6 Layer1 PA smoke).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Phase 6 implementation commit: see `git log -1 --oneline` / `git rev-parse HEAD` after push
- Windows: `git config --global --add safe.directory <repo>` if needed

## B. Task scope

Phase **6**: **Layer1 PA smoke run** — one strategy YAML + one smoke YAML + one data window → signals → execution → `TradeResult` metrics → small artifacts (no grid, no candidates).

**In scope:** `docs/LAYER1_CONTRACT.md`, `docs/BACKTEST_CONTRACT.md`, smoke config, signal adapter, TradeResult-only metrics, `run_layer1_smoke`, `layer1` CLI, PA preflight (`parse_bool_like`, `score_mode`), synthetic tests + optional local QQQ smoke, `artifacts/layer1_pa_smoke_phase6/`.

**Out of scope:** parameter grids, candidate YAML generation/promotion, GAP/CCI, Layer2/3, management overlays, portfolio sizing, WFO, profitability claims.

## C. Preflight fixes

- `parse_bool_like` in `strategies/config_validation.py` (`require_vwap_side`).
- `signal.score_mode` must be `simple_pa_v1` (Phase 6); generator guard in `buy_sell_close_trend.py`.
- `CHANGES.md` / `PHASE_PLAN.md` status alignment.

## D. Layer1 / backtest contract

- Layer1 smoke role: first plumbing proof (see `LAYER1_CONTRACT.md`).
- Backtest orchestration does not compute PnL independently (`BACKTEST_CONTRACT.md`).

## E. Smoke config

- `configs/layer1/smoke_pa_qqq_2024h1.yaml`
- QQQ 2024-01-01..2024-06-30, reference execution, `max_trades_per_session: 1`.

## F. Signal adapter

- `src/intraday/backtest/signal_adapter.py` — `SignalAdapterResult`.

## G. Metrics

- `src/intraday/backtest/metrics.py` — `summarize_trade_results`.

## H. Runner / CLI

- `src/intraday/layer1/runner.py` — `run_layer1_smoke`
- `python -m intraday.cli.main layer1 run --config configs/layer1/smoke_pa_qqq_2024h1.yaml`

## I. Local QQQ PA smoke

- With curated data: 48360 rows; 4092 entries; 124 executed (session cap); metrics in `artifacts/layer1_pa_smoke_phase6/local_qqq_pa_smoke.*`.
- `artifacts/layer1_pa_smoke_phase6/local_run/` is **gitignored** (regenerate locally).

## J. Tests / validation

- `python -m compileall -q src` — pass
- `pytest -q` — **286** passed
- Ruff format/check — pass
- CLI: `--help`, `doctor`, `validate structure`, `layer1`, `data validate-curated`, `features inspect`, `strategies inspect` — pass

See `artifacts/layer1_pa_smoke_phase6/validation_results.*`.

## K. Explicit non-implemented items

- Layer1 **controlled grid** / sweep orchestration (next phase label).
- Candidate promotion, candidate YAMLs, GAP/CCI, Layer2 router, Layer3 validation, management overlays, portfolio sizing, broad research, WFO/live/paper.

## L. Risks / blockers

- Smoke scan policy materially reduces executed count vs raw entries (by design).
- Local curated data absent → document skip; rely on synthetic tests.

## M. Files changed (high level)

- `src/intraday/{backtest,layer1,cli,execution,strategies}/`
- `configs/layer1/smoke_pa_qqq_2024h1.yaml`
- `docs/{LAYER1_CONTRACT,BACKTEST_CONTRACT,LAYER_FLOW,PHASE_PLAN,ARCHITECTURE}.md`
- `tests/unit/test_{signal_adapter,backtest_metrics,layer1_config,layer1_runner,execution_spec_merge,strategy_config_validation}.py`
- `tests/smoke/test_layer1_cli.py`
- `artifacts/layer1_pa_smoke_phase6/*` (review tables; not `local_run/`)
- Status: `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `NEXT_HANDOFF.md`
- `.gitignore` (local_run + pytest runner dirs under phase6 tree)

## N. Artifact hygiene

- No raw/curated parquet, caches, npy/npz/memmap, or row-level heavy trade dumps staged.
- `local_run/` and `_pytest_runner*/` under `artifacts/layer1_pa_smoke_phase6/` gitignored.

## O. Decision

`LAYER1_PA_SMOKE_COMPLETE`

## P. Recommended next step

`IMPLEMENT_LAYER1_PA_CONTROLLED_GRID`
