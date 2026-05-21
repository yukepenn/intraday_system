# Feature / Strategy Contract Audit (Phase19 Immediate Fix)

## Strategy contract compliance after the immediate fix

All current-10 and Phase19 core strategies remain compliant with the
Strategy contract after this immediate fix:

- Strategies consume `BarMatrix + FeatureMatrix + strategy YAML` only.
- Strategies emit `SignalMatrix` only; no execution call, no PnL
  computation, no entry/target price materialization.
- Strategies must not read parquet/cache directly. None do.
- Strategies must not compute ad-hoc market-fact features.
  - Short-side branches were retrofitted using **existing** feature
    columns. No new ad-hoc features were introduced.
  - `pa_buy_sell_close_trend`, `vwap_trend_pullback`, `cci_extreme_snapback`,
    `stochastic_oversold_cross` now request `rolling_high_20` from the
    feature matrix only when `side_mode != long_only`. The column comes
    from existing feature kernels.
- `target_r` only; no target prices materialized.
- Missing required features still raise `ConfigError` / fail closed.
  This is enforced by the same `require_feature_columns(...)` call.
- `side_mode` controls what a strategy may emit; execution `allow_short`
  remains the final authority. Strategy YAMLs do not override execution
  `allow_short`.

## Feature contract compliance

- No new feature kernels were added in this immediate fix.
- No new feature labels were added; no `should_buy` / `should_short` labels.
- No outcome labels were added; no PnL/R/fill labels.
- No centered pivots.
- Existing rolling/cumulative intraday features remain session-aware.
- No QT runtime dependency was introduced.

## Setup-code governance

- `src/intraday/strategies/setup_codes.py` is the single authoritative
  runtime registry.
- Metadata YAMLs and audit artifacts match the registry.
- CSV/MD artifacts are audit-only; runtime never reads them.
- Future code ranges are reserved in the same module.

## Execution semantics

- Execution PnL/R/accounting semantics are unchanged.
- The signal adapter and Layer1 runner are unchanged in this immediate
  fix.

## Non-runs

- No actual Layer1 economic grids.
- No expanded/full grids.
- No `select-dry-run`.
- No candidate YAML created.
- No promotion.
- No Layer2/3.
- No WFO/live/paper.
- No economic claims.
