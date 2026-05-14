# Phase 4 baseline inventory

- **Date:** 2026-05-13
- **Branch:** `main`
- **Local HEAD (pre-work):** `723787f`
- **Remote `origin/main` (pre-work):** `723787f` (matched after `git fetch`)
- **Working tree:** clean at baseline; Phase 4 implementation adds tracked source/docs/tests/artifacts
- **NEXT_HANDOFF (pre-work) decision:** `FAST_EXECUTION_PARITY_COMPLETE`
- **NEXT_HANDOFF (pre-work) recommended next step:** `IMPLEMENT_FEATURE_ENGINE_MVP`
- **Phase 3 tests (from handoff):** `pytest` 171 passed; Ruff + compileall pass

## Files inspected (representative)

Root handoff and design: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `intraday_system_design_instructions.txt`, `pyproject.toml`, `.gitignore`

Contracts / architecture: `docs/DESIGN_BASELINE.md`, `docs/ARCHITECTURE.md`, `docs/DATA_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `docs/CACHE_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, `docs/LAYER_FLOW.md`, `docs/PHASE_PLAN.md`, `docs/QT_REFERENCE_POLICY.md`, `docs/DEVELOPMENT_WORKFLOW.md`

Core / data / execution: `src/intraday/core/{types,arrays,config,errors,hashing,constants,registry}.py`, `src/intraday/data/{loader,validate}.py`, `src/intraday/execution/{reference,fast,parity}.py`

Feature skeleton → MVP: `src/intraday/features/**`, `configs/features/pa_core_v1.yaml`, CLI `src/intraday/cli/{main,feature_cmds}.py`

## Explicit non-goals (Phase 4)

PA/GAP/CCI strategy signals; Layer1/2/3; candidate YAML; router; management overlays; portfolio sizing; sweeps; PnL outside execution; QT runtime dependency; CSV/MD as runtime config; committing parquet/cache/npz; feature fast kernels.
