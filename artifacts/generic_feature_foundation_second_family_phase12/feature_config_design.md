# Feature config design

New config **`configs/features/orb_core_v1.yaml`** — does **not** modify `pa_core_v1.yaml`.

| Group | Outputs | Rationale |
| --- | --- | --- |
| vwap | vwap, vwap_slope_5 | VWAP reference + slope for ORB filters |
| orb | orb_high/low/mid/range/width_pct @ 15m | Opening range facts |
| volatility | atr_like_20, range_mean_20 | Risk/context sizing facts |

**Hash impact:** `pa_core_v1` hash unchanged (config untouched). New `orb_core_v1` hash: `e3c3df12cb5a2bdd787d5a5deaeada374d9b0787d7c0b993a309eb5bfc03d27d` (9 columns).
