# NEXT_HANDOFF

Last updated: **2026-05-13** (Phase 3 fast execution + parity).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- After this task’s commit: use `git log -1 --oneline` and `git rev-parse HEAD` for the authoritative SHA (pre-Phase-3 baseline was `a53ca95` in `artifacts/execution_fast_phase3/baseline_inventory.*`).
- Windows: `git config --global --add safe.directory <repo>` if Git reports “dubious ownership”.

## B. Task scope

Phase **3**: **fast execution skeleton + parity** — `TradeIntent` + `BarMatrix` + `ExecutionSpec` → `TradeResult` via `simulate_trade_path_fast`, parity-matched to `simulate_trade_path_reference`.

**In scope:** Numba post-entry kernel; shared `materialize_trade`; finite guards (`INVALID_MARKET_DATA`, tightened `INVALID_INTENT` / `INVALID_STOP`); parity helpers; synthetic parity matrix under `tests/parity/`; docs and status refresh.

**Out of scope (unchanged):** batch `simulate_trade_paths_fast`, feature kernels, strategy logic, Layer1/2/3, candidate YAML, portfolio sizing, management overlays inside execution, research sweeps.

## C. Reference hardening

- `TradeIntent.validate_shape`: finite `qty` / `target_r`; finite `raw_stop_price` → `INVALID_STOP`.
- `materialize_trade`: non-finite `open[entry_bar]` → `INVALID_MARKET_DATA`.
- `simulate_trade_path_reference`: non-finite `high`/`low` on scan bars; non-finite `close` when used for EOD/max-hold/session roll/end fallback; non-finite raw exit in `finalize` → `INVALID_MARKET_DATA`.
- Rejected-row convention unchanged (`entry_bar=-1`, `exit_bar=-1`, NaN prices, zero PnL/R).
- Tests: `tests/unit/test_execution_contracts.py`, `test_execution_materialize.py`, `test_execution_reference.py`, plus parity file for market rejects.

## D. Fast contract

- Public: `simulate_trade_path_fast(bars, intent, spec, management_plan=None) -> TradeResult`.
- `management_plan != None` → `IntradaySystemError` (same message as reference).
- Policy codes for kernel: `stop_first`/`conservative` → 0, `target_first` → 1; side `+1`/`-1`.
- Fixed return tuple from kernel converted to `TradeResult` in Python.

## E. Fast kernel implementation

- `_simulate_trade_path_fast_kernel` in `fast.py`, `@njit(cache=True)`.
- Inlines exit slippage, gross/net PnL, R-multiple to match `cost.py` formulas.
- Materialization not duplicated in Numba (calls `materialize_trade` in wrapper).

## F. Parity test matrix

- `tests/parity/test_execution_fast_parity.py` — 35 named scenarios (materialization rejects, long/short paths, same-bar, EOD/max-hold, costs, management error).
- `tests/unit/test_execution_fast_contract.py` — API smoke + trivial parity.
- Matrix tables: `artifacts/execution_fast_phase3/parity_test_matrix.*`.

## G. Supported / unsupported semantics

**Supported (fast):** Phase 2 fixed-R single-trade semantics mirrored on synthetic tests (next-open via shared materializer, session/cross-session/window rejects, stop/target/EOD/max-hold ordering, same-bar policies, slippage/commission/R, long/short with `allow_short`, session roll, truncation, finite-data rejects).

**Unsupported:** scale-out, trailing, no-followthrough, portfolio sizing, router decisions, batch multi-intent fast API, strategies, Layer1/2/3.

## H. Tests / validation

- `python -m compileall -q src` — pass
- `pytest -q` — **171** passed
- Ruff format/check — pass
- CLI: `--help`, `doctor`, `validate structure` — pass
- Data smoke (local curated present): `data validate-curated` + `data load-bars` QQQ 2024H1 — pass

See `artifacts/execution_fast_phase3/validation_results.*`.

## I. Explicit non-implemented items

- `simulate_trade_paths_fast` batch path.
- Feature engine, strategies, Layer1 runner, Layer2 router, Layer3 validation.
- Management overlays (scale-out, trailing, no-followthrough) and portfolio sizing.

## J. Risks / blockers

- **Git safe.directory** on some Windows setups.
- **SPY** legacy raw layout until migrated.
- **Early-close / exchange calendar** heuristics unchanged from Phase 1B.
- **Numba** first-call compile/cache behavior in cold CI (mitigated by tests).

## K. Files changed (high level)

- `src/intraday/execution/{fast,parity,reference,materialize,__init__}.py`, `src/intraday/execution/intent.py`
- `src/intraday/core/types.py`
- `src/intraday/cli/main.py` (help string)
- `docs/{EXECUTION_CONTRACT,PHASE_PLAN}.md`, `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `NEXT_HANDOFF.md`
- `tests/parity/test_execution_fast_parity.py`, `tests/unit/test_execution_fast_contract.py`, `tests/unit/test_execution_{contracts,materialize,reference}.py`
- Ruff-driven format on: `src/intraday/core/{arrays,config,paths}.py`, `src/intraday/features/engine.py`, `src/intraday/layer1/grid.py`, `tests/smoke/test_data_cli.py`, `tests/unit/test_layer1_grid.py`, `tests/unit/test_timestamp_semantics.py`
- `artifacts/execution_fast_phase3/*`

## L. Artifact hygiene

- No raw/curated parquet, cache, npy/npz/memmap, or forbidden paths **staged**.

## M. Optional CLI

- No `execution smoke` subcommand; synthetic coverage lives under `tests/`.

## N. Decision

`FAST_EXECUTION_PARITY_COMPLETE`

## O. Recommended next step

`IMPLEMENT_FEATURE_ENGINE_MVP`
