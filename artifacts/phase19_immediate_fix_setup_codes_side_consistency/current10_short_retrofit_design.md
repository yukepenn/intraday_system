# Current-10 Short Retrofit Design (Phase19 Immediate Fix)

This document records the per-strategy short-side logic added to each
current-10 strategy. Default behavior remains `long_only`; short branches
activate only when `signal.side_mode` is `short_only` or `both`.

## Generic helpers (`src/intraday/strategies/common.py`)

- `compute_short_stop(...)` mirrors `compute_long_stop` and supports
  `signal_high`, `rolling_high_20`, `atr_buffer`, `orb_high`, `orb_mid`,
  `vwap_atr_buffer`, `prior_high_buffer`.
- `build_side_aware_signal_matrix(...)` builds a `SignalMatrix` from
  `long_entry`/`short_entry` candidates, applies `side_mode` filtering,
  enforces `long_stop < close` and `short_stop > close`, makes the per-bar
  side decision mutually exclusive (long wins), thins by
  `max_trades_per_day` if provided, and emits per-side setup codes.

## Validators

- `validate_side_aware_strategy_base(...)` accepts `allowed_side_modes`
  explicitly. `validate_long_only_strategy_base(...)` remains a
  backward-compat wrapper. `CURRENT10_SIDE_MODES = (long_only,
  short_only, both)` is the default for the current-10 validators.

## Per-strategy short logic

| Strategy | Short trigger (summary) | Short stop default | Short setup code |
| --- | --- | --- | --- |
| pa_buy_sell_close_trend | body_pct >= min, (1 - close_pos) >= cp_min, trend_slope <= -trend_min, close_vs_mean <= -cv_min; symmetric VWAP / rolling-low filters | signal_high (mapped from signal_low) | 8001 |
| orb_continuation | close < orb_low - breakout_buffer; symmetric VWAP/slope filters | signal_high / orb_high / orb_mid / atr_buffer | 9001 |
| orb_retest_continuation | prior breakdown below orb_low, retest upward, close stays below orb_low | symmetric per long_stop_mode | 9002 |
| failed_orb | prior breach above orb_high, reject back below orb_high or orb_mid | symmetric per long_stop_mode | 9003 |
| gap_acceptance_failure | gap_up, rejection back below prior_close / VWAP / prior_high | symmetric per long_stop_mode | 10001 |
| vwap_trend_pullback | close below VWAP, vwap_slope <= -min_vwap_slope, rally back near VWAP | signal_high / rolling_high_20 / vwap_atr_buffer / atr_buffer | 11001 |
| vwap_reclaim_reject | prior above-VWAP state, current close rejects below VWAP threshold | signal_high / vwap_atr_buffer / atr_buffer | 11002 |
| prior_day_level_trap | breach above short_level_type (default prior_high), reject back below | signal_high / prior_high_buffer / atr_buffer | 12001 |
| cci_extreme_snapback | CCI was overbought, crosses below cross_below_threshold; symmetric VWAP / slope filters | signal_high / rolling_high_20 / atr_buffer | 13001 |
| stochastic_oversold_cross | K was overbought, K crosses below D; symmetric filters | signal_high / rolling_high_20 / atr_buffer | 13002 |

## Non-goals (this phase)

- No execution `allow_short` toggling inside strategy YAMLs.
- No economic Layer1 grid runs.
- No candidate YAML, no select-dry-run, no promotion.
- No Layer2/3, no WFO, no live/paper.
- No new feature kernels; reduced-feature short variants used where a
  required feature was unavailable.

## Backward compatibility

- Default behavior of every current-10 strategy remains `long_only`.
- Missing `side_mode` validates as `long_only`.
- Legacy `signal.side: long_only` still validates.
- Compatibility is defined as behavior equivalence, not raw hash identity.
  `compute_signal_hash(...)` includes the resolved strategy config hash, so
  migrating a config key from `signal.side` to canonical `signal.side_mode`
  can legitimately change `strategy_config_hash` / `signal_hash` even when
  generated entries, sides, stops, targets, scores, setup codes, and trade
  behavior are equivalent.
