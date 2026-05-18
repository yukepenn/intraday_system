# QT reference inventory (read-only)

QT path inspected: `D:\OneDrive - Washington University in St. Louis\QT\src\`

No QT imports. No code ported.

## Features (QT `src/features/`)

| QT module | intraday analogue | Family relevance |
| --- | --- | --- |
| `vwap.py` | `kernels/vwap.py` | PA, ORB, VWAP, GAP |
| `orb.py` | `kernels/orb.py` | ORB, PA |
| `volatility.py` | `kernels/volatility.py` | all |
| `price_action.py` | `kernels/price_action.py` | PA |
| `volume.py` | `kernels/volume.py` | VWAP, GAP |
| `regime.py` | `kernels/regime.py` | PA |
| `indicators.py` | skeleton only | CCI |
| `levels.py` | **missing** | GAP, prior-close strategies |
| `pa_swings.py`, `pa_magnet_columns.py` | **missing** | PA extensions (defer) |
| `channels.py`, `time_features.py` | **missing** | defer |

## Strategies (QT `src/strategies/strategy/`)

| QT strategy | Possible family | intraday status |
| --- | --- | --- |
| `pa_buy_sell_close_trend.py` | PA | implemented (held) |
| `orb_continuation.py` | ORB | **selected second MVP** |
| `failed_orb.py` | ORB variant | defer after continuation MVP |
| `gap_acceptance_failure.py` | GAP | needs levels + gap facts |
| `cci_extreme_snapback.py` | CCI | needs CCI indicator kernel |
| `vwap_reclaim_reject.py` | VWAP | needs session prior-bar facts |
| `vwap_trend_pullback.py` | VWAP | more complex; defer |

## QT controlled candidates (reference only)

`testing_parameters_results/l1_execution_backed_controlled/` contains `GAP_ACCEPTANCE_FAILURE_L1M_*.yaml` and `CCI_EXTREME_SNAPBACK_L1M_*.yaml` — useful for **parameter vocabulary**, not runtime import.

## High-value reference for ORB MVP

`orb_continuation.py` `required_features()`: `vwap`, `vwap_slope_5`, `orb_high/low/mid`, `orb_width_pct`, `after_orb`, `above_orb_high`, `below_orb_low` plus bar OHLC/session fields.

Most ORB bounds exist in `pa_core_v1`; gaps are `vwap_slope_5`, `orb_width_pct` (derivable), and boolean flags (strategy timing vs bar `minute` + ORB features).
