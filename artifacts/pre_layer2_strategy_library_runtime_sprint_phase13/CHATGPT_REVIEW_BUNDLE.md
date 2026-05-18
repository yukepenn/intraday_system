# Phase 13 — PRE_LAYER2_STRATEGY_LIBRARY_RUNTIME_SPRINT_V1

## Summary

- **Phase:** `PHASE13_PRE_LAYER2_STRATEGY_LIBRARY_RUNTIME_SPRINT_V1`
- **Pre-task HEAD:** `448a721b543a77ef5362378e8d8bdda1d6c9b8c4`
- **Decision:** `PRE_LAYER2_STRATEGY_LIBRARY_RUNTIME_COMPLETE`
- **Next step:** `RUN_LAYER1_STRATEGY_LIBRARY_SMALL_GRID`

## Feature groups added

| Group | Outputs |
| --- | --- |
| `levels` | prior-session OHLC, `open_gap_pct`, dist_to_prior_*_pct |
| `indicators` | `cci_20`, `stoch_k_14`, `stoch_d_14_3` |

New feature configs: `opening_core_v1`, `gap_level_core_v1`, `vwap_level_core_v1`, `indicator_core_v1`, `strategy_library_core_v1`.

`pa_core_v1` and `orb_core_v1` hashes pinned stable in tests.

## Strategies added (long-only signal_v1)

| Strategy | Setup code | Feature set |
| --- | ---: | --- |
| `orb_continuation` | 2001 | `opening_core_v1` |
| `orb_retest_continuation` | 2002 | `opening_core_v1` |
| `failed_orb` | 2003 | `opening_core_v1` |
| `gap_acceptance_failure` | 3001 | `gap_level_core_v1` |
| `vwap_trend_pullback` | 4001 | `vwap_level_core_v1` |
| `vwap_reclaim_reject` | 4002 | `vwap_level_core_v1` |
| `prior_day_level_trap` | 5001 | `gap_level_core_v1` |
| `cci_extreme_snapback` | 6001 | `indicator_core_v1` |
| `stochastic_oversold_cross` | 6002 | `indicator_core_v1` |

Existing anchor: `pa_buy_sell_close_trend` (1001) unchanged.

## Tests / validation

- `pytest` full: **441** passed
- `pytest` smoke: **25** passed
- `compileall`, `doctor`, `validate structure`, `features list/inspect`, `strategies list`: pass
- Real-data `features build QQQ`: skipped (no local curated parquet)

## QT reference

- Local QT path: **unavailable** — implementations follow repo contracts only.

## Known limitations

- Some strategy unit tests are validation/smoke-level; expand synthetic entry/no-lookahead per family in Phase 14 if needed.
- Grids are skeletons (≤24 combos) for Phase 14 plumbing, not tuned alpha.

## Non-goals preserved

See `scope_guard_non_goals.md`.
