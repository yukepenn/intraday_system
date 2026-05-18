# Feature requirements audit

Feature set baseline for ORB MVP: **`pa_core_v1`** (reuse) plus optional **`orb_core_v1`** extension in a future mini foundation phase.

## ORB continuation (`orb_continuation`)

| Fact | Available | Column / source | Action |
| --- | --- | --- | --- |
| ORB high/low/mid/range | yes | `orb_*_15` | available_now |
| VWAP + side | yes | `vwap`, `vwap_side` | available_now |
| ATR-like | yes | `atr_like_20` | available_now |
| Bar OHLC + minute | yes | `BarMatrix` | available_now (not FeatureMatrix) |
| Breakout vs ORB | strategy | compare `close` vs `orb_high` | strategy logic OK |
| After ORB window | strategy | `bars.minute >= open_minutes` | strategy logic OK |
| VWAP slope 5 | no | — | add_generic_feature_later (`vwap_slope` kernel) |
| ORB width % | partial | from `orb_range`/`orb_mid` | add_generic_feature_later or strategy ratio (prefer feature) |
| Prior day close | no | — | defer (GAP family) |
| CCI | no | — | defer (CCI family) |

## GAP acceptance/failure (deferred)

Requires `prior_day_close`, `session_open`, `gap_prior_range_norm` — **levels** feature group not in intraday.

## CCI extreme snapback (deferred)

Requires `cci` + session oversold history — `indicators.compute_cci` not implemented.

## VWAP reclaim (deferred)

Requires `prev_high`, `prev_close`, `wrong_stack`, session rolling priors — not in `pa_core_v1`.

## Rules applied

- No strategy-specific signal features (e.g. `entry_trigger_flag` as a column).
- Market facts stay in features; boolean breakout timing may use `BarMatrix.minute` + ORB columns.
- Bulk QT import rejected.
