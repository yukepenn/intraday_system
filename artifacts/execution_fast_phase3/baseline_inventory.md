# Phase 3 baseline inventory

Generated at start of `IMPLEMENT_FAST_EXECUTION_SKELETON_AND_PARITY`.

| Field | Value |
| --- | --- |
| Local branch | main |
| Local HEAD (pre-work) | a53ca95d7f779db4c72324eb747337c3db8cc6bf |
| Remote origin/main (pre-work) | a53ca95d7f779db4c72324eb747337c3db8cc6bf |
| Local / remote matched | yes |
| Working tree (pre-work) | clean |
| NEXT_HANDOFF decision (pre-work) | REFERENCE_EXECUTION_ENGINE_COMPLETE |
| NEXT_HANDOFF recommended next step (pre-work) | IMPLEMENT_FAST_EXECUTION_SKELETON_AND_PARITY |
| Phase 2 test status (from handoff) | pytest 127 passed |

## Files inspected (read-first list)

Root: NEXT_HANDOFF.md, README.md, PROJECT_STATUS.md, PROGRESS.md, CHANGES.md, intraday_system_design_instructions.txt, pyproject.toml, .gitignore.

Docs: DESIGN_BASELINE.md, ARCHITECTURE.md, DATA_CONTRACT.md, CONFIG_CONTRACT.md, CACHE_CONTRACT.md, EXECUTION_CONTRACT.md, LAYER_FLOW.md, PHASE_PLAN.md, QT_REFERENCE_POLICY.md, DEVELOPMENT_WORKFLOW.md.

Execution: spec.py, intent.py, records.py, materialize.py, reference.py, cost.py, fast.py, parity.py, **init**.py.

Core: types.py, arrays.py, config.py, errors.py, hashing.py, constants.py; data loader/validate as referenced.

Configs: configs/execution/intraday_default.yaml, configs/data/ibkr_qqq_1m.yaml.

Tests: tests/unit/test_execution_*.py, tests/smoke/test_execution_reference_smoke.py, tests/helpers/bars.py.

## Explicit non-goals (Phase 3)

Feature kernels, strategies, Layer1/2/3, candidate YAML, portfolio sizing, management overlays in execution, research sweeps, QQQ-dependent core parity tests, PnL outside `src/intraday/execution/`, CSV/MD runtime config, committing parquet/cache/npy/npz/memmap.
