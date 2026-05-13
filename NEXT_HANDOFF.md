# NEXT_HANDOFF

Last updated: **2026-05-13** (Phase 2 reference execution engine).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- After this task’s commit: use `git log -1 --oneline` and `git rev-parse HEAD` for the authoritative SHA (pre-Phase-2 baseline was `7110c1f` in `artifacts/execution_reference_phase2/baseline_inventory.*`).
- Windows: `git config --global --add safe.directory <repo>` if Git reports “dubious ownership”.

## B. Task scope

Phase **2** only: **reference execution truth** in Python — `TradeIntent` + `BarMatrix` + `ExecutionSpec` → `TradeResult` via `materialize_trade` and `simulate_trade_path_reference`.

**In scope:** next-open entry, session-boundary guard, entry/exit slippage, stop/risk/min-risk validation, fixed-R target from actual entry, intrabar stop/target, same-bar policy, EOD and max-hold ordering, truncated-window and session-roll defensive exits, gross/net PnL, R-multiple, reject/exit reasons, synthetic tests.

**Out of scope (unchanged):** Numba fast path (beyond placeholder), feature kernels, strategy logic, Layer1/2/3, candidate YAML, portfolio sizing, management overlays inside execution, research sweeps.

## C. Execution contract

- `ExecutionSpec` validates all numeric bounds and enums; `from_config` / `load_execution_spec` / `to_dict`.
- `TradeIntent.validate_shape` + materialization rejects for session/window/stop/risk/short.
- `TradeResult.rejected` / `accepted_trade` convention documented in `docs/EXECUTION_CONTRACT.md`.
- New `RejectReason.INVALID_INTENT` — see `artifacts/execution_reference_phase2/execution_contract_changes.md`.

## D. Materialization semantics

- `entry_bar = signal_bar + 1`; `NO_NEXT_BAR`, `CROSS_SESSION_ENTRY`, `OUTSIDE_TRADING_WINDOW` (when `minute[entry_bar] > eod_exit_minute`), `SHORT_NOT_ALLOWED`, `INVALID_STOP`, `RISK_TOO_SMALL`.
- Entry slippage adverse per side; target from slippaged entry and `target_r`.
- Max-hold: intent `> 0` wins; else `max_hold_bars_default`; else unlimited.

## E. Reference path semantics

- Per bar: intrabar stop/target → EOD (`minute >= eod_exit_minute`) → max-hold; **EOD before max-hold** on the same bar.
- `conservative` same-bar policy equals `stop_first`.
- Session change while open → exit prior bar close as `EOD`; end-of-matrix fallback → last bar close `EOD`.
- `management_plan != None` → `IntradaySystemError`.

## F. Cost / R conventions

- `cost.py`: `apply_entry_slippage`, `apply_exit_slippage`, `compute_gross_pnl`, `compute_net_pnl`, `compute_r_multiple`; `apply_slippage` = entry alias.

## G. Tests / validation

- `python -m compileall -q src` — pass
- `pytest -q` — **127** passed (synthetic execution tests; no QQQ in unit tests)
- Ruff format/check — pass
- CLI: `--help`, `doctor`, `validate structure` — pass
- Data smoke (local curated present): `data validate-curated` + `data load-bars` QQQ 2024H1 — pass

See `artifacts/execution_reference_phase2/validation_results.*`.

## H. Explicit non-implemented items

- `execution.fast` Numba batch simulator (placeholder only).
- Feature engine, strategies, Layer1 runner, Layer2 router, Layer3 validation.
- Management overlays (scale-out, trailing, no-followthrough) and portfolio sizing.

## I. Risks / blockers

- **Git safe.directory** on some Windows setups.
- **SPY** legacy raw layout until migrated.
- **Early-close / exchange calendar** heuristics unchanged from Phase 1B.

## J. Files changed (high level)

- `src/intraday/execution/{spec,intent,records,cost,materialize,reference,__init__}.py`
- `src/intraday/core/types.py` (`INVALID_INTENT`)
- `src/intraday/data/schema.py` (OHLCV constant rename / alias)
- `data/**/README.md`, `docs/{EXECUTION_CONTRACT,PHASE_PLAN,LAYER_FLOW}.md`
- `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `NEXT_HANDOFF.md`
- `tests/helpers/bars.py`, `tests/unit/test_execution_*.py`, `tests/smoke/test_execution_reference_smoke.py`
- `artifacts/execution_reference_phase2/*`

## K. Artifact hygiene

- No raw/curated parquet, cache, npy/npz/memmap, or forbidden paths **staged**.

## L. Optional CLI

- No `execution smoke` subcommand (skipped to avoid CLI scope creep); synthetic coverage lives under `tests/`.

## M. Decision

`REFERENCE_EXECUTION_ENGINE_COMPLETE`

## N. Recommended next step

`IMPLEMENT_FAST_EXECUTION_SKELETON_AND_PARITY`
