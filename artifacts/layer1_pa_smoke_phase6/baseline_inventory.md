# Phase 6 baseline inventory (Layer1 PA smoke)

Generated during `IMPLEMENT_LAYER1_PA_SMOKE_RUN`.

| Field | Value |
| --- | --- |
| Local branch | `main` |
| Local HEAD SHA (start of Phase 6 work) | `68b141bef5ff611f81d51114da1d223b860cd600` |
| Remote `main` SHA (after `git fetch`) | `68b141bef5ff611f81d51114da1d223b860cd600` |
| Local/remote matched | yes |
| Working tree | clean aside from Phase 6 implementation files |
| NEXT_HANDOFF decision (start) | `PA_STRATEGY_MVP_COMPLETE` |
| NEXT_HANDOFF recommended next (start) | `IMPLEMENT_LAYER1_PA_SMOKE_RUN` |
| Phase 5 tests (prior handoff) | `pytest` 257 passed |

## Files inspected (design + code)

Root: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `pyproject.toml`, `.gitignore`.

Contracts: `docs/DESIGN_BASELINE.md`, `docs/ARCHITECTURE.md`, `docs/DATA_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `docs/CACHE_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, `docs/FEATURE_CONTRACT.md`, `docs/STRATEGY_CONTRACT.md`, `docs/LAYER_FLOW.md`, `docs/PHASE_PLAN.md`, `docs/QT_REFERENCE_POLICY.md`, `docs/DEVELOPMENT_WORKFLOW.md`.

Core pipeline: `src/intraday/core/{arrays,types,config,hashing,errors}.py`, `src/intraday/data/loader.py`, `src/intraday/features/engine.py`, `src/intraday/strategies/{pa/buy_sell_close_trend,config_validation,contracts,loader,registry}.py`, `src/intraday/execution/{spec,intent,records,reference,fast,parity}.py`, `src/intraday/{backtest,layer,cli}/` as touched.

## Explicit non-goals (Phase 6)

No broad sweeps, no PA parameter grids, no candidate YAML generation/promotion, no GAP/CCI, no Layer2/3, no management overlays, no portfolio sizing, no new feature kernels except preflight fixes, no PnL outside `execution/`.
