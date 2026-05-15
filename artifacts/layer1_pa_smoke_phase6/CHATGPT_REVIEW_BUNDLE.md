# CHATGPT_REVIEW_BUNDLE — Phase 6 Layer1 PA smoke

Readable on GitHub; summarizes scope, plumbing, and validation.

## A. Git baseline

- Branch: `main`
- Pre-Phase-6 HEAD: `68b141bef5ff611f81d51114da1d223b860cd600` (matched `origin/main` at task start)

## B. Why Phase 6

Prove first **end-to-end** path: `BarMatrix` → `FeatureMatrix` → `SignalMatrix` → `TradeIntent` → execution → `TradeResult` → metrics → small artifacts — without grids, candidates, or Layer2/3.

## C. Preflight fixes

- `parse_bool_like` for `require_vwap_side` (no `bool("false")` bug)
- `signal.score_mode` must be `simple_pa_v1` (Phase 6)
- Stale status entries updated (`CHANGES` / `PHASE_PLAN`)

## D. Contracts

- `docs/LAYER1_CONTRACT.md` — Layer1 smoke role and non-goals
- `docs/BACKTEST_CONTRACT.md` — orchestration vs execution ownership

## E. Smoke config

- `configs/layer1/smoke_pa_qqq_2024h1.yaml` — QQQ 2024H1, reference execution, `max_trades_per_session: 1`

## F. Signal adapter

- `src/intraday/backtest/signal_adapter.py` — `SignalAdapterResult` with skip reason counts

## G. Metrics

- `src/intraday/backtest/metrics.py` — `BacktestMetrics` / `summarize_trade_results` (TradeResult-only)

## H. Runner / CLI

- `src/intraday/layer1/runner.py` — `run_layer1_smoke`
- `python -m intraday.cli.main layer1 run --config ...`

## I. Local QQQ PA smoke

- 48360 rows, 4092 entries, 124 executed (session cap), metrics in `local_qqq_pa_smoke.md` / `.csv`
- **Interpretation:** plumbing check only; not edge/profit proof

## J. Tests / validation

- `pytest` **286** passed; ruff format/check; compileall; CLI doctor/validate/layer1

## K. Not implemented

Grids, candidate YAML, promotion, GAP/CCI, Layer2 router, Layer3 validation, management overlays, portfolio sizing, WFO/live/paper.

## L. Risks / blockers

- Smoke metrics depend on session scan policy (intentionally conservative).
- `local_run/` outputs are gitignored; committed tables under `artifacts/layer1_pa_smoke_phase6/` are summaries.

## M. Decision / next

- **Decision:** `LAYER1_PA_SMOKE_COMPLETE`
- **Next:** `IMPLEMENT_LAYER1_PA_CONTROLLED_GRID`

## N. Source map / key tables

See `SOURCE_MAP.csv` and `chatgpt_key_tables.csv`.
