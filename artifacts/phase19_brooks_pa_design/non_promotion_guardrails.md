# Phase19 Non-Promotion Guardrails

Phase19 is a design-only phase. This document records the guardrails that must hold during the Phase19 design phase and remain in force during the Phase19 implementation phase. They apply to Cursor, Codex review, and any future agent.

## Universal guardrails

- No candidate YAML created under `configs/candidates/**/*.yaml`.
- No candidate promotion CLI execution.
- No `python -m intraday.cli.main layer1 select-dry-run ...` execution.
- No `python -m intraday.cli.main layer1 grid ...` (full run) execution.
- No Layer2 router, combiner, conflict policy, daily risk state, or portfolio sizing implementation or configuration.
- No Layer3 frozen-validation configuration or run.
- No WFO (walk-forward optimization) or mini-WFO run.
- No live trading configuration or run.
- No paper trading configuration or run.
- No actual broad/expanded/full Layer1 grid runs at the Phase19 level. Inspect-only is the maximum allowed.
- No economic claims (profit factor, Sharpe, top-row R, drawdown ranking) attached to any Phase19 strategy.
- No H2 (2024H2) used as confirmation evidence. H2 remains diagnostic-only per Phase14/15/16/17/18/18B/18C/18D.
- No top-row ranking of Phase19 strategies by any metric derived from a grid run.

## Phase19 design-only guardrails (this phase)

- Phase19 design is **not** candidate evidence. It is integration and onboarding readiness only.
- Phase19 design output (CSV/MD artifacts) does not enable strategy promotion under any circumstance.
- Phase19 design does NOT authorize implementation. Implementation begins only after Codex review and ChatGPT Pro + user review of this design.
- The Brooks PA strategies 11-20 are not candidates after design completion. They are designs.
- The Brooks PA feature foundation (`pa_brooks_core_v1`, `pa_brooks_range_v1`, `pa_brooks_opening_v1`, `pa_brooks_reversal_v1`, optional `pa_brooks_magnet_v1`) is not a runtime artifact in this phase. No feature kernel or YAML is created.

## Phase19 implementation guardrails (future phase)

These hold once the implementation phase begins.

- Phase19 implementation produces source code, configs, and tests; it does NOT produce candidate YAML, select-dry-run results, or any artifact suggesting candidate readiness.
- Phase19 implementation is **strategy-library/template readiness only**. Output is "registered, validated, inspectable" — not "promotion-ready", "Layer2-ready", or "live/paper-ready".
- Diagnostic strategies (18, 19, 20) must remain diagnostic-only in implementation. They carry `metadata.diagnostic_only: true` and must NOT be promoted to candidate status from Phase19 evidence alone. Their `target_r` ranges in the grid skeletons are deliberately bounded; the target_r grid is diagnostic.
- Brooks core strategies (11-17) must NOT be auto-promoted. Promotion requires a future, explicit, multi-window evidence phase that does not exist yet.
- Phase19 implementation must not retrofit short branches onto current-10 strategies.
- Phase19 implementation must not alter execution truth, fill semantics, or PnL accounting.
- Phase19 implementation must not introduce a second PnL truth path.
- Phase19 implementation must not introduce target-price materialization in the strategy layer. Strategies emit `target_r` only.

## Default-safe behavior preservation

- `configs/execution/intraday_default.yaml` MUST keep `allow_short: false` unchanged.
- All current-10 base configs (under `configs/strategies/base/`) MUST remain unchanged in Phase19 implementation.
- All current-10 grid YAMLs (under `configs/strategies/grids/`) MUST remain unchanged.
- All current-10 metadata YAMLs (under `configs/strategies/metadata/`) MUST remain unchanged.
- All current-10 strategy source files (under `src/intraday/strategies/`) MUST remain unchanged.
- All current-10 unit tests (`tests/unit/test_strategy_<current10>.py`, `tests/unit/test_phase18b_*`, `tests/unit/test_phase18c_*`, `tests/unit/test_phase18d_*`) MUST continue to pass byte-for-byte.

## Artifact hygiene

- Phase19 design artifacts contain ONLY `.md` and `.csv` files under `artifacts/phase19_brooks_pa_design/`.
- No `.parquet`, `.npy`, `.npz`, `.memmap`, `.log`, raw/curated/cache files are committed in this phase or in the implementation phase under any `artifacts/phase19_*/` directory.
- No row-level trades, equity curves, top_runs, or heavy run output is committed.
- `artifacts/layer1_10_strategy_rational_expanded_grid_phase16/runs/` remains untracked local-only hygiene debt and MUST NOT be staged in this phase.
- `CODEX_REVIEW.md` MUST NOT be edited by Cursor in this phase.
- `git add .` is forbidden; only explicit file paths are staged.

## Repository file-class guardrails

| Forbidden to commit | Why |
|---------------------|-----|
| `data/raw/**`, `data/curated/**`, `data/cache/**` | Local-only |
| `*.parquet`, `*.npy`, `*.npz`, `*.memmap`, `*.log` | Heavy data not source |
| Row-level trade or equity dumps | Heavy data |
| `top_runs/**` | Heavy data |
| `configs/candidates/**/*.yaml` | Promotion locked |
| `configs/layer2/**/*.yaml`, `configs/layer3/**/*.yaml` | Layer2/3 locked |
| `configs/wfo/**`, `configs/live/**`, `configs/paper/**` | Future phases only |
| Any Phase19 runtime strategy source file in THIS design phase | Design-only |
| Any Phase19 runtime config YAML in THIS design phase | Design-only |
| Edits to `signal_adapter.py`, `contracts.py`, execution code, current-10 strategies in THIS design phase | Design-only |

## Interpretation rule

A Phase19 design completion label of `PHASE19_BROOKS_PA_DESIGN_COMPLETE` means:

- The design package is parseable and operationalizes existing contracts.
- The design package is ready for Codex review and ChatGPT Pro + user review.
- The implementation phase is provisionally authorized once external review accepts the design.

It does NOT mean:

- The strategies will be profitable.
- The strategies are ranked.
- The strategies are promotion-ready.
- The strategies are Layer2-ready or live/paper-ready.
- The Brooks features will improve any economic metric.
