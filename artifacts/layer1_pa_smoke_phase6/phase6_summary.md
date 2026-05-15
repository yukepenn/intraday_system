# Phase 6 summary — Layer1 PA smoke

## Implemented

- Layer1 smoke YAML + validation (`layer1/config.py`)
- Signal adapter (`backtest/signal_adapter.py`)
- Metrics aggregation (`backtest/metrics.py`)
- ExecutionSpec merge helper (`execution/spec.py`)
- Smoke runner + artifacts (`layer1/runner.py`, `layer1/reports.py`, `layer1/result.py`)
- CLI `layer1 run` / `inspect` (`cli/layer1_cmds.py`, `cli/main.py`)
- Docs: `LAYER1_CONTRACT.md`, `BACKTEST_CONTRACT.md`
- Preflight: strict bool + `score_mode` validation
- Tests: unit + smoke (286 total)

## Not implemented (explicit)

Parameter grids, candidate YAML promotion, GAP/CCI, Layer2/3, management overlays, portfolio sizing, WFO, broad research.

## Decision

See `layer1_pa_smoke_phase6_decision.md`.
