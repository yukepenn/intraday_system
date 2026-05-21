# Phase19 Non-Goals

Phase19 is design-only and limited to:

- system-wide side-support architecture design
- Brooks PA feature foundation design
- Brooks PA strategies 11-20 design
- file/test/validation plans for the future implementation phase
- design artifacts (CSV/MD) under `artifacts/phase19_brooks_pa_design/`

Phase19 is NOT:

- No candidate YAML.
- No candidate promotion.
- No `layer1 select-dry-run` execution.
- No actual `layer1 grid` runs.
- No expanded/full grid runs.
- No Layer2 router, combiner, conflict policy, daily risk state, or portfolio sizing.
- No Layer3 frozen validation, no folds.
- No WFO (walk-forward optimization) or mini-WFO.
- No live trading.
- No paper trading.
- No economic claims (no PnL, R, profit factor, Sharpe, top-row ranking).
- No use of H2 (2024H2) as confirmation evidence; H2 remains diagnostic-only as in prior phases.
- No top-row retuning derived from Phase16/17/18 grid results.
- No hard-coded thresholds inside Brooks strategies that were derived from observed Phase16/17/18 results. All thresholds in this design are rational ranges only.
- No QT runtime dependency. QT is reference-only and read-only per `docs/QT_REFERENCE_POLICY.md`.
- No QT import in any source file.
- No copying of QT folder layout, kernels, or runtime architecture.
- No execution truth change. `simulate_trade_path_reference` remains canonical. `simulate_trade_path_fast` is acceleration only.
- No new `RejectReason`, no new `ExitReason`, no change to fill / stop / target / EOD / max-hold semantics.
- No management overlays (scale-out, trailing stops, no-followthrough).
- No materialization of target prices in strategies; strategies emit `target_r` only.
- No materialization of range_mid, magnet, or measured-move target prices in strategies.
- No PA-specific feature hacks; Brooks features must be generic market facts.
- No outcome labels (no `pa_is_winner`, no `pa_target_reached_*`).
- No future-bar dependencies in any Brooks feature; current bar allowed only under bar-close-signal / next-open-execution.
- No centered rolling pivots; swing/wedge/MTR features must be prior-exclusive or delayed-confirmed.
- No new feature kernels in this design phase.
- No new strategy source files in this design phase.
- No new feature YAMLs in this design phase.
- No new runtime strategy config YAMLs in this design phase.
- No edits to `src/intraday/backtest/signal_adapter.py` in this design phase.
- No edits to `src/intraday/strategies/contracts.py` in this design phase.
- No edits to `src/intraday/execution/*.py` in this design phase.
- No edits to `register_builtin_strategies()` in this design phase.
- No edits to `configs/execution/intraday_default.yaml` in this design phase.
- No edits to any current-10 strategy source file, base YAML, metadata YAML, or grid YAML.
- No `v2` suffix on any new Phase19 file or directory; `_v2` may only appear when referring to existing Phase18B/C/D current-10 historical artifacts.
- No staging of `data/raw/`, `data/curated/`, `data/cache/`, parquet, `.npy`, `.npz`, memmap, row-level trades/equity, top_runs, or other heavy local outputs.
- No staging of the local `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` tree.
- No edits to `CODEX_REVIEW.md`.
- No `git add .`; only explicit file paths are staged.
- No strategies 21-50 in this design.
- No retrofit of short branches onto current-10 strategies in this design or in the Phase19 implementation phase.

Inspect / grid-inspect / strategy-inspect / feature-inspect output is configuration readiness only. It is NOT alpha evidence and must not be used to rank strategies by R, profit factor, drawdown, or any economic metric.
