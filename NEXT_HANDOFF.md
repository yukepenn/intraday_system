# NEXT_HANDOFF

Last updated: **2026-05-15** (Phase 5 PA strategy signal MVP).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Pre-Phase-5 baseline: `ef7dcd34c2c22cda6679d7ca2df19d852bfe2474`
- After commit: `git log -1 --oneline` / `git rev-parse HEAD`
- Windows: `git config --global --add safe.directory <repo>` if needed

## B. Task scope

Phase **5**: **PA strategy signal MVP** — `BarMatrix` + `FeatureMatrix` + strategy YAML → `SignalMatrix` (no execution, no PnL, no Layer1).

**In scope:** `docs/STRATEGY_CONTRACT.md`, `SignalMatrix` validation + `signal_hash`, strategy registry/loader/validation, `pa_buy_sell_close_trend`, PA base/metadata/grid YAML, `strategies` CLI, synthetic + no-lookahead tests, `artifacts/strategy_pa_phase5/`.

**Out of scope:** Layer1/2/3, backtests, PnL, execution calls from strategy, GAP/CCI/VWAP/ORB strategies, candidate YAML, grid sweeps, management, portfolio sizing, strategy fast kernels.

## C. Strategy contract

- Inputs: `BarMatrix`, `FeatureMatrix`, strategy config; no parquet.
- Output: `SignalMatrix` only (`signal_v1`).
- Non-entry: `side=0`, NaN stop/target_r/score, `setup_code=0`.
- Entry (Phase 5 long-only): `side=+1`, finite stop `< close`, `target_r>0`, finite score, setup code `1001`.
- Timing: signal at bar close; current-bar features allowed; no future bars.
- Missing feature columns → `ConfigError`.
- Normative: `docs/STRATEGY_CONTRACT.md`.

## D. Strategy configs / metadata / grid

- **Base:** `configs/strategies/base/pa_buy_sell_close_trend.yaml`
- **Metadata:** `configs/strategies/metadata/pa_buy_sell_close_trend.yaml`
- **Grid skeleton:** `configs/strategies/grids/pa_buy_sell_close_trend_focused.yaml` (not run in Phase 5)

## E. Registry / loader / validation

- `register_builtin_strategies()` → `pa_buy_sell_close_trend`
- `load_strategy_config` / `load_strategy_metadata` / `load_strategy_grid` / `validate_strategy_config`
- PA validation: entry window 0..389, `long_only`, stop modes, `target_r>0`

## F. PA signal logic

- Module: `src/intraday/strategies/pa/buy_sell_close_trend.py`
- Required features: `body_pct`, `close_position_in_range`, `trend_slope_like_20`, `close_vs_rolling_mean_20`, `vwap_side`, `atr_like_20`, `rolling_low_20`, `bar_range`
- Stop modes: `signal_low`, `rolling_low`, `atr_buffer`
- Score: `simple_pa_v1`
- Not QT-exact (no climax/CBC3 filters)

## G. SignalMatrix semantics

- `validate_signal_matrix` in `intraday.strategies.contracts`
- `compute_signal_hash` includes strategy version, config hash, feature_hash

## H. No-lookahead tests

- `tests/unit/test_strategy_pa_buy_sell_close_trend.py` — future feature/bar mutations + current-bar rule
- Artifact: `artifacts/strategy_pa_phase5/no_lookahead_tests.*`

## I. Local QQQ signal smoke

- QQQ 2024-01-01..2024-06-30: 48360 rows, 4092 entries, `signal_hash` `ad0aa021cdd2001d687652328d5ef6bc772a1455b632eaf55d842df1275149cc`
- `--no-cache` / `cache_used: false`; no row-level signal files written
- See `artifacts/strategy_pa_phase5/local_qqq_signal_smoke.*`

## J. Tests / validation

- `python -m compileall -q src` — pass
- `pytest -q` — **257** passed
- Ruff format/check — pass
- CLI: `--help`, `doctor`, `validate structure`, `strategies list|inspect|generate-smoke` — pass
- Data/feature smoke (local curated): pass

See `artifacts/strategy_pa_phase5/validation_results.*`.

## K. Explicit non-implemented items

- Layer1 runner; backtest sweep; candidate generation; GAP/CCI strategies; Layer2 router; Layer3 validation; management overlays; portfolio sizing; broad sweeps; strategy fast kernels; PnL outside execution; `max_trades_per_day` enforcement in signal generator.

## L. Risks / blockers

- PA MVP ≠ full QT parity.
- High local entry count not validated for edge quality.
- Git `safe.directory` on some Windows setups.

## M. Files changed (high level)

- `src/intraday/strategies/{contracts,registry,loader,config_validation,pa/buy_sell_close_trend.py}`
- `src/intraday/cli/{main,strategy_cmds}.py`
- `configs/strategies/{base,metadata,grids}/pa_buy_sell_close_trend*.yaml`
- `docs/STRATEGY_CONTRACT.md`, `docs/{LAYER_FLOW,PHASE_PLAN}.md`
- `tests/unit/test_strategy_*.py`, `tests/smoke/test_strategy_cli.py`, `tests/helpers/strategy.py`
- Status: `README.md`, `PROJECT_STATUS.md`, `PROGRESS.md`, `CHANGES.md`, `NEXT_HANDOFF.md`
- `artifacts/strategy_pa_phase5/*`

## N. Artifact hygiene

- No raw/curated parquet, feature/signal cache, npy/npz/memmap, or row-level signals staged.

## O. Decision

`PA_STRATEGY_MVP_COMPLETE`

## P. Recommended next step

`IMPLEMENT_LAYER1_PA_SMOKE_RUN`
