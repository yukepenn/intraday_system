# Phase 5 review bundle — PA strategy signal MVP

## Git baseline

- Branch: `main`
- Pre-work HEAD: `ef7dcd34c2c22cda6679d7ca2df19d852bfe2474` (matched `origin/main`)
- Post-work: see `git log -1` after Phase 5 commit

## Why Phase 5

Phase 4 delivered `FeatureMatrix` market facts. Phase 5 proves the strategy contract: strategies consume features and emit `SignalMatrix` without execution, PnL, or Layer1.

## Strategy contract

- Inputs: `BarMatrix`, `FeatureMatrix`, YAML config
- Output: `SignalMatrix` (`signal_v1`)
- Non-entry: `side=0`, NaN stop/target_r/score, `setup_code=0`
- Entry (long-only): `side=+1`, finite stop below close, `target_r>0`, setup code `1001`
- `signal_hash` = SHA-256(strategy identity + config hash + feature_hash)
- Normative: `docs/STRATEGY_CONTRACT.md`

## PA configs

- Base: `configs/strategies/base/pa_buy_sell_close_trend.yaml` (runtime)
- Metadata: `configs/strategies/metadata/pa_buy_sell_close_trend.yaml`
- Grid: `configs/strategies/grids/pa_buy_sell_close_trend_focused.yaml` (not swept)

## Registry / loader / validation

Built-in `pa_buy_sell_close_trend` via `register_builtin_strategies()`. Loader + PA-specific validation for entry window, stop modes, `target_r`, `long_only`.

## PA signal logic

Long-only entries when PA-core thresholds pass and stop is valid (`signal_low`, `rolling_low`, or `atr_buffer`). Score mode `simple_pa_v1`. Not full QT parity (uses `trend_slope_like_20` / `close_vs_rolling_mean_20` instead of QT trend_score / climax filters).

## SignalMatrix semantics

Validated by `validate_signal_matrix`. Execution enters next bar open (future phase wiring).

## No-lookahead tests

Future mutations to features/bars after index `k` do not change signals at indices `<= k`. Current-bar feature changes may affect signal at `t` (bar-close rule).

## Local QQQ signal smoke

48360 rows, 4092 entries, `signal_hash` `ad0aa021cdd2001d687652328d5ef6bc772a1455b632eaf55d842df1275149cc`, no cache written. Details: `local_qqq_signal_smoke.md`.

## Validation results

257 pytest passed; ruff + compileall green. See `validation_results.md`.

## Explicit non-implemented

Layer1 runner, backtest sweep, candidate generation, GAP/CCI strategies, Layer2 router, Layer3 validation, management overlays, portfolio sizing, broad research, strategy fast kernels, PnL outside execution.

## Risks / blockers

- PA logic is MVP approximation vs QT (documented).
- Entry rate on QQQ 2024H1 ~8.5% — not profitability-tested.
- `max_trades_per_day` in config not enforced in signal generator (Layer1/execution concern).

## Decision

`PA_STRATEGY_MVP_COMPLETE`

## Recommended next step

`IMPLEMENT_LAYER1_PA_SMOKE_RUN`
