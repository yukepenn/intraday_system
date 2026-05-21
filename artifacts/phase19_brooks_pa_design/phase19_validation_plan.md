# Phase19D — Validation Plan (For Future Implementation Phase)

This document lists the commands the **future implementation phase** must run and pass. **No** runtime command in this list is executed by the design phase. The design phase only runs the design-validation commands recorded in `validation_results.csv`.

## 1. Design-phase commands (executed in THIS Cursor task)

| Command | Purpose | Allowed in design-only phase |
|---------|---------|------------------------------|
| `git status --short` | Preflight | yes |
| `git log --oneline -10` | Preflight | yes |
| `git branch --show-current` | Preflight | yes |
| `python -m intraday.cli.main --help` | CLI sanity | yes |
| `python -m intraday.cli.main doctor` | Environment diagnostics | yes |
| `python -m intraday.cli.main validate structure` | Repo structure | yes |
| `python -m compileall -q src tests` | Compilation sanity | yes |
| `python -m pytest -q tests/unit/test_phase19_design_artifact_schema.py` | Phase19 artifact schema (if added) | yes |
| `python -m pytest -q tests/unit/test_phase19_design_no_runtime_leakage.py` | Phase19 no-runtime-leakage guard (if added) | yes |
| `python -m ruff check src tests` | Lint | yes |
| `python -m ruff format --check src tests` | Format check | yes |

If `python -m ruff check src tests` fails due to OneDrive/Windows `.ruff_cache` access denied, rerun with `python -m ruff check --no-cache src tests`. Both modes are acceptable for design-only validation.

## 2. Implementation-phase commands (must NOT be run in the design phase)

The future Phase19 implementation phase must run these and record results to its own `validation_results.csv`. None of these are allowed in this design-only phase.

### Phase19A — Side support implementation

| Command | Purpose |
|---------|---------|
| `python -m pytest -q tests/unit/test_phase19_side_support_contract.py` | Side-aware SignalMatrix contract |
| `python -m pytest -q tests/unit/test_phase19_signal_adapter_short_support.py` | Adapter accepts short; rejects only `side ∉ {LONG,SHORT}` |
| `python -m pytest -q tests/unit/test_phase19_side_mode_default_safe.py` | Default execution config remains `allow_short=false`; current-10 unchanged |
| `python -m pytest -q tests/smoke` | Existing smoke suite still passes |
| `python -m pytest -q tests/parity/test_execution_fast_parity.py` | Execution parity preserved |

### Phase19B — Brooks PA feature foundation

| Command | Purpose |
|---------|---------|
| `python -m intraday.cli.main features list` | Feature group registration includes new Brooks groups |
| `python -m intraday.cli.main features inspect --config configs/features/pa_brooks_core_v1.yaml` | Slice F1 inspect |
| `python -m intraday.cli.main features inspect --config configs/features/pa_brooks_range_v1.yaml` | Slice F1 inspect |
| `python -m intraday.cli.main features inspect --config configs/features/pa_brooks_opening_v1.yaml` | Slice F2 inspect |
| `python -m intraday.cli.main features inspect --config configs/features/pa_brooks_reversal_v1.yaml` | Slice F3 inspect |
| `python -m pytest -q tests/unit/test_phase19_brooks_features.py` | No-lookahead / session reset / determinism / bounds / inf rejection |

### Phase19C — Strategies 11-20

For each strategy `S ∈ {pa_second_entry_pullback, pa_trading_range_bls_hs, pa_failed_breakout_trap, pa_opening_reversal_sr, pa_breakout_pullback_continuation, pa_tight_channel_pullback, pa_broad_channel_zone, pa_mtr_reversal_diagnostic, pa_wedge_reversal_diagnostic, pa_climax_reversal_diagnostic}`:

| Command | Purpose |
|---------|---------|
| `python -m intraday.cli.main strategies list` | Phase19 strategies registered (count goes from 10 to 20) |
| `python -m intraday.cli.main strategies inspect --strategy S --config configs/strategies/base/phase19/S.yaml` | Per-strategy base config inspect |
| `python -m intraday.cli.main layer1 grid-inspect --config configs/layer1/phase19_brooks_pa_grid_inspect/qqq_2024h1_S_grid_inspect.yaml` | Per-strategy Layer1 grid-inspect-only |
| `python -m pytest -q tests/unit/test_phase19_brooks_strategy_configs.py` | Validators reject invalid YAML |
| `python -m pytest -q tests/unit/test_phase19_brooks_strategy_signals.py` | SignalMatrix contract + side_mode permutations + setup codes + deterministic hash |
| `python -m pytest -q tests/unit/test_phase19_missing_features.py` | Missing-feature ConfigError fail-closed |
| `python -m pytest -q tests/unit/test_phase19_no_lookahead.py` | No-lookahead and session reset for long and short branches |
| `python -m pytest -q tests/unit/test_phase19_no_runtime_leakage.py` | No parquet/cache/PnL/execution in strategy modules |

### Phase19D — Artifact schema + guardrails

| Command | Purpose |
|---------|---------|
| `python -m pytest -q tests/unit/test_phase19_artifact_schema.py` | Required artifacts exist; CSV schemas correct; key tables present |
| `python -m ruff check src tests` (`--no-cache` fallback acceptable) | Lint |
| `python -m ruff format --check src tests` | Format check |

## 3. Forbidden commands (never run by Phase19 implementation either)

The following commands are forbidden in **both** the design phase and the implementation phase. They are listed here so the future implementation phase remembers the non-goals.

| Command | Why forbidden |
|---------|---------------|
| `python -m intraday.cli.main layer1 grid ...` (full run) | No actual Layer1 grid runs in Phase19 |
| `python -m intraday.cli.main layer1 select-dry-run ...` | No selection in Phase19 |
| Candidate YAML export/promotion CLI (any) | No promotion in Phase19 |
| Layer2 router commands (any) | Layer2 stays locked |
| Layer3 frozen-validation commands (any) | Layer3 stays locked |
| WFO commands (any) | Walk-forward locked |
| Live / paper commands (any) | Live/paper locked |
| Heavy data download (any) | Out of scope |
| Broad grid runs (any) | Out of scope |

## 4. Layer1 grid-inspect-only doctrine

The Phase19 inspect-only configs under `configs/layer1/phase19_brooks_pa_grid_inspect/` must satisfy:

- `output.artifact_root` is a repo-relative path; never absolute.
- `grid.allow_prefix_slicing: false`.
- `grid.require_no_fixed_grid_overlap: true`.
- `grid.max_combos <= 24`.
- `description` documents that this is inspect-only and must not be run as a research grid.
- `execution.config` points at `configs/execution/intraday_default.yaml` (or a future `configs/execution/intraday_default_short_enabled.yaml` once that file exists under explicit approval).

`python -m intraday.cli.main layer1 grid-inspect` is the only Layer1 command allowed during Phase19 implementation. `layer1 grid` (full run) and `layer1 select-dry-run` remain forbidden.

## 5. Recording results

Every command run in the implementation phase must be recorded as a row in that phase's `artifacts/<future_dir>/validation_results.csv` with `command`, `status` ∈ `{pass, fail, cache_error, not_run}`, and `notes`.

## 6. Non-economic interpretation rule

Phase19 implementation may say strategies 11-20 are **registered, validated, and inspectable**. It must NOT say they are **profitable, ranked, promotion-ready, Layer2-ready, or live/paper-ready**. Inspect output is configuration readiness, not alpha evidence.
