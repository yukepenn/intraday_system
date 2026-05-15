# baseline_inventory — Phase 6b start

Generated: **2026-05-15**

## Git / environment

| Item | Value |
| --- | --- |
| Branch | `main` |
| Local HEAD (before Phase 6b code) | `8ed49ff1d7f9ed5fe0013c335155010a8a36d8ce` |
| `origin/main` at preflight (after fetch) | `8ed49ff1d7f9ed5fe0013c335155010a8a36d8ce` |
| Local / remote match | yes |
| Working tree at Phase 0 snapshot | modified (implementation in progress for this bundle) |

## Handoff (pre-work)

| Item | Value |
| --- | --- |
| `NEXT_HANDOFF` decision | `LAYER1_PA_SMOKE_COMPLETE` |
| `NEXT_HANDOFF` recommended next | `IMPLEMENT_LAYER1_PA_CONTROLLED_GRID` |

## Phase 6 smoke reference

- `pytest` count at Phase 6 handoff: **286** (see prior `NEXT_HANDOFF.md`).
- Smoke artifacts: `artifacts/layer1_pa_smoke_phase6/`.

## Files inspected (design pass)

Root: `NEXT_HANDOFF.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `pyproject.toml`, `.gitignore`, `docs/*_CONTRACT.md`, `docs/PHASE_PLAN.md`, `docs/LAYER_FLOW.md`, `src/intraday/layer1/*`, `src/intraday/backtest/metrics.py`, `src/intraday/cli/main.py`, existing Phase 6 tests.

## Explicit non-goals (Phase 6b)

- Broad PA grids, prefix-biased slicing as research design, candidate YAML promotion, candidate selection as runtime truth, GAP/CCI, Layer2 router, Layer3 validation, WFO, management overlays, portfolio sizing, live/paper trading, PnL outside execution.

See `baseline_inventory.csv`.
